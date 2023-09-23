# documents/search.py
import logging
import os
import re
from datetime import datetime
from typing import List, Optional

import openai
import qdrant_client
import tiktoken
import requests
from django.conf import settings
from langchain import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import VertexAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever, Document
from langchain.vectorstores import Qdrant
from paradigm_client.remote_model import RemoteModel
from pydantic import BaseModel
from transformers import AutoTokenizer, pipeline

from ai.services.anonymize_service import Anonymizer
from ai.services.embedding import get_embedding, get_query_prefix
from documents.models import Category

logger = logging.getLogger("cassandre")


class DocsRetriever(BaseRetriever, BaseModel):
    """ Simple BaseRetriever for qa chain """
    documents: List[Document]

    def get_relevant_documents(self, query: str) -> List[Document]:
        return self.documents

    async def aget_relevant_documents(self, query: str) -> List[Document]:
        raise NotImplementedError

class DocumentSearch:

    def __init__(self, category):
        self.abbreviation_dict = {"sft": "supplément familial de traitement", "iff": "indemnité forfaitaire de formation"}
        self.category = category
        self.embeddings = get_embedding()
        self.query_prefix = get_query_prefix()
        url = settings.QDRANT_URL
        self.client = qdrant_client.QdrantClient(url=url, prefer_grpc=True)
        self.docsearch = Qdrant(self.client, self.category.slug, self.embeddings.embed_query)

    def get_relevant_documents(self, query, threshold=0.80, k=6):
        query = self.normalize_query(query)
        res = self.docsearch.similarity_search_with_score(query, k=self.category.k)
        documents: List[Document] = []
        for doc, score in res:
            if score < threshold:
                continue
            page = doc.metadata.get("page", "")
            source = doc.metadata.get("origin", "")
            
            doc.page_content = (
                f"{doc.page_content}\nsource: {source} - page {page}\n"
            )
            documents.append(doc)
        return documents

    def hyde_query(self, query):
        hypothetical_prompt_template = PromptTemplate(
            input_variables=["question"],
            template=f"""{{question}}""",
        )
        hypothetical_prompt = hypothetical_prompt_template.format(question=query)
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "En tant que Cassandre, experte en mouvement inter-académique des enseignants, Cassandre, transforme la question en réponse hypothetique"},
                {"role": "user", "content": hypothetical_prompt},
            ],
        )

        return response['choices'][0]['message']['content']

    def normalize_query(self, query):
        query = query.lower()
        for abbr, full_form in self.abbreviation_dict.items():
            query = re.sub(fr'\b{abbr}\b', f'{abbr} ({full_form})', query)
        return f"{self.query_prefix}{query}"

def search_documents(query, history, engine="gpt-3.5-turbo", category_slug="documents", callback=None):
    query = Anonymizer().anonymize(query)
    category = Category.objects.get(slug=category_slug)

    document_search = DocumentSearch(category=category)
    documents = document_search.get_relevant_documents(query)

    if engine == "falcon":
        return query_falcon(category, query, documents)
    if engine == "paradigm":
        return query_lighton(category, query, documents)
    elif engine == "fastchat":
        return query_fastchat(category, query, documents)
    elif engine == "vertexai":
        return query_vertexai(category, query, documents)
    else:
        return query_openai(category, query, documents, engine, callback=callback)


def query_lighton(category, query, documents):
    host_ip = os.environ["PARADIGM_HOST"]
    model = RemoteModel(host_ip, model_name="llm-mini")

    context = "###\n".join([doc.page_content for doc in documents])
    prompt_template = PromptTemplate(
        input_variables=["question", "context"],
        template=category.prompt
    )

    # Utilise l'API Tokenize pour obtenir les ID de tokens pour "Je ne sais pas"
    tokenize_response = model.tokenize("Je ne sais pas")

    # Récupére les ID de tokens à partir de la réponse
    token_ids = [list(token.values())[0] for token in tokenize_response.tokens]

    # Ajoute un biais positif pour ces tokens
    biases = {token_id: 5 for token_id in token_ids}

    prompt = prompt_template.format(context=context, question=query)

    logger.debug("### paradigm")
    logger.debug(f"Prompt: {prompt}")
    logger.debug(f"Number of tokens: {len(model.tokenize(prompt).tokens)}")

    stop_words = ["\n\n", "\nQuestion:"] # List of stopping strings to use during the generation
    parameters = {
        "n_tokens": 200,
        "temperature": 0,
        "biases": biases,
        "stop_regex": r"(?i)(" + "|".join(re.escape(word) for word in stop_words) + ")"
    }

    paradigm_result = model.create(prompt, **parameters)
    if hasattr(paradigm_result, "completions") and len(paradigm_result.completions) > 0:
        return {"result": paradigm_result.completions[0].output_text}
    else:
        return {"result": "No completions found"}


def query_openai(category, query, documents, engine, callback):
    now = datetime.now()
    formatted_date_time = now.strftime("%d %B %Y à %H:%M")

    prompt_template = PromptTemplate(
        input_variables=["question", "context"],
        template=f"{category.prompt}"
    )

    context = "\n".join([doc.page_content for doc in documents])
    prompt = prompt_template.format(context=context, question=query)
    enc = tiktoken.get_encoding("cl100k_base")
    logger.debug(f"Prompt: {prompt}")
    logger.debug(f"Number of tokens: {len(enc.encode(prompt))}")

    callbacks = [callback] if callback is not None else []

    if engine == "gpt-3.5-turbo-instruct":
        llm = OpenAI(streaming=True, temperature=0, model_name=engine, callbacks=callbacks)
    else:
        llm = ChatOpenAI(streaming=True, temperature=0, model_name=engine, callbacks=callbacks)

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=DocsRetriever(documents=documents),
    )
    qa.combine_documents_chain.llm_chain.prompt = prompt_template

    results = qa({"query": query}, return_only_outputs=True)
    return results

def query_falcon(category, query, documents):
    now = datetime.now()
    formatted_date_time = now.strftime("%d %B %Y à %H:%M")

    prompt_template = PromptTemplate(
        input_variables=["question", "context"],
        template=f"{category.prompt}"
    )

    context = "\n***\n" + "\n***\n".join([doc.page_content for doc in documents]) + "\n***\n"
    prompt = prompt_template.format(context=context, question=query)
    logger.debug(f"Prompt: {prompt}")

    data = {
        "system": "Only respond if the answer is contained in the text above",
        "messages": [prompt],
        "max_tokens": 500,
        "temperature": 0.2,
        "top_k": 10,
        "top_p": 0.5
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(settings.TEXT_SYNTH_API_KEY)
    }

    response = requests.post('https://api.textsynth.com/v1/engines/falcon_40B-chat/chat', headers=headers, json=data)
    response_json = response.json()
    return {"result": response_json['text']}


def query_vertexai(category, query, documents):
    now = datetime.now()
    formatted_date_time = now.strftime("%d %B %Y à %H:%M")

    prompt_template = PromptTemplate(
        input_variables=["question", "context"],
        template=f"{category.prompt}"
    )

    context = "\n".join([doc.page_content for doc in documents])
    prompt = prompt_template.format(context=context, question=query)
    enc = tiktoken.get_encoding("cl100k_base")
    logger.debug(f"Prompt: {prompt}")
    logger.debug(f"Number of tokens: {len(enc.encode(prompt))}")

    qa = RetrievalQA.from_chain_type(
        llm=VertexAI(),
        chain_type="stuff",
        retriever=DocsRetriever(documents=documents),
    )
    qa.combine_documents_chain.llm_chain.prompt = prompt_template

    results = qa({"query": query}, return_only_outputs=True)
    return results


def query_fastchat(category, query, documents):
    # model = "tiiuae/falcon-7b-instruct"
    model = "lmsys/fastchat-t5-3b-v1.0"
    tokenizer = AutoTokenizer.from_pretrained(model)
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        # torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        device="mps",
        model_kwargs={
            # "load_in_8bit": False,
            "max_length": 512,
            "temperature": 0.0,
        },
    )
    hf_llm = HuggingFacePipeline(pipeline=pipe)

    now = datetime.now()
    formatted_date_time = now.strftime("%d %B %Y à %H:%M")

    prompt_template = PromptTemplate(
        input_variables=["question", "context"],
        template=category.prompt)

    qa = RetrievalQA.from_chain_type(
        llm=hf_llm,
        chain_type="stuff",
        retriever=DocsRetriever(documents=documents),
    )
    qa.combine_documents_chain.llm_chain.prompt = prompt_template

    results = qa({"query": query}, return_only_outputs=True)
    return results

# documents/search.py
import logging
import os
import re
from datetime import datetime
from typing import List, Optional

import openai
import qdrant_client
import tiktoken
from django.conf import settings
from langchain import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import VertexAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever, Document
from langchain.vectorstores import Qdrant
from paradigm_client.remote_model import RemoteModel
from pydantic import BaseModel
from transformers import AutoTokenizer, pipeline

from documents.anonymize import Anonymizer
from documents.embedding import get_embedding
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
        url = settings.QDRANT_URL
        self.client = qdrant_client.QdrantClient(url=url, prefer_grpc=True)
        self.docsearch = Qdrant(self.client, self.category.slug, self.embeddings.embed_query)

    def get_relevant_documents(self, query, threshold=0.80, k=6):
        query = self.normalize_query(query)
        print(query)
        res = self.docsearch.similarity_search_with_score(query, k=self.category.k)
        documents: List[Document] = []
        for doc, score in res:
            if score < threshold:
                continue
            doc.page_content = (
                f"la source est \"{doc.metadata['origin']}\"\nLe contenu est :\"{doc.page_content}\""
            )
            print(score)
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
        return query

def search_documents(query, history, engine="gpt-3.5-turbo", category_slug="documents", callback=None):
    query = Anonymizer().anonymize(query)
    category = Category.objects.get(slug=category_slug)

    document_search = DocumentSearch(category=category)
    documents = document_search.get_relevant_documents(query)

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

    parameters = {
        "n_tokens": 500,
        "temperature": 0,
        "biases": biases,
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
        template=f"Nous sommes le {formatted_date_time}.{category.prompt}"
    )

    context = "\n".join([doc.page_content for doc in documents])
    prompt = prompt_template.format(context=context, question=query)
    enc = tiktoken.get_encoding("cl100k_base")
    logger.debug(f"Prompt: {prompt}")
    logger.debug(f"Number of tokens: {len(enc.encode(prompt))}")

    callbacks = [callback] if callback is not None else []

    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(streaming=True, temperature=0, model_name=engine, callbacks=callbacks),
        chain_type="stuff",
        retriever=DocsRetriever(documents=documents),
    )
    qa.combine_documents_chain.llm_chain.prompt = prompt_template

    results = qa({"query": query}, return_only_outputs=True)
    return results

def query_vertexai(category, query, documents):
    now = datetime.now()
    formatted_date_time = now.strftime("%d %B %Y à %H:%M")

    prompt_template = PromptTemplate(
        input_variables=["question", "context"],
        template=f"Nous sommes le {formatted_date_time}.{category.prompt}"
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

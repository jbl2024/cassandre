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
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever, Document
from langchain.vectorstores import Qdrant
from paradigm_client.remote_model import RemoteModel
from pydantic import BaseModel
from transformers import pipeline

from documents.anonymize import Anonymizer
from documents.embedding import get_embedding
from documents.models import Category

logger = logging.getLogger("cassandre")


class DocsRetriever(BaseRetriever, BaseModel):
    """Simple BaseRetriever for qa chain"""

    documents: List[Document]

    def get_relevant_documents(self, query: str) -> List[Document]:
        return self.documents

    async def aget_relevant_documents(self, query: str) -> List[Document]:
        raise NotImplementedError


class DocumentSearch:
    def __init__(self, category, k):
        self.category = category
        self.k = k
        self.embeddings = get_embedding()
        url = settings.QDRANT_URL
        self.client = qdrant_client.QdrantClient(url=url, prefer_grpc=True)
        self.docsearch = Qdrant(
            self.client, self.category.slug, self.embeddings.embed_query
        )

    def get_relevant_documents(self, query, threshold=0.80, k=6):
        res = self.docsearch.similarity_search_with_score(query, k=self.k)
        documents: List[Document] = []
        for doc, score in res:
            if score < threshold:
                continue
            doc.page_content = (
                f"source : {doc.metadata['origin']} - page {doc.metadata['page']}\n{doc.page_content}"
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
                {
                    "role": "system",
                    "content": "En tant que Cassandre, experte en mouvement inter-académique des enseignants, Cassandre, transforme la question en réponse hypothetique",
                },
                {"role": "user", "content": hypothetical_prompt},
            ],
        )

        return response["choices"][0]["message"]["content"]


def search_documents_debug(engine, category_id, prompt, k, query, raw_input=False, callback=None):
    query = Anonymizer().anonymize(query)
    category = Category.objects.get(id=category_id)

    document_search = DocumentSearch(category=category, k=k)
    if raw_input:
        documents = []
    else:
        documents = document_search.get_relevant_documents(query)

    if engine == "paradigm":
        return query_lighton(prompt, query, documents, raw_input)
    elif engine == "fastchat":
        return query_fastchat(prompt, query, documents, raw_input)
    else:
        return query_openai(prompt, query, documents, engine, raw_input, callback=callback)


def query_lighton(prompt, query, documents, raw_input):
    host_ip = os.environ["PARADIGM_HOST"]
    model = RemoteModel(host_ip, model_name="llm-mini")

    context = "\n***\n" + "\n***\n".join([doc.page_content for doc in documents]) + "\n***\n"

    if raw_input:
        prompt = "{question}{context}" + prompt
    prompt_template = PromptTemplate(
        input_variables=["question", "context"], template=prompt
    )

    # Utilise l'API Tokenize pour obtenir les ID de tokens pour "Je ne sais pas"
    tokenize_response = model.tokenize("Je ne sais pas")

    # Récupére les ID de tokens à partir de la réponse
    token_ids = [list(token.values())[0] for token in tokenize_response.tokens]

    # Ajoute un biais positif pour ces tokens
    biases = {token_id: 5 for token_id in token_ids}

    prompt = prompt_template.format(context=context, question=query)

    token_count = len(model.tokenize(prompt).tokens)
    logger.debug("*** paradigm")
    logger.debug(f"Prompt: {prompt}")
    logger.debug(f"Number of tokens: {token_count}")

    stop_words = ["\n\n", "\nQuestion:"] # List of stopping strings to use during the generation
    parameters = {
        "n_tokens": 200,
        "temperature": 0,
        "biases": biases,
        "stop_regex": r"(?i)(" + "|".join(re.escape(word) for word in stop_words) + ")"
    }

    paradigm_result = model.create(prompt, **parameters)
    if hasattr(paradigm_result, "completions") and len(paradigm_result.completions) > 0:
        return {"result": paradigm_result.completions[0].output_text, "input": prompt, "token_count": token_count}
    else:
        return {"result": "No completions found"}


def query_openai(prompt, query, documents, engine, raw_input, callback):
    now = datetime.now()
    formatted_date_time = now.strftime("%d %B %Y à %H:%M")

    if raw_input:
        prompt = "{question}{context}" + prompt


    prompt_template = PromptTemplate(
        input_variables=["question", "context"],
        template=f"{prompt}",
    )

    context = "\n***\n" + "\n***\n".join([doc.page_content for doc in documents]) + "\n***\n"
    prompt = prompt_template.format(context=context, question=query)
    enc = tiktoken.get_encoding("cl100k_base")
    token_count = len(enc.encode(prompt))
    logger.debug(f"Prompt: {prompt}")
    logger.debug(f"Number of tokens: {token_count}")

    callbacks = [callback] if callback is not None else []

    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(
            streaming=True, temperature=0, model_name=engine, callbacks=callbacks
        ),
        chain_type="stuff",
        retriever=DocsRetriever(documents=documents),
    )
    qa.combine_documents_chain.llm_chain.prompt = prompt_template

    results = qa({"query": query}, return_only_outputs=True)
    return {"result": results["result"], "input": prompt, "token_count": token_count}


def query_fastchat(prompt, query, documents, raw_input):
    pipe = pipeline(
        task="text2text-generation",
        model="lmsys/fastchat-t5-3b-v1.0",
        model_kwargs={
            "load_in_8bit": False,
            "max_length": 512,
            "temperature": 0.0,
        },
    )
    hf_llm = HuggingFacePipeline(pipeline=pipe)

    now = datetime.now()
    formatted_date_time = now.strftime("%d %B %Y à %H:%M")

    if raw_input:
        prompt = "{question}{context}" + prompt

    prompt_template = PromptTemplate(
        input_variables=["question", "context"], template=prompt
    )

    qa = RetrievalQA.from_chain_type(
        llm=hf_llm,
        chain_type="stuff",
        retriever=DocsRetriever(documents=documents),
    )
    qa.combine_documents_chain.llm_chain.prompt = prompt_template

    results = qa({"query": query}, return_only_outputs=True)
    return results

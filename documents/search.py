# documents/search.py
import locale
import logging
import os
import re
from datetime import datetime
from typing import List, Optional

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

from documents.embedding import get_embedding

logger = logging.getLogger("cassandre")


class DocsRetriever(BaseRetriever, BaseModel):
    documents: List[Document]

    def get_relevant_documents(self, query: str) -> List[Document]:
        return self.documents

    async def aget_relevant_documents(self, query: str) -> List[Document]:
        raise NotImplementedError


def search_documents(query, history, engine="gpt-3.5-turbo"):
    locale.setlocale(locale.LC_TIME, "fr_FR")

    embeddings = get_embedding()
    url = settings.QDRANT_URL
    client = qdrant_client.QdrantClient(url=url, prefer_grpc=True)
    docsearch = Qdrant(client, "documents", embeddings.embed_query)

    res = docsearch.similarity_search_with_score(query, k=7)
    documents: List[Document] = []
    for doc, score in res:
        if score < 0.80:
            continue
        doc.page_content = (
            f"source:'{doc.metadata['origin']}'\ncontenu:{doc.page_content}"
        )
        print(score)
        documents.append(doc)

    if engine == "paradigm":
        return query_lighton(query, documents)
    elif engine == "fastchat":
        return query_fastchat(query, documents)
    else:
        return query_openai(query, documents, engine)


def query_lighton(query, documents):
    host_ip = os.environ["PARADIGM_HOST"]
    model = RemoteModel(host_ip, model_name="llm-mini")

    context = "\n".join([doc.page_content for doc in documents])

    prompt_template = PromptTemplate(
        input_variables=["question", "context"],
        template=f"""Tu es Cassandre et tu réponds aux questions en utilisant **uniquement** les informations contenues dans le document.
Si tu ne connais pas la réponse, tu réponds simplement "Je ne sais pas" sans rien ajouter d'autre. 
Si la réponse n'est pas contenue dans le document, tu réponds "Je ne sais pas".
Si tu ne sais pas répondre, tu n'invente rien.
Tu te base seulement sur le document pour générer la réponse.
Document: \"{{context}}\"
Questions: \"{{question}}\"
Réponse: D'après ce qui est décrit dans ce document, je peux dire que""",
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


def query_openai(query, documents, engine):
    now = datetime.now()
    formatted_date_time = now.strftime("%d %B %Y à %H:%M")

    prompt_template = PromptTemplate(
        input_variables=["question", "context"],
        template=f"""Nous sommes le {formatted_date_time}.
Tu es un un robot qui accompagne les gestionnaires qui gèrent le mouvement inter-académique des enseignants. 
Tu réponds en français au féminin. Ton nom est Cassandre.
Tu n'as pas besoin de dire bonjour, ni de préciser que tu es un robot d'accompagnement.
Si tu ne connais pas la réponse, tu n'inventes rien et tu suggère de contacter le responsable du mouvement. 
Tu réponds en indiquant la source qui t'a permis de répondre à la question (dans le contexte c'est le champ "source:")
Le contexte que tu connais est le suivant:  {{context}}.
La question est la suivante: {{question}}""",
    )

    context = "\n".join([doc.page_content for doc in documents])
    prompt = prompt_template.format(context=context, question=query)
    enc = tiktoken.get_encoding("cl100k_base")
    logger.debug(f"Prompt: {prompt}")
    logger.debug(f"Number of tokens: {len(enc.encode(prompt))}")

    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0, model_name=engine),
        chain_type="stuff",
        retriever=DocsRetriever(documents=documents),
    )
    qa.combine_documents_chain.llm_chain.prompt = prompt_template

    results = qa({"query": query}, return_only_outputs=True)
    return results


def query_fastchat(query, documents):
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

    prompt_template = PromptTemplate(
        input_variables=["question", "context"],
        template=f"""Nous sommes le {formatted_date_time}.
Tu es Cassandre et tu réponds à la question en utilisant **uniquement** les informations contenues dans le document.
Si la réponse n'est pas contenue dans le document, tu réponds "Je ne sais pas". 
Document: {{context}}
Question: {{question}}
Réponse: Selon ce document,""")

    qa = RetrievalQA.from_chain_type(
        llm=hf_llm,
        chain_type="stuff",
        retriever=DocsRetriever(documents=documents),
    )
    qa.combine_documents_chain.llm_chain.prompt = prompt_template

    results = qa({"query": query}, return_only_outputs=True)
    return results

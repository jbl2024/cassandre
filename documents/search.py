# documents/search.py
from django.conf import settings
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from datetime import datetime
from documents.embedding import get_embedding
import qdrant_client
import locale
from paradigm_client.remote_model import RemoteModel
import os
import re
import logging

logger = logging.getLogger('cassandre')


def search_documents(query, history, engine="gpt-3.5-turbo"):
    embeddings = get_embedding()
    url = settings.QDRANT_URL
    client = qdrant_client.QdrantClient(
        url=url, prefer_grpc=True
    )
    docsearch = Qdrant(
        client=client, collection_name="documents", 
        embedding_function=embeddings.embed_query
    )    

    res = docsearch.similarity_search(query, k=4)
    context = ""
    for doc in res:
        cleaned_page_content = re.sub(r'\s+', ' ', doc.page_content.strip())
        context = f"{context}\nsource: f{doc.metadata['origin']} - contenu: {cleaned_page_content}"
        logger.debug(doc)

    if engine == "paradigm":
        return query_lighton(query, context)
    else:
        return query_openai(query, engine, docsearch, context)

def query_lighton(query, context):
    prompt_template =  PromptTemplate(
        input_variables=["question", "context"],
        template=f"""Tu es Cassandre et tu réponds à la question en utilisant **uniquement** les informations contenues dans le document.
Si la réponse n'est pas contenue dans le document, tu réponds "Je ne sais pas". 
Document: {{context}}
Question: {{question}}
Réponse: Selon ce document,""",
    )

    prompt = prompt_template.format(context=context, question=query)
    logger.debug("### paradigm")

    host_ip = os.environ["PARADIGM_HOST"]
    model = RemoteModel(host_ip, model_name="llm-mini")
    logger.debug(prompt)
    logger.debug(len(prompt))
    paradigm_result = model.create(prompt, n_tokens=500, temperature=0)
    if hasattr(paradigm_result, 'completions') and len(paradigm_result.completions) > 0:
        return {'result': paradigm_result.completions[0].output_text}
    else:
        return {'result': 'No completions found'}

def query_openai(query, engine, docsearch, context):
    now = datetime.now()
    formatted_date_time = now.strftime("%d %B %Y à %H:%M")

    prompt_template = PromptTemplate(
        input_variables=["question", "context", "date"],
        template=f"""Nous sommes le {{date}}
Tu es un un robot qui accompagne les gestionnaires qui gèrent le mouvement inter-académique des enseignants. 
Tu réponds en français au féminin. Ton nom est Cassandre.
Tu n'as pas besoin de dire bonjour, ni de préciser que tu es un robot d'accompagnement.
Si tu ne connais pas la réponse, tu n'inventes rien et tu suggère de contacter le responsable du mouvement. 
Tu réponds en indiquant la source qui t'a permis de répondre à la question (dans le contexte c'est le champ "source:")
Le contexte que tu connais est le suivant:  {{context}}.
La question est la suivante: {{question}}""",
    )


    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0, model_name=engine),
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
    )

    prompt = prompt_template.format(context=context, question=query, date=formatted_date_time)
    results = qa({"query": prompt}, return_only_outputs=True)
    return results

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

    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
    now = datetime.now()

    # Formater la date et l'heure en français
    formatted_date_time = now.strftime("%d %B %Y à %H:%M")

    res = docsearch.similarity_search(query, k=4)
    context = ""
    for doc in res:
        context = f"{context}\n{doc.page_content}"
        print(doc)
    prompt = PromptTemplate(
        input_variables=["question", "context", "date"],
        template=f"""
        Nous sommes le {{date}}
        Tu es un un robot qui accompagne les gestionnaires qui gèrent le mouvement inter-académique des enseignants. 
        Tu réponds en français au féminin. Ton nom est Cassandre.
        Tu n'as pas besoin de dire bonjour, ni de préciser que tu es un robot d'accompagnement.
        Si tu ne connais pas la réponse, tu n'inventes rien et tu suggère de contacter le responsable du mouvement. 
        Le context que tu connais est le suivant: {{context}}.
        La question est la suivante: {{question}}
        """,
    )

    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0, model_name=engine),
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
        return_source_documents=True,
        verbose=True
    )

    final_prompt = prompt.format(context=context, question=query, date=formatted_date_time)
    print("#####")
    print(final_prompt)
    print("#####")
    print(len(final_prompt))
    print("#####")
    results = qa({"query": prompt.format(context=context, question=query, date=formatted_date_time)}, return_only_outputs=True)
    return results

# documents/search.py
from django.conf import settings
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from datetime import datetime
import qdrant_client

def search_documents(query, engine="gpt-3.5-turbo"):
    embeddings = OpenAIEmbeddings()
    url = settings.QDRANT_URL
    client = qdrant_client.QdrantClient(
        url=url, prefer_grpc=True
    )
    docsearch = Qdrant(
        client=client, collection_name="documents", 
        embedding_function=embeddings.embed_query
    )    

    now = datetime.now()

    # Formater la date et l'heure en français
    formatted_date_time = now.strftime("%d %B %Y à %H:%M")

    prompt = PromptTemplate(
        input_variables=["question"],
        template=f"""
        Nous sommes le {formatted_date_time}
        Tu es un un robot d'aide pour les enseignants qui participent au mouvement inter-académique, 
        tu réponds en français au féminin. Ton nom est Cassandre.
        Si dans ta réponse tu vas parler des syndicats, tu réponds que tu ne sais pas.
        Si tu ne connais pas la réponse, tu n'inventes rien. 
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

    results = qa({"query": prompt.format(question=query)}, return_only_outputs=True)
    print(results)
    return results

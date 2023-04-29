# documents/search.py
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings

def search_documents(query, persist_directory="chroma_db"):
    embeddings = OpenAIEmbeddings()
    # embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    # embeddings = HuggingFaceEmbeddings(model_name="Cedille/fr-boris")
    docsearch = Chroma(
        persist_directory=persist_directory, embedding_function=embeddings
    )

    prompt = PromptTemplate(
        input_variables=["question"],
        template="Tu es un un robot d'aide pour les enseignants qui participent au mouvement inter-académique, tu réponds en français. Si tu ne connais pas la réponse, tu n'inventes rien. La question est la suivante: {question}",
    )

    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"),
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
        return_source_documents=True,
        verbose=True
    )

    results = qa({"query": prompt.format(question=query)}, return_only_outputs=True)
    print(results)
    return results

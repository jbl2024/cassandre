# documents/search.py
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings


def search_documents(query, persist_directory="chroma_db_st"):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    docsearch = Chroma(
        persist_directory=persist_directory, embedding_function=embeddings
    )

    prompt = PromptTemplate(
        input_variables=["question"],
        template="Je suis un robot d'aide pour les enseignants qui participent au mouvement inter-académique, je réponds en français. La question est la suivante: {question}?",
    )

    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"),
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
        return_source_documents=True
    )

    results = qa({"query": prompt.format(question=query)}, return_only_outputs=False)
    print(results)
    return results

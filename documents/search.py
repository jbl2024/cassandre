# documents/search.py
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

def search_documents(query, persist_directory='chroma_db'):
    embeddings = OpenAIEmbeddings()
    docsearch = Chroma(persist_directory=persist_directory, embedding_function=embeddings)


    prompt = PromptTemplate(
        input_variables=["question"],
        template="Je suis un robot d'aide pour les enseignants qui participent au mouvement inter-académique, je réponds en français. La question est la suivante: {question}?",
    )

    qa = RetrievalQAWithSourcesChain.from_chain_type(OpenAI(temperature=0, model_name="gpt-3.5-turbo"), chain_type="stuff", retriever=docsearch.as_retriever())
    results = qa({"question": prompt.format(question=query)}, return_only_outputs=True)
    print(results)
    return results
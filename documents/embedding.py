from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings import SentenceTransformerEmbeddings 

def get_embedding():
    # return SentenceTransformerEmbeddings(model_name="hkunlp/instructor-xl")
    return OpenAIEmbeddings()

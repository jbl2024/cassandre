from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings import SentenceTransformerEmbeddings 

def get_embedding():
    return SentenceTransformerEmbeddings(model_name="hkunlp/instructor-xl")
    # return SentenceTransformerEmbeddings(model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1")
    # return OpenAIEmbeddings()

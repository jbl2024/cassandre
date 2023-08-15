from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings import SentenceTransformerEmbeddings 

def get_embedding():
    # return SentenceTransformerEmbeddings(model_name="hkunlp/instructor-xl")
    # return SentenceTransformerEmbeddings(model_name="BAAI/bge-small-en")
    return OpenAIEmbeddings()

# Represent this sentence for searching relevant passages:

def get_query_prefix():
    return ""
    # return "Represent this sentence for searching relevant passages:"
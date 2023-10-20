"""
This module provides functions for working with language embeddings.
"""
from langchain.embeddings import OpenAIEmbeddings

from langchain.embeddings.huggingface import (
    HuggingFaceInstructEmbeddings,
    HuggingFaceBgeEmbeddings,
)

EMBEDDING = "intfloat/multilingual-e5-large"


def get_embedding():
    """
    Return an embedding model.

    Returns:
        OpenAIEmbeddings: An instance of the OpenAIEmbeddings class.
    """
    if EMBEDDING == "hkunlp/instructor-xl":
        return HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    if EMBEDDING == "hkunlp/instructor-large":
        return HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")
    elif EMBEDDING == "BAAI/bge-small-en-v1.5":
        return HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    elif EMBEDDING == "BAAI/bge-base-en-v1.5":
        return HuggingFaceBgeEmbeddings(model_name="BAAI/bge-base-en-v1.5")
    elif EMBEDDING == "BAAI/bge-large-en-v1.5":
        return HuggingFaceBgeEmbeddings(model_name="BAAI/bge-large-en-v1.5")
    elif EMBEDDING == "intfloat/multilingual-e5-large":
        return HuggingFaceInstructEmbeddings(
            model_name="intfloat/multilingual-e5-large",
            query_instruction="query: ",
            embed_instruction="passage: ",
        )
    elif EMBEDDING == "openai":
        return OpenAIEmbeddings()


def get_query_prefix():
    """
    Returns the query prefix for searching relevant passages.

    Returns:
        str: A string representing the query prefix.
    """
    return ""

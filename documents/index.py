from django.conf import settings
from langchain.vectorstores import Qdrant
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredFileLoader
from documents.models import Document
from django.core.files.storage import default_storage
import io
import os
import tempfile
from documents.embedding import get_embedding
import logging

logger = logging.getLogger('cassandre')

def index_documents():
    documents = Document.objects.all()
    docs = []

    for document in documents:
        with default_storage.open(document.file.name, "rb") as file:
            file_content = file.read()

            # Extract the file extension from the original file
            file_ext = os.path.splitext(document.file.name)[-1]

            # Create a temporary file with the same extension
            with tempfile.NamedTemporaryFile(
                suffix=file_ext, delete=False
            ) as temp_file:
                logger.info(f"Loading: {document.title or document.file}")
                temp_file.write(file_content)
                temp_file.flush()

                loader = UnstructuredFileLoader(temp_file.name, mode="single")
                loaded_documents = loader.load()
                for doc in loaded_documents:
                    doc.metadata["origin"] = document.title or os.path.basename(
                        document.file.name
                    )
                docs.extend(loaded_documents)
                logger.info(
                    f"Successfully loaded document: {document.title or document.file}"
                )
    logger.info(f"All documents are loaded, splitting data")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(docs)
    logger.info(f"Splitting data done")

    logger.info(f"Indexing data started")
    embeddings = get_embedding()
    url = settings.QDRANT_URL
    Qdrant.from_documents(
        documents=texts,
        embedding=embeddings,
        url=url,
        prefer_grpc=True,
        collection_name="documents",
    )
    logger.info(f"Successfully indexed documents")

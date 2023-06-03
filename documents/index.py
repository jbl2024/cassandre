import io
import logging
import os
import re
import tempfile

from django.conf import settings
from django.core.files.storage import default_storage
from langchain.document_loaders import (PDFMinerLoader, PDFPlumberLoader,
                                        PyPDFLoader, UnstructuredFileLoader)
from langchain.schema import Document as LangchainDocument
from langchain.text_splitter import (NLTKTextSplitter,
                                     RecursiveCharacterTextSplitter)
from langchain.vectorstores import Qdrant

from documents.embedding import get_embedding
from documents.models import Category, Correction, Document


def clean_text(text):
    # Remove duplicated consecutive spaces
    text = re.sub(r"\s+", " ", text)

    # Remove duplicated consecutive end of lines
    text = re.sub(r"\n+", "\n", text)

    # Remove leading and trailing spaces
    text = text.strip()

    # Special case for FAQ documents where each question has a "réponse" block
    # so we add separator so that the splitter will keep question/answer together
    text = text.replace("Question:", "\n\nQuestion:")

    return text


logger = logging.getLogger("cassandre")


def index_documents(category_id=None):
    if category_id is None:
        categories = Category.objects.all()
    else:
        categories = Category.objects.filter(id=category_id)
    for category in categories:
        documents = Document.objects.filter(category=category)
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

                    loader = PDFPlumberLoader(temp_file.name)
                    loaded_documents = loader.load()

                    for doc in loaded_documents:
                        doc.page_content = clean_text(doc.page_content)
                        doc.metadata["origin"] = document.title or os.path.basename(
                            document.file.name
                        )
                    docs.extend(loaded_documents)
                    logger.info(
                        f"Successfully loaded document: {document.title or document.file}"
                    )
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.SPLIT_CHUNK_SIZE,
            chunk_overlap=settings.SPLIT_CHUNK_OVERLAP,
        )
        # disabled for now
        # text_splitter = NLTKTextSplitter(
        #     chunk_size=settings.SPLIT_CHUNK_SIZE,
        #     chunk_overlap=settings.SPLIT_CHUNK_OVERLAP,
        # )
        texts = text_splitter.split_documents(docs)

        corrections = Correction.objects.filter(category=category)
        for correction in corrections:
            document = LangchainDocument(
                page_content=f"Question: {correction.query}\nRéponse: {correction.answer}",
                metadata={
                    "origin": f"correction manuelle",
                    "source": f"correction-{correction.id}",
                    "page": 1,
                },
            )
            texts.append(document)

        embeddings = get_embedding()
        url = settings.QDRANT_URL
        Qdrant.from_documents(
            documents=texts,
            embedding=embeddings,
            url=url,
            prefer_grpc=True,
            collection_name=category.slug,
        )
        logger.info(
            f"Successfully indexed {documents.count()} document(s) and {corrections.count()} correction(s) for category {category.name}"
        )
    logger.info(f"Successfully indexed all documents")

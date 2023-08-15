import io
import logging
import os
import re
import tempfile

import qdrant_client
from django.conf import settings
from django.core.files.storage import default_storage
from langchain.document_loaders import (PDFMinerLoader, PDFPlumberLoader,
                                        PyPDFLoader, TextLoader,
                                        UnstructuredFileLoader,
                                        UnstructuredMarkdownLoader)
from langchain.schema import Document as LangchainDocument
from langchain.text_splitter import (MarkdownTextSplitter, NLTKTextSplitter,
                                     RecursiveCharacterTextSplitter,
                                     SpacyTextSplitter)
from langchain.vectorstores import Qdrant

from documents.embedding import get_embedding
from documents.models import Category, Correction, Document

from .chunk import split_markdown


def clean_text(text, full=True):
    # Remove duplicated consecutive spaces
    if full is True:
        # Remove duplicated consecutive end of lines
        text = re.sub(r"\n+", "\n", text)

        # Remove leading and trailing spaces
        text = text.strip()

        text = re.sub(r"\s+", " ", text)
    # Special case for FAQ documents where each question has a "réponse" block
    # so we add separator so that the splitter will keep question/answer together
    text = text.replace("Question:", "\n\n\n\nQuestion:")

    return text


logger = logging.getLogger("cassandre")


def get_categories(category_id=None):
    return (
        Category.objects.all()
        if category_id is None
        else Category.objects.filter(id=category_id)
    )


def load_and_split_pdf(temp_file, document):
    """
    Load and split a PDF document.

    Args:
        temp_file (File): The temporary file containing the PDF document.
        document (str): The name of the document.

    Returns:
        list: A list of split text documents.
    """
    loader = PDFPlumberLoader(temp_file.name)
    loaded_documents = process_loaded_documents(loader.load(), document)

    text_splitter = SpacyTextSplitter(
        pipeline="fr_core_news_lg",
        chunk_size=settings.SPLIT_CHUNK_SIZE,
        chunk_overlap=settings.SPLIT_CHUNK_OVERLAP,
    )
    return text_splitter.split_documents(loaded_documents)


def load_and_split_md(temp_file, document):
    """
    Load and split a markdown file into smaller documents.

    Args:
        temp_file (File): A temporary file object containing the markdown content.
        document (str): The name of the document.

    Returns:
        list: A list of split documents.

    Raises:
        None

    Notes:
        - This function uses a TextLoader to load the content from the temporary file.
        - The loaded content is then processed using process_loaded_documents().
        - The processed documents are split using a MarkdownTextSplitter.

    """
    loader = TextLoader(temp_file.name)
    loaded_documents = process_loaded_documents(
        loader.load(), document, full_clean=False
    )
    splitted_docs = []
    for doc in loaded_documents:
        items = split_markdown(doc.page_content)
        for item in items:
            splitted_docs.append(
                LangchainDocument(page_content=item, metadata=doc.metadata)
            )

    return splitted_docs
    # text_splitter = MarkdownTextSplitter(
    #     chunk_size=settings.SPLIT_CHUNK_SIZE,
    #     chunk_overlap=settings.SPLIT_CHUNK_OVERLAP,
    # )
    # return text_splitter.split_documents(loaded_documents)


def process_loaded_documents(loaded_documents, document, full_clean=True):
    """
    Process the loaded documents.

    Args:
        loaded_documents (list): A list of documents to be processed.
        document (Document): The document object.

    Returns:
        list: The processed list of documents.
    """
    for doc in loaded_documents:
        doc.page_content = clean_text(doc.page_content, full_clean)
        doc.metadata["origin"] = document.title or os.path.basename(document.file.name)
    return loaded_documents


def index_documents(category_id=None):
    """
    Indexes all the documents in the specified category.

    :param category_id: The ID of the category to index documents for. If not specified, all categories will be indexed.
    """
    categories = get_categories(category_id)

    for category in categories:
        documents = Document.objects.filter(category=category)
        texts = []

        for document in documents:
            with default_storage.open(document.file.name, "rb") as file:
                file_content = file.read()
                file_ext = os.path.splitext(document.file.name)[-1]

                with tempfile.NamedTemporaryFile(
                    suffix=file_ext, delete=False
                ) as temp_file:
                    logger.info(f"Loading: {document.title or document.file}")
                    temp_file.write(file_content)
                    temp_file.flush()

                    if file_ext == ".pdf":
                        texts.extend(load_and_split_pdf(temp_file, document))
                    elif file_ext == ".md":
                        texts.extend(load_and_split_md(temp_file, document))

                    logger.info(
                        f"Successfully loaded document: {document.title or document.file}"
                    )

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
        q = qdrant_client.QdrantClient(url=url, prefer_grpc=True)
        q.delete_collection(category.slug)
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

    logger.info("Successfully indexed all documents")

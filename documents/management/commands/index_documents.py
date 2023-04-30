from django.conf import settings
from django.core.management.base import BaseCommand
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredFileLoader
from documents.models import Document
import os
import shutil

class Command(BaseCommand):
    help = 'Index all documents in the Document app, create embeddings and save them in Chroma vector DB'

    def add_arguments(self, parser):
        parser.add_argument('--persist_directory', type=str, default='chroma_db', help='The directory to persist the Chroma vector database')

    def handle(self, *args, **options):

        documents = Document.objects.all()

        docs = []
        for document in documents:
            loader = UnstructuredFileLoader(document.file.path, mode="elements")
            loaded_documents = loader.load()
            docs.extend(loaded_documents)
            self.stdout.write(self.style.SUCCESS(f'Successfully loaded document: {document.title or document.file}'))

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
        texts = text_splitter.split_documents(docs)

        embeddings = OpenAIEmbeddings()
        url = settings.QDRANT_URL
        Qdrant.from_documents(
            documents=texts,
            embedding=embeddings,
            url=url,
            prefer_grpc=True,
            collection_name="documents"
        )        


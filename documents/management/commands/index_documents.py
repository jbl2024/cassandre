from django.core.management.base import BaseCommand
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import HuggingFaceEmbeddings 
from documents.models import Document
import os
import shutil

class Command(BaseCommand):
    help = 'Index all documents in the Document app, create embeddings and save them in Chroma vector DB'

    def add_arguments(self, parser):
        parser.add_argument('--persist_directory', type=str, default='chroma_db', help='The directory to persist the Chroma vector database')

    def handle(self, *args, **options):
        persist_directory = options['persist_directory']
        # Create persist_directory if it doesn't exist
        if not os.path.exists(persist_directory):
            os.makedirs(persist_directory)
        # Delete all files inside persist_directory if it exists
        else:
            for filename in os.listdir(persist_directory):
                file_path = os.path.join(persist_directory, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to delete {file_path}. Reason: {str(e)}'))

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
        # embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        # embeddings = HuggingFaceEmbeddings(model_name="Cedille/fr-boris")
        Chroma.from_documents(texts, embeddings, persist_directory=persist_directory)


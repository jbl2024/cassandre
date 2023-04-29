from django.core.management.base import BaseCommand
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredFileLoader

from documents.models import Document

class Command(BaseCommand):
    help = 'Index all documents in the Document app, create embeddings and save them in Chroma vector DB'

    def add_arguments(self, parser):
        parser.add_argument('--persist_directory', type=str, default='chroma_db', help='The directory to persist the Chroma vector database')

    def handle(self, *args, **options):
        persist_directory = options['persist_directory']

        documents = Document.objects.all()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

        docs = []
        for document in documents:
            loader = UnstructuredFileLoader(document.file.path, mode="elements")
            loaded_documents = loader.load()
            docs.extend(loaded_documents)
            self.stdout.write(self.style.SUCCESS(f'Successfully indexed document: {document.title or document.file}'))

        texts = text_splitter.split_documents(docs)

        embeddings = OpenAIEmbeddings()
        docsearch = Chroma.from_documents(texts, embeddings, persist_directory=persist_directory)


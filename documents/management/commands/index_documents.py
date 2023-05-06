from django.core.management.base import BaseCommand
from documents.index import index_documents

class Command(BaseCommand):
    help = 'Index all documents in the Document app, create embeddings and save them in Chroma vector DB'

    def add_arguments(self, parser):
        parser.add_argument('--persist_directory', type=str, default='chroma_db', help='The directory to persist the Chroma vector database')

    def handle(self, *args, **options):
        index_documents()

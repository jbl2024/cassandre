from django.conf import settings
from django.core.management.base import BaseCommand
import qdrant_client
from documents.embedding import get_embedding
from documents.index import index_documents
from langchain.vectorstores import Qdrant
from documents.search import search_documents

class Command(BaseCommand):
    help = 'Search inside VectorDB and call LLM for final result'

    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='The query string')
        parser.add_argument('engine', type=str, help='The search engine to use')

    def handle(self, *args, **options):
        query = options['query']      
        engine = options['engine']

        results = search_documents(query, "", engine)  
        self.stdout.write(results['result'])

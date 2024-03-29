from django.conf import settings
from django.core.management.base import BaseCommand
import qdrant_client
from ai.services.embedding import get_embedding
from ai.services.index_service import index_documents
from langchain.vectorstores import Qdrant
from ai.services.search_service import search_documents

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

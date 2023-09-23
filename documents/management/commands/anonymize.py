from django.conf import settings
from django.core.management.base import BaseCommand
import qdrant_client
from ai.services.anonymize_service import Anonymizer
from ai.services.embedding import get_embedding
from ai.services.index_service import index_documents
from langchain.vectorstores import Qdrant

from documents.models import Category
from documents.search import DocumentSearch

class Command(BaseCommand):
    help = 'Anonymize text'

    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='The query string')

    def handle(self, *args, **options):
        query = options['query']        
        anonymized_query = Anonymizer().anonymize(query)

        self.stdout.write(anonymized_query)
        
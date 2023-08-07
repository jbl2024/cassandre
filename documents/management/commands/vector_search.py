from django.conf import settings
from django.core.management.base import BaseCommand
import qdrant_client
from documents.anonymize import Anonymizer
from documents.embedding import get_embedding
from documents.index import index_documents
from langchain.vectorstores import Qdrant

from documents.models import Category
from documents.search import DocumentSearch

class Command(BaseCommand):
    help = 'Search inside vector DB'

    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='The query string')
        parser.add_argument(
            "category_slug", type=str, help="Indicates the slug of the category"
        )

    def handle(self, *args, **options):
        query = options['query']        
        category_slug = options["category_slug"]

        self.stdout.write("Category slug: %s" % category_slug)

        query = Anonymizer().anonymize(query)
        category = Category.objects.get(slug=category_slug)

        document_search = DocumentSearch(category=category)
        documents = document_search.get_relevant_documents(query)
        for doc in documents:
            self.stdout.write(doc.page_content)

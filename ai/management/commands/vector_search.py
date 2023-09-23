from django.core.management.base import BaseCommand

from ai.services.anonymize_service import Anonymizer
from documents.models import Category
from ai.services.search_service import DocumentSearch


class Command(BaseCommand):
    """
    This is the Command class for the management command 'vector_search'.
    It provides a command-line interface to search inside the vector database.
    It takes a query string and a category slug as arguments.
    """

    help = "Search inside vector DB"

    def add_arguments(self, parser):
        parser.add_argument("query", type=str, help="The query string")
        parser.add_argument(
            "category_slug", type=str, help="Indicates the slug of the category"
        )

    def handle(self, *args, **options):
        query = options["query"]
        category_slug = options["category_slug"]

        self.stdout.write(f"Category slug: {category_slug}")

        query = Anonymizer().anonymize(query)
        category = Category.objects.get(slug=category_slug)

        document_search = DocumentSearch(category=category)
        documents = document_search.get_relevant_documents(query)
        for doc in documents:
            self.stdout.write(doc.page_content)

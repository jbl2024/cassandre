from django.core.management.base import BaseCommand
from ai.services.index_service import index_documents


class Command(BaseCommand):
    """
    This command indexes all documents in the Document app, 
    creates embeddings and saves them in vector database.
    It takes an optional argument --category_id to index documents of a specific category.
    """
    help = ("Index all documents in the Document app, create embeddings "
            "and save them in vector database")

    def add_arguments(self, parser):
        parser.add_argument(
            "--category_id", type=str, default=None, help="The category id"
        )

    def handle(self, *args, **options):
        category_id = options["category_id"]
        index_documents(category_id)

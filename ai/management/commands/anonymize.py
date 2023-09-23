from django.core.management.base import BaseCommand

from ai.services.anonymize_service import Anonymizer


class Command(BaseCommand):
    """
    This is a Django management command class. It is used to anonymize text.
    """
    help = "Anonymize text"

    def add_arguments(self, parser):
        parser.add_argument("query", type=str, help="The query string")

    def handle(self, *args, **options):
        query = options["query"]
        anonymized_query = Anonymizer().anonymize(query)

        self.stdout.write(anonymized_query)

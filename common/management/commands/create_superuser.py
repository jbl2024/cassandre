import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a superuser if it does not exist"

    def handle(self, *args, **options):
        """
        This method handles the creation of a superuser if it does not exist.
        It fetches the username, email, and password from the environment variables.
        If the user does not exist, it creates a new superuser.
        If the user already exists, it prints a warning message.
        """

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "adminpassword")

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created superuser: {username}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Superuser {username} already exists")
            )

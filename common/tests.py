# pylint: disable=missing-docstring

from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase


class CreateSuperuserCommandTestCase(TestCase):
    @patch(
        "os.environ",
        {
            "DJANGO_SUPERUSER_USERNAME": "testadmin",
            "DJANGO_SUPERUSER_EMAIL": "testadmin@example.com",
            "DJANGO_SUPERUSER_PASSWORD": "testpassword",
        },
    )
    def test_create_superuser_if_not_exists(self):
        out = StringIO()
        call_command(
            "create_superuser", stdout=out
        )  # Replace with the actual name of your command
        output = out.getvalue().strip()

        # Check if the superuser was created in the test database
        user_exists = User.objects.filter(username="testadmin").exists()
        self.assertTrue(user_exists)

        # Check that the expected success message was outputted
        self.assertIn("Successfully created superuser: testadmin", output)

    @patch(
        "os.environ",
        {
            "DJANGO_SUPERUSER_USERNAME": "testadmin",
            "DJANGO_SUPERUSER_EMAIL": "testadmin@example.com",
            "DJANGO_SUPERUSER_PASSWORD": "testpassword",
        },
    )
    def test_warns_if_superuser_already_exists(self):
        # Manually create the superuser first
        User.objects.create_superuser(
            "testadmin", "testadmin@example.com", "testpassword"
        )

        out = StringIO()
        call_command(
            "create_superuser", stdout=out
        )  # Replace with the actual name of your command
        output = out.getvalue().strip()

        # Check that the expected warning message was outputted
        self.assertIn("Superuser testadmin already exists", output)

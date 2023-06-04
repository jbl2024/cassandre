import hashlib
import unittest

from .anonymize import Anonymizer
from django.db import IntegrityError
from django.test import TestCase
from django.utils.text import slugify

from .models import Category, Correction, Document


class CategoryModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Test Category")

    def test_string_representation(self):
        self.assertEqual(str(self.category), "Test Category")

    def test_slug_created(self):
        self.assertEqual(self.category.slug, slugify(self.category.name))

    def test_prompt_created(self):
        self.assertIsNotNone(self.category.prompt)

class DocumentModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.document = Document.objects.create(file="testfile.txt", title="Test Document", category=self.category)

    def test_string_representation(self):
        self.assertEqual(str(self.document), "Test Document")

class CorrectionModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.correction = Correction.objects.create(query="Test query", answer="Test answer", category=self.category)

    def test_string_representation(self):
        self.assertEqual(str(self.correction), f"Correction for {self.category.name}")

    def test_query_hash_created(self):
        self.assertEqual(self.correction.query_hash, hashlib.sha1(self.correction.query.encode()).hexdigest())


    def test_uniqueness_constraint(self):
        # Try to create a new Correction with the same category and query
        with self.assertRaises(IntegrityError):
            duplicate_correction = Correction.objects.create(query="Test query", answer="Another test answer", category=self.category)


class TestAnonymizer(unittest.TestCase):

    def setUp(self):
        self.anonymizer = Anonymizer()

    def test_anonymize_with_named_entities(self):
        text = "Jean Pierre habite à Paris et travaille pour le ministère"
        anonymized_text = self.anonymizer.anonymize(text)
        self.assertEqual(anonymized_text, "Madame/Monsieur habite à Paris et travaille pour le ministère")

        text = "Bonjour, je m'appelle John Doe, je suis affecté au rectorat de Paris, que puis-je faire ? Bien cordialement, Jérôme Blondon"
        anonymized_text = self.anonymizer.anonymize(text)
        self.assertEqual(anonymized_text, "Bonjour, je m'appelle Madame/Monsieur, je suis affecté au rectorat de Paris, que puis-je faire ? Bien cordialement, Madame/Monsieur")

        text = "Bonjour, je m'appelle John Doe, mon numen est le 46G9987654XYZ"
        anonymized_text = self.anonymizer.anonymize(text)
        self.assertEqual(anonymized_text, "Bonjour, je m'appelle Madame/Monsieur, mon numen est le CONFIDENTIEL")

        text = "Bonjour, je m'appelle John Doe, mon email est foo@bar.com"
        anonymized_text = self.anonymizer.anonymize(text)
        self.assertEqual(anonymized_text, "Bonjour, je m'appelle Madame/Monsieur, mon email est private@example.com")

    def test_anonymize_without_named_entities(self):
        text = "Il n'y a rien à anonymiser ici"
        anonymized_text = self.anonymizer.anonymize(text)
        self.assertEqual(anonymized_text, text)
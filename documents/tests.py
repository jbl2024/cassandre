# pylint: disable=missing-docstring
# pylint: disable=line-too-long

import hashlib
import unittest

from django.db import IntegrityError
from django.test import TestCase
from django.utils.text import slugify

from ai.services.chunk import split_markdown

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
        self.document = Document.objects.create(
            file="testfile.txt", title="Test Document", category=self.category
        )

    def test_string_representation(self):
        self.assertEqual(str(self.document), "Test Document")


class CorrectionModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.correction = Correction.objects.create(
            query="Test query", answer="Test answer", category=self.category
        )

    def test_string_representation(self):
        self.assertEqual(str(self.correction), f"Correction for {self.category.name}")

    def test_query_hash_created(self):
        self.assertEqual(
            self.correction.query_hash,
            hashlib.sha1(self.correction.query.encode()).hexdigest(),
        )

    def test_uniqueness_constraint(self):
        # Try to create a new Correction with the same category and query
        with self.assertRaises(IntegrityError):
            _duplicate_correction = Correction.objects.create(
                query="Test query", answer="Another test answer", category=self.category
            )


class SplitMarkdownTestCase(TestCase):
    def test_extract_sections_basic(self):
        text = """
        # Title1
        This is a content under Title1.
        Another content

        ## SubTitle1
        This is a content under SubTitle1.
        """

        sections = split_markdown(text)
        expected_output = [
            "Title1\nThis is a content under Title1.\nAnother content",
            "Title1 > SubTitle1\nThis is a content under SubTitle1.",
        ]

        self.assertEqual(sections, expected_output)

    def test_extract_sections_advanced(self):
        text = """
        # Stagiaires

        Réf.: BOEN n°6 du 28-10-2021 – Lignes directrices de gestion académiques

        ## 3.3.3.4. Stagiaires n'ayant ni la qualité d'ex-fonctionnaire ni celle d'ex-contractuel de I'EN

        ### 3.3.3.4.1. Conditions a remplir

        Deux bonifications

        ### 3.3.3.4.2. Bonifications

        Test
        
        ## 3.3.3.5. Divers

        Divers
        """

        sections = split_markdown(text)
        expected_output = [
            "Stagiaires\nRéf.: BOEN n°6 du 28-10-2021 – Lignes directrices de gestion académiques",
            "Stagiaires > 3.3.3.4. Stagiaires n'ayant ni la qualité d'ex-fonctionnaire ni celle d'ex-contractuel de I'EN > 3.3.3.4.1. Conditions a remplir\nDeux bonifications",
            "Stagiaires > 3.3.3.4. Stagiaires n'ayant ni la qualité d'ex-fonctionnaire ni celle d'ex-contractuel de I'EN > 3.3.3.4.2. Bonifications\nTest",
            "Stagiaires > 3.3.3.5. Divers\nDivers",
        ]

        self.assertEqual(sections, expected_output)

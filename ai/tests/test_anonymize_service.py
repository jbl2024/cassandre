# pylint: disable=missing-docstring
# pylint: disable=line-too-long

import unittest

from ai.services.anonymize_service import Anonymizer


class TestAnonymizer(unittest.TestCase):
    def setUp(self):
        self.anonymizer = Anonymizer()

    def test_anonymize_with_named_entities(self):
        text = "Jean Pierre habite à Paris et travaille pour le ministère"
        anonymized_text = self.anonymizer.anonymize(text)
        self.assertEqual(
            anonymized_text,
            "Madame/Monsieur habite à Paris et travaille pour le ministère",
        )

        text = "Bonjour, je m'appelle John Doe, je suis affecté au rectorat de Paris, que puis-je faire ? Bien cordialement, Jérôme Blondon"
        anonymized_text = self.anonymizer.anonymize(text)
        self.assertEqual(
            anonymized_text,
            "Bonjour, je m'appelle Madame/Monsieur, je suis affecté au rectorat de Paris, que puis-je faire ? Bien cordialement, Madame/Monsieur",
        )

        text = "Bonjour, je m'appelle John Doe, mon numen est le 46G9987654XYZ"
        anonymized_text = self.anonymizer.anonymize(text)
        self.assertEqual(
            anonymized_text,
            "Bonjour, je m'appelle Madame/Monsieur, mon numen est le CONFIDENTIEL",
        )

        text = "Bonjour, je m'appelle John Doe, mon email est foo@bar.com"
        anonymized_text = self.anonymizer.anonymize(text)
        self.assertEqual(
            anonymized_text,
            "Bonjour, je m'appelle Madame/Monsieur, mon email est private@example.com",
        )

        text = "Bonjour, je m'appelle Fatiah BENBARKA, mon email est foo@bar.com"
        anonymized_text = self.anonymizer.anonymize(text)
        self.assertEqual(
            anonymized_text,
            "Bonjour, je m'appelle Madame/Monsieur, mon email est private@example.com",
        )

    def test_anonymize_without_named_entities(self):
        text = "Il n'y a rien à anonymiser ici"
        anonymized_text = self.anonymizer.anonymize(text)
        self.assertEqual(anonymized_text, text)

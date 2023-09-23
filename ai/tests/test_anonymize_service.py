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

    def test_anonymize_with_insee_numbers(self):
        text = "Mon numéro INSEE est 198012301234567."
        anonymized_text = self.anonymizer.anonymize(text)
        self.assertEqual(anonymized_text, "Mon numéro INSEE est CONFIDENTIEL.")

        text = "mon numéro de ss est 295102345678923."
        anonymized_text = self.anonymizer.anonymize(text)
        self.assertEqual(anonymized_text, "mon numéro de ss est CONFIDENTIEL.")

    def test_anonymize_with_french_phone_numbers(self):
        text = "Appelez-moi au 01 23 45 67 89 ou au 09.87.65.43.21!"
        anonymized_text = self.anonymizer.anonymize(text)
        self.assertEqual(anonymized_text, "Appelez-moi au CONFIDENTIEL ou au CONFIDENTIEL!")

        text = "Mon numéro est le 0123456789."
        anonymized_text = self.anonymizer.anonymize(text)
        self.assertEqual(anonymized_text, "Mon numéro est le CONFIDENTIEL.")

        text = "Vous pouvez également me joindre au 0123456789"
        anonymized_text = self.anonymizer.anonymize(text)
        self.assertEqual(anonymized_text, "Vous pouvez également me joindre au CONFIDENTIEL")

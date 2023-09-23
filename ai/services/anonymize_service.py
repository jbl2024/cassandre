import re
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from pybloom_live import BloomFilter


class Anonymizer:
    """
    This class is used to anonymize sensitive information in a text. It uses a Bloom Filter
    to store the named entities found in the text and replaces them with a generic placeholder.
    It also anonymizes email addresses, phone numbers, NUMEN numbers, and INSEE numbers by replacing
    them with a placeholder.
    """

    def __init__(
        self,
        model_name="Jean-Baptiste/camembert-ner-with-dates",
        capacity=1000000,
        error_rate=0.1,
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        self.nlp = pipeline(
            "ner",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple",
        )
        self.filter = BloomFilter(capacity=capacity, error_rate=error_rate)

    def add_to_filter(self, entities):
        """
        This method adds the named entities found in the entities list to the Bloom Filter.

        Args:
            entities (list): The recognized entities from the text.
        """
        for entity in entities:
            if entity["entity_group"] == "PER":  # Adjust this label if necessary
                self.filter.add(entity["word"])

    def anonymize_email(self, text, placeholder="private@example.com"):
        """
        This method anonymizes the email addresses found in the text by replacing them
        with a placeholder.

        Args:
            text (str): The text to anonymize.
            placeholder (str): The placeholder to replace the email addresses with.
            Defaults to "private@example.com".

        Returns:
            str: The anonymized text.
        """
        email_pattern = r"[\w\.-]+@[\w\.-]+"
        anonymized_text = re.sub(email_pattern, placeholder, text)
        return anonymized_text

    def anonymize_phone_numbers(self, text, placeholder="CONFIDENTIEL"):
        """
        This method anonymizes the phone numbers found in the text by replacing them
        with a placeholder.

        Args:
            text (str): The text to anonymize.
            placeholder (str): The placeholder to replace the phone numbers with.
            Defaults to "CONFIDENTIEL".

        Returns:
            str: The anonymized text.
        """
        phone_number_pattern = r"\b0\d(?:[\s.-]?\d{2}){4}\b"
        anonymized_text = re.sub(phone_number_pattern, placeholder, text)
        return anonymized_text

    def anonymize_numen(self, text, placeholder="CONFIDENTIEL"):
        """
        This method anonymizes the NUMEN (numero d'identification de l'education nationale)
        found in the text by replacing them with a placeholder.

        Args:
            text (str): The text to anonymize.
            placeholder (str): The placeholder to replace the NUMEN with.
            Defaults to "CONFIDENTIEL".

        Returns:
            str: The anonymized text.
        """
        numen_pattern = r"\b\d{2}[A-Z]\d{7}[A-Z]{3}\b"
        anonymized_text = re.sub(numen_pattern, placeholder, text)
        return anonymized_text

    def anonymize_insee(self, text, placeholder="CONFIDENTIEL"):
        """
        This method anonymizes the INSEE
        (Institut national de la statistique et des études économiques)
        numbers found in the text by replacing them with a placeholder.

        Args:
            text (str): The text to anonymize.
            placeholder (str): The placeholder to replace the INSEE numbers with.
            Defaults to "CONFIDENTIEL".

        Returns:
            str: The anonymized text.
        """
        insee_pattern = r"(\d{15})"
        anonymized_text = re.sub(insee_pattern, placeholder, text)
        return anonymized_text

    def anonymize(self, text):
        """
        This method anonymizes the text by replacing named entities, phone numbers,
        NUMEN numbers, INSEE numbers, and email addresses with placeholders.

        Args:
            text (str): The text to anonymize.

        Returns:
            str: The anonymized text.
        """
        anonymized_text = text

        entities = self.nlp(anonymized_text)
        self.add_to_filter(entities)

        for entity in entities:
            if entity["word"] in self.filter:
                anonymized_text = anonymized_text.replace(
                    entity["word"], "Madame/Monsieur"
                )

        # Anonymize phone numbers
        anonymized_text = self.anonymize_phone_numbers(anonymized_text)

        # Anonymize NUMEN numbers
        anonymized_text = self.anonymize_numen(anonymized_text)

        # Anonymize INSEE numbers
        anonymized_text = self.anonymize_insee(anonymized_text)

        # Anonymize email addresses
        anonymized_text = self.anonymize_email(anonymized_text)
        return anonymized_text

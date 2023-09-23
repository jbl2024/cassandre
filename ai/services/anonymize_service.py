import re
import spacy
from pybloom_live import BloomFilter

class Anonymizer:
    def __init__(self, model='fr_core_news_lg', capacity=1000000, error_rate=0.1):
        self.nlp = spacy.load(model)
        self.filter = BloomFilter(capacity=capacity, error_rate=error_rate)

    def add_to_filter(self, doc):
        for ent in doc.ents:
            if ent.label_ == 'PER':
                self.filter.add(ent.text)

    def anonymize_email(self, text, placeholder="private@example.com"):
        email_pattern = r'[\w\.-]+@[\w\.-]+'
        anonymized_text = re.sub(email_pattern, placeholder, text)
        return anonymized_text

    def anonymize_phone_numbers(self, text, placeholder="CONFIDENTIEL"):
        phone_number_pattern = r'\b0\d(\s|\.)?(\d{2}(\s|\.)?){4}\b'
        anonymized_text = re.sub(phone_number_pattern, placeholder, text)
        return anonymized_text

    def anonymize_numen(self, text, placeholder="CONFIDENTIEL"):
        numen_pattern = r'\b\d{2}[A-Z]\d{7}[A-Z]{3}\b'
        anonymized_text = re.sub(numen_pattern, placeholder, text)
        return anonymized_text

    def anonymize(self, text):
        doc = self.nlp(text)
        self.add_to_filter(doc)
        anonymized_text = doc.text
        for ent in doc.ents:
            if ent.text in self.filter:
                anonymized_text = anonymized_text.replace(ent.text, "Madame/Monsieur")

        # Anonymize phone numbers
        anonymized_text = self.anonymize_phone_numbers(anonymized_text)

        # Anonymize NUMEN numbers
        anonymized_text = self.anonymize_numen(anonymized_text)

        # Anonymize email addresses
        anonymized_text = self.anonymize_email(anonymized_text)

        return anonymized_text

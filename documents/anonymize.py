import re
import spacy
from pybloom_live import BloomFilter

class Anonymizer:
    def __init__(self, model='fr_core_news_sm', capacity=1000000, error_rate=0.1):
        self.nlp = spacy.load(model)
        self.filter = BloomFilter(capacity=capacity, error_rate=error_rate)

    def add_to_filter(self, doc):
        for ent in doc.ents:
            if ent.label_ == 'PER':
                self.filter.add(ent.text)

    def anonymize(self, text):
        doc = self.nlp(text)
        self.add_to_filter(doc)
        anonymized_text = doc.text
        for ent in doc.ents:
            if ent.text in self.filter:
                anonymized_text = anonymized_text.replace(ent.text, "Madame/Monsieur")

        # Replace phone numbers
        anonymized_text = re.sub(r'\b0\d(\s|\.)?(\d{2}(\s|\.)?){4}\b', 'CONFIDENTIEL', anonymized_text)

        # Replace NUMEN numbers
        anonymized_text = re.sub(r'\b\d{2}[A-Z]\d{7}[A-Z]{3}\b', 'CONFIDENTIEL', anonymized_text)

        return anonymized_text

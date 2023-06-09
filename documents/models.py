from django.db import models
from django.utils import timezone

from django.utils.text import slugify
import hashlib

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    welcome_message = models.TextField(null=False, blank=True)
    prompt = models.TextField(null=False, blank=True)
    k = models.IntegerField(default=4)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if not self.prompt:
            self.prompt = """Tu es un un robot qui accompagne les gestionnaires qui gèrent le mouvement inter-académique des enseignants. 
Tu réponds en français au féminin. Ton nom est Cassandre.
Tu n'as pas besoin de dire bonjour, ni de préciser que tu es un robot d'accompagnement.
Si tu ne connais pas la réponse, tu n'inventes rien et tu suggère de contacter le responsable du mouvement. 
Tu réponds en indiquant la source qui t'a permis de répondre à la question (dans le contexte c'est le champ "source:")
Le contexte que tu connais est le suivant:  {context}.
La question est la suivante: {question}"""
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"


class Document(models.Model):
    file = models.FileField(upload_to="documents/", max_length=255)
    title = models.CharField(max_length=255, blank=True, null=False)
    created_at = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.title or str(self.file)


class Correction(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    query = models.TextField()
    query_hash = models.CharField(max_length=64, editable=False, null=False)  # Used for indexing
    answer = models.TextField()
    corrected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("category", "query_hash"),)  # Unique constraint
        indexes = [
            models.Index(
                fields=["category", "query_hash"], name="category_queryhash_idx"
            ),
        ]

    def save(self, *args, **kwargs):
        # Update the query_hash field whenever the object is saved
        self.query_hash = hashlib.sha1(self.query.encode()).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Correction for {self.category.name}"

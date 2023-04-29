from django.db import models
from django.utils import timezone

class Document(models.Model):
    file = models.FileField(upload_to='documents/')
    title = models.CharField(max_length=255, blank=True, null=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title or str(self.file)

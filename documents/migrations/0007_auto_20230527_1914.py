from django.db import migrations
import hashlib

def generate_query_hashes(apps, schema_editor):
    Correction = apps.get_model('documents', 'Correction')
    for correction in Correction.objects.all():
        correction.query_hash = hashlib.sha256(correction.query.encode()).hexdigest()
        correction.save(update_fields=['query_hash'])

class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0006_correction_query_hash_and_more'),
    ]

    operations = [
        migrations.RunPython(generate_query_hashes),
    ]

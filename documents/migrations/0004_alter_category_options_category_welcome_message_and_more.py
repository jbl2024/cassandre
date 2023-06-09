# Generated by Django 4.2 on 2023-05-17 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_category_document_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories'},
        ),
        migrations.AddField(
            model_name='category',
            name='welcome_message',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='prompt',
            field=models.TextField(blank=True),
        ),
    ]

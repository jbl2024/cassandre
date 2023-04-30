from celery import shared_task
from django.core import management

@shared_task
def index_documents():
    management.call_command('index_documents')

from cassandre.celery import shared_task
from django.core import management

@shared_task
def index_documents(persist_directory='chroma_db'):
    management.call_command('index_documents', persist_directory=persist_directory)

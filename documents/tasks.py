from celery import shared_task
from documents.index import index_documents

@shared_task
def index_documents():
    index_documents()

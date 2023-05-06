from celery import shared_task
from documents import index

@shared_task
def index_documents():
    index.index_documents()

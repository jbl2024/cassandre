from celery import shared_task
from documents import index

@shared_task
def index_documents():
    index.index_documents()

@shared_task
def index_documents_in_category(category_id):
    index.index_documents(category_id)

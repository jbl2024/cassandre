from celery import shared_task
from ai.services import index_service

@shared_task
def index_documents():
    """
    This function indexes the documents.
    """
    index_service.index_documents()

@shared_task
def index_documents_in_category(category_id):
    """
    Indexes the documents in the specified category.

    Args:
        category_id (int): The ID of the category whose documents should be indexed.
    """
    index_service.index_documents(category_id)

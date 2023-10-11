import requests
from celery import shared_task
from django.conf import settings
from requests.auth import HTTPBasicAuth

from ai.services.search_service import search_documents


@shared_task
def async_search(callback_url, query, category_slug, engine="gpt-3.5-turbo"):
    """
    This function performs an asynchronous search operation.
    It takes in a callback URL, a query, a category slug, and an engine type.
    It then uses these parameters to perform a chat operation using the
    specified chat service. The result of the chat operation is then sent
    to the callback URL.

    Args:
        callback_url (str): The URL to which the result of the chat operation will be sent.
        query (str): The query to be used in the chat operation.
        category_slug (str): The slug of the category to be used in the chat operation.
        engine (str, optional): The type of engine to be used in the chat operation. 
          Defaults to "gpt-3.5-turbo".

    Returns:
        tuple: A tuple containing the status code and text of the response from the callback URL.
    """

    username = settings.PUBLIK_USERNAME
    password = settings.PUBLIK_PASSWORD

    result = search_documents(query=query, engine=engine, category_slug=category_slug)

    response = requests.post(
        callback_url, json=result, auth=HTTPBasicAuth(username, password), timeout=3600
    )

    return response.status_code, response.text

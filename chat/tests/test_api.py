# pylint: disable=missing-docstring

from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from documents.models import Category


class ChatViewTest(APITestCase):
    def setUp(self):
        # Optionally set up a sample category if required
        self.category = Category.objects.create(
            name="Example Category", slug="example-category"
        )

    @patch("chat.views.search_documents")
    def test_chat_api(self, mock_search_documents):
        # Set up the mocked response
        mock_response = {"result": "Mocked chat response", "source_documents": []}
        mock_search_documents.return_value = mock_response

        # Set up API endpoint payload
        payload = {
            "query": "Hello",
            "engine": "gpt-3.5-turbo",
        }

        response = self.client.post(
            reverse("search_api", args=[self.category.slug]), payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), mock_response)

        # Ensure chat function is called with the correct parameters
        mock_search_documents.assert_called_once_with(
            payload["query"], payload["engine"], self.category.slug
        )

    def test_invalid_chat_api_call(self):
        # You can add more tests, like what happens if data is invalid
        payload = {
            "query": "",
        }

        response = self.client.post(
            reverse("search_api", args=[self.category.slug]), payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "query", response.json()
        )  # Check that the error is about the 'query' field


class AsyncSearchViewTest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Example Category", slug="example-category"
        )

    @patch("chat.views.async_search.delay")
    def test_async_search_api(self, mock_async_search):
        # Set up API endpoint payload
        payload = {
            "callback_url": "http://example.com/callback/",
            "query": "Hello",
            "engine": "gpt-3.5-turbo",
            "category_slug": self.category.slug,
        }

        response = self.client.post(reverse("async_search_api"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure async_search function is called with the correct parameters
        mock_async_search.assert_called_once_with(
            callback_url=payload["callback_url"],
            query=payload["query"],
            category_slug=payload["category_slug"],
            engine=payload["engine"],
        )

    def test_invalid_async_search_api_call(self):
        # Test with missing callback_url
        payload = {
            "query": "Hello",
            "engine": "gpt-3.5-turbo",
            "category_slug": self.category.slug,
        }

        response = self.client.post(reverse("async_search_api"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("callback_url", response.json())

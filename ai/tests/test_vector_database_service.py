# pylint: disable=missing-docstring

from unittest.mock import Mock, patch

from django.test import TestCase

from ai.services.vector_database_service import create_collection


class TestVectorDatabaseService(TestCase):
    @patch("ai.services.embedding.get_embedding")
    @patch("qdrant_client.QdrantClient")
    @patch("langchain.vectorstores.Qdrant.from_documents")
    def test_create_collection(
        self, mock_from_documents, mock_qdrant_client, mock_get_embedding
    ):
        # Mocking out external calls
        mock_get_embedding.return_value = "some_embedding"

        create_collection("test_collection", ["text1", "text2"])

        # Validate QdrantClient was initialized with the right parameters
        mock_qdrant_client.assert_called_once_with(
            url="http://localhost:6333", prefer_grpc=True
        )
        mock_client = mock_qdrant_client.return_value
        mock_client.delete_collection.assert_called_once_with("test_collection")

        mock_from_documents.assert_called()  # Add further assertions based on expected behavior


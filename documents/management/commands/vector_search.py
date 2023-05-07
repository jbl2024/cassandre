from django.conf import settings
from django.core.management.base import BaseCommand
import qdrant_client
from documents.embedding import get_embedding
from documents.index import index_documents
from langchain.vectorstores import Qdrant

class Command(BaseCommand):
    help = 'Search inside vector DB'

    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='The query string')

    def handle(self, *args, **options):
        query = options['query']        
        embeddings = get_embedding()
        url = settings.QDRANT_URL
        client = qdrant_client.QdrantClient(
            url=url, prefer_grpc=True
        )
        docsearch = Qdrant(
            client=client, collection_name="documents", 
            embedding_function=embeddings.embed_query
        )    

        res = docsearch.similarity_search_with_score(query, k=4)
        for doc, score in res:
            self.stdout.write(f"# {doc.metadata['origin']} -> {score}")
            self.stdout.write(doc.page_content)

from ..config.settings import settings
from qdrant_client.models import PointStruct, Distance, VectorParams

class QdrantRepository:

    def __init__(self,client):
        self.client = client
        self.collection_name = settings.QDRANT_COLLECTION


    def create_collections(self):
        pass


    def collection_exists(self):
        pass



    def search(self):
        pass


    def save(self):
        pass


    def get_qdrant_client(self):
        return self.client
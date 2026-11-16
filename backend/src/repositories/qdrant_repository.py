from ..config.settings import settings
from qdrant_client.models import PointStruct, ScoredPoint, Distance, VectorParams

class QdrantRepository:

    def __init__(self,client):
        self.client = client
        self.collection_name = settings.QDRANT_COLLECTION

    # Realiza a criação de uma colecao
    def create_collections(self, vector_size : int) -> bool:
        if self.client.collection_exists(self.collection_name):
            return False

        self.client.create_collection(
            collection_name = self.collection_name,
            vectors_config = VectorParams(
                size = vector_size,
                distance=Distance.COSINE
            ) 
        )

        print("Criacao da colection foi realizada com sucesso!\n")
        return True

    # Realiza a verificao da colecao
    def collection_exists(self) -> bool:
        return self.client.collection_exists(self.collection_name)


    # Verifica se o banco vetorial esta vazio
    def is_empty(self):

        if not self.collection_exists():
            return True

        count_result = self.client.count(collection_name=self.collection_name)
        return count_result.count == 0


    # Faz a busca no banco do qdrant pelo documento mais similar ao query_vector
    def search(self, query_vector, limit=5) -> list[ScoredPoint]:
        response = self.client.query_points(
            collection_name = self.collection_name,
            query= query_vector, 
            limit = limit
        )
        return response.points

    # Realiza o salvamento do embedding no banco
    def save(self, points : list[PointStruct]):
        self.client.upsert(
            collection_name = self.collection_name,
            points = points
        )
        print("Armazenado com sucesso! \n")
        

    # Retorna o client do qdrant
    def get_qdrant_client(self):
        return self.client
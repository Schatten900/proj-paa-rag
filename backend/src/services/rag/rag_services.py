from ...repositories.qdrant_repository import QdrantRepository
from ..rag.embedding_services import EmbeddingService
from ..rag.ingestion_services import IngestionService


class RagService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        ingestion_service: IngestionService,
        qdrant_repository: QdrantRepository,
    ):
        self.embedding_service = embedding_service
        self.ingestion_service = ingestion_service
        self.qdrant_repository = qdrant_repository

    def retrieve(self, query: str, limit: int = 3):

        # Caso o banco vetorial esteja vazio, popule o banco
        if self.qdrant_repository.is_empty():
            self.ingestion_service.ingest()

        # Realiza o embed da pergunta
        query_vector = self.embedding_service.embed_chunk(query)

        # Recupera no banco um documento similar
        return self.qdrant_repository.search(
            query_vector=query_vector,
            limit = limit
        )
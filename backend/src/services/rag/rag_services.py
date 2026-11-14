class RagService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.ingestion_service = IngestionService()
        self.qdrant_repository = QdrantRepository()
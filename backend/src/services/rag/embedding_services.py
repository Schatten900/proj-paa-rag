import requests

from ...config.settings import settings

class EmbeddingService:

    def __init__(self):
        pass


    def embed_chunk(self,chunk : str) -> list[float]:
        # Chama o embedding do ollama para vetorizar o chunk recebido

        response = requests.post(
            f"{settings.OLLAMA_URL}/api/embed",
            json={
                "model": settings.OLLAMA_EMBEDDING_MODEL,
                "input": chunk
            },
            timeout=60
        )
        response.raise_for_status()

        print("Embedding: \n")
        print(response.json()["embeddings"][0])

        return response.json()["embeddings"][0]
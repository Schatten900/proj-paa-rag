from ..rag.embedding_services import EmbeddingService


class SpliterService:

    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service

    # Funcao para criar todos os chunks de um documento
    def create_chunks(self,document):
        pass


    # Retorna todos os chunks com embedding de um documento
    def read_markdown(self,document) -> list[float]:

        # Cria todos os chunk do documento
        chunks = self.create_chunks(document)

        # Realiza o embed dos chunks
        embed_chunks = []
        for chunk in chunks:
            embed_chunk = self.embedding_service.embed_chunk(chunk)
            embed_chunks.append(embed_chunk)

        # Retorna todos os embeddings
        return embed_chunks

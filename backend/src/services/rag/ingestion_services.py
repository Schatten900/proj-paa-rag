from ..spliter.markdown_services import MarkdownService
from ..spliter.spliter_services import SpliterService
from ...repositories.qdrant_repository import QdrantRepository
from ..spliter.dataset_loader_service import DatasetLoaderService

class IngestionService:

    def __init__(
        self,
        dataset_loader_service: DatasetLoaderService,
        markdown_service: MarkdownService,
        spliter_service: SpliterService,
        qdrant_repository: QdrantRepository,
    ):
        self.dataset_loader_service = dataset_loader_service
        self.markdown_service = markdown_service
        self.spliter_service = spliter_service
        self.qdrant_repository = qdrant_repository

    def ingest(self):
        # Pega do dataset escolhido os dados
        documents = self.dataset_loader_service.load()

        # Chama MarkdownService para conversão
        markdown_documents = []
        for document in documents:
            markdown_document = self.markdown_service.convert(document)
            markdown_documents.append(markdown_document)

        # SplitService para criar os chunks

        for markdown_document in markdown_documents:
            # Retorna todos os chunks embed de um documento
            embed_chunks = self.spliter_service.read_markdown(markdown_document)

            # Salvando os chunks no qdrant
            for embed_chunk in embed_chunks:
                self.qdrant_repository.save(embed_chunk)
            

        


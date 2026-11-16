from .llm_services import LlmService
from .prompt_builder import PromptBuilderService
from ..rag.rag_services import RagService
from ...repositories.qdrant_repository import QdrantRepository


class ChatService:
    def __init__(
        self,
        rag_service: RagService,
        prompt_builder_service: PromptBuilderService,
        llm_service: LlmService,
    ):
        self.rag_service = rag_service
        self.prompt_builder_service = prompt_builder_service
        self.llm_service = llm_service


    def chat(self,question):

        print("Iniciando a conversa")

        # Busca pelo banco vetorial dados proximos da pergunta

        documents = self.rag_service.retrieve(question)

        # Converte para texto os documentos encontrados  
        context_texts = [point.payload["text"] for point in documents if point.payload]

        print(f"documentos gerados: {context_texts}")

        # Cria o prompt da mensagem 
        prompt = self.prompt_builder_service.build(question, context_texts)

        # Faz a chamada ao llm
        return self.llm_service.generate(prompt)
        

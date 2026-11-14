from .llm_services import LlmService
from .prompt_builder import PromptBuilderService
from ..rag.rag_services import RagService


class ChatService:
    def __init__(self):
        self.rag_service = RagService()
        self.prompt_builder_service = PromptBuilderService()
        self.llm_service = LlmService()


    def chat(self,question):

        # Busca pelo banco vetorial dados proximos da pergunta, aqui entra rag_service


        # Cria o prompt da mensagem

        prompt = 

        # Faz a chamada ao llm

        self.llm_service.generate(prompt)
        

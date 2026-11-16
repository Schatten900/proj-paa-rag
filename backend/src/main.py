from flask import Flask, jsonify, request
from qdrant_client import QdrantClient

#=============
# Imports
#=============

from .config.settings import settings
from .services.llm.chat_services import ChatService
from .services.llm.llm_services import LlmService
from .services.llm.prompt_builder import PromptBuilderService
from .services.rag.embedding_services import EmbeddingService
from .services.rag.ingestion_services import IngestionService
from .services.rag.rag_services import RagService
from .services.spliter.dataset_loader_service import DatasetLoaderService
from .services.spliter.markdown_services import MarkdownService
from .services.spliter.spliter_services import SpliterService
from .repositories.qdrant_repository import QdrantRepository


app = Flask(__name__)


#============
# Client
#============

qdrant_client = QdrantClient(
    url=settings.QDRANT_URL
)

qdrant_repository = QdrantRepository(qdrant_client)

#=============
# Services
#=============

embedding_service = EmbeddingService()
dataset_loader_service = DatasetLoaderService()
markdown_service = MarkdownService()
spliter_service = SpliterService(embedding_service)
ingestion_service = IngestionService(
    dataset_loader_service,
    markdown_service,
    spliter_service,
    qdrant_repository,
)
rag_service = RagService(
    embedding_service,
    ingestion_service,
    qdrant_repository,
)
prompt_builder_service = PromptBuilderService()
llm_service = LlmService()
chat_service = ChatService(
    rag_service,
    prompt_builder_service,
    llm_service,
)



#=============
# Rotas
#=============

# Serve para alimentar o banco vetorial com os dados
@app.post("/ingest")
def ingest():
    try:
        ingestion_service.ingest()

        return jsonify({ 
            "status":"ok", 
            "message":"Banco carregado com sucesso!"
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.post("/chat")
def chat():
    try:
        data = request.get_json()
        question = data.get("message")

        if not question:
            return jsonify({"error":"mensagem é necessária"}),400

        response = chat_service.chat(question)

        return jsonify({
            "status": "ok",
            "message": response
        }), 200


    except Exception as e:
        return jsonify({"error": str(e)}), 500
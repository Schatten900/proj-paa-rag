from flask import Flask, jsonify, request
from qdrant_client import QdrantClient
import os
import requests

#=============
# Imports
#=============

from .config import settings
from .services.llm.chat_services import ChatService


from .repositories.qdrant_repository import QdrantRepository 


app = Flask(__name__)


#============
# Client
#============

qdrant_client = QdrantClient(
    url = settings.QDRANT.URL
)

qdrant_repository =  QdrantRepository(qdrant_client)

#=============
# Services
#=============

chat_service = ChatService()



#=============
# Rotas
#=============

# Serve para alimentar o banco vetorial com os dados
@app.post("/ingest")
def ingest():
    try:
        if qdrant_client.is_empty():
            #popula o banco vetorial
            print("Populado com sucesso")

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
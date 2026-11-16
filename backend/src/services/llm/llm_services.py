import requests
from ...config.settings import settings

class LlmService:
    def __init__(self):
        pass

    def generate(self,prompt : str ) -> str:

        # Configuracoes do modelo
        url = f"{settings.OLLAMA_URL}/api/generate"
        payload = {
            "model": settings.OLLAMA_LLM_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.4,
                "num_predict": 60,
            }
        }

        # Tempo de resposta
        response = requests.post(url,json=payload,timeout=300)
        response.raise_for_status()

        # retorna o json do modelo
        return response.json().get("response", "")
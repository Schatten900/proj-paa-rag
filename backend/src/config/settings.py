import os


class Settings:
    QDRANT_URL = os.getenv(
        "QDRANT_URL",
        "http://qdrant:6333"
    )

    QDRANT_COLLECTION = os.getenv(
        "QDRANT_COLLECTION",
        "knowledge_base"
    )

    OLLAMA_URL = os.getenv(
        "OLLAMA_URL",
        "http://ollama:11434"
    )

    OLLAMA_LLM_MODEL = os.getenv(
        "OLLAMA_LLM_MODEL",
        "qwen2.5:3b"  
    )

    OLLAMA_EMBEDDING_MODEL = os.getenv(
        "OLLAMA_EMBEDDING_MODEL",
        "nomic-embed-text"
    )


settings = Settings()
#!/bin/sh

set -e

echo "Iniciando Ollama..."

ollama serve &

OLLAMA_PID=$!

echo "Aguardando Ollama ficar disponível..."

until ollama list > /dev/null 2>&1
do
    sleep 2
done

echo "Ollama está disponível."

LLM_MODEL="${OLLAMA_MODEL:-qwen2.5:3b}"
EMBEDDING_MODEL="${OLLAMA_EMBEDDING_MODEL:-nomic-embed-text}"

echo "Verificando LLM: ${LLM_MODEL}"

if ! ollama list | grep -q "${LLM_MODEL}"; then
    echo "Baixando ${LLM_MODEL}..."
    ollama pull "${LLM_MODEL}"
else
    echo "${LLM_MODEL} já está disponível."
fi

echo "Verificando modelo de embeddings: ${EMBEDDING_MODEL}"

if ! ollama list | grep -q "${EMBEDDING_MODEL}"; then
    echo "Baixando ${EMBEDDING_MODEL}..."
    ollama pull "${EMBEDDING_MODEL}"
else
    echo "${EMBEDDING_MODEL} já está disponível."
fi

echo "Modelos disponíveis:"
ollama list

echo "Ollama pronto."

wait ${OLLAMA_PID}
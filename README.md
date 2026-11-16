# Chatbot RAG local

Chatbot baseado em uma LLM executada localmente com Ollama. A arquitetura usa RAG (Retrieval-Augmented Generation): antes de responder, o backend deve recuperar no Qdrant trechos relevantes de um dataset do Hugging Face e enviá-los como contexto para o modelo.

## Visão rápida

<table>
	<tr>
		<td><strong>API Flask</strong><br>Recebe pedidos de ingestão e perguntas; coordena os serviços do backend.</td>
		<td><strong>Ollama</strong><br>Executa localmente a LLM <code>qwen2.5:3b</code> e o modelo de embeddings <code>nomic-embed-text</code>.</td>
	</tr>
	<tr>
		<td><strong>Qdrant</strong><br>Armazena os vetores dos chunks e permite recuperar os mais similares à pergunta.</td>
		<td><strong>Dataset Hugging Face</strong><br>Origem planejada dos documentos; o carregador está preparado como serviço, mas ainda sem implementação.</td>
	</tr>
</table>

## Arquitetura e fluxo

```
flowchart LR
		subgraph Ingestao[Pipeline de ingestão]
				HF[Dataset Hugging Face] --> Loader[DatasetLoaderService]
				Loader --> Markdown[MarkdownService]
				Markdown --> Split[SpliterService]
				Split --> Embed[EmbeddingService]
				Embed --> Ollama[Ollama]
				Embed --> Points[Pontos: vetor + texto + metadados]
				Points --> Repo[QdrantRepository]
				Repo --> Qdrant[(Qdrant)]
		end

		subgraph Chat[Pipeline de pergunta e resposta]
				Client[Cliente HTTP] --> API[Flask: POST /chat]
				API --> ChatService[ChatService]
				ChatService --> RAG[RagService]
				RAG --> QueryEmbed[Embedding da pergunta]
				QueryEmbed --> Ollama
				QueryEmbed --> Search[Busca por similaridade]
				Search --> Qdrant
				Qdrant --> Context[Chunks recuperados]
				Context --> Prompt[PromptBuilderService]
				Prompt --> Generate[LlmService]
				Generate --> Ollama
				Ollama --> Answer[Resposta]
				Answer --> Client
		end
```

### Pipeline de ingestão

1. `DatasetLoaderService.load()` carrega registros do dataset escolhido no Hugging Face.
2. `MarkdownService.convert()` transforma cada registro em conteúdo Markdown. A gravação e leitura de arquivos também podem ser feitas por `save()` e `read()` quando necessário.
3. `SpliterService.create_chunks()` divide o Markdown em trechos menores. O tamanho, a sobreposição e a preservação de metadados devem ser definidos nessa etapa.
4. `EmbeddingService.embed_chunk()` envia cada trecho para o endpoint `/api/embed` do Ollama e obtém seu vetor.
5. A ingestão monta pontos Qdrant com identificador, vetor e payload. O payload deve preservar pelo menos o texto, por exemplo `{"text": "...", "source": "...", "chunk_index": 0}`.
6. `QdrantRepository` cria a coleção e faz `upsert` dos pontos. A coleção configurada é `knowledge_base`, com distância cosseno.

O registro original, o texto convertido, o chunk e seu vetor são conceitos diferentes. O Qdrant deve receber um ponto por chunk, não apenas uma lista de números; o texto e a origem ficam no payload para serem usados na resposta.

### Pipeline de chat

1. O cliente envia uma pergunta para `POST /chat`.
2. `ChatService` pede ao `RagService` os documentos relacionados.
3. `RagService` gera um embedding para a pergunta e usa `QdrantRepository.search()` para recuperar os pontos mais similares.
4. Os textos dos pontos formam o contexto. `PromptBuilderService` combina esse contexto com a pergunta e as instruções de resposta.
5. `LlmService` envia o prompt ao endpoint `/api/generate` do Ollama e devolve a resposta ao backend.

### Instâncias dos serviços

O `main.py` é o ponto de composição do backend: ele cria uma instância de cada serviço e injeta as dependências. Por exemplo, a mesma instância de `EmbeddingService` é compartilhada pelo splitter e pelo RAG; o mesmo `QdrantRepository` é compartilhado pela ingestão e pela recuperação. Assim, os serviços não criam clientes ou dependências paralelas dentro dos próprios construtores.

## Organização do código

```
backend/
	Dockerfile
	src/
		main.py                         # Aplicação Flask e composição dos serviços
		config/settings.py              # URLs, modelos e coleção via ambiente
		repositories/qdrant_repository.py
		services/
			llm/                          # Chat, construção de prompt e geração
			rag/                          # Embeddings, ingestão e recuperação
			spliter/                      # Loader, Markdown e divisão em chunks
		requirements.txt
ollama/
	Dockerfile
	entrypoint.sh                     # Inicia Ollama e baixa os modelos
docker-compose.yml
README.md
```

## Executar com Docker Compose

### Pré-requisitos

- Docker Engine com o plugin `docker compose`.
- Recursos de memória e CPU suficientes para executar a LLM localmente. A primeira inicialização baixa os modelos e pode demorar.

### Iniciar os serviços

Na raiz do repositório:

```
docker compose up --build
```

O Compose inicia três serviços:

| Serviço | Endereço local | Função |
| --- | --- | --- |
| Backend | `http://localhost:5000` | API Flask |
| Ollama | `http://localhost:11434` | Embeddings e geração de texto |
| Qdrant | `http://localhost:6333` | Banco vetorial HTTP; gRPC em `localhost:6334` |

O backend aguarda os healthchecks do Ollama e do Qdrant. O container do Ollama baixa `qwen2.5:3b` e `nomic-embed-text` quando eles ainda não existem. Os modelos e os dados do Qdrant ficam nos volumes `bot_ollama_data` e `bot_qdrant_data`.

Para encerrar os containers, sem apagar os volumes:

```
docker compose down
```

### Testar a API

Solicitar a ingestão:

```
curl -X POST http://localhost:5000/ingest
```

Enviar uma pergunta:

```
curl -X POST http://localhost:5000/chat \
	-H 'Content-Type: application/json' \
	-d '{"message":"Qual é o assunto dos documentos?"}'
```

O formato de resposta do chat é:

```
{
	"status": "ok",
	"message": "Resposta gerada pelo modelo"
}
```

O formato descreve o contrato da rota. No estado atual, a ingestão pode retornar HTTP 500 porque o carregador ainda não retorna documentos; o chat também depende de uma coleção preenchida com payloads contendo `text`.

## Configuração

As variáveis abaixo são definidas no `docker-compose.yml`; os valores padrão do backend estão em `backend/src/config/settings.py`.

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `OLLAMA_URL` | `http://ollama:11434` | Endereço do Ollama na rede do Compose |
| `OLLAMA_LLM_MODEL` | `qwen2.5:3b` | Modelo de geração |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` | Modelo de embeddings |
| `QDRANT_URL` | `http://qdrant:6333` | Endereço do Qdrant na rede do Compose |
| `QDRANT_COLLECTION` | `knowledge_base` | Nome da coleção vetorial |

As dependências Python estão em `backend/src/requirements.txt`. O projeto usa `datasets` para viabilizar a futura integração com Hugging Face; a divisão dos textos será implementada no próprio projeto, sem uma biblioteca externa de splitter.

## Estado atual e próximos passos

- **Estrutura conectada:** Flask, composição de dependências, chamadas HTTP ao Ollama e acesso ao Qdrant.
- **A implementar:** carregamento do dataset em `DatasetLoaderService.load()`, conversão em `MarkdownService.convert()` e chunking em `SpliterService.create_chunks()`.
- **Persistência a completar:** gerar `PointStruct` por chunk com ID, vetor e payload, e garantir que a coleção seja criada com a dimensão correta antes do `upsert`.
- **Ingestão a validar:** atualmente `read_markdown()` retorna embeddings, mas `QdrantRepository.save()` espera pontos Qdrant; essa transformação precisa ser feita na camada de ingestão.
- **Frontend:** ainda não implementado; a interação disponível está planejada pela API HTTP.
- **Qualidade da resposta:** o prompt pede uma resposta em JSON, mas o formato ainda precisa ser validado e aplicado de forma consistente na chamada ao modelo.

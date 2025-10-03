import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from typing import Any, Optional
import chromadb


class RAGService:
    def __init__(self):
        """Inicializa o serviço de RAG com ChromaDB, compatível com Chroma 0.4/0.5 e 1.x.

        - Tenta usar SentenceTransformerEmbeddings (modelo local) ou OpenAIEmbeddings como fallback.
        - Para Chroma 1.x, calcula embeddings no cliente e passa via `embeddings=`.
        - Para versões antigas (0.4/0.5), mantém o uso de `embedding_function` na coleção.
        """

        # Caminho do DB e garantia de diretório
        db_dir = Path(__file__).parent.parent.parent / "data" / "chroma_db"
        db_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(db_dir))

        # Inicializa embedding function com fallback
        self.embedding_function: Optional[Any] = self._init_embedding_function()

        # Alguns releases do Chroma aceitam `embedding_function` na coleção; outros não.
        self._supports_collection_embedding = True
        try:
            if self.embedding_function is not None:
                self.collection = self.client.get_or_create_collection(
                    name="personabot_interactions",
                    embedding_function=self.embedding_function,
                )
            else:
                # Sem embedder do lado do cliente (modo degradado)
                self.collection = self.client.get_or_create_collection(name="personabot_interactions")
        except Exception:
            # Chroma 1.x (ou validações internas) podem falhar ao receber um objeto de embedding externo
            # Nesses casos, não acoplamos o embedder à coleção e calculamos embeddings no cliente.
            self._supports_collection_embedding = False
            self.collection = self.client.get_or_create_collection(name="personabot_interactions")

    def _init_embedding_function(self) -> Optional[Any]:
        """Tenta inicializar embeddings locais (sentence-transformers) e, se falhar,
        usa OpenAIEmbeddings (requer OPENAI_API_KEY). Caso contrário, retorna None.
        """
        # Garante que o .env seja carregado, mesmo quando usado fora do main
        try:
            load_dotenv(find_dotenv(usecwd=True), override=False)
        except Exception:
            pass
        # Preferência: modelo local via sentence-transformers (recomendado para privacidade/custo)
        # 1) Tenta o pacote recomendado sem warnings de depreciação
        try:
            from langchain_huggingface import HuggingFaceEmbeddings

            return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        except Exception:
            pass

        # 2) Fallback para a implementação antiga do LangChain Community
        try:
            from langchain_community.embeddings import SentenceTransformerEmbeddings
            return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        except Exception:
            pass

        # Fallback: OpenAI Embeddings
        try:
            if os.getenv("OPENAI_API_KEY"):
                from langchain_openai import OpenAIEmbeddings

                return OpenAIEmbeddings()
        except Exception:
            pass

        # Sem embedder disponível (modo somente texto, não recomendado)
        return None

    def _ensure_embeddings_for_add(self, texts: list[str]) -> Optional[list[list[float]]]:
        """Para Chroma 1.x (sem embedder na coleção), calcula embeddings no cliente.
        Retorna lista de vetores ou None se indisponível.
        """
        if self.embedding_function is None:
            return None
        # LangChain embeddings tipicamente expõem `embed_documents`
        if hasattr(self.embedding_function, "embed_documents"):
            return self.embedding_function.embed_documents(texts)
        return None

    def store_interaction(self, interaction_id: str, text: str, metadata: dict):
        """Armazena uma interação (pergunta ou resposta) no ChromaDB."""
        add_kwargs = {}
        if not self._supports_collection_embedding:
            vectors = self._ensure_embeddings_for_add([text])
            if vectors is not None:
                add_kwargs["embeddings"] = vectors

        self.collection.add(
            ids=[interaction_id],
            documents=[text],
            metadatas=[metadata],
            **add_kwargs,
        )

    def search_similar_interactions(self, query_text: str, n_results: int = 3) -> list:
        """Busca por interações similares no banco de dados (usa embeddings no cliente quando necessário)."""
        if not self._supports_collection_embedding:
            if self.embedding_function is None:
                raise RuntimeError(
                    "RAG indisponível: instale 'sentence-transformers' ou defina OPENAI_API_KEY para usar OpenAIEmbeddings."
                )
            # Preferir consulta com embeddings para compatibilidade com Chroma 1.x
            if hasattr(self.embedding_function, "embed_query"):
                qvec = self.embedding_function.embed_query(query_text)
                results = self.collection.query(query_embeddings=[qvec], n_results=n_results)
            else:
                # Fallback extremo (não recomendado): tentar por texto
                results = self.collection.query(query_texts=[query_text], n_results=n_results)
        else:
            # Versões antigas do Chroma aceitam query_texts com embedder acoplado à coleção
            results = self.collection.query(query_texts=[query_text], n_results=n_results)

        return results.get("documents", [[]])[0]

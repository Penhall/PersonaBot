import chromadb
from pathlib import Path
from langchain_community.embeddings import SentenceTransformerEmbeddings

class RAGService:
    def __init__(self):
        """Inicializa o serviço de RAG com ChromaDB."""
        db_path = str(Path(__file__).parent.parent.parent / "data" / "chroma_db")
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="personabot_interactions",
            embedding_function=self.embedding_function
        )

    def store_interaction(self, interaction_id: str, text: str, metadata: dict):
        """Armazena uma interação (pergunta ou resposta) no ChromaDB."""
        self.collection.add(
            ids=[interaction_id],
            documents=[text],
            metadatas=[metadata]
        )

    def search_similar_interactions(self, query_text: str, n_results: int = 3) -> list:
        """Busca por interações similares no banco de dados."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results['documents'][0]

import pytest
import shutil
from pathlib import Path
from src.rag.rag_service import RAGService

@pytest.fixture
def rag_service_fixture():
    """Fixture para criar uma instância limpa do RAGService para cada teste."""
    # Usa um diretório de teste para o DB vetorial
    test_db_path = Path(__file__).parent / "test_chroma_db"
    
    # Limpa o diretório de teste antes de cada execução
    if test_db_path.exists():
        shutil.rmtree(test_db_path)
    
    # Monkeypatch o caminho do DB no RAGService para usar o diretório de teste
    original_path = RAGService.__init__
    def patched_init(self):
        self.client = pytest.importorskip('chromadb').PersistentClient(path=str(test_db_path))
        self.embedding_function = pytest.importorskip('langchain_community.embeddings').SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="test_interactions",
            embedding_function=self.embedding_function
        )
    
    RAGService.__init__ = patched_init
    service = RAGService()
    
    yield service
    
    # Limpeza após o teste
    shutil.rmtree(test_db_path)
    RAGService.__init__ = original_path

def test_store_and_search(rag_service_fixture: RAGService):
    """Testa se o serviço consegue armazenar e depois buscar uma interação."""
    service = rag_service_fixture
    
    # Dados de teste
    interaction_id = "test_id_1"
    text = "O que você pensa sobre inteligência artificial?"
    metadata = {"user": "test_user", "timestamp": "2025-01-01T12:00:00Z"}
    
    # Armazena a interação
    service.store_interaction(interaction_id, text, metadata)
    
    # Busca por uma interação similar
    query = "Você tem alguma opinião sobre IA?"
    results = service.search_similar_interactions(query, n_results=1)
    
    # Verifica se o resultado é o esperado
    assert len(results) == 1
    assert results[0] == text

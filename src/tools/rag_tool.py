from __future__ import annotations

from typing import Any
from langchain.tools import BaseTool


class RAGSearchTool(BaseTool):
    """Ferramenta de busca no RAG integrada como LangChain BaseTool."""

    name: str = "RAGSearch"
    description: str = (
        "Busca por interações similares no banco de memória para reduzir alucinação. "
        "Use SEMPRE que a pergunta for factual/objetiva."
    )

    rag_service: Any = None

    def _run(self, query: str) -> str:
        try:
            docs = self.rag_service.search_similar_interactions(query, n_results=5) or []
            if not docs:
                return "Nenhum contexto relevante encontrado."
            return "\n".join(f"- {d}" for d in docs)
        except Exception as e:
            return f"[RAG erro] {e}"

    async def _arun(self, query: str) -> str:  # pragma: no cover
        # Execução assíncrona não utilizada neste projeto
        return self._run(query)


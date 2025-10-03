from __future__ import annotations

from crewai import Crew, Process
from src.agents.agent_manager import AgentManager


def is_safe_to_respond(question: str) -> bool:
    """Filtro simples para exemplos/uso web; personalize conforme necessário."""
    blocked_words = ["política", "religião", "conteúdo adulto"]
    lower = question.lower()
    return not any(w in lower for w in blocked_words)


def run_single_interaction(question: str) -> str:
    """Executa uma interação única com a Crew e retorna o texto final."""
    if not is_safe_to_respond(question):
        return "Desculpe, não posso responder a esse tipo de pergunta."

    manager = AgentManager()
    memory_agent = manager.create_memory_agent()
    persona_agent = manager.create_persona_agent()
    response_agent = manager.create_response_agent()
    tasks = manager.create_tasks(memory_agent, persona_agent, response_agent)

    # injeta a pergunta e contexto do RAG na primeira task
    try:
        similar = manager.rag_service.search_similar_interactions(question, n_results=5)
    except Exception:
        similar = []
    rag_snippets = "\n- " + "\n- ".join(similar) if similar else "\n- (nenhum contexto relevante)"
    tasks[0].description = (
        f'A pergunta do usuário é: "{question}". '
        'Busque no RAG por interações passadas que sejam relevantes para essa pergunta.'
        f"\nContexto do RAG (se houver):{rag_snippets}"
    )

    crew = Crew(
        agents=[memory_agent, persona_agent, response_agent],
        tasks=tasks,
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff()
    # CrewOutput tem .raw; fallback ao próprio objeto (tests já cobrem)
    return getattr(result, "raw", result)


def run_single_interaction_with_persona(question: str, persona: dict) -> str:
    """Executa uma interação usando uma persona específica (override)."""
    if not is_safe_to_respond(question):
        return "Desculpe, não posso responder a esse tipo de pergunta."

    manager = AgentManager(persona_config=persona)
    memory_agent = manager.create_memory_agent()
    persona_agent = manager.create_persona_agent()
    response_agent = manager.create_response_agent()
    tasks = manager.create_tasks(memory_agent, persona_agent, response_agent)

    try:
        similar = manager.rag_service.search_similar_interactions(question, n_results=5)
    except Exception:
        similar = []
    rag_snippets = "\n- " + "\n- ".join(similar) if similar else "\n- (nenhum contexto relevante)"
    tasks[0].description = (
        f'A pergunta do usuário é: "{question}". '
        'Busque no RAG por interações passadas que sejam relevantes para essa pergunta.'
        f"\nContexto do RAG (se houver):{rag_snippets}"
    )

    crew = Crew(
        agents=[memory_agent, persona_agent, response_agent],
        tasks=tasks,
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff()
    return getattr(result, "raw", result)

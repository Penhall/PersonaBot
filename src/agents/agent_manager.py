import os
from crewai import Agent, Task, LLM
from typing import Any
from src.rag.rag_service import RAGService
from src.config_loader import load_persona_config

class AgentManager:
    def __init__(self, persona_config: dict | None = None):
        self.rag_service = RAGService()
        self.persona_config = persona_config or load_persona_config()
        self.llm = self._create_llm()

    def _rag_tool(self) -> Any:
        """Cria uma ferramenta de busca no RAG para fornecer contexto factual.

        Retorna um dicionário compatível com CrewAI (name, description, func),
        garantindo compatibilidade sem depender de tipos específicos de Tool.
        """
        def _run(query: str) -> str:
            try:
                docs = self.rag_service.search_similar_interactions(query, n_results=5) or []
                if not docs:
                    return "Nenhum contexto relevante encontrado."
                return "\n".join(f"- {d}" for d in docs)
            except Exception as e:
                return f"[RAG erro] {e}"

        return {
            "name": "RAGSearch",
            "description": (
                "Busca por interações similares no banco de memória para reduzir alucinação. "
                "Use SEMPRE que a pergunta for factual/objetiva."
            ),
            "func": _run,
        }

    def _create_llm(self) -> LLM:
        """Cria a instância de LLM com base nas variáveis de ambiente.

        Suporte:
        - OpenAI (padrão): usa `OPENAI_API_KEY` e `OPENAI_MODEL` (ex.: gpt-4o-mini)
        - Ollama: defina `LLM_PROVIDER=ollama`, `OLLAMA_BASE_URL` e `OLLAMA_MODEL` (ex.: llama3.1)
        """
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        # Parâmetros de geração para reduzir alucinação
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
        top_p = float(os.getenv("LLM_TOP_P", "0.9"))
        try:
            max_tokens = int(os.getenv("LLM_MAX_TOKENS", "256"))
        except ValueError:
            max_tokens = 256
        if provider == "ollama":
            model = os.getenv("OLLAMA_MODEL", "llama3.1")
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            # O litellm aceita o prefixo 'ollama/' para o modelo
            return LLM(
                model=f"ollama/{model}",
                base_url=base_url,
                api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )

        # OpenAI (padrão)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return LLM(model=model, temperature=temperature, top_p=top_p, max_tokens=max_tokens)

    def create_memory_agent(self) -> Agent:
        use_rag_tool = os.getenv("USE_RAG_TOOL", "false").strip().lower() in ("1", "true", "yes")
        return Agent(
            role="Memory and Context Manager",
            goal="Buscar interações passadas e contexto relevante para uma nova pergunta.",
            backstory="Você é um especialista em recuperar informações de um banco de dados vetorial para fornecer contexto crucial.",
            tools=[self._rag_tool()] if use_rag_tool else [],
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )

    def create_persona_agent(self) -> Agent:
        style_params = self.persona_config.get('style_params', {})
        style_lines = []
        if isinstance(style_params, dict) and style_params:
            for k, v in style_params.items():
                style_lines.append(f"- **{k.capitalize()}:** {v}")
        style_block = "\n".join(style_lines)

        persona_backstory = f"""Você é um assistente de IA cuja única missão é garantir que cada resposta do bot siga estritamente a persona de '{self.persona_config['name']}'.

        **Detalhes da Persona:**
        - **Tom de Voz:** {', '.join(self.persona_config['tone_of_voice'])}
        - **Tópicos Favoritos:** {', '.join(self.persona_config['favorite_topics'])}
        - **Tópicos a Evitar:** {', '.join(self.persona_config['avoided_topics'])}
        {'\n**Parâmetros de Estilo:**\n' + style_block if style_block else ''}

        Regras de Factualidade (SEM EXCEÇÕES):
        - Para perguntas factuais/objetivas, priorize precisão sobre estilo; não invente.
        - Se o contexto não trouxer evidências suficientes, oriente a responder com "Não tenho certeza" ou peça esclarecimentos.
        - Prefira respostas curtas e diretas quando a pergunta for objetiva.

        Você NUNCA deve desviar desta persona. Sua saída deve ser instruções claras para o próximo agente sobre o que e COMO responder (inclusive nível de confiança/cautela)."""
        return Agent(
            role="Persona Keeper",
            goal=f"Garantir que a resposta final esteja 100% alinhada com a persona de '{self.persona_config['name']}'.",
            backstory=persona_backstory,
            tools=[],
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )

    def create_response_agent(self) -> Agent:
        return Agent(
            role="Final Response Generator",
            goal="Criar uma resposta final, curta, correta e natural para o usuário, baseada no contexto e nas diretrizes da persona.",
            backstory=(
                "Você prioriza exatidão sobre floreio em perguntas factuais. "
                "Se tiver baixa confiança, declare isso brevemente (ex.: 'Não tenho certeza'). "
                "Evite inventar dados. Mantenha concisão e clareza."
            ),
            tools=[],
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )

    def create_tasks(self, memory_agent, persona_agent, response_agent):
        context_task = Task(
            description=(
                "Dada a pergunta do usuário, busque no RAG por interações passadas que sejam relevantes.\n"
                "Use a ferramenta RAGSearch com a pergunta original e retorne um resumo dos pontos factuais encontrados."
            ),
            agent=memory_agent,
            expected_output="Um resumo do contexto encontrado ou uma nota de que nenhum contexto foi encontrado."
        )

        persona_task = Task(
            description="Com base no contexto da memória e na pergunta do usuário, defina as diretrizes para a resposta final, garantindo que a persona seja mantida.",
            agent=persona_agent,
            context=[context_task],
            expected_output="Instruções claras para o Gerador de Resposta sobre o que e como responder."
        )

        response_task = Task(
            description="Use as diretrizes da persona para criar uma resposta final para o usuário. A resposta deve ser curta, como um tweet.",
            agent=response_agent,
            context=[persona_task],
            expected_output="A resposta final e formatada para ser postada."
        )

        return [context_task, persona_task, response_task]

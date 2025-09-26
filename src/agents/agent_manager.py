from crewai import Agent, Task
from src.rag.rag_service import RAGService
from src.config_loader import load_persona_config

class AgentManager:
    def __init__(self):
        self.rag_service = RAGService()
        self.persona_config = load_persona_config()

    def create_memory_agent(self) -> Agent:
        return Agent(
            role="Memory and Context Manager",
            goal="Buscar interações passadas e contexto relevante para uma nova pergunta.",
            backstory="Você é um especialista em recuperar informações de um banco de dados vetorial para fornecer contexto crucial.",
            tools=[],
            allow_delegation=False,
            verbose=True
        )

    def create_persona_agent(self) -> Agent:
        persona_backstory = f"""Você é um assistente de IA cuja única missão é garantir que cada resposta do bot siga estritamente a persona de '{self.persona_config['name']}'.

        **Detalhes da Persona:**
        - **Tom de Voz:** {', '.join(self.persona_config['tone_of_voice'])}
        - **Tópicos Favoritos:** {', '.join(self.persona_config['favorite_topics'])}
        - **Tópicos a Evitar:** {', '.join(self.persona_config['avoided_topics'])}

        Você NUNCA deve desviar desta persona. Sua resposta final deve ser a instrução para o próximo agente, não a resposta para o usuário."""
        return Agent(
            role="Persona Keeper",
            goal=f"Garantir que a resposta final esteja 100% alinhada com a persona de '{self.persona_config['name']}'.",
            backstory=persona_backstory,
            tools=[],
            allow_delegation=False,
            verbose=True
        )

    def create_response_agent(self) -> Agent:
        return Agent(
            role="Final Response Generator",
            goal="Criar uma resposta final, curta e natural para o usuário, baseada no contexto e nas diretrizes da persona.",
            backstory="Você é um escritor criativo que se especializou em criar posts para redes sociais que soam autênticos e humanos.",
            tools=[],
            allow_delegation=False,
            verbose=True
        )

    def create_tasks(self, memory_agent, persona_agent, response_agent):
        context_task = Task(
            description="Dada a pergunta do usuário, busque no RAG por interações passadas que sejam relevantes.",
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

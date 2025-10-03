import pytest
from unittest.mock import MagicMock
from crewai import Crew, Process
from src.agents.agent_manager import AgentManager

@pytest.fixture
def mocked_agent_manager(mocker):
    """Fixture que substitui (mocks) as dependências externas do AgentManager."""
    # Desativa ferramentas no Agent durante testes para evitar validações de Tool
    mocker.patch.dict('os.environ', {'USE_RAG_TOOL': 'false'})
    # Mock do RAGService para não interagir com o DB real
    mocker.patch('src.agents.agent_manager.RAGService', return_value=MagicMock())
    
    # Mock do load_persona_config para retornar uma persona de teste
    mock_persona = {
        'name': 'Test Persona',
        'tone_of_voice': ['neutro', 'informativo'],
        'favorite_topics': ['testes', 'software'],
        'avoided_topics': ['nenhum']
    }
    mocker.patch('src.agents.agent_manager.load_persona_config', return_value=mock_persona)
    
    # Mock do LLM para que os agentes retornem respostas previsíveis
    mocker.patch('crewai.agent.Agent.execute_task', side_effect=[
        "Contexto encontrado: O usuário gosta de testes.",
        "Diretriz: Responda de forma neutra e informativa sobre testes.",
        "Claro, testes são essenciais para a qualidade do software."
    ])
    
    return AgentManager()

def test_crew_kickoff(mocked_agent_manager: AgentManager):
    """Testa se o kickoff da Crew executa o fluxo e retorna o resultado esperado."""
    manager = mocked_agent_manager

    # Criar agentes e tarefas com o manager mockado
    memory_agent = manager.create_memory_agent()
    persona_agent = manager.create_persona_agent()
    response_agent = manager.create_response_agent()
    tasks = manager.create_tasks(memory_agent, persona_agent, response_agent)

    # Montar a Crew
    crew = Crew(
        agents=[memory_agent, persona_agent, response_agent],
        tasks=tasks,
        process=Process.sequential
    )

    # A pergunta do usuário que inicia o processo
    user_question = "O que você acha de testes?"
    tasks[0].description = f'A pergunta do usuário é: "{user_question}". Busque contexto.'

    # Executar a Crew
    final_result = crew.kickoff()

    # Verificar se o resultado final é o esperado do último agente mockado
    final_text = getattr(final_result, "raw", final_result)
    assert final_text == "Claro, testes são essenciais para a qualidade do software."

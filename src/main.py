import os
from dotenv import load_dotenv, find_dotenv
from crewai import Crew, Process
from src.agents.agent_manager import AgentManager

# Carrega variáveis de ambiente do .env (busca de forma resiliente pela raiz do projeto)
load_dotenv(find_dotenv(usecwd=True))

# Provider condicional: OpenAI (padrão) ou Ollama
provider = os.getenv("LLM_PROVIDER", "openai").lower()
# Só exige OPENAI_API_KEY quando o provider for OpenAI
if provider != "ollama" and not os.getenv("OPENAI_API_KEY"):
    raise ValueError("A variável de ambiente OPENAI_API_KEY não foi definida e o provider atual não é 'ollama'.")

def is_safe_to_respond(question: str) -> bool:
    """Verifica se a pergunta é segura para responder."""
    # Filtro simples de palavras-chave. Pode ser expandido com um modelo de moderação.
    blocked_words = ["política", "religião", "conteúdo adulto"]
    
    for word in blocked_words:
        if word in question.lower():
            print(f"Filtro de segurança: Palavra ''{word}'' encontrada. Ignorando a mensagem.")
            return False
    return True

def main():
    """Ponto de entrada principal do PersonaBot."""
    print("Iniciando o PersonaBot...")

    manager = AgentManager()

    # Criar agentes
    memory_agent = manager.create_memory_agent()
    persona_agent = manager.create_persona_agent()
    response_agent = manager.create_response_agent()

    # Criar tarefas
    tasks = manager.create_tasks(memory_agent, persona_agent, response_agent)

    # Montar a Crew
    crew = Crew(
        agents=[memory_agent, persona_agent, response_agent],
        tasks=tasks,
        process=Process.sequential,
        verbose=True
    )

    # O código abaixo é um exemplo de como o loop principal poderia funcionar.
    # Ele está comentado para evitar execução contínua durante o desenvolvimento inicial.

    # from src.twitter.client import TwitterClient
    # import time

    # client = TwitterClient()
    # last_processed_id = None # Em um cenário real, isso seria persistido

    # while True:
    #     print("Verificando por novas menções...")
    #     mentions = client.get_recent_mentions(last_processed_id)
        
    #     for mention in reversed(mentions): # Processa da mais antiga para a mais nova
    #         if not is_safe_to_respond(mention.text):
    #             continue

    #         print(f"Processando menção: {mention.text}")
    #         tasks[0].description = f'A pergunta do usuário é: "{mention.text}". Busque contexto.'
    #         final_response = crew.kickoff()
            
    #         print(f"Resposta gerada: {final_response}")
    #         # client.post_reply(final_response, mention.id)
            
    #         last_processed_id = mention.id
        
    #     print("Aguardando 60 segundos para a próxima verificação...")
    #     time.sleep(60)

    # Exemplo de execução com uma pergunta
    print("\n--- Exemplo de Interação (Execução Única) ---")
    user_question = "O que você acha de café?"

    if not is_safe_to_respond(user_question):
        return

    # Passando a pergunta para a primeira tarefa, incluindo contexto do RAG quando disponível
    try:
        similar = manager.rag_service.search_similar_interactions(user_question, n_results=3)
    except Exception:
        similar = []
    rag_snippets = "\n- " + "\n- ".join(similar) if similar else "\n- (nenhum contexto relevante)"
    tasks[0].description = (
        f'A pergunta do usuário é: "{user_question}". '\
        f'Busque no RAG por interações passadas que sejam relevantes para essa pergunta.'
        f"\nContexto do RAG (se houver):{rag_snippets}"
    )

    result = crew.kickoff()

    print("\n--- Resposta Final ---")
    print(result)

if __name__ == "__main__":
    main()

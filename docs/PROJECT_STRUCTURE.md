# Estrutura de Arquivos e Pastas do Projeto PersonaBot

Este documento detalha a organização dos diretórios e arquivos para o PersonaBot, garantindo um desenvolvimento modular e escalável.

- **`/` (Raiz do Projeto)**
  - `requirements.txt`: Lista de todas as dependências Python do projeto (ex: `crewai`, `chromadb`, `tweepy`).
  - `GEMINI.md`: Arquivo de contexto para o assistente de IA Gemini, com visão geral e comandos do projeto.
  - `.gitignore`: Arquivo para ignorar diretórios e arquivos do controle de versão (ex: `__pycache__/`, `*.pyc`, `config/credentials.yaml`, `data/`).

- **`/src`**: Contém todo o código-fonte da aplicação.
  - `main.py`: Ponto de entrada (entrypoint) da aplicação. Responsável por inicializar e executar o bot.
  - `config_loader.py`: Módulo para carregar configurações dos arquivos YAML.
  - **`/src/agents/`**: Definição dos agentes do CrewAI.
    - `persona_manager.py`: Agente que garante a coerência da resposta com a persona definida.
    - `memory_manager.py`: Agente que interage com o sistema RAG para buscar contexto.
    - `response_generator.py`: Agente que cria a resposta final.
  - **`/src/rag/`**: Lógica do sistema de Retrieval-Augmented Generation (RAG).
    - `rag_service.py`: Serviço principal para armazenar e recuperar interações do banco de dados vetorial.
  - **`/src/twitter/`**: Módulo de integração com a API do Twitter/X.
    - `client.py`: Cliente para ler menções, DMs e postar respostas.
  - **`/src/utils/`**: Funções utilitárias (ex: logging, formatação de texto).

- **`/config`**: Armazena todos os arquivos de configuração.
  - `persona.yaml`: Define a identidade, tom de voz e regras da persona do bot.
  - `credentials.yaml.example`: Arquivo de exemplo para as credenciais de API (Twitter, LLM). O arquivo real (`credentials.yaml`) não deve ser versionado.

- **`/data`**: Guarda os dados persistentes gerados pela aplicação.
  - `database.sqlite`: Banco de dados relacional (SQLite) para o histórico de interações.
  - **`/chroma_db/`**: Diretório onde o ChromaDB (ou outro DB vetorial) armazena os embeddings.

- **`/docs`**: Documentação do projeto.
  - `PRD personabot.md`: Documento de Requisitos do Produto.
  - `Backlog.md`: Backlog de funcionalidades e épicos.
  - `PROJECT_STRUCTURE.md`: Este arquivo.
  - `IMPLEMENTATION_PLAN.md`: Plano de implementação detalhado.

- **`/tests`**: Contém os testes automatizados.
  - `test_rag_service.py`: Testes para o sistema de memória.
  - `test_crew.py`: Testes para a orquestração dos agentes.
  - `test_twitter_client.py`: Testes para a integração com o Twitter (usando mocks).

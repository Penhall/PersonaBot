# PersonaBot

Bot de redes sociais em Python com múltiplos agentes (CrewAI) e memória contextual via RAG (ChromaDB). O objetivo é responder de forma curta e natural, mantendo uma persona consistente definida em `config/persona.yaml`. O repositório já inclui um exemplo de execução única e a base para um loop de menções no Twitter.

## Visão Geral
- Orquestração: CrewAI com 3 agentes (memória, persona, resposta).
- Memória: RAG com ChromaDB e embeddings `all-MiniLM-L6-v2`.
- LLM: usa `OPENAI_API_KEY` (carregado via `.env` ou variável de ambiente).
- Twitter: cliente base com Tweepy (exemplo; loop comentado em `src/main.py`).
- Testes: Pytest para o fluxo da Crew e serviço RAG.

## Estrutura do Projeto
- `src/main.py`: ponto de entrada; demonstra uma execução única.
- `src/agents/agent_manager.py`: cria agentes e tarefas do CrewAI.
- `src/rag/rag_service.py`: persistência e busca vetorial (ChromaDB).
- `src/config_loader.py`: leitura de `config/persona.yaml`.
- `src/twitter/client.py`: esqueleto de integração com Twitter (Tweepy).
- `config/persona.yaml`: definição da persona (exemplo incluído).
- `config/credentials.yaml.example`: exemplo de credenciais (não versionar o real).
- `tests/`: testes de unidade/integrados.
- `docs/`: PRD, backlog, plano e estrutura do projeto.
- `src/web/`: UI web simples (FastAPI) para configurar persona, ambiente e interagir.
 - `src/web/`: UI web simples (FastAPI) para configurar persona, ambiente e interagir.
   - Multi‑Persona: compare respostas de várias personas, edite parâmetros (sliders) e crie novas personas.

## Pré‑requisitos
- Python 3.10+ (recomendado)
- Dependências do `requirements.txt`
- Acesso à internet no primeiro uso do RAG para baixar o modelo de embeddings `all-MiniLM-L6-v2` (via `langchain_community.embeddings`).

## Instalação
1) Crie e ative um ambiente virtual:
- Windows (PowerShell): `python -m venv .venv; .\\.venv\\Scripts\\Activate.ps1`
- Linux/macOS: `python -m venv .venv && source .venv/bin/activate`

2) Instale as dependências:
- `pip install -r requirements.txt`

## Configuração
- Variáveis de ambiente (LLM):
  - Defina `OPENAI_API_KEY` no ambiente ou crie um arquivo `.env` na raiz contendo:
    - `OPENAI_API_KEY=sk-...`
- Persona:
  - Edite `config/persona.yaml` para ajustar nome, tom de voz e tópicos da persona.
- Credenciais do Twitter:
  - Copie `config/credentials.yaml.example` para `config/credentials.yaml` e preencha as chaves.
  - Observação: o `TwitterClient` usa OAuth 1.1 para postar e um `bearer_token` (v2) placeholder no código. Ajuste o bearer no código ou estenda o esquema de credenciais conforme sua necessidade.
- Armazenamento do RAG:
  - O ChromaDB persiste dados em `data/chroma_db` (criado automaticamente). Esse diretório já está no `.gitignore`.

## Como Executar
- Execução única (exemplo):
  - `python src/main.py`
  - O script valida `OPENAI_API_KEY` e executa uma interação de exemplo com a Crew.
- Loop de menções no Twitter (opcional):
  - O trecho está comentado em `src/main.py`. Para usar:
    - Preencha `config/credentials.yaml`, ajuste o bearer token em `src/twitter/client.py` e descomente o bloco referente ao `TwitterClient` e ao loop.
    - Considere adicionar delays e salvamento de interações no RAG após responder.

- UI Web (console de configuração e interação):
  - `uvicorn src.web.app:app --reload --port 8000`
  - Acesse: `http://localhost:8000`
  - Funções:
    - Editar `persona.yaml` (visual/edição direta como YAML simples)
    - Editar vars do `.env` (LLM_PROVIDER, OPENAI/OLLAMA)
    - Editar `config/credentials.yaml`
    - Campo de pergunta e resposta para interação rápida com o bot
    - Multi‑Persona: pergunta única, cartões por persona (2 colunas), abas “Resposta/Persona”, sliders de estilo e criação de novas personas

## Testes
- Rode os testes com:
  - `pytest -q`
- Observações:
  - O teste de RAG usa um diretório de banco isolado e `importorskip` para dependências; garanta as libs instaladas.

## Notas e Limitações
- O fluxo de Twitter é um esqueleto para MVP; exige completar credenciais e ajustes de rate limit/delays.
- O filtro de segurança em `src/main.py` é simples (palavras bloqueadas); refine conforme seu caso.
- O modelo de embeddings `all-MiniLM-L6-v2` pode ser baixado no primeiro uso (necessário acesso à rede).
- Por compatibilidade ampla, o RAG como Tool vem desativado por padrão (`USE_RAG_TOOL=false`).
  - A injeção de contexto do RAG já ocorre automaticamente no fluxo (sem Tool).
  - Se seu ambiente suportar Tools do LangChain/CrewAI sem conflitos de versão, ative `USE_RAG_TOOL=true` na UI/Console para reforçar a consulta factual.

## Documentação Relacionada
- `docs/IMPLEMENTATION_PLAN.md`: plano de implementação (MVP).
- `docs/PROJECT_STRUCTURE.md`: estrutura planejada do projeto.
- `docs/motivacao/PRD personabot.md`: PRD do PersonaBot.
- `docs/motivacao/Backlog.md.md`: backlog e epics.

## Roadmap (sugestão)
- Finalizar loop de menções e respostas com atraso humano.
- Persistir interações (pergunta/resposta) no RAG após cada resposta.
- Melhorar prompts dos agentes e moderação.
- Adicionar testes extras para Twitter e persona.

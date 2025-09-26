# Plano de Implementação do Projeto PersonaBot (MVP)

Este plano descreve os passos para desenvolver a versão MVP do PersonaBot, com base no PRD e no Backlog do projeto.

---

### **Fase 1: Estrutura e Configuração do Projeto**

> **Objetivo:** Montar o esqueleto do projeto, configurar o ambiente e definir a persona inicial.

- [ ] **1.1. Criar Estrutura de Pastas:**
  - Criar os diretórios: `/src`, `/config`, `/data`, `/docs`, `/tests`.
  - Adicionar os arquivos iniciais de documentação (`PRD`, `Backlog`, etc.) na pasta `/docs`.

- [ ] **1.2. Ambiente de Desenvolvimento:**
  - Criar o arquivo `requirements.txt` com as dependências iniciais: `python-dotenv`, `crewai`, `chromadb`, `langchain-openai` (ou outro LLM).
  - Criar um ambiente virtual (`python -m venv .venv`) e instalar as dependências (`pip install -r requirements.txt`).

- [ ] **1.3. Configuração da Persona:**
  - Criar o arquivo `config/persona.yaml` com a persona exemplo do "Guaxinim Filósofo".
  - Implementar o módulo `src/config_loader.py` para carregar este arquivo.

- [ ] **1.4. Controle de Versão:**
  - Inicializar um repositório Git (`git init`).
  - Criar e configurar o arquivo `.gitignore` para ignorar `*.pyc`, `__pycache__`, `.venv`, `config/credentials.yaml` e o diretório `/data`.

---

### **Fase 2: Núcleo de Agentes e Memória (Lógica Principal)**

> **Objetivo:** Implementar a capacidade do bot de pensar, lembrar e manter sua personalidade.

- [ ] **2.1. Implementar o Sistema de Memória (RAG):**
  - Configurar o ChromaDB no `src/rag/rag_service.py` para persistir os dados em `/data/chroma_db`.
  - Criar a função para armazenar uma nova interação (mensagem + resposta) e seu embedding.
  - Criar a função para buscar interações passadas com base na similaridade de uma nova mensagem.

- [ ] **2.2. Desenvolver os Agentes do CrewAI:**
  - Em `/src/agents/`, criar os três agentes principais:
    1.  **Memory & Context Agent:** Usa o `rag_service` para buscar contexto relevante.
    2.  **Persona Keeper Agent:** Recebe o contexto e a persona do `persona.yaml` para garantir que a resposta siga o tom de voz e as regras.
    3.  **Response Generator Agent:** Gera a resposta final com base nas informações dos outros agentes.

- [ ] **2.3. Orquestrar o Crew:**
  - Em `src/main.py`, criar a `Crew` que executa os agentes na sequência correta.
  - Criar uma tarefa (Task) que recebe uma mensagem de entrada e produz uma resposta final.

- [ ] **2.4. Testes Iniciais:**
  - Em `/tests`, criar testes unitários para o `rag_service` (adicionar e buscar itens).
  - Criar um teste de integração para a `Crew`, fornecendo um prompt estático e validando a resposta gerada.

---

### **Fase 3: Integração com o Twitter e Operação**

> **Objetivo:** Conectar o bot ao mundo real, permitindo que ele interaja no Twitter.

- [ ] **3.1. Cliente do Twitter:**
  - Desenvolver o `src/twitter/client.py` usando uma biblioteca como `tweepy`.
  - Implementar a função para ler menções recentes ao bot.
  - Implementar a função para postar uma resposta a um tweet específico.

- [ ] **3.2. Loop Principal de Execução:**
  - Em `src/main.py`, criar o loop principal que:
    1.  Verifica por novas menções a cada X minutos.
    2.  Para cada nova menção, executa a `Crew` para gerar uma resposta.
    3.  Adiciona um delay aleatório (ex: 2 a 15 minutos) antes de postar.
    4.  Usa o cliente do Twitter para postar a resposta.
    5.  Armazena a interação no sistema RAG.

- [ ] **3.3. Gerenciamento de Credenciais:**
  - Criar o arquivo `config/credentials.yaml.example`.
  - Usar `python-dotenv` ou carregar o `config/credentials.yaml` de forma segura para obter as chaves da API do Twitter e do LLM.

---

### **Fase 4: Refinamento e Testes End-to-End**

> **Objetivo:** Garantir que o bot se comporte de forma humana e robusta antes do lançamento completo.

- [ ] **4.1. Testes End-to-End:**
  - Executar o bot em um ambiente de teste (ou com uma conta de Twitter de teste).
  - Enviar diferentes tipos de menções para avaliar a qualidade e a coerência das respostas.

- [ ] **4.2. Refinamento dos Prompts:**
  - Ajustar os prompts dos agentes no CrewAI com base nos resultados dos testes para melhorar a naturalidade e evitar respostas robóticas.

- [ ] **4.3. Implementar Filtros de Segurança:**
  - Adicionar uma verificação básica para ignorar ou responder genericamente a mensagens com conteúdo ofensivo ou fora de escopo.

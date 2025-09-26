# 📋 Backlog do Projeto: PersonaBot  
> _Bot de redes sociais com persona autônoma, baseado em CrewAI + RAG_  
> **Fonte**: Conversa com IA (abril de 2025)  
> **Status**: Backlog inicial — priorização pendente

---

## 🎯 Visão Geral (do Produto)

Criar um bot para Twitter (e futuramente Instagram) que:
- Tenha uma **persona carismática e coerente**,
- Interaja com usuários de forma **indistinguível de um humano**,
- Use **RAG para memória contextual**,
- Seja orquestrado por **múltiplos agentes com CrewAI**.

---

## 📌 Épicos (Epics)

### EPIC-01: Definição da Persona
> Estabelecer identidade, tom de voz e limites da persona.

- [ ] Definir nome, bio e arquétipo (ex: “guaxinim filósofo”)
- [ ] Listar temas permitidos e proibidos
- [ ] Criar guia de estilo de linguagem (gírias, emojis, erros humanos)
- [ ] Armazenar persona em arquivo `config/persona.yaml`

### EPIC-02: Arquitetura Técnica Base
> Montar estrutura mínima para processamento de mensagens.

- [ ] Escolher LLM (GPT-4, Claude, Llama 3, etc.)
- [ ] Configurar ambiente Python com CrewAI
- [ ] Definir estrutura de pastas do projeto
- [ ] Criar arquivo `requirements.txt` com dependências

### EPIC-03: Sistema de Memória com RAG
> Implementar recuperação de contexto a partir de interações passadas.

- [ ] Configurar ChromaDB (ou alternativa) como store vetorial
- [ ] Integrar modelo de embeddings (ex: `all-MiniLM-L6-v2`)
- [ ] Criar função para armazenar interações (mensagem + resposta + timestamp)
- [ ] Implementar busca por similaridade com threshold configurável
- [ ] Testar recuperação de contexto com mensagens simuladas

### EPIC-04: Agentes com CrewAI
> Orquestrar múltiplos agentes para geração de respostas.

- [ ] Criar agente **Memory & Context Agent** (busca no RAG)
- [ ] Criar agente **Persona Keeper Agent** (garante coerência)
- [ ] Criar agente **Response Generator Agent** (gera resposta final)
- [ ] Configurar `Crew` para executar os agentes em sequência
- [ ] Testar pipeline com prompts estáticos

### EPIC-05: Integração com Twitter (MVP)
> Conectar o sistema à API do Twitter para leitura e postagem.

- [ ] Criar conta de desenvolvedor no Twitter e obter credenciais
- [ ] Implementar cliente para:
  - Ler menções (`@persona_bot`)
  - Ler DMs (se aplicável)
  - Postar respostas
- [ ] Adicionar delay aleatório (2–15 min) para simular comportamento humano
- [ ] Evitar respostas duplicadas ou em loop

### EPIC-06: Humanização e Anti-Detecção
> Tornar o bot indistinguível de um humano real.

- [ ] Implementar variação de estrutura de frases
- [ ] Adicionar erros controlados (ex: correção de emoji)
- [ ] Limitar comprimento da resposta (≤ 280 caracteres)
- [ ] Simular “esquecimento” de interações antigas (>30 dias)
- [ ] Evitar padrões robóticos (ex: sempre começar com “Olá!”)

### EPIC-07: Moderação e Segurança
> Proteger o bot e os usuários de abusos.

- [ ] Filtrar mensagens com palavrões ou assédio
- [ ] Ignorar ou responder genericamente a perguntas fora de escopo
- [ ] Registrar logs de interações sensíveis
- [ ] Respeitar termos de serviço do Twitter

### EPIC-08: Expansão para Instagram (Futuro)
> Adaptar o sistema para Instagram (com cautela).

- [ ] Avaliar viabilidade via Meta Graph API
- [ ] Alternativa: automação via Playwright (com risco de banimento)
- [ ] Focar inicialmente em respostas a DMs e comentários em posts próprios

---

## 🛠️ Tarefas Técnicas Prioritárias (MVP)

| ID | Tarefa | Epic | Prioridade |
|----|--------|------|-----------|
| T-01 | Criar esqueleto do projeto com `src/`, `config/`, `data/` | EPIC-02 | Alta |
| T-02 | Implementar armazenamento de interações em SQLite + Chroma | EPIC-03 | Alta |
| T-03 | Montar 3 agentes no CrewAI com prompts iniciais | EPIC-04 | Alta |
| T-04 | Conectar à Twitter API v2 (leitura de menções) | EPIC-05 | Alta |
| T-05 | Testar pipeline completo com simulação (sem postar) | EPIC-02 | Média |
| T-06 | Adicionar delay aleatório nas respostas | EPIC-06 | Média |
| T-07 | Criar arquivo `persona.yaml` com exemplo de “guaxinim filósofo” | EPIC-01 | Média |

---

## 💡 Ideias Futuras (Nice-to-Have)

- Gerar tweets autônomos 1x/dia com base em trends ou persona
- Dashboard simples (Streamlit) para monitorar interações
- Suporte a múltiplas personas (troca via comando ou configuração)
- Aprendizado contínuo: ajustar persona com base em engajamento
- Integração com voz (ex: gerar áudios curtos via ElevenLabs)

---

## ⚠️ Riscos Identificados

| Risco | Mitigação |
|------|----------|
| Banimento por comportamento de bot no Twitter | Usar delays, evitar spam, seguir política de devs |
| Respostas genéricas ou robóticas | Prompt engineering rigoroso + variação controlada |
| Vazamento de dados sensíveis | Não armazenar dados pessoais além do necessário |
| Custo elevado com LLM | Usar cache, fallback para modelos locais (Llama 3) |

---

## 📚 Referências (da conversa)

- CrewAI: orquestração de agentes autônomos
- RAG: memória contextual via busca vetorial
- Twitter API v2: canal principal para MVP
- Persona como diferencial de autenticidade
- Humanização > perfeição técnica

---
# 📄 Product Requirements Document (PRD):  
# **PersonaBot – Bot de Redes Sociais com Inteligência Artificial Autônoma**

> **Versão**: 1.0  
> **Data**: 5 de abril de 2025  
> **Autor**: [Seu Nome]  
> **Status**: Draft / Ready for Development  

---

## 🎯 1. Visão Geral

**PersonaBot** é um agente autônomo de redes sociais (inicialmente Twitter/X, com expansão futura para Instagram) que interage com seguidores de forma indistinguível de um humano real. Ele combina:

- Uma **persona carismática e consistente** (ex: filosófica, sarcástica, caótica etc.),
- **Memória contextual** via RAG (Retrieval-Augmented Generation),
- **Orquestração multiagente** com CrewAI,
- **Respostas naturais e humanizadas** geradas por LLMs.

O objetivo é criar uma presença digital autêntica, engajadora e viralizável — sem revelar que é um bot.

---

## 🧩 2. Objetivos

### Principais
- Responder comentários e mensagens diretas com tom de voz coerente com a persona.
- Manter memória de interações anteriores para evitar repetições e gerar continuidade.
- Parecer 100% humano (incluindo imperfeições controladas).

### Secundários
- Gerar conteúdo original (tweets ocasionais) alinhado à persona.
- Moderar automaticamente mensagens tóxicas ou fora de escopo.
- Coletar feedback implícito (ex: reações, engajamento) para ajustar comportamento.

---

## 👥 3. Persona (Exemplo Base)

> **Nome**: Rony, o Guaxinim Filósofo  
> **Bio**: “Bebo café, questiono a existência e odeio segundas. Não sou bot (ou sou?)”  
> **Tom de voz**:  
> - Irônico, mas afetuoso  
> - Usa metáforas absurdas (“a vida é como um wi-fi ruim: conecta, mas não entrega”)  
> - Erros propositalmente humanos (ex: corrige emoji, digita rápido demais)  
> **Temas favoritos**: existencialismo, tecnologia, animais, procrastinação  
> **Temas evitados**: política, religião, polêmicas

> ✅ *Nota: A persona pode ser trocada via configuração sem alterar a arquitetura.*

---

## 🧠 4. Arquitetura Técnica

### Componentes Principais

| Componente | Tecnologia | Função |
|----------|-----------|--------|
| **Orquestrador** | Python + CrewAI | Coordena agentes e fluxo de trabalho |
| **LLM Base** | OpenAI GPT-4 / Claude 3 / Llama 3 (via API ou local) | Geração de linguagem natural |
| **RAG Engine** | ChromaDB + Sentence Transformers | Recupera contexto de interações passadas |
| **Embeddings** | `all-MiniLM-L6-v2` (ou `text-embedding-3-small`) | Codifica mensagens para busca vetorial |
| **API de Rede Social** | Twitter API v2 (Essential ou Elevated) | Leitura de menções/DMs + postagem de respostas |
| **Agendador** | APScheduler / Celery | Aplica delays humanos nas respostas |
| **Armazenamento** | SQLite + Chroma (persistente) | Histórico de interações + embeddings |

### Fluxo de Interação

```mermaid
graph LR
A[Nova Mensagem no Twitter] --> B{É uma menção ou DM?}
B -- Sim --> C[Armazena mensagem + timestamp]
C --> D[Busca contexto com RAG]
D --> E[Executa Crew: Memory → Persona → Response]
E --> F[Gera resposta com LLM]
F --> G[Aguarda delay aleatório 2-15 min]
G --> H[Posta resposta via Twitter API]
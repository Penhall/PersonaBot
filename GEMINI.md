# GEMINI.md: PersonaBot

## Project Overview

PersonaBot is a Python-based social media bot designed to interact with users on platforms like Twitter and Instagram. The bot leverages a multi-agent system orchestrated by **CrewAI** and a **Retrieval-Augmented Generation (RAG)** system for contextual memory. The core of the project is to create a bot with a charismatic and consistent persona that is indistinguishable from a human.

The main technologies used in this project are:
*   **Python**: The primary programming language.
*   **CrewAI**: For orchestrating multiple AI agents.
*   **RAG (Retrieval-Augmented Generation)**: To provide contextual memory from past interactions.
*   **ChromaDB (or similar)**: As a vector store for the RAG system.
*   **LLMs (GPT-4, Claude, Llama 3, etc.)**: For generating natural language responses.

## Building and Running

### 1. Setup Environment

To set up the development environment, you need to have Python installed. Then, you can install the required dependencies from the `requirements.txt` file.

```bash
# TODO: Create requirements.txt and add dependencies
pip install -r requirements.txt
```

### 2. Configure the Persona

The bot's persona is defined in a `config/persona.yaml` file. You can customize the persona by editing this file.

```yaml
# Example config/persona.yaml
name: "Rony, o Guaxinim Filósofo"
bio: "Bebo café, questiono a existência e odeio segundas. Não sou bot (ou sou?)"
tone_of_voice:
  - "Irônico, mas afetuoso"
  - "Usa metáforas absurdas"
  - "Erros propositalmente humanos"
favorite_topics: ["existencialismo", "tecnologia", "animais", "procrastinação"]
avoided_topics: ["política", "religião", "polêmicas"]
```

### 3. Running the Bot

To run the bot, you will need to execute the main Python script.

```bash
# TODO: Create the main script to run the bot
python src/main.py
```

## Development Conventions

*   **Code Style**: The project follows standard Python coding conventions (PEP 8).
*   **Testing**: The project should have a suite of tests to ensure the bot's functionality and the persona's consistency.
*   **Contributions**: Contributions should follow the guidelines outlined in the project's backlog and PRD. Before implementing a new feature, it's important to discuss it with the team.

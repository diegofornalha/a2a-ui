# A2A Python Example UI

Interface de usuário para o sistema Agent2Agent (A2A) desenvolvida em Python.

## Descrição

Esta é uma interface web moderna para interagir com agentes A2A, construída usando FastAPI, Mesop e outras tecnologias Python modernas.

## Funcionalidades

- Interface web responsiva
- Gerenciamento de agentes
- Conversas em tempo real
- Visualização de eventos e tarefas
- Configurações do sistema

## Instalação

```bash
# Usando uv (recomendado)
uv pip install -e .

# Ou usando pip
pip install -e .
```

## Execução

```bash
# Usando o script de inicialização
./start_a2a_ui.sh

# Ou diretamente
python main.py
```

## Acesso

A interface estará disponível em: http://localhost:12000

## Páginas Disponíveis

- **Home**: http://localhost:12000/
- **Agents**: http://localhost:12000/agents
- **Conversation**: http://localhost:12000/conversation
- **Events**: http://localhost:12000/event_list
- **Tasks**: http://localhost:12000/task_list
- **Settings**: http://localhost:12000/settings

## Tecnologias

- FastAPI
- Mesop
- Uvicorn
- A2A SDK
- Pydantic
- E outras dependências listadas no pyproject.toml

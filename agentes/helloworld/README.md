# HelloWorld Agent

A simple A2A (Agent-to-Agent) protocol implementation for testing and demonstration purposes.

## Description

The HelloWorld Agent responds to messages with a simple "Hello World" response, demonstrating the basic A2A protocol communication.

## Setup

```bash
uv sync
uv run python main_helloworld.py
```

## A2A Protocol Endpoints

- `/discover` - Agent discovery endpoint
- `/communicate` - Agent communication endpoint  
- `/health` - Health check endpoint
- `/.well-known/agent.json` - Agent card metadata
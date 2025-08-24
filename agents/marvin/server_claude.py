#!/usr/bin/env python3
"""
Servidor A2A para o agente Marvin usando Claude Code SDK.
Compatível com o protocolo Agent-to-Agent.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
import uvicorn

# Adicionar caminhos
sys.path.insert(0, '/home/codable/terminal/claude-code-sdk-python/src')
sys.path.insert(0, '/home/codable/terminal/app-agentflix/web/a2a-ui')

# Importar agente Claude
from agent_claude import ClaudeExtractorAgent

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="Marvin Agent (Claude SDK)",
    description="Agente Marvin usando Claude Code SDK local",
    version="1.0.0"
)

# Instância global do agente
marvin_agent = None


def get_agent():
    """Obtém ou cria instância do agente Marvin."""
    global marvin_agent
    if marvin_agent is None:
        marvin_agent = ClaudeExtractorAgent(
            instructions="""
            Você é o Marvin, um assistente inteligente e útil.
            Você usa Claude Code SDK para processar informações.
            
            Suas capacidades incluem:
            1. Extração de informações estruturadas
            2. Responder perguntas de forma clara
            3. Fazer perguntas clarificadoras quando necessário
            4. Manter contexto da conversa
            
            Seja conciso, preciso e útil em suas respostas.
            """,
            result_type=dict
        )
    return marvin_agent


@app.get("/")
async def root():
    """Endpoint raiz com informações do agente."""
    return {
        "name": "Marvin Agent",
        "version": "1.0.0",
        "powered_by": "Claude Code SDK",
        "description": "Agente inteligente usando Claude local",
        "endpoints": {
            "invoke": "/invoke",
            "stream": "/stream",
            "health": "/health",
            "agent_card": "/.well-known/agent.json"
        }
    }


@app.get("/health")
async def health():
    """Verifica saúde do serviço."""
    # Verificar se Claude está disponível
    import subprocess
    try:
        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True,
            text=True,
            timeout=2
        )
        claude_available = result.returncode == 0
        claude_version = result.stdout.strip() if claude_available else None
    except:
        claude_available = False
        claude_version = None
    
    return {
        "status": "healthy",
        "agent": "Marvin",
        "sdk": "Claude Code SDK",
        "claude_available": claude_available,
        "claude_version": claude_version
    }


@app.get("/.well-known/agent.json")
async def agent_card():
    """Retorna o Agent Card para protocolo A2A."""
    return {
        "name": "Marvin Agent",
        "description": "Assistente inteligente para extração de informações usando Claude Code SDK",
        "version": "1.0.0",
        "protocol": "a2a/1.0",
        "url": f"http://localhost:{os.getenv('MARVIN_PORT', '8180')}",
        "capabilities": [
            "extraction",
            "conversation",
            "clarification",
            "streaming"
        ],
        "authentication": {
            "type": "none"
        },
        "endpoints": {
            "invoke": "/invoke",
            "stream": "/stream"
        },
        "powered_by": "Claude Code SDK",
        "no_api_key_required": True
    }


@app.post("/invoke")
async def invoke(request: Request):
    """
    Endpoint principal para invocar o agente.
    Compatível com protocolo A2A.
    """
    try:
        data = await request.json()
        
        # Extrair query e session_id
        query = data.get("query", "")
        session_id = data.get("session_id", data.get("sessionId", "default"))
        
        if not query:
            raise HTTPException(status_code=400, detail="Query é obrigatória")
        
        logger.info(f"Invoke request - Session: {session_id}, Query: {query[:50]}...")
        
        # Obter agente
        agent = get_agent()
        
        # Processar query
        result = await agent.invoke(query, session_id)
        
        logger.info(f"Invoke response - Complete: {result.get('is_task_complete')}")
        
        return {
            "success": True,
            "result": result,
            "session_id": session_id,
            "powered_by": "Claude Code SDK"
        }
        
    except Exception as e:
        logger.error(f"Erro no invoke: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stream")
async def stream_endpoint(request: Request):
    """
    Endpoint de streaming para respostas incrementais.
    """
    try:
        data = await request.json()
        
        query = data.get("query", "")
        session_id = data.get("session_id", data.get("sessionId", "default"))
        
        if not query:
            raise HTTPException(status_code=400, detail="Query é obrigatória")
        
        logger.info(f"Stream request - Session: {session_id}, Query: {query[:50]}...")
        
        # Obter agente
        agent = get_agent()
        
        async def generate():
            """Gerador de streaming."""
            try:
                async for chunk in agent.stream(query, session_id):
                    yield f"data: {json.dumps(chunk)}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                error_msg = {"error": str(e)}
                yield f"data: {json.dumps(error_msg)}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Powered-By": "Claude Code SDK"
            }
        )
        
    except Exception as e:
        logger.error(f"Erro no stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/discover")
async def discover():
    """
    Endpoint de descoberta A2A.
    Retorna capacidades do agente.
    """
    return {
        "agent": "Marvin",
        "capabilities": {
            "extraction": True,
            "streaming": True,
            "context_memory": True,
            "clarifying_questions": True
        },
        "sdk": "Claude Code SDK",
        "no_api_key": True,
        "endpoints": {
            "invoke": "/invoke",
            "stream": "/stream",
            "health": "/health"
        }
    }


def main():
    """Função principal para executar o servidor."""
    port = int(os.getenv('MARVIN_PORT', '8180'))
    host = os.getenv('MARVIN_HOST', '0.0.0.0')
    
    print("=" * 60)
    print("🤖 Marvin Agent Server (Claude SDK)")
    print("=" * 60)
    print(f"✅ Rodando em: http://{host}:{port}")
    print("✅ Usando Claude Code SDK (sem API keys!)")
    print("=" * 60)
    print("\nEndpoints:")
    print(f"  GET  http://localhost:{port}/")
    print(f"  GET  http://localhost:{port}/health")
    print(f"  GET  http://localhost:{port}/.well-known/agent.json")
    print(f"  POST http://localhost:{port}/invoke")
    print(f"  POST http://localhost:{port}/stream")
    print(f"  POST http://localhost:{port}/discover")
    print("\nPressione Ctrl+C para parar")
    print("-" * 60)
    
    # Executar servidor
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
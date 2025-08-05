"""
Servidor Backend Simples para Aplicação Mesop
Fornece endpoints necessários para a página de eventos
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class Event(BaseModel):
    """Modelo de evento"""
    id: str
    context_id: str
    role: str
    actor: str
    content: List[Dict[str, Any]]
    timestamp: str


class Conversation(BaseModel):
    """Modelo de conversa"""
    conversation_id: str
    name: str
    is_active: bool
    messages: List[str] = []


class Message(BaseModel):
    """Modelo de mensagem"""
    messageId: str
    contextId: str
    role: str
    parts: List[Dict[str, Any]] = []


class Task(BaseModel):
    """Modelo de tarefa"""
    id: str
    context_id: str
    state: str
    description: str


# Estado global do servidor
events: List[Event] = []
conversations: List[Conversation] = []
messages: List[Message] = []
tasks: List[Task] = []
agents: List[Dict[str, Any]] = []

app = FastAPI(title="A2A Backend Server", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Endpoint de saúde do servidor"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/conversation/create")
async def create_conversation():
    """Cria uma nova conversa"""
    conversation_id = f"conv_{len(conversations) + 1}"
    conversation = Conversation(
        conversation_id=conversation_id,
        name=f"Conversa {len(conversations) + 1}",
        is_active=True
    )
    conversations.append(conversation)
    return {"result": conversation}


@app.post("/conversation/list")
async def list_conversations():
    """Lista todas as conversas"""
    return {"result": conversations}


@app.post("/message/send")
async def send_message(request: Request):
    """Envia uma mensagem"""
    data = await request.json()
    message_data = data.get("params", {})
    
    message = Message(
        messageId=f"msg_{len(messages) + 1}",
        contextId=message_data.get("contextId", "default"),
        role=message_data.get("role", "user"),
        parts=message_data.get("parts", [])
    )
    
    messages.append(message)
    
    # Criar evento associado
    event = Event(
        id=f"event_{len(events) + 1}",
        context_id=message.contextId,
        role=message.role,
        actor="user",
        content=message.parts,
        timestamp=datetime.now().isoformat()
    )
    events.append(event)
    
    # PROCESSAMENTO AUTOMÁTICO DE MENSAGENS
    print(f"🔄 Iniciando processamento automático para mensagem: {message.messageId}")
    try:
        await process_message_automatically(message)
        print(f"✅ Processamento automático concluído para: {message.messageId}")
    except Exception as e:
        print(f"❌ Erro no processamento automático: {e}")
        import traceback
        traceback.print_exc()
    
    return {
        "result": {
            "message_id": message.messageId,
            "context_id": message.contextId
        }
    }

async def process_message_automatically(message: Message):
    """Processa mensagens automaticamente e delega para agentes"""
    import asyncio
    import httpx
    
    print(f"🔍 Iniciando processamento automático para mensagem: {message.messageId}")
    
    # Verificar se é uma mensagem de delegação
    content = ""
    if message.parts:
        for part in message.parts:
            if isinstance(part, dict) and part.get("type") == "text":
                content += part.get("text", "")
    
    print(f"📝 Conteúdo da mensagem: {content}")
    
    if "delegue" in content.lower() or "delegate" in content.lower():
        print(f"🔄 Processando delegação: {content}")
        
        # Identificar o agente alvo
        target_agent = None
        if "criativo" in content.lower():
            target_agent = "http://localhost:8003"
        elif "estrategista" in content.lower():
            target_agent = "http://localhost:8002"
        elif "copywriter" in content.lower():
            target_agent = "http://localhost:8004"
        elif "otimizador" in content.lower():
            target_agent = "http://localhost:8005"
        
        print(f"🎯 Agente alvo identificado: {target_agent}")
        
        if target_agent:
            try:
                print(f"📤 Enviando para o Actor/Orchestrator: http://localhost:8001/communicate")
                async with httpx.AsyncClient(timeout=10.0) as client:
                    # Enviar mensagem para o Actor que coordena os agentes
                    response = await client.post(
                        "http://localhost:8001/communicate",
                        json={
                            "jsonrpc": "2.0",
                            "method": "process_request",
                            "params": {
                                "query": content,
                                "conversation_id": message.contextId
                            },
                            "id": f"delegation_{message.messageId}"
                        }
                    )
                    
                    print(f"📥 Resposta do agente: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"📋 Resultado: {result}")
                        if result.get("result"):
                            # Criar resposta do agente
                            result_text = result["result"]
                            if isinstance(result_text, dict):
                                # Se result é um dicionário, extrair o texto
                                result_text = result_text.get("result", str(result_text))
                            elif not isinstance(result_text, str):
                                result_text = str(result_text)
                            
                            agent_response = Message(
                                messageId=f"agent_response_{len(messages) + 1}",
                                contextId=message.contextId,
                                role="assistant",
                                parts=[{"type": "text", "text": result_text}]
                            )
                            messages.append(agent_response)
                            print(f"✅ Resposta do agente: {result_text[:100]}...")
                        else:
                            print(f"❌ Agente não retornou resultado válido")
                    else:
                        print(f"❌ Erro ao comunicar com agente: {response.status_code}")
                        print(f"📄 Conteúdo da resposta: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao processar delegação: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ Agente não identificado na mensagem: {content}")
    else:
        print(f"📝 Mensagem normal processada: {content[:50]}...")


@app.post("/events/get")
async def get_events():
    """Retorna todos os eventos"""
    return {"result": events}


@app.post("/message/list")
async def list_messages(request: Request):
    """Lista mensagens de uma conversa"""
    data = await request.json()
    conversation_id = data.get("params", "")
    
    # Filtrar mensagens por conversation_id
    filtered_messages = [
        msg for msg in messages 
        if msg.contextId == conversation_id
    ]
    
    return {"result": filtered_messages}


@app.post("/message/pending")
async def pending_messages():
    """Retorna mensagens pendentes"""
    return {"result": {}}


@app.post("/task/list")
async def list_tasks():
    """Lista todas as tarefas"""
    return {"result": tasks}


@app.post("/agent/register")
async def register_agent(request: Request):
    """Registra um novo agente"""
    data = await request.json()
    agent_url = data.get("params", "")
    
    agent = {
        "url": agent_url,
        "name": f"Agent {len(agents) + 1}",
        "description": f"Agente registrado em {agent_url}",
        "enabled": True,
        "status": "online"
    }
    
    agents.append(agent)
    return {"result": {"success": True}}


@app.post("/agent/remove")
async def remove_agent(request: Request):
    """Remove um agente"""
    data = await request.json()
    agent_url = data.get("params", "")
    
    global agents
    agents = [agent for agent in agents if agent["url"] != agent_url]
    
    return {"result": {"success": True}}


@app.post("/agent/list")
async def list_agents():
    """Lista todos os agentes"""
    return {"result": agents}


@app.post("/agent/toggle")
async def toggle_agent(request: Request):
    """Habilita/desabilita um agente"""
    data = await request.json()
    params = data.get("params", {})
    agent_url = params.get("agent_url", "")
    enabled = params.get("enabled", True)
    
    for agent in agents:
        if agent["url"] == agent_url:
            agent["enabled"] = enabled
            return {
                "result": {
                    "success": True,
                    "message": f"Agente {'habilitado' if enabled else 'desabilitado'}"
                }
            }
    
    return {
        "result": {
            "success": False,
            "message": "Agente não encontrado"
        }
    }


@app.post("/agent/refresh")
async def refresh_agents():
    """Força redescoberta de agentes"""
    # Simular descoberta de agentes
    discovered_agents = [
        {
            "url": "http://localhost:9999",
            "name": "HelloWorld Agent",
            "description": "Agente Hello World",
            "enabled": True,
            "status": "online"
        },
        {
            "url": "http://localhost:10030",
            "name": "Marvin Agent", 
            "description": "Agente Marvin",
            "enabled": True,
            "status": "online"
        }
    ]
    
    global agents
    agents = discovered_agents
    
    return {
        "result": {
            "discovered_count": len(discovered_agents),
            "message": f"Descoberta atualizada: {len(discovered_agents)} agentes encontrados"
        }
    }


@app.post("/api_key/update")
async def update_api_key(request: Request):
    """Atualiza a chave da API"""
    data = await request.json()
    api_key = data.get("api_key", "")
    
    # Simular atualização da chave
    os.environ["GOOGLE_API_KEY"] = api_key
    
    return {"result": {"success": True}}


if __name__ == "__main__":
    print("🚀 Iniciando Servidor Backend A2A na porta 8085...")
    print("📡 Endpoints disponíveis:")
    print("   - GET  /health")
    print("   - POST /conversation/create")
    print("   - POST /conversation/list")
    print("   - POST /message/send")
    print("   - POST /events/get")
    print("   - POST /message/list")
    print("   - POST /agent/list")
    print("   - POST /agent/refresh")
    print("")
    print("🔗 URL: http://localhost:8085")
    print("📊 Health Check: http://localhost:8085/health")
    print("")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8085,
        log_level="info"
    ) 
#!/usr/bin/env python3
"""
Servidor simples para o Marvin Agent
"""

import asyncio
import uvicorn
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório pai ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

from agent import ExtractorAgent
from agent_executor import ExtractorAgentExecutor
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from pydantic import BaseModel, EmailStr, Field


class ContactInfo(BaseModel):
    """Structured contact information extracted from text."""
    name: str = Field(description="Person's first and last name")
    email: EmailStr = Field(description="Email address")
    phone: str = Field(description="Phone number if present")
    organization: str | None = Field(None, description="Organization or company if mentioned")
    role: str | None = Field(None, description="Job title or role if mentioned")


def get_agent_card(host: str, port: int):
    """Returns the Agent Card for the ExtractorAgent."""
    capabilities = AgentCapabilities(streaming=True)
    skill = AgentSkill(
        id="extract_contacts",
        name="Contact Information Extraction",
        description="Extracts structured contact information from text",
        tags=["contact info", "structured extraction", "information extraction"],
        examples=["My name is John Doe, email: john@example.com, phone: (555) 123-4567"],
    )
    return AgentCard(
        name="Marvin Contact Extractor",
        description="Extracts structured contact information from text using Marvin's extraction capabilities",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text", "text/plain", "application/json"],
        defaultOutputModes=["text", "text/plain", "application/json"],
        capabilities=capabilities,
        skills=[skill],
    )


def main():
    """Iniciar o servidor Marvin"""
    host = "localhost"
    port = 10030
    
    print(f"🚀 Iniciando servidor Marvin em {host}:{port}...")
    
    # Criar o agente
    agent = ExtractorAgent(
        instructions="Politely interrogate the user for their contact information. The schema of the result type implies what things you _need_ to get from the user.",
        result_type=ContactInfo
    )
    
    # Criar o handler de requisições
    request_handler = DefaultRequestHandler(
        agent_executor=ExtractorAgentExecutor(agent=agent),
        task_store=InMemoryTaskStore(),
    )
    
    # Criar o servidor
    server = A2AStarletteApplication(
        agent_card=get_agent_card(host, port), 
        http_handler=request_handler
    )
    
    print("✅ Servidor configurado, iniciando...")
    
    # Iniciar o servidor
    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Teste rápido do Marvin com a nova chave
"""

import asyncio
import sys
import os
from pathlib import Path

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

# Verificar se a chave está configurada
api_key = os.getenv('OPENAI_API_KEY')
print(f"🔑 Chave OpenAI configurada: {api_key[:20]}..." if api_key else "❌ Chave não encontrada")

# Adicionar path
sys.path.append(str(Path(__file__).parent))

from agents.marvin.agent import ExtractorAgent
from pydantic import BaseModel, EmailStr, Field

class ContactInfo(BaseModel):
    name: str = Field(description="Person's first and last name")
    email: EmailStr = Field(description="Email address")
    phone: str = Field(description="Phone number if present")
    organization: str | None = Field(None, description="Organization or company if mentioned")
    role: str | None = Field(None, description="Job title or role if mentioned")

async def test():
    """Teste simples"""
    try:
        agent = ExtractorAgent(
            instructions="Extraia informações de contato.",
            result_type=ContactInfo
        )
        
        result = await agent.invoke("Nome: Diego Alcantara, Idade: 30 anos, Cargo: CEO", "test_session")
        print("✅ Resultado:", result)
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(test())
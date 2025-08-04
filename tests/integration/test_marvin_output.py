#!/usr/bin/env python3
"""
Script para testar o output do Marvin e mostrar o formato exato
"""

import asyncio
import json
import sys
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

from agents.marvin.agent import ExtractorAgent
from pydantic import BaseModel, EmailStr, Field


class ContactInfo(BaseModel):
    """Structured contact information extracted from text."""
    name: str = Field(description="Person's first and last name")
    email: EmailStr = Field(description="Email address")
    phone: str = Field(description="Phone number if present")
    organization: str | None = Field(None, description="Organization or company if mentioned")
    role: str | None = Field(None, description="Job title or role if mentioned")


async def test_marvin_output():
    """Testar o output do Marvin com exemplos reais"""
    
    # Criar o agente
    agent = ExtractorAgent(
        instructions="Extraia informações de contato do texto fornecido de forma precisa e estruturada.",
        result_type=ContactInfo
    )
    
    # Exemplos de teste
    test_cases = [
        "João Silva, Desenvolvedor na TechCorp, joao.silva@techcorp.com, (11) 99999-9999",
        "Maria Santos | Gerente de Vendas | Empresa XYZ | maria@xyz.com.br | +55 21 98765-4321",
        "Dr. Carlos Mendes, cardiologista, carlos@clinica.med.br, telefone (11) 2222-3333"
    ]
    
    print("🧪 TESTE DO OUTPUT DO MARVIN")
    print("=" * 50)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n📝 EXEMPLO {i}:")
        print(f"Input: {test_text}")
        print("-" * 30)
        
        try:
            # Processar com o agente
            result = await agent.invoke(test_text, f"test_session_{i}")
            
            print("📊 OUTPUT COMPLETO:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            print("\n💾 DADOS ESTRUTURADOS:")
            if result.get('data'):
                for key, value in result['data'].items():
                    print(f"  {key}: {value}")
            
            print("\n💬 RESPOSTA DO AGENTE:")
            if result.get('text_parts'):
                for part in result['text_parts']:
                    print(f"  {part.text}")
            
            print("\n" + "=" * 50)
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_marvin_output())
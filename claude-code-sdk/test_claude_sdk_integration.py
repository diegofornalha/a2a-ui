#!/usr/bin/env python3
"""
Script de teste completo da integração Claude SDK com A2A-UI
Demonstra todas as funcionalidades integradas
"""

import asyncio
import sys
from datetime import datetime

# Adicionar ao path
sys.path.insert(0, '.')

# Importar componentes
from agents.claude_sdk_agent import get_claude_sdk_agent
from service.client.claude_sdk_client import ClaudeSDKClient


async def test_basic_chat():
    """Testa chat básico"""
    print("\n" + "="*60)
    print("🗣️ TESTE 1: Chat Básico")
    print("="*60)
    
    agent = get_claude_sdk_agent()
    
    questions = [
        "Olá! Quem é você?",
        "O que é Python?",
        "Como criar uma lista em Python?"
    ]
    
    for question in questions:
        print(f"\n👤 Pergunta: {question}")
        response = await agent.process_message(question)
        
        if response["success"]:
            print(f"🤖 Resposta: {response['content'][:200]}...")
        else:
            print(f"❌ Erro: {response['error']}")


async def test_code_generation():
    """Testa geração de código"""
    print("\n" + "="*60)
    print("🔧 TESTE 2: Geração de Código")
    print("="*60)
    
    agent = get_claude_sdk_agent()
    
    tasks = [
        ("função para calcular fatorial", "python"),
        ("componente React de botão", "javascript"),
        ("classe de usuário com validação", "python")
    ]
    
    for description, language in tasks:
        print(f"\n📝 Tarefa: {description} ({language})")
        response = await agent.generate_code(description, language)
        
        if response["success"]:
            print(f"✅ Código gerado:")
            print("```" + language)
            print(response['code'][:300])
            if len(response['code']) > 300:
                print("...")
            print("```")
        else:
            print(f"❌ Erro: {response['error']}")


async def test_code_analysis():
    """Testa análise de código"""
    print("\n" + "="*60)
    print("🔍 TESTE 3: Análise de Código")
    print("="*60)
    
    agent = get_claude_sdk_agent()
    
    code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
    
    analyses = ["explain", "optimize", "review"]
    
    for task in analyses:
        print(f"\n📊 Análise tipo: {task}")
        response = await agent.analyze_code(code, task=task)
        
        if response["success"]:
            print(f"✅ Resultado:")
            print(response['analysis'][:300] + "...")
        else:
            print(f"❌ Erro: {response['error']}")


async def test_task_execution():
    """Testa execução de tarefas A2A"""
    print("\n" + "="*60)
    print("🎯 TESTE 4: Execução de Tarefas A2A")
    print("="*60)
    
    agent = get_claude_sdk_agent()
    
    # Tarefa simples
    print("\n📋 Tarefa simples:")
    task = "Crie um plano para desenvolver uma API REST de blog"
    response = await agent.execute_task(task)
    
    if response["success"]:
        print(f"✅ Resultado:")
        print(response['result'][:400] + "...")
    else:
        print(f"❌ Erro: {response['error']}")
    
    # Tarefa com múltiplos agentes
    print("\n👥 Tarefa com múltiplos agentes:")
    task = "Analise os prós e contras de usar Python vs JavaScript"
    agents = ["backend-developer", "frontend-developer", "devops"]
    response = await agent.execute_task(task, agents=agents)
    
    if response["success"]:
        print(f"✅ Resultado com perspectivas de {len(agents)} agentes:")
        print(response['result'][:400] + "...")
    else:
        print(f"❌ Erro: {response['error']}")


async def test_streaming():
    """Testa streaming de respostas"""
    print("\n" + "="*60)
    print("📡 TESTE 5: Streaming de Respostas")
    print("="*60)
    
    agent = get_claude_sdk_agent()
    
    print("\n🌊 Pergunta: Liste 5 benefícios de Python")
    print("🤖 Resposta (streaming):")
    
    chunk_count = 0
    async for chunk_data in agent.stream_response("Liste 5 benefícios de Python"):
        if chunk_data["success"]:
            print(chunk_data["chunk"], end="", flush=True)
            chunk_count += 1
        else:
            print(f"\n❌ Erro: {chunk_data['error']}")
            break
    
    print(f"\n\n✅ Recebidos {chunk_count} chunks")


async def test_conversation_context():
    """Testa manutenção de contexto na conversa"""
    print("\n" + "="*60)
    print("💬 TESTE 6: Contexto de Conversa")
    print("="*60)
    
    agent = get_claude_sdk_agent()
    conversation_id = f"test-conv-{datetime.now().timestamp()}"
    
    # Conversa com contexto
    messages = [
        "Meu nome é João",
        "Qual é meu nome?",
        "Vou aprender Python",
        "O que eu vou aprender?"
    ]
    
    for msg in messages:
        print(f"\n👤: {msg}")
        response = await agent.process_message(
            msg, 
            conversation_id=conversation_id,
            context={"session": "test"}
        )
        
        if response["success"]:
            print(f"🤖: {response['content'][:200]}...")
        else:
            print(f"❌ Erro: {response['error']}")
    
    # Verificar histórico
    print(f"\n📜 Histórico: {len(agent.conversation_history)} mensagens")


async def test_client_directly():
    """Testa o cliente SDK diretamente"""
    print("\n" + "="*60)
    print("🔌 TESTE 7: Cliente SDK Direto")
    print("="*60)
    
    client = ClaudeSDKClient()
    
    if not client.initialized:
        print("❌ Cliente não inicializado")
        return
    
    # Query simples
    print("\n📝 Query simples:")
    response = await client.query_simple("O que é IA?")
    if response.success:
        print(f"✅ Resposta: {response.content[:200]}...")
    else:
        print(f"❌ Erro: {response.error}")
    
    # Query com ferramentas
    print("\n🔧 Query com ferramentas:")
    response = await client.query_with_tools(
        "Liste os arquivos Python no diretório atual",
        allowed_tools=["Read"]
    )
    if response.success:
        print(f"✅ Resposta: {response.content[:200]}...")
        if response.metadata and "tools_used" in response.metadata:
            print(f"   Ferramentas usadas: {response.metadata['tools_used']}")
    else:
        print(f"❌ Erro: {response.error}")


async def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "🚀"*30)
    print("TESTE COMPLETO - INTEGRAÇÃO CLAUDE SDK COM A2A-UI")
    print("🚀"*30)
    
    # Verificar se o agente está pronto
    agent = get_claude_sdk_agent()
    
    print("\n📊 Status Inicial:")
    status = agent.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    if not agent.is_ready:
        print("\n❌ Agente não está pronto!")
        print("💡 Instale o Claude SDK: pip install claude-code-sdk")
        return
    
    print("\n✅ Sistema pronto! Iniciando testes...")
    
    # Executar testes
    tests = [
        ("Chat Básico", test_basic_chat),
        ("Geração de Código", test_code_generation),
        ("Análise de Código", test_code_analysis),
        ("Execução de Tarefas", test_task_execution),
        ("Streaming", test_streaming),
        ("Contexto de Conversa", test_conversation_context),
        ("Cliente Direto", test_client_directly)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            print(f"\n🔄 Executando: {name}")
            await test_func()
            results.append((name, "✅ Sucesso"))
        except Exception as e:
            print(f"❌ Erro no teste {name}: {e}")
            results.append((name, f"❌ Erro: {e}"))
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    for name, result in results:
        print(f"  {name}: {result}")
    
    # Status final
    print("\n📊 Status Final:")
    final_status = agent.get_status()
    print(f"  Conversas: {final_status['conversation_count']}")
    print(f"  SDK: {'✅ Ativo' if final_status['sdk_initialized'] else '❌ Inativo'}")
    
    print("\n" + "🎉"*30)
    print("TESTES CONCLUÍDOS!")
    print("🎉"*30)


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║           TESTE DE INTEGRAÇÃO CLAUDE SDK + A2A           ║
    ╠══════════════════════════════════════════════════════════╣
    ║  Este script testa a integração completa do Claude SDK   ║
    ║  com o sistema A2A-UI, substituindo o Gemini/Vertex AI   ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        import anyio
        anyio.run(run_all_tests)
    except ImportError:
        print("❌ anyio não instalado. Instalando...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "anyio"])
        print("✅ Tente executar novamente!")
    except KeyboardInterrupt:
        print("\n\n⏹️ Testes interrompidos pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
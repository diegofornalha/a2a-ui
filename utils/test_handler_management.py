#!/usr/bin/env python3
"""
Script de teste para demonstrar o gerenciamento de handlers
e como ele evita o erro "Unknown handler id".
"""

import asyncio
import time
from handler_manager import handler_manager, start_handler_monitoring
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def simulate_agent_lifecycle():
    """Simula o ciclo de vida de agentes conectando e desconectando."""
    
    # 1. Iniciar monitoramento
    logger.info("🚀 Iniciando monitoramento de handlers...")
    await start_handler_monitoring()
    
    # 2. Simular registro de handlers para agentes
    agents = [
        ("http://localhost:9999", ["handler_abc123", "handler_def456"]),
        ("http://localhost:10030", ["handler_ghi789", "handler_jkl012"]),
        ("http://localhost:12000", ["handler_mno345", "handler_pqr678"])
    ]
    
    logger.info("📝 Registrando handlers para agentes...")
    for agent_url, handlers in agents:
        for handler_id in handlers:
            handler_manager.register_handler(handler_id, agent_url)
            logger.info(f"  ✅ Handler {handler_id} registrado para {agent_url}")
    
    # 3. Mostrar estado inicial
    logger.info("\n📊 Estado inicial dos agentes:")
    for agent_url in handler_manager.agent_status:
        status = "🟢 Online" if handler_manager.agent_status[agent_url] else "🔴 Offline"
        handler_count = len(handler_manager.agent_handlers.get(agent_url, set()))
        logger.info(f"  {agent_url}: {status} ({handler_count} handlers)")
    
    # 4. Aguardar um pouco
    logger.info("\n⏳ Aguardando 5 segundos...")
    await asyncio.sleep(5)
    
    # 5. Simular que agente na porta 12000 ficou offline
    logger.info("\n🔴 Simulando que agente na porta 12000 ficou offline...")
    handler_manager.agent_status["http://localhost:12000"] = False
    
    # 6. Tentar usar um handler do agente offline
    logger.info("\n🧪 Testando handlers:")
    test_handlers = ["handler_abc123", "handler_mno345", "handler_ghi789"]
    
    for handler_id in test_handlers:
        is_valid = handler_manager.is_handler_valid(handler_id)
        agent_url = handler_manager.handler_agents.get(handler_id, "Unknown")
        
        if is_valid:
            logger.info(f"  ✅ Handler {handler_id} é válido (agente {agent_url} online)")
        else:
            logger.warning(f"  ❌ Handler {handler_id} é inválido (agente {agent_url} offline)")
    
    # 7. Simular limpeza de handlers do agente offline
    logger.info("\n🧹 Limpando handlers do agente offline...")
    await handler_manager._handle_agent_disconnection("http://localhost:12000")
    
    # 8. Mostrar estado após limpeza
    logger.info("\n📊 Estado após limpeza:")
    for agent_url in handler_manager.agent_status:
        status = "🟢 Online" if handler_manager.agent_status[agent_url] else "🔴 Offline"
        handler_count = len(handler_manager.agent_handlers.get(agent_url, set()))
        logger.info(f"  {agent_url}: {status} ({handler_count} handlers)")
    
    # 9. Verificar handlers removidos
    logger.info("\n🔍 Verificando handlers após limpeza:")
    for handler_id in ["handler_mno345", "handler_pqr678"]:
        if handler_id in handler_manager.handler_agents:
            logger.error(f"  ❌ Handler {handler_id} ainda existe (não deveria!)")
        else:
            logger.info(f"  ✅ Handler {handler_id} foi removido corretamente")
    
    # 10. Parar monitoramento
    logger.info("\n🛑 Parando monitoramento...")
    await handler_manager.stop_monitoring()
    
    logger.info("\n✅ Teste concluído!")


async def demonstrate_error_prevention():
    """Demonstra como o sistema previne o erro 'Unknown handler id'."""
    
    logger.info("\n" + "="*60)
    logger.info("🎯 DEMONSTRAÇÃO: Prevenção do erro 'Unknown handler id'")
    logger.info("="*60)
    
    # Cenário 1: Sem gerenciamento de handlers (erro ocorre)
    logger.info("\n📌 Cenário 1: SEM gerenciamento de handlers")
    logger.info("  1. Agente na porta 12000 está online")
    logger.info("  2. UI registra handler_id: f0c2f3bd...")
    logger.info("  3. Agente desconecta")
    logger.info("  4. Usuário clica em botão")
    logger.info("  5. ❌ ERRO: Unknown handler id: f0c2f3bd...")
    
    # Cenário 2: Com gerenciamento de handlers (erro prevenido)
    logger.info("\n📌 Cenário 2: COM gerenciamento de handlers")
    logger.info("  1. Agente na porta 12000 está online")
    logger.info("  2. UI registra handler_id no HandlerManager")
    logger.info("  3. Agente desconecta")
    logger.info("  4. HandlerManager detecta desconexão")
    logger.info("  5. HandlerManager marca handlers como inválidos")
    logger.info("  6. Usuário clica em botão")
    logger.info("  7. ✅ Sistema verifica handler antes de executar")
    logger.info("  8. ✅ Exibe mensagem amigável: 'Agente offline'")
    logger.info("  9. ✅ Nenhum erro de 'Unknown handler id'!")
    
    logger.info("\n💡 Benefícios:")
    logger.info("  • Experiência do usuário melhorada")
    logger.info("  • Sem erros criptográficos para o usuário")
    logger.info("  • Possibilidade de reconexão automática")
    logger.info("  • Logging detalhado para debugging")


async def main():
    """Função principal do teste."""
    try:
        # Executar simulação do ciclo de vida
        await simulate_agent_lifecycle()
        
        # Demonstrar prevenção de erro
        await demonstrate_error_prevention()
        
    except Exception as e:
        logger.error(f"Erro durante teste: {e}")
    finally:
        # Garantir limpeza
        await handler_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
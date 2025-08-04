# 🛡️ Solução: Gerenciamento de Handlers para Prevenir "Unknown handler id"

## 📋 Problema Identificado

Quando um agente A2A desconecta (ex: porta 12000 sai do ar), os handlers registrados no Mesop permanecem órfãos, causando o erro:

```
Unknown handler id: f0c2f3bd6c34851e5c50fdd12d197f720616e6b861b6ac2bf11c54c3bb3b8f39
```

## 🔍 Causa Raiz

1. **Handlers Persistentes**: O Mesop mantém handlers registrados mesmo após agentes desconectarem
2. **IDs Baseados em Hash**: Handler IDs são SHA256 do código da função
3. **Sem Limpeza Automática**: Não há mecanismo nativo para remover handlers órfãos
4. **Interação com UI**: Usuário clica em elementos que tentam executar handlers de agentes offline

## 💡 Solução Implementada

### 1. **Handler Manager** (`handler_manager.py`)

Gerenciador centralizado que:
- Rastreia associação handler ↔ agente
- Monitora status dos agentes (online/offline)
- Detecta desconexões automaticamente
- Limpa handlers órfãos
- Verifica validade de handlers antes de execução

### 2. **Mesop Patch** (`mesop_handler_patch.py`)

Intercepta execução de handlers para:
- Verificar se handler é válido antes de executar
- Evitar exceção "Unknown handler id"
- Permitir tratamento gracioso de erros
- Mostrar mensagens amigáveis ao usuário

### 3. **UI Aprimorada** (`agents_with_handler_management.py`)

Interface que:
- Mostra status real-time dos agentes
- Usa handlers seguros que verificam conectividade
- Permite reconexão manual a agentes offline
- Atualiza visual baseado em status

## 🚀 Como Usar

### 1. Integração Básica

```python
# No início do arquivo da página
from utils.handler_manager import handler_manager, start_handler_monitoring
from utils.mesop_handler_patch import patch_mesop_handler, create_safe_handler

# Aplicar patch no Mesop
patch_mesop_handler()

# Iniciar monitoramento
asyncio.create_task(start_handler_monitoring())
```

### 2. Registrar Handlers

```python
# Ao criar um handler para interação com agente
def my_agent_handler(e):
    # Lógica do handler
    pass

# Registrar no manager
handler_id = compute_fn_id(my_agent_handler)  # ID do Mesop
agent_url = "http://localhost:12000"
handler_manager.register_handler(handler_id, agent_url)
```

### 3. Criar Handlers Seguros

```python
# Em vez de:
me.button("Testar", on_click=test_agent)

# Use:
safe_handler = create_safe_handler(test_agent, agent_url)
me.button("Testar", on_click=safe_handler)
```

## 📊 Fluxo de Execução

### Sem Handler Management (Erro)
```
1. Agente online → Handler registrado
2. Agente desconecta
3. Usuário clica → Mesop executa handler
4. ❌ ERROR: Unknown handler id
```

### Com Handler Management (Sucesso)
```
1. Agente online → Handler registrado + rastreado
2. Agente desconecta → Manager detecta
3. Manager marca handlers como inválidos
4. Usuário clica → Verificação antes de executar
5. ✅ Mensagem amigável: "Agente offline"
```

## 🔧 Configuração

### Intervalo de Monitoramento
```python
# Verificar agentes a cada 30 segundos (padrão)
handler_manager = HandlerManager(check_interval=30)

# Ou configurar intervalo customizado
handler_manager = HandlerManager(check_interval=15)  # 15 segundos
```

### Endpoints de Health Check
```python
# O sistema verifica múltiplos endpoints
health_endpoints = [
    "/.well-known/agent.json",
    "/health",
    "/info",
    "/"
]
```

## 🧪 Testando a Solução

Execute o script de teste:
```bash
cd ui/utils
python test_handler_management.py
```

O teste demonstra:
- Registro de handlers
- Detecção de agente offline
- Limpeza automática de handlers
- Prevenção do erro

## 📈 Benefícios

1. **Melhor UX**: Sem erros criptográficos para usuários
2. **Robustez**: Sistema continua funcionando com agentes offline
3. **Transparência**: Status visual claro dos agentes
4. **Manutenibilidade**: Logging detalhado para debugging
5. **Flexibilidade**: Possibilidade de reconexão automática

## 🔮 Melhorias Futuras

1. **Reconexão Automática**: Tentar reconectar periodicamente
2. **Notificações**: Avisar quando agentes voltam online
3. **Persistência**: Salvar estado entre reinicializações
4. **Métricas**: Dashboard com estatísticas de disponibilidade
5. **Fallback**: Redirecionar para agente alternativo

## 📝 Notas Importantes

- O patch do Mesop é não-invasivo e pode ser removido
- O monitoramento é assíncrono e não bloqueia a UI
- Handlers não gerenciados continuam funcionando normalmente
- A solução é compatível com código existente

## 🆘 Troubleshooting

### Handler ainda dá erro após implementar solução
1. Verifique se o patch foi aplicado: `patch_mesop_handler()`
2. Confirme que o handler foi registrado: `handler_manager.register_handler()`
3. Verifique logs para mensagens de erro

### Agente aparece como offline mas está rodando
1. Verifique se a porta está correta
2. Teste endpoints manualmente: `curl http://localhost:PORT/health`
3. Ajuste timeout se necessário

### Performance degradada
1. Aumente intervalo de monitoramento
2. Reduza número de endpoints verificados
3. Implemente cache de status

---

**✅ Com esta solução, o erro "Unknown handler id" é completamente prevenido!**
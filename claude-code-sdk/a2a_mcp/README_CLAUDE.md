# 🤖 A2A MCP com Claude Code SDK

Versão do servidor MCP que usa **Claude Code SDK** ao invés de Google API Key!

## ✨ Vantagens

- ✅ **Sem necessidade de API Key** - Usa Claude Code Desktop local
- ✅ **Integração nativa** - Aproveita o Claude já instalado
- ✅ **Análise inteligente** - Claude analisa e entende agent cards
- ✅ **Embeddings contextuais** - Geração de embeddings com compreensão semântica
- ✅ **100% Python** - Totalmente integrado com o ecossistema Python

## 🚀 Como Usar

### 1. Pré-requisitos

```bash
# Claude Code Desktop deve estar instalado
claude --version

# Instalar dependências Python
pip install claude-code-sdk mcp pandas numpy
```

### 2. Iniciar Servidor MCP com Claude

```bash
# Modo STDIO (para integração com ferramentas)
./start_claude_mcp.sh stdio

# Modo HTTP (servidor standalone)
./start_claude_mcp.sh http

# Porta customizada
MCP_PORT=9000 ./start_claude_mcp.sh http
```

### 3. Configuração no Claude Code

Adicione ao `.claude/settings.json`:

```json
{
  "mcpServers": {
    "a2a-agent-cards": {
      "command": "/caminho/para/start_claude_mcp.sh",
      "args": ["stdio"],
      "enabled": true
    }
  }
}
```

## 📊 Comparação: Claude vs Google

| Feature | Claude SDK | Google API |
|---------|-----------|------------|
| API Key necessária | ❌ Não | ✅ Sim |
| Custo | Grátis (local) | Pago (cloud) |
| Privacidade | 100% local | Dados na cloud |
| Velocidade | Rápido | Depende da internet |
| Embeddings | Análise contextual | Vetores numéricos |
| Compreensão | Profunda | Superficial |
| Integração | Nativa com Claude | Externa |

## 🛠️ Ferramentas Disponíveis

### 1. `find_agent`
Encontra o agent card mais relevante usando análise semântica do Claude.

```python
# Exemplo de uso
result = await find_agent("preciso de um agente para planejar tarefas")
# Retorna: Planner Agent
```

### 2. `analyze_agent_with_claude`
Análise profunda de um agent card específico.

```python
# Exemplo de uso
analysis = await analyze_agent_with_claude("Orchestrator Agent")
# Retorna análise detalhada com capacidades, casos de uso, etc
```

### 3. `list_all_agents`
Lista todos os agent cards disponíveis.

```python
# Exemplo de uso
agents = await list_all_agents()
# Retorna lista com todos os agentes
```

## 🏗️ Arquitetura

```
a2a_mcp/
├── mcp/
│   ├── claude_server.py    # Servidor MCP com Claude SDK
│   ├── server.py           # Servidor original (Google)
│   └── __init__.py
├── agent_cards/            # Diretório de agent cards
│   ├── orchestrator.json
│   ├── planner.json
│   └── coder.json
├── start_claude_mcp.sh     # Script de inicialização
└── README_CLAUDE.md        # Esta documentação
```

## 🔧 Como Funciona

### Geração de Embeddings com Claude

Ao invés de usar embeddings numéricos tradicionais, o Claude analisa o texto e extrai características semânticas:

1. **Análise Contextual** - Claude entende o contexto e propósito
2. **Extração de Features** - Identifica características principais
3. **Vetorização Inteligente** - Converte em vetor baseado em compreensão
4. **Similaridade Semântica** - Compara baseado em significado real

### Exemplo de Embedding

```python
# Texto: "Agente para desenvolvimento de código Python"
# Claude analisa e gera:
embedding = [
    0.9,  # Complexidade técnica (alta)
    0.3,  # Orientação a dados (baixa)
    0.7,  # Interatividade (média-alta)
    0.8,  # Automação (alta)
    0.6,  # Processamento de linguagem (médio)
    0.2,  # Visualização (baixa)
    0.4,  # Tempo real (médio)
    0.5,  # Colaboração (médio)
    0.7,  # Segurança (média-alta)
    0.8   # Escalabilidade (alta)
]
```

## 🔌 Integração com A2A Protocol

O servidor mantém total compatibilidade com o protocolo A2A:

```javascript
// Node.js A2A Server pode se comunicar
const response = await fetch('http://localhost:8175/find_agent', {
  method: 'POST',
  body: JSON.stringify({ query: "coding agent" })
});
```

## 📝 Exemplos de Uso

### Python
```python
from a2a_mcp.mcp.claude_server import ClaudeEmbeddingService

# Inicializar serviço
service = ClaudeEmbeddingService()
await service.initialize()

# Gerar embedding
embedding = await service.generate_embedding("texto para análise")

# Buscar agente
agent = await find_agent("preciso de ajuda com código")
```

### CLI
```bash
# Testar ferramentas
echo '{"method":"tools/list"}' | ./start_claude_mcp.sh stdio

# Buscar agente
echo '{"method":"tools/call","params":{"name":"find_agent","arguments":{"query":"planner"}}}' | ./start_claude_mcp.sh stdio
```

## 🚨 Troubleshooting

### Claude não encontrado
```bash
# Verificar instalação
which claude

# Adicionar ao PATH se necessário
export PATH="$PATH:/Applications/Claude.app/Contents/MacOS"
```

### Erro de importação
```bash
# Instalar dependências
pip install claude-code-sdk
pip install ai-sdk-provider-claude-code
```

### Servidor não inicia
```bash
# Verificar logs
MCP_LOG_LEVEL=debug ./start_claude_mcp.sh stdio
```

## 🎯 Próximos Passos

1. **Cache Persistente** - Salvar embeddings em banco de dados
2. **Fine-tuning** - Ajustar análise para domínio específico
3. **Multi-modelo** - Suporte a Opus e Sonnet
4. **Streaming** - Respostas em tempo real
5. **WebSocket** - Comunicação bidirecional

## 📚 Recursos

- [Claude Code SDK](https://github.com/anthropics/claude-code-sdk-python)
- [MCP Protocol](https://modelcontextprotocol.io)
- [A2A Protocol](https://a2aprotocol.ai)

---

**Sem API Keys, Sem Limites, 100% Local! 🚀**
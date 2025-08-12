# Testes de API A2A

Este diretório contém testes automatizados para validar a implementação da API A2A (Agent-to-Agent Protocol).

## Estrutura dos Testes

### 📁 Arquivos de Teste

- `test_agent_card.py` - Testes do endpoint `/.well-known/agent.json`
- `test_message_send.py` - Testes do endpoint `/message/send` (JSON-RPC)
- `test_message_stream.py` - Testes do endpoint `/message/stream` (SSE)
- `test_error_handling.py` - Testes de cenários de erro

### 📁 Configuração

- `conftest.py` - Fixtures e configurações pytest
- `pytest.ini` - Configuração do pytest
- `requirements.txt` - Dependências dos testes
- `.env.example` - Exemplo de variáveis de ambiente

## Cobertura dos Testes

### ✅ AgentCard (`test_agent_card.py`)
- Descoberta de agente via `/.well-known/agent.json`
- Validação de campos obrigatórios (name, description, version, url)
- Verificação de capabilities (streaming, pushNotifications)
- Validação de skills do agente

### ✅ Message Send (`test_message_send.py`)
- Envio básico de mensagens via JSON-RPC 2.0
- Validação de estruturas de requisição/resposta
- Testes com contexto (contextId)
- Validação de erros para requisições malformadas

### ✅ Message Stream (`test_message_stream.py`)
- Streaming via Server-Sent Events (SSE)
- Validação de eventos JSON-RPC em stream
- Verificação de capabilities de streaming
- Testes de timeout e comportamento assíncrono

### ✅ Error Handling (`test_error_handling.py`)
- Códigos de erro padrão JSON-RPC (-32700 a -32603)
- Códigos de erro específicos A2A (-32001 a -32006)
- Validação de estrutura de erros
- Cenários de conteúdo não suportado

## Como Executar

### 1. Instalação das Dependências

```bash
pip install -r tests/api/requirements.txt
```

### 2. Configuração do Ambiente

Copie e configure o arquivo de ambiente:

```bash
cp tests/api/.env.example tests/api/.env
# Edite o arquivo .env com as configurações do seu servidor
```

### 3. Execução dos Testes

#### Todos os testes:
```bash
pytest tests/api/
```

#### Testes específicos:
```bash
# Apenas testes de AgentCard
pytest tests/api/test_agent_card.py -v

# Apenas testes de envio de mensagem
pytest tests/api/test_message_send.py -v

# Apenas testes de streaming
pytest tests/api/test_message_stream.py -v

# Apenas testes de erro
pytest tests/api/test_error_handling.py -v
```

#### Com relatório HTML:
```bash
pytest tests/api/ --html=reports/api_tests.html
```

#### Com cobertura:
```bash
pytest tests/api/ --cov=. --cov-report=html
```

## Configuração do Servidor

Antes de executar os testes, certifique-se de que:

1. **Servidor A2A está rodando** na URL especificada em `A2A_TEST_URL`
2. **AgentCard está acessível** em `/.well-known/agent.json`
3. **Endpoints necessários** estão implementados:
   - `/message/send` (JSON-RPC)
   - `/message/stream` (SSE) - se suportado pelo agente

## Interpretação dos Resultados

### ✅ Sucesso
- Todos os testes passaram
- API está implementada corretamente conforme especificação A2A

### ❌ Falhas Comuns

#### `Connection Error`
- Servidor não está rodando
- URL incorreta no `.env`

#### `Agent Card Not Found (404)`
- Endpoint `/.well-known/agent.json` não implementado
- Servidor não segue convenção A2A

#### `JSON-RPC Errors`
- Implementação de JSON-RPC 2.0 incorreta
- Estrutura de resposta não conforme

#### `Streaming Not Supported`
- Agente não declara `capabilities.streaming: true`
- Endpoint `/message/stream` não implementado

## Marcadores de Teste

Use marcadores para executar grupos específicos:

```bash
# Apenas testes de descoberta
pytest tests/api/ -m agent_card

# Apenas testes de erro
pytest tests/api/ -m error_handling

# Apenas testes que podem ser lentos
pytest tests/api/ -m "not slow"
```

## Logs e Debug

Para debug detalhado:

```bash
# Com logs detalhados
pytest tests/api/ -v -s --log-cli-level=DEBUG

# Parar no primeiro erro
pytest tests/api/ -x

# Executar teste específico
pytest tests/api/test_agent_card.py::TestAgentCard::test_agent_card_discovery -v
```

## Contribuindo

Ao adicionar novos testes:

1. Siga o padrão de nomenclatura `test_*.py`
2. Use fixtures do `conftest.py`
3. Adicione docstrings descritivas
4. Inclua prints informativos para debug
5. Use assertions claras com mensagens

## Referências

- [Especificação A2A](https://github.com/google/a2a)
- [JSON-RPC 2.0](https://www.jsonrpc.org/specification)
- [Server-Sent Events](https://developer.mozilla.org/docs/Web/API/Server-sent_events)
- [Pytest Documentation](https://docs.pytest.org/)
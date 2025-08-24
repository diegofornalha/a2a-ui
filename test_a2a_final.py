#!/usr/bin/env python3
"""
Script corrigido para testar os tipos a2a - versão final
"""

from a2a.types import Message, TextPart
import json

# Criar uma mensagem de teste
test_message = Message(
    parts=[TextPart(text="Hello, how can I help you?")],
    role='user',
    message_id='msg_001',
    context_id='ctx_001'
)

print("✅ Mensagem criada com sucesso!")

# FORMA CORRETA de acessar o texto
# Opção 1: Verificar o tipo primeiro
part = test_message.parts[0]
if hasattr(part, 'text'):
    print(f"📝 Conteúdo (método 1): {part.text}")

# Opção 2: Usar model_dump para converter em dicionário
message_dict = test_message.model_dump()
print(f"📝 Conteúdo (método 2): {message_dict['parts'][0]['text']}")

# Opção 3: Acessar diretamente se souber que é TextPart
if isinstance(test_message.parts[0], TextPart):
    print(f"📝 Conteúdo (método 3): {test_message.parts[0].text}")

print(f"👤 Role: {test_message.role}")
print(f"🆔 Message ID: {test_message.message_id}")
print(f"📍 Context ID: {test_message.context_id}")

print("\n📋 Informações sobre a estrutura:")
print(f"  - Tipo de parts[0]: {type(test_message.parts[0])}")
print(f"  - parts[0] tem 'text'?: {hasattr(test_message.parts[0], 'text')}")

# Mostrar JSON da mensagem
print("\n📄 Estrutura JSON da mensagem:")
print(json.dumps(message_dict, indent=2))

print("\n✨ Teste concluído com sucesso!")
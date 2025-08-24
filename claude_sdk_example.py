"""
Exemplo de uso do Claude Code SDK
Demonstrando TextBlock, UserMessage e AssistantMessage
"""

# Primeiro, vamos instalar o claude_code_sdk se não estiver instalado
# pip install claude-code-sdk

# Importações básicas do Claude Code SDK
try:
    from claude_code_sdk import TextBlock, UserMessage, AssistantMessage
    print("✅ Claude Code SDK importado com sucesso!")
except ImportError:
    print("❌ Claude Code SDK não está instalado.")
    print("Para instalar, execute: pip install claude-code-sdk")
    
    # Simulação das classes para demonstração
    class TextBlock:
        """Bloco de texto simples para mensagens"""
        def __init__(self, text: str, type: str = "text"):
            self.text = text
            self.type = type
        
        def __repr__(self):
            return f"TextBlock(text='{self.text[:50]}...', type='{self.type}')"
    
    class UserMessage:
        """Mensagem enviada pelo usuário"""
        def __init__(self, content: str | list, role: str = "user"):
            self.content = content if isinstance(content, list) else [TextBlock(content)]
            self.role = role
        
        def __repr__(self):
            return f"UserMessage(role='{self.role}', content={self.content})"
    
    class AssistantMessage:
        """Resposta do Claude"""
        def __init__(self, content: str | list, role: str = "assistant"):
            self.content = content if isinstance(content, list) else [TextBlock(content)]
            self.role = role
        
        def __repr__(self):
            return f"AssistantMessage(role='{self.role}', content={self.content})"


# Exemplos de uso
def exemplo_basico():
    """Exemplo básico de criação de mensagens"""
    print("\n=== Exemplo Básico ===")
    
    # Criando um bloco de texto simples
    texto = TextBlock("Olá, Claude! Como você está hoje?")
    print(f"TextBlock criado: {texto}")
    
    # Criando uma mensagem do usuário
    user_msg = UserMessage("Me ajude a entender Python melhor")
    print(f"UserMessage criada: {user_msg}")
    
    # Criando uma resposta do assistente
    assistant_msg = AssistantMessage(
        "Claro! Vou ajudá-lo a entender Python. Por onde gostaria de começar?"
    )
    print(f"AssistantMessage criada: {assistant_msg}")


def exemplo_conversa():
    """Exemplo de uma conversa completa"""
    print("\n=== Exemplo de Conversa ===")
    
    conversa = []
    
    # Primeira mensagem do usuário
    conversa.append(UserMessage("O que é uma lista em Python?"))
    
    # Resposta do assistente
    conversa.append(AssistantMessage(
        "Uma lista em Python é uma estrutura de dados ordenada e mutável "
        "que pode armazenar múltiplos valores. Exemplo: [1, 2, 3, 'texto']"
    ))
    
    # Segunda mensagem do usuário
    conversa.append(UserMessage("Como adiciono itens a uma lista?"))
    
    # Segunda resposta do assistente
    conversa.append(AssistantMessage(
        "Você pode adicionar itens usando:\n"
        "• lista.append(item) - adiciona ao final\n"
        "• lista.insert(posição, item) - adiciona em posição específica\n"
        "• lista.extend([itens]) - adiciona múltiplos itens"
    ))
    
    # Exibindo a conversa
    for i, msg in enumerate(conversa, 1):
        role = "👤 Usuário" if isinstance(msg, UserMessage) else "🤖 Claude"
        content = msg.content[0].text if isinstance(msg.content, list) else msg.content
        print(f"\n{i}. {role}:")
        print(f"   {content}")


def exemplo_multiplos_blocos():
    """Exemplo com múltiplos blocos de texto em uma mensagem"""
    print("\n=== Exemplo com Múltiplos Blocos ===")
    
    # Mensagem com múltiplos blocos
    blocos = [
        TextBlock("Aqui está um exemplo de código:", type="text"),
        TextBlock("```python\ndef saudar(nome):\n    return f'Olá, {nome}!'\n```", type="code"),
        TextBlock("Esta função recebe um nome e retorna uma saudação.", type="text")
    ]
    
    user_msg = UserMessage(blocos)
    print(f"Mensagem com {len(blocos)} blocos criada")
    
    for i, bloco in enumerate(blocos, 1):
        print(f"  Bloco {i} ({bloco.type}): {bloco.text[:50]}...")


def exemplo_estrutura_completa():
    """Exemplo de estrutura completa para interação com Claude"""
    print("\n=== Estrutura Completa de Interação ===")
    
    class ConversaClaudeSDK:
        def __init__(self):
            self.historico = []
        
        def adicionar_mensagem_usuario(self, texto: str):
            msg = UserMessage(texto)
            self.historico.append(msg)
            return msg
        
        def adicionar_resposta_claude(self, texto: str):
            msg = AssistantMessage(texto)
            self.historico.append(msg)
            return msg
        
        def obter_contexto(self):
            """Retorna o histórico formatado para envio à API"""
            return [
                {
                    "role": msg.role,
                    "content": msg.content[0].text if isinstance(msg.content, list) else msg.content
                }
                for msg in self.historico
            ]
    
    # Usando a estrutura
    conversa = ConversaClaudeSDK()
    
    # Simulando uma interação
    conversa.adicionar_mensagem_usuario("Explique o que é recursão")
    conversa.adicionar_resposta_claude(
        "Recursão é uma técnica onde uma função chama a si mesma. "
        "É útil para resolver problemas que podem ser divididos em subproblemas similares."
    )
    conversa.adicionar_mensagem_usuario("Mostre um exemplo")
    conversa.adicionar_resposta_claude(
        "def fatorial(n):\n"
        "    if n <= 1:\n"
        "        return 1\n"
        "    return n * fatorial(n-1)"
    )
    
    # Exibindo o contexto formatado
    contexto = conversa.obter_contexto()
    print("Contexto formatado para API:")
    for msg in contexto:
        print(f"  {msg['role']}: {msg['content'][:60]}...")


if __name__ == "__main__":
    print("=" * 60)
    print("DEMONSTRAÇÃO DO CLAUDE CODE SDK")
    print("TextBlock, UserMessage e AssistantMessage")
    print("=" * 60)
    
    exemplo_basico()
    exemplo_conversa()
    exemplo_multiplos_blocos()
    exemplo_estrutura_completa()
    
    print("\n" + "=" * 60)
    print("Para usar o SDK real, instale com:")
    print("pip install claude-code-sdk")
    print("=" * 60)
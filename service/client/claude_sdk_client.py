"""
Cliente para integração com Claude Code SDK
Substitui o uso do Gemini/Vertex AI
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, AsyncIterator
from dataclasses import dataclass
import anyio

# Importar Claude Code SDK
from claude_code_sdk import (
    TextBlock,
    UserMessage,
    AssistantMessage,
    ClaudeCodeOptions,
    query,
    ResultMessage
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ClaudeSDKResponse:
    """Resposta do Claude SDK"""
    success: bool
    content: str = ""
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ClaudeSDKClient:
    """
    Cliente para integração com Claude Code SDK
    Compatível com a interface do sistema A2A
    """
    
    def __init__(self):
        """Inicializa o cliente Claude SDK"""
        self.initialized = False
        self.default_options = ClaudeCodeOptions(
            system_prompt="You are a helpful AI assistant integrated with the A2A framework. Be concise and helpful.",
            max_turns=3
        )
        self._initialize()
    
    def _initialize(self):
        """Verifica e inicializa o SDK"""
        try:
            # Testar importação
            from claude_code_sdk import query
            self.initialized = True
            logger.info("✅ Claude Code SDK inicializado com sucesso")
        except ImportError as e:
            logger.error(f"❌ Erro ao importar Claude Code SDK: {e}")
            logger.info("💡 Instale com: pip install claude-code-sdk")
            self.initialized = False
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar: {e}")
            self.initialized = False
    
    async def query_simple(
        self, 
        prompt: str, 
        context: Optional[str] = None
    ) -> ClaudeSDKResponse:
        """
        Query simples ao Claude
        
        Args:
            prompt: Pergunta do usuário
            context: Contexto adicional
            
        Returns:
            ClaudeSDKResponse com a resposta
        """
        if not self.initialized:
            return ClaudeSDKResponse(
                success=False,
                error="Claude SDK não está inicializado"
            )
        
        try:
            # Adicionar contexto ao prompt se fornecido
            full_prompt = prompt
            if context:
                full_prompt = f"{context}\n\n{prompt}"
            
            # Coletar resposta completa
            response_text = ""
            metadata = {}
            
            async for message in query(prompt=full_prompt, options=self.default_options):
                if isinstance(message, AssistantMessage):
                    # Processar resposta do assistente
                    if isinstance(message.content, str):
                        response_text += message.content
                    elif isinstance(message.content, list):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                response_text += block.text + "\n"
                
                elif isinstance(message, ResultMessage):
                    # Capturar metadados
                    if hasattr(message, 'total_cost_usd'):
                        metadata['cost'] = message.total_cost_usd
                    if hasattr(message, 'total_tokens'):
                        metadata['tokens'] = message.total_tokens
            
            return ClaudeSDKResponse(
                success=True,
                content=response_text.strip(),
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"❌ Erro na query: {e}")
            return ClaudeSDKResponse(
                success=False,
                error=str(e)
            )
    
    async def generate_code(
        self,
        description: str,
        language: str = "python",
        framework: Optional[str] = None
    ) -> ClaudeSDKResponse:
        """
        Gera código usando Claude SDK
        
        Args:
            description: Descrição do código
            language: Linguagem de programação
            framework: Framework opcional
            
        Returns:
            ClaudeSDKResponse com o código
        """
        try:
            # Preparar prompt específico para geração de código
            prompt = f"Generate {language} code:\n{description}"
            if framework:
                prompt += f"\nUsing framework: {framework}"
            prompt += "\nProvide only the code without explanations."
            
            # Configurar opções para geração de código
            code_options = ClaudeCodeOptions(
                system_prompt=f"You are an expert {language} developer. Generate clean, efficient code.",
                max_turns=1
            )
            
            code_response = ""
            async for message in query(prompt=prompt, options=code_options):
                if isinstance(message, AssistantMessage):
                    if isinstance(message.content, str):
                        code_response = message.content
                    elif isinstance(message.content, list):
                        code_response = "\n".join([
                            block.text for block in message.content 
                            if isinstance(block, TextBlock)
                        ])
            
            return ClaudeSDKResponse(
                success=True,
                content=code_response
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar código: {e}")
            return ClaudeSDKResponse(
                success=False,
                error=str(e)
            )
    
    async def analyze_code(
        self,
        code: str,
        language: str = "python",
        task: str = "analyze"
    ) -> ClaudeSDKResponse:
        """
        Analisa código usando Claude SDK
        
        Args:
            code: Código a analisar
            language: Linguagem do código
            task: Tipo de análise
            
        Returns:
            ClaudeSDKResponse com a análise
        """
        try:
            task_prompts = {
                "analyze": "Analyze this code and identify potential issues:",
                "review": "Review this code and suggest improvements:",
                "optimize": "Optimize this code for better performance:",
                "explain": "Explain what this code does:"
            }
            
            prompt = f"{task_prompts.get(task, 'Analyze this code:')}\n\n```{language}\n{code}\n```"
            
            # Configurar para análise
            analysis_options = ClaudeCodeOptions(
                system_prompt=f"You are a {language} code expert. Provide detailed analysis.",
                max_turns=1
            )
            
            analysis = ""
            async for message in query(prompt=prompt, options=analysis_options):
                if isinstance(message, AssistantMessage):
                    if isinstance(message.content, str):
                        analysis = message.content
                    elif isinstance(message.content, list):
                        analysis = "\n".join([
                            block.text for block in message.content 
                            if isinstance(block, TextBlock)
                        ])
            
            return ClaudeSDKResponse(
                success=True,
                content=analysis
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar código: {e}")
            return ClaudeSDKResponse(
                success=False,
                error=str(e)
            )
    
    async def execute_with_a2a(
        self,
        task: str,
        agents: Optional[List[str]] = None
    ) -> ClaudeSDKResponse:
        """
        Executa tarefa com simulação A2A
        
        Args:
            task: Descrição da tarefa
            agents: Lista de agentes para simular
            
        Returns:
            ClaudeSDKResponse com o resultado
        """
        try:
            # Simular coordenação A2A
            if agents:
                prompt = f"Execute this task with multiple perspectives from these agents: {', '.join(agents)}\n\nTask: {task}"
            else:
                prompt = f"Execute this task: {task}"
            
            # Configurar para execução de tarefa
            task_options = ClaudeCodeOptions(
                system_prompt="You are a task coordinator. Break down and execute tasks systematically.",
                max_turns=2
            )
            
            result = ""
            async for message in query(prompt=prompt, options=task_options):
                if isinstance(message, AssistantMessage):
                    if isinstance(message.content, str):
                        result += message.content + "\n"
                    elif isinstance(message.content, list):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                result += block.text + "\n"
            
            return ClaudeSDKResponse(
                success=True,
                content=result.strip()
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar tarefa: {e}")
            return ClaudeSDKResponse(
                success=False,
                error=str(e)
            )
    
    async def stream_response(
        self,
        prompt: str
    ) -> AsyncIterator[str]:
        """
        Stream de resposta do Claude
        
        Args:
            prompt: Prompt para gerar resposta
            
        Yields:
            Chunks da resposta
        """
        if not self.initialized:
            yield "❌ Claude SDK não está inicializado"
            return
        
        try:
            async for message in query(prompt=prompt, options=self.default_options):
                if isinstance(message, AssistantMessage):
                    if isinstance(message.content, str):
                        yield message.content
                    elif isinstance(message.content, list):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                yield block.text
                                
        except Exception as e:
            logger.error(f"❌ Erro no streaming: {e}")
            yield f"Erro: {e}"
    
    async def query_with_tools(
        self,
        prompt: str,
        allowed_tools: List[str] = None
    ) -> ClaudeSDKResponse:
        """
        Query com ferramentas habilitadas
        
        Args:
            prompt: Pergunta do usuário
            allowed_tools: Lista de ferramentas permitidas
            
        Returns:
            ClaudeSDKResponse com a resposta
        """
        try:
            # Configurar com ferramentas
            tools_options = ClaudeCodeOptions(
                system_prompt="You are a helpful assistant with access to tools.",
                allowed_tools=allowed_tools or ["Read"],
                max_turns=2
            )
            
            response_text = ""
            tool_results = []
            
            async for message in query(prompt=prompt, options=tools_options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        block_type = type(block).__name__
                        
                        if isinstance(block, TextBlock):
                            response_text += block.text + "\n"
                        elif block_type == "ToolUseBlock":
                            # Capturar uso de ferramenta
                            tool_results.append({
                                "type": "tool_use",
                                "tool": getattr(block, 'tool_name', 'unknown')
                            })
                        elif block_type == "ToolResultBlock":
                            # Capturar resultado
                            tool_results.append({
                                "type": "tool_result",
                                "result": getattr(block, 'result', 'unknown')
                            })
            
            return ClaudeSDKResponse(
                success=True,
                content=response_text.strip(),
                metadata={"tools_used": tool_results} if tool_results else None
            )
            
        except Exception as e:
            logger.error(f"❌ Erro na query com ferramentas: {e}")
            return ClaudeSDKResponse(
                success=False,
                error=str(e)
            )


# Teste do cliente
if __name__ == "__main__":
    async def test_client():
        print("🧪 Testando Claude SDK Client")
        print("-" * 50)
        
        client = ClaudeSDKClient()
        
        if not client.initialized:
            print("❌ Cliente não inicializado. Instale o SDK:")
            print("   pip install claude-code-sdk")
            return
        
        # Teste simples
        print("\n📝 Teste de query simples:")
        response = await client.query_simple("What is Python?")
        if response.success:
            print(f"✅ Resposta: {response.content[:200]}...")
        else:
            print(f"❌ Erro: {response.error}")
        
        # Teste de geração de código
        print("\n🔧 Teste de geração de código:")
        response = await client.generate_code(
            "function to calculate fibonacci",
            language="python"
        )
        if response.success:
            print(f"✅ Código:\n{response.content}")
        else:
            print(f"❌ Erro: {response.error}")
        
        # Teste de streaming
        print("\n📡 Teste de streaming:")
        print("Resposta: ", end="")
        async for chunk in client.stream_response("Count to 3"):
            print(chunk, end="")
        print()
        
        print("\n✅ Testes concluídos!")
    
    # Executar testes
    anyio.run(test_client)
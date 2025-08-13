"""
Cliente para usar Claude Code CLI diretamente (sem API key)
Versão corrigida sem flags inexistentes
"""

import subprocess
import json
import asyncio
import logging
from typing import Optional, Dict, Any, AsyncGenerator
from dataclasses import dataclass
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ClaudeResponse:
    """Resposta do Claude CLI"""
    content: str
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ClaudeCLIClient:
    """
    Cliente que usa o Claude Code CLI diretamente
    Não precisa de API key pois usa a autenticação local do CLI
    """
    
    def __init__(self):
        """Inicializa o cliente CLI"""
        self.claude_command = "claude"
        self._verify_cli()
    
    def _verify_cli(self):
        """Verifica se o Claude CLI está instalado"""
        try:
            result = subprocess.run(
                [self.claude_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"✅ Claude CLI encontrado: {result.stdout.strip()}")
            else:
                raise RuntimeError(f"Claude CLI com erro: {result.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                "Claude CLI não encontrado. Instale com: npm install -g @anthropic-ai/claude-code"
            )
    
    async def query_simple(self, prompt: str, context: Optional[str] = None) -> ClaudeResponse:
        """
        Executa query usando o Claude CLI
        
        Args:
            prompt: Pergunta/comando para o Claude
            context: Contexto adicional
            
        Returns:
            ClaudeResponse com a resposta
        """
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"{context}\n\n{prompt}"
            
            logger.info(f"🤖 Executando via CLI: {prompt[:100]}...")
            
            # Comando básico do Claude
            cmd = [self.claude_command, "-p", full_prompt]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                response_text = stdout.decode('utf-8')
                return ClaudeResponse(
                    content=response_text,
                    success=True
                )
            else:
                error_msg = stderr.decode('utf-8') or "Erro desconhecido"
                logger.error(f"❌ Erro do CLI: {error_msg}")
                return ClaudeResponse(
                    content="",
                    success=False,
                    error=error_msg
                )
                
        except Exception as e:
            logger.error(f"❌ Erro ao executar CLI: {str(e)}")
            return ClaudeResponse(
                content="",
                success=False,
                error=str(e)
            )
    
    async def analyze_code(
        self, 
        code: str, 
        language: str = "python",
        task: str = "analyze"
    ) -> ClaudeResponse:
        """
        Analisa código usando Claude CLI
        """
        prompts = {
            "analyze": f"Analise este código {language}:\n```{language}\n{code}\n```",
            "review": f"Revise este código {language}:\n```{language}\n{code}\n```",
            "optimize": f"Otimize este código {language}:\n```{language}\n{code}\n```",
            "explain": f"Explique este código {language}:\n```{language}\n{code}\n```"
        }
        
        prompt = prompts.get(task, prompts["analyze"])
        return await self.query_simple(prompt)
    
    async def generate_code(
        self,
        description: str,
        language: str = "python",
        framework: Optional[str] = None
    ) -> ClaudeResponse:
        """
        Gera código usando Claude CLI
        """
        prompt = f"Gere código {language}"
        if framework:
            prompt += f" usando {framework}"
        prompt += f" para: {description}"
        
        return await self.query_simple(prompt)
    
    async def stream_response(
        self,
        prompt: str
    ) -> AsyncGenerator[str, None]:
        """
        Stream de resposta do Claude CLI
        
        Nota: Claude CLI pode não suportar streaming nativo,
        então simulamos com execução normal
        """
        try:
            response = await self.query_simple(prompt)
            if response.success:
                # Simular streaming dividindo a resposta em chunks
                words = response.content.split()
                chunk_size = 5
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i:i+chunk_size])
                    yield chunk + " "
                    await asyncio.sleep(0.1)  # Simular delay
            else:
                yield f"Erro: {response.error}"
                
        except Exception as e:
            logger.error(f"❌ Erro no streaming: {str(e)}")
            yield f"Erro: {str(e)}"
    
    async def execute_with_a2a(
        self,
        task: str,
        agents: Optional[list] = None
    ) -> ClaudeResponse:
        """
        Executa tarefa simulando coordenação A2A
        """
        agents = agents or ["developer", "reviewer", "tester"]
        agents_str = ", ".join(agents)
        
        prompt = f"""Execute esta tarefa: {task}

Analise sob as perspectivas de: {agents_str}

Forneça uma solução completa considerando todas as perspectivas."""
        
        return await self.query_simple(prompt)
    
    async def test_connection(self) -> bool:
        """
        Testa se o CLI está funcionando
        """
        try:
            response = await self.query_simple("Responda apenas: OK")
            return response.success and "OK" in response.content.upper()
        except Exception as e:
            logger.error(f"❌ Falha no teste: {str(e)}")
            return False


# Exemplo de uso
if __name__ == "__main__":
    async def main():
        print("🧪 Testando Claude CLI Client (versão corrigida)")
        print("-" * 50)
        
        client = ClaudeCLIClient()
        
        # Teste 1: Conexão
        print("\n1️⃣ Testando conexão...")
        connected = await client.test_connection()
        print(f"   Conectado: {'✅ Sim' if connected else '❌ Não'}")
        
        if not connected:
            print("\n⚠️ Claude CLI não está respondendo")
            print("Possíveis soluções:")
            print("1. Verifique se está logado: claude login")
            print("2. Teste manualmente: claude -p 'teste'")
            return
        
        # Teste 2: Query simples
        print("\n2️⃣ Query simples...")
        response = await client.query_simple("O que é Python?")
        if response.success:
            print(f"   ✅ Resposta: {response.content[:200]}...")
        else:
            print(f"   ❌ Erro: {response.error}")
        
        # Teste 3: Gerar código
        print("\n3️⃣ Gerando código...")
        response = await client.generate_code(
            "função hello world",
            language="python"
        )
        if response.success:
            print(f"   ✅ Código:")
            print(response.content[:300])
        
        # Teste 4: Streaming simulado
        print("\n4️⃣ Streaming simulado...")
        print("   ", end="")
        async for chunk in client.stream_response("Liste 3 cores"):
            print(chunk, end="", flush=True)
        print()
        
        print("\n✅ Testes concluídos!")
    
    asyncio.run(main())
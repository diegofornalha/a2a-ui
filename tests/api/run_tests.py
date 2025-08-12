#!/usr/bin/env python3
"""
Script para executar testes de API A2A com diferentes configurações.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Executa um comando e exibe o resultado."""
    print(f"\n🔄 {description}")
    print(f"Comando: {' '.join(cmd)}")
    print("-" * 50)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - SUCESSO")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ {description} - FALHA")
        if result.stderr:
            print(result.stderr)
        if result.stdout:
            print(result.stdout)
    
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="Executa testes de API A2A")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="URL do servidor A2A")
    parser.add_argument("--timeout", type=int, default=30,
                       help="Timeout para requisições")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Output verbose")
    parser.add_argument("--html-report", action="store_true",
                       help="Gerar relatório HTML")
    parser.add_argument("--coverage", action="store_true",
                       help="Incluir análise de cobertura")
    parser.add_argument("--test-file", 
                       help="Executar apenas um arquivo de teste específico")
    parser.add_argument("--marker", "-m",
                       help="Executar apenas testes com marcador específico")
    
    args = parser.parse_args()
    
    # Configura variáveis de ambiente
    os.environ["A2A_TEST_URL"] = args.url
    os.environ["A2A_TEST_TIMEOUT"] = str(args.timeout)
    
    # Diretório base dos testes
    test_dir = Path(__file__).parent
    
    print("🧪 Executando Testes de API A2A")
    print(f"URL do Servidor: {args.url}")
    print(f"Timeout: {args.timeout}s")
    print(f"Diretório: {test_dir}")
    
    # Verifica se o servidor está acessível
    print("\n🔍 Verificando conectividade com servidor...")
    try:
        import requests
        response = requests.get(f"{args.url}/.well-known/agent.json", timeout=5)
        if response.status_code == 200:
            agent_card = response.json()
            print(f"✅ Servidor acessível: {agent_card.get('name', 'Nome não encontrado')}")
        else:
            print(f"⚠️ Servidor responde mas AgentCard não encontrado (HTTP {response.status_code})")
    except Exception as e:
        print(f"❌ Erro ao conectar com servidor: {e}")
        print("⚠️ Continuando com os testes mesmo assim...")
    
    # Monta comando pytest
    cmd = ["python", "-m", "pytest"]
    
    # Adiciona diretório de testes
    if args.test_file:
        cmd.append(str(test_dir / args.test_file))
    else:
        cmd.append(str(test_dir))
    
    # Opções básicas
    if args.verbose:
        cmd.extend(["-v", "-s"])
    
    # Marcadores
    if args.marker:
        cmd.extend(["-m", args.marker])
    
    # Relatório HTML
    if args.html_report:
        report_dir = test_dir.parent.parent / "reports"
        report_dir.mkdir(exist_ok=True)
        cmd.extend(["--html", str(report_dir / "api_tests.html")])
    
    # Cobertura
    if args.coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    # Outras opções úteis
    cmd.extend([
        "--tb=short",
        "--color=yes",
        "--disable-warnings"
    ])
    
    # Executa os testes
    success = run_command(cmd, "Executando testes de API A2A")
    
    # Sumário final
    print("\n" + "="*60)
    if success:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ API A2A está funcionando corretamente")
    else:
        print("💥 ALGUNS TESTES FALHARAM!")
        print("❌ Verifique a implementação da API A2A")
    
    if args.html_report:
        report_path = test_dir.parent.parent / "reports" / "api_tests.html"
        print(f"📊 Relatório HTML disponível em: {report_path}")
    
    print("="*60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
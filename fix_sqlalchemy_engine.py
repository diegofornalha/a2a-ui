#!/usr/bin/env python3
"""
Exemplo de como criar um engine robusto para evitar erros de transação
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

def create_robust_engine(database_url: str) -> AsyncEngine:
    """Cria um AsyncEngine com configuração robusta."""
    
    # Configurações específicas por tipo de banco
    connect_args = {}
    
    if "postgresql" in database_url:
        connect_args = {
            "server_settings": {"jit": "off"},
            "command_timeout": 60,
            "options": "-c statement_timeout=60000"  # 60 segundos
        }
    elif "mysql" in database_url:
        connect_args = {
            "connect_timeout": 60,
        }
    
    return create_async_engine(
        database_url,
        echo=False,  # Mude para True para debug SQL
        pool_pre_ping=True,  # Verifica conexões antes de usar
        pool_recycle=3600,  # Recicla conexões após 1 hora
        pool_size=5,
        max_overflow=10,
        connect_args=connect_args
    )

# Exemplo de uso:
if __name__ == "__main__":
    # Para PostgreSQL
    engine = create_robust_engine("postgresql+asyncpg://user:pass@localhost/db")
    
    # Para MySQL
    # engine = create_robust_engine("mysql+aiomysql://user:pass@localhost/db")
    
    # Para SQLite (desenvolvimento)
    # engine = create_robust_engine("sqlite+aiosqlite:///./test.db")
    
    print("Engine criado com configuração robusta!")

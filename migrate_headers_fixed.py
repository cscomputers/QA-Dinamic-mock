#!/usr/bin/env python3
"""
Script de migração para adicionar suporte a headers customizados
Este script adiciona a coluna 'headers' à tabela qa_mocks se ela não existir
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection_string():
    """Constrói a string de conexão do SQL Server."""
    server = os.getenv("DB_SERVER", "localhost")
    port = os.getenv("DB_PORT", "1433")
    database = os.getenv("DB_NAME", "qa_mocks")
    username = os.getenv("DB_USER", "sa")
    password = os.getenv("DB_PASSWORD")
    driver = os.getenv("DB_DRIVER", "SQL Server")
    
    if not password:
        raise ValueError("DB_PASSWORD não foi configurada")
    
    return f"mssql+pyodbc://{username}:{password}@{server}:{port}/{database}?driver={driver}&TrustServerCertificate=yes"

def migrate_headers():
    """Executa a migração para adicionar a coluna headers."""
    load_dotenv()
    
    print("🔄 Iniciando migração de headers...")
    
    try:
        # Conecta ao banco
        connection_string = get_connection_string()
        engine = create_engine(connection_string, echo=False)
        
        # Verifica se a tabela qa_mocks existe
        inspector = inspect(engine)
        if not inspector.has_table('qa_mocks'):
            print("❌ Tabela qa_mocks não encontrada. Execute o setup do banco primeiro.")
            return False
        
        # Verifica se a coluna headers já existe
        columns = inspector.get_columns('qa_mocks')
        column_names = [col['name'] for col in columns]
        
        if 'headers' in column_names:
            print("✅ Coluna 'headers' já existe na tabela qa_mocks")
            return True
        
        # Adiciona a coluna headers usando transação
        with engine.begin() as conn:
            print("➕ Adicionando coluna 'headers' à tabela qa_mocks...")
            
            alter_sql = """
            ALTER TABLE qa_mocks 
            ADD headers NTEXT NULL DEFAULT '{}'
            """
            
            conn.execute(text(alter_sql))
            print("✅ Coluna 'headers' adicionada com sucesso!")
            
            # Atualiza registros existentes que podem ter headers NULL
            print("🔄 Atualizando registros existentes...")
            
            update_sql = """
            UPDATE qa_mocks 
            SET headers = '{}' 
            WHERE headers IS NULL
            """
            
            result = conn.execute(text(update_sql))
            print(f"✅ {result.rowcount} registros atualizados")
        
        # Verifica a migração fora da transação
        with engine.connect() as conn:
            print("🔍 Verificando migração...")
            verify_sql = "SELECT COUNT(*) as total FROM qa_mocks"
            result = conn.execute(text(verify_sql))
            total = result.fetchone()[0]
            
            print(f"✅ Migração concluída! Total de mocks: {total}")
            return True
            
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        return False

def main():
    """Função principal."""
    print("🗃️  MIGRAÇÃO DE HEADERS - QA MOCKS")
    print("=" * 40)
    
    try:
        success = migrate_headers()
        if success:
            print("\n🎉 Migração concluída com sucesso!")
            print("💡 Agora você pode usar headers customizados nos seus mocks")
            return 0
        else:
            print("\n❌ Falha na migração")
            return 1
            
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Script de migração completo para QA API (PostgreSQL)
- Cria a tabela qa_api se não existir
- Adiciona as colunas headers, created_at, updated_at se não existirem
- Cria índice e trigger para updated_at
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection_string():
    server = os.getenv("DB_SERVER", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "qa_api")
    username = os.getenv("DB_USER", "acloman")
    password = os.getenv("DB_PASSWORD")
    if not password:
        raise ValueError("DB_PASSWORD não foi configurada")
    return f"postgresql+psycopg2://{username}:{password}@{server}:{port}/{database}"

def migrate_all():
    load_dotenv()
    print("🔄 Iniciando migração completa QA API...")
    try:
        connection_string = get_connection_string()
        engine = create_engine(connection_string, echo=False)
        inspector = inspect(engine)
        with engine.begin() as conn:
            # Cria tabela se não existir
            if not inspector.has_table('qa_api'):
                print("➕ Criando tabela qa_api...")
                conn.execute(text('''
                CREATE TABLE qa_api (
                    id VARCHAR(10) PRIMARY KEY,
                    uri VARCHAR(500) NOT NULL,
                    http_method VARCHAR(10) NOT NULL,
                    status_code INT NOT NULL,
                    response_body TEXT NOT NULL,
                    uri_pattern VARCHAR(500) NOT NULL
                )'''))
                print("✅ Tabela criada!")
            # Adiciona colunas se não existirem
            columns = [col['name'] for col in inspector.get_columns('qa_api')]
            if 'headers' not in columns:
                print("➕ Adicionando coluna headers...")
                conn.execute(text("ALTER TABLE qa_api ADD COLUMN headers JSONB DEFAULT '{}'::jsonb"))
            if 'created_at' not in columns:
                print("➕ Adicionando coluna created_at...")
                conn.execute(text("ALTER TABLE qa_api ADD COLUMN created_at TIMESTAMPTZ DEFAULT NOW()"))
            if 'updated_at' not in columns:
                print("➕ Adicionando coluna updated_at...")
                conn.execute(text("ALTER TABLE qa_api ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW()"))
            # Atualiza valores nulos
            conn.execute(text("UPDATE qa_api SET headers = '{}'::jsonb WHERE headers IS NULL"))
            conn.execute(text("UPDATE qa_api SET created_at = NOW() WHERE created_at IS NULL"))
            conn.execute(text("UPDATE qa_api SET updated_at = NOW() WHERE updated_at IS NULL"))
            # Cria índice
            idx = [i['name'] for i in inspector.get_indexes('qa_api')]
            if 'ix_qa_api_method_uri' not in idx:
                print("➕ Criando índice ix_qa_api_method_uri...")
                conn.execute(text("CREATE INDEX ix_qa_api_method_uri ON qa_api(http_method, uri)"))
            # Cria trigger para updated_at
            triggers = conn.execute(text("SELECT tgname FROM pg_trigger WHERE NOT tgisinternal AND tgrelid = 'qa_api'::regclass")).fetchall()
            if not any('trg_qa_api_updated_at' in t[0] for t in triggers):
                print("➕ Criando trigger trg_qa_api_updated_at...")
                conn.execute(text('''
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                   NEW.updated_at = NOW();
                   RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                CREATE TRIGGER trg_qa_api_updated_at
                BEFORE UPDATE ON qa_api
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
                '''))
        print("✅ Migração completa!")
        return True
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        return False

def main():
    print("🗃️  MIGRAÇÃO COMPLETA - QA API (PostgreSQL)")
    print("=" * 40)
    try:
        success = migrate_all()
        if success:
            print("\n🎉 Migração concluída com sucesso!")
            return 0
        else:
            print("\n❌ Falha na migração")
            return 1
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

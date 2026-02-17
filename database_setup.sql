-- Script de criação do banco de dados para QA API (PostgreSQL)
-- Execute este script no psql ou ferramenta gráfica

-- Criar o banco de dados qa_api se não existir
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'qa_api') THEN
      CREATE DATABASE qa_api;
   END IF;
END$$;

-- Conectar ao banco de dados qa_api antes de executar o restante
-- \c qa_api

-- Criar a tabela de mocks
CREATE TABLE IF NOT EXISTS qa_api (
    id VARCHAR(10) PRIMARY KEY,
    uri VARCHAR(500) NOT NULL,
    http_method VARCHAR(10) NOT NULL,
    status_code INT NOT NULL,
    response_body TEXT NOT NULL,
    uri_pattern VARCHAR(500) NOT NULL,
    headers JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Criar índice para melhor performance nas consultas
CREATE INDEX IF NOT EXISTS IX_qa_api_method_uri ON qa_api(http_method, uri);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_qa_api_updated_at ON qa_api;
CREATE TRIGGER trg_qa_api_updated_at
BEFORE UPDATE ON qa_api
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Mensagem de sucesso
DO $$ BEGIN RAISE NOTICE 'Banco de dados qa_api configurado com sucesso!'; END $$;
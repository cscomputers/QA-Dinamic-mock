-- Script de criação do banco de dados para QA Mocks
-- Execute este script no SQL Server Management Studio ou Azure Data Studio

-- Criar o banco de dados qa_mocks se não existir
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'qa_mocks')
CREATE DATABASE qa_mocks;
GO

-- Usar o banco de dados qa_mocks
USE qa_mocks;
GO

-- Criar a tabela de mocks
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='qa_mocks' AND xtype='U')
CREATE TABLE qa_mocks (
    id NVARCHAR(10) PRIMARY KEY,
    uri NVARCHAR(500) NOT NULL,
    http_method NVARCHAR(10) NOT NULL,
    status_code INT NOT NULL,
    response_body NTEXT NOT NULL,
    uri_pattern NVARCHAR(500) NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE()
);
GO

-- Criar índice para melhor performance nas consultas
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_qa_mocks_method_uri' AND object_id = OBJECT_ID('qa_mocks'))
CREATE INDEX IX_qa_mocks_method_uri ON qa_mocks(http_method, uri);
GO

-- Adicionar trigger para atualizar updated_at automaticamente
IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_qa_mocks_updated_at')
DROP TRIGGER TR_qa_mocks_updated_at;
GO

CREATE TRIGGER TR_qa_mocks_updated_at
ON qa_mocks
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE qa_mocks 
    SET updated_at = GETUTCDATE()
    FROM qa_mocks m
    INNER JOIN inserted i ON m.id = i.id;
END;
GO

PRINT 'Banco de dados qa_mocks configurado com sucesso!';
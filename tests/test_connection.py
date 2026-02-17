from src.database_manager import DatabaseManager
import os
from dotenv import load_dotenv
import pyodbc

load_dotenv()
print('=== Teste de Conectividade SQL Server ===')
print(f'Servidor: {os.getenv("DB_SERVER")}:{os.getenv("DB_PORT")}')
print(f'Banco: {os.getenv("DB_NAME")}')
print(f'Usuário: {os.getenv("DB_USER")}')
print()

# Teste 1: Conectar no banco master
try:
    server = os.getenv("DB_SERVER")
    port = os.getenv("DB_PORT") 
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    driver = os.getenv("DB_DRIVER")
    
    # Conecta no master primeiro
    conn_str = f"DRIVER={{{driver}}};SERVER={server},{port};DATABASE=master;UID={username};PWD={password};TrustServerCertificate=yes"
    print("Testando conexão no banco 'master'...")
    
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # Verifica se o banco qa_api existe
    cursor.execute("SELECT name FROM sys.databases WHERE name = 'qa_api'")
    result = cursor.fetchone()
    
    if result:
        print("✅ Banco 'qa_api' já existe!")
    else:
        print("ℹ️ Banco 'qa_api' não existe. Criando...")
        cursor.execute("CREATE DATABASE qa_api")
        conn.commit()
        print("✅ Banco 'qa_api' criado com sucesso!")
    
    cursor.close()
    conn.close()
    
    # Teste 2: Conectar no banco qa_api
    print("\nTestando conexão no banco 'qa_api'...")
    db = DatabaseManager()
    if db.is_connected():
        print('✅ Conexão com banco qa_api estabelecida com sucesso!')
        print('✅ Sistema irá usar persistência no SQL Server')
        
        # Testa criação de tabela
        try:
            with db.engine.connect() as conn:
                db.metadata.create_all(db.engine)
                print('✅ Tabela qa_api criada/verificada com sucesso!')
        except Exception as e:
            print(f'⚠️ Erro ao criar tabela: {e}')
        
    else:
        print('❌ Não foi possível conectar ao banco qa_api')
        print('ℹ️ Sistema irá usar fallback para memória')
        
except Exception as e:
    print(f'❌ Erro: {e}')
    print('ℹ️ Sistema irá usar fallback para memória')
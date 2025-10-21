# QA Mocks API - Sistema Híbrido de Mocks

Sistema avançado de mocks para QA com persistência híbrida (Banco de Dados + Memória) e fallback automático.

## 🚀 Funcionalidades

- ✅ **Persistência Híbrida**: Salva no SQL Server com fallback para memória
- ✅ **Fallback Automático**: Se o banco estiver indisponível, usa memória
- ✅ **Alta Performance**: Consultas em memória para acesso rápido
- ✅ **Configuração Flexível**: Via variáveis de ambiente
- ✅ **Mocks Dinâmicos**: Suporte a parâmetros e substituição de variáveis
- ✅ **Status Monitoring**: Endpoint para verificar status do sistema
- ✅ **Múltiplos Formatos**: Criação individual ou em lote

## 📋 Pré-requisitos

- Python 3.8+
- SQL Server (opcional, com fallback para memória)
- ODBC Driver 17 for SQL Server (se usando banco)

## 🛠️ Instalação

1. **Navegue até a pasta do projeto:**
   ```bash
   cd qa-mocks-hybrid
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o banco de dados (opcional):**
   - Configure as variáveis no arquivo (ajuste a senha do banco, o resto deve estar ok.) `.env`
   - Abra a pasta src e Execute o script `database_setup.sql` no SQL Server

4. **Configure as variáveis de ambiente:**
   Edite o arquivo `.env`:
   ```env
   # Configuração do Banco de Dados
   USE_DATABASE=true
   DB_SERVER=127.0.0.1
   DB_PORT=1460
   DB_NAME=qa_mocks
   DB_USER=SA
   DB_PASSWORD=Sua_senha
   DB_DRIVER=ODBC Driver 17 for SQL Server

   # Configuração do Sistema
   FALLBACK_TO_MEMORY=true
   ```

## 🎯 Como Usar

### 🔧 Configuração do Ambiente de Desenvolvimento

#### Opção 1: VS Code Workspace (Recomendado)
```bash
# Abra o arquivo workspace no VS Code
code qa-mocks-hybrid.code-workspace
```
Isso configurará automaticamente o diretório correto e extensões recomendadas.

#### Opção 2: Console de Desenvolvimento PowerShell
```powershell
# Execute o script para abrir console configurado
.\open-dev-console.ps1
```

### 🚀 Iniciando o Servidor


#### Opção 1: Script de Inicialização Completo
```bash
# Batch (Windows)
start.bat

# PowerShell (Recomendado)
.\start.ps1
```

#### Opção 2: Comando Manual
**Atenção:** Sempre execute o comando a partir da raiz do projeto (pasta `qa-mocks-hybrid`). Não execute de dentro da pasta `src/`, pois isso causará erro de importação!

```bash
python -m uvicorn src.qa_api:app --host 0.0.0.0 --port 40028 --reload
```

### Verificar status do sistema:
```http
GET /status
```

### Criar mocks:
```http
POST /mocks
Content-Type: application/json

{
    "uri": "/users/:id",
    "http_method": "GET",
    "status_code_response": 200,
    "response": {
        "id": "id",
        "name": "João Silva",
        "email": "joao@test.com"
    }
}
```

### Criar múltiplos mocks:
```http
POST /mocks
Content-Type: application/json

[
    {
        "uri": "/users/:id",
        "http_method": "GET",
        "status_code_response": 200,
        "response": {"id": "id", "name": "User"}
    },
    {
        "uri": "/orders/:orderId",
        "http_method": "GET", 
        "status_code_response": 200,
        "response": {"orderId": "orderId", "status": "pending"}
    }
]
```

### Testar o mock criado:
```http
GET /users/123
# Retorna: {"id": "123", "name": "João Silva", "email": "joao@test.com"}
```

## 📚 API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/status` | Status do sistema (novo) |
| `POST` | `/mocks/configurar/endpoint` | Criar mock(s) |
> **Atenção:** Se você criar um mock com o mesmo `uri` e método HTTP de um já existente, o sistema irá atualizar o mock existente (status code e response) automaticamente.
| `GET` | `/mocks` | Listar todos os mocks |
| `GET` | `/mocks/{id}` | Consultar mock específico |
| `PUT` | `/mocks/{id}` | Atualizar mock |
| `DELETE` | `/mocks/{id}` | Remover mock |
| `DELETE` | `/mocks` | Remover todos os mocks |
| `*` | `/{qualquer_path}` | Executar mock |

## 🔧 Configurações Avançadas

### Modos de Operação

1. **Somente Banco de Dados**:
   ```env
   USE_DATABASE=true
   FALLBACK_TO_MEMORY=false
   ```

2. **Híbrido com Fallback** (Recomendado):
   ```env
   USE_DATABASE=true
   FALLBACK_TO_MEMORY=true
   ```

3. **Somente Memória**:
   ```env
   USE_DATABASE=false
   FALLBACK_TO_MEMORY=true
   ```

### Exemplo de Response com Variáveis Dinâmicas

```json
{
    "uri": "/api/orders/:orderId/items/:itemId",
    "http_method": "GET",
    "status_code_response": 200,
    "response": {
        "orderId": "orderId",
        "itemId": "itemId",
        "quantity": "quantity",
        "message": "Item itemId do pedido orderId processado"
    }
}
```

**Chamada**: `GET /api/orders/123/items/456?quantity=2`

**Response**:
```json
{
    "orderId": "123",
    "itemId": "456", 
    "quantity": "2",
    "message": "Item 456 do pedido 123 processado"
}
```

## 🧪 Testes

Execute o script de teste automatizado:
```bash
python test_mocks.py
```

## 🏗️ Estrutura do Projeto

```
qa-mocks-hybrid/
├── src/                       # Código principal do projeto (pacote Python)
│   ├── __init__.py
│   ├── database_manager.py     # Gerenciador do banco SQL Server
│   ├── mocks_manager.py        # Gerenciador híbrido de mocks
│   └── qa_api.py               # API principal FastAPI
├── tests/                     # Testes automatizados
│   ├── __init__.py
│   ├── test_connection.py      # Teste de conectividade BD
│   └── test_mocks.py           # Testes unitários do sistema de mocks
├── database_setup.sql         # Script de criação do banco
├── requirements.txt           # Dependências Python
├── .env                       # Configurações do sistema
├── start.bat                  # Script inicialização (Batch)
├── start.ps1                  # Script inicialização (PowerShell)
├── open-dev-console.ps1       # Console de desenvolvimento
├── qa-mocks-hybrid.code-workspace # Workspace VS Code
└── README.md                  # Esta documentação
```

### Importação dos módulos

Para importar os módulos corretamente após a reorganização:

```python
from src.database_manager import DatabaseManager
from src.mocks_manager import MocksManager
```

### Executando testes

```bash
python -m pytest tests/
```

Ou para rodar um teste específico:

```bash
python tests/test_mocks.py
```

## 📊 Monitoramento

O endpoint `/status` retorna informações sobre o sistema:

```json
{
    "database_connected": true,
    "total_mocks": 5,
    "use_database": true,
    "fallback_to_memory": true
}
```

## 🔄 Vantagens do Sistema Híbrido

- **Persistência**: Mocks salvos no banco sobrevivem a reinicializações
- **Performance**: Consultas rápidas através da cache em memória
- **Confiabilidade**: Fallback automático se o banco falhar
- **Flexibilidade**: Configurável para diferentes cenários de uso
- **Escalabilidade**: Suporte a múltiplas instâncias compartilhando o mesmo banco

## 🐛 Solução de Problemas

1. **Erro de conexão com banco**: Verifique as configurações no `.env` e se o SQL Server está rodando
2. **ODBC Driver não encontrado**: Instale o driver apropriado para seu sistema
3. **Fallback para memória**: Normal se `FALLBACK_TO_MEMORY=true` e banco indisponível

## 🚀 Deploy em Produção

Para produção, recomenda-se:
- Usar banco de dados dedicado
- Configurar connection pooling
- Implementar logs estruturados  
- Monitoramento de health checks
- Backup automático dos mocks
# QA API (Dinamic Mock)

Sistema de mocks dinâmicos para QA, com persistência em PostgreSQL, pronto para rodar localmente ou em servidor (Raspberry Pi/CasaOS).

---

## Pré-requisitos
- Python 3.11+ (recomendado)
- PostgreSQL 13+
- (Opcional) Docker e Docker Compose
- Git

---

## Instalação e Execução Local (Windows/Linux)

1. **Clone o repositório:**
   ```sh
   git clone https://git.entersoft.com.br/acloman/qa_api.git
   cd qa_api
   ```

2. **Crie e configure o arquivo `.env`:**
   Copie o exemplo e ajuste as variáveis conforme seu ambiente:
   ```sh
   cp .env.example .env
   # Edite .env conforme necessário
   ```

3. **Instale as dependências:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure o banco de dados:**
   - Crie o banco e tabelas executando o script `database_setup.sql` no PostgreSQL:
     ```sh
     psql -U <usuario> -h <host> -d postgres -f database_setup.sql
     ```

5. **Rode a API localmente:**
   ```sh
   python -m uvicorn src.qa_api:app --host 0.0.0.0 --port 8090 --reload
   ```
   Ou:
   ```sh
   python src/qa_api.py
   ```

6. **Acesse a API:**
   - Swagger: [http://localhost:8090/docs](http://localhost:8090/docs)
   - Status: [http://localhost:8090/status](http://localhost:8090/status)

---

## Execução no Servidor (Raspberry Pi/CasaOS)

1. **Copie o projeto para o servidor:**
   ```sh
   scp -r ./qa_api pi@<ip-servidor>:/mnt/nas/apps/apis/qa_api
   # Ou use git clone diretamente no servidor
   ```

2. **Acesse a pasta do projeto:**
   ```sh
   cd /mnt/nas/apps/apis/qa_api
   ```

3. **Configure o ambiente:**
   - Ajuste o `.env` para apontar para o PostgreSQL do servidor.
   - Instale dependências:
     ```sh
     pip install -r requirements.txt
     ```
   - Execute o script SQL no PostgreSQL do servidor.

4. **(Opcional) Configure start automático com systemd:**
   Crie `/etc/systemd/system/qa_api.service`:
   ```ini
   [Unit]
   Description=QA API (FastAPI/Uvicorn)
   After=network.target

   [Service]
   User=pi
   WorkingDirectory=/mnt/nas/apps/apis/qa_api
   Environment="PATH=/mnt/nas/apps/apis/qa_api/.venv/bin"
   ExecStart=/mnt/nas/apps/apis/qa_api/.venv/bin/python -m uvicorn src.qa_api:app --host 0.0.0.0 --port 8090
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   Ative e inicie:
   ```sh
   sudo systemctl daemon-reload
   sudo systemctl enable qa_api
   sudo systemctl start qa_api
   sudo systemctl status qa_api
   ```

5. **Configure o proxy reverso no nginx/nginx proxy manager:**
   - Aponte o domínio desejado para `http://localhost:8090`.

---

## Testes
- Testes automáticos: `python -m unittest tests/`
- Teste de headers: `python test_headers_simple.py`

---

## Observações
- O nome do banco, tabela e pasta deve ser sempre `qa_api` (com underline).
- Para rodar sem sudo, adicione o usuário ao grupo docker e ajuste permissões da pasta.
- Para dúvidas, consulte o arquivo `HEADERS_IMPLEMENTATION_COMPLETE.md`.

---

## Contato
- Responsável: acloman
- Repositório: https://git.entersoft.com.br/acloman/qa_api.git

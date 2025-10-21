@echo off
echo ================================================
echo    QA Mocks Hybrid - Sistema de Mocks Avançado
echo ================================================
echo.

cd /d "%~dp0"

echo [1/3] Verificando dependências...
pip install -r requirements.txt --quiet

echo [2/3] Testando conexão com banco de dados...
python tests\test_connection.py

echo.
echo [3/3] Iniciando servidor...
echo.
echo 🚀 Servidor iniciando em: http://localhost:40028
echo 📖 Documentação: http://localhost:40028/docs
echo 📊 Status: http://localhost:40028/status
echo.
echo Para parar o servidor, pressione Ctrl+C
echo.

python -m uvicorn src.qa_api:app --host 0.0.0.0 --port 40028 --reload
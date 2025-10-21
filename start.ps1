Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   QA Mocks Hybrid - Sistema de Mocks Avançado" -ForegroundColor Cyan  
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

Write-Host "[1/3] Verificando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

Write-Host "[2/3] Testando conexão com banco de dados..." -ForegroundColor Yellow
python tests/test_connection.py

Write-Host ""
Write-Host "[3/3] Iniciando servidor..." -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 Servidor iniciando em: http://localhost:40028" -ForegroundColor Green
Write-Host "📖 Documentação: http://localhost:40028/docs" -ForegroundColor Green
Write-Host "📊 Status: http://localhost:40028/status" -ForegroundColor Green
Write-Host ""
Write-Host "Para parar o servidor, pressione Ctrl+C" -ForegroundColor Red
Write-Host ""

python -m uvicorn src.qa_api:app --host 0.0.0.0 --port 40028 --reload
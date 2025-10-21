# QA Mocks Hybrid - Atalho de Desenvolvimento
# Execute este arquivo para abrir o terminal no diretório correto

# Define o diretório do projeto
$projectPath = "C:\Desenv\projects\fastApi\qa-mocks-hybrid"

# Navega para o diretório
Set-Location $projectPath

# Limpa a tela
Clear-Host

# Exibe informações do projeto
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   QA Mocks Hybrid - Sistema de Mocks Avançado" -ForegroundColor Cyan  
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 Diretório atual: " -NoNewline -ForegroundColor Yellow
Write-Host $projectPath -ForegroundColor White
Write-Host ""
Write-Host "🚀 Comandos disponíveis:" -ForegroundColor Green
Write-Host "  • .\start.ps1              - Iniciar servidor completo" -ForegroundColor White
Write-Host "  • python tests/test_connection.py - Testar conexão BD" -ForegroundColor White  
Write-Host "  • python tests/test_mocks.py      - Executar testes" -ForegroundColor White
Write-Host "  • python -m uvicorn src.qa_api:app --port 40028 --reload - Iniciar servidor" -ForegroundColor White
Write-Host ""
Write-Host "📖 Documentação:" -ForegroundColor Green
Write-Host "  • README.md - Documentação completa" -ForegroundColor White
Write-Host "  • http://localhost:40028/docs - Swagger UI (quando servidor rodando)" -ForegroundColor White
Write-Host ""

# Define o título da janela do PowerShell
$Host.UI.RawUI.WindowTitle = "QA Mocks Hybrid - Development Console"
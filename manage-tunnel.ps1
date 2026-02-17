# Script para gerenciar túnel público da API QA Mocks
# Autor: Sistema QA Mocks
# Data: 22/10/2025

param(
    [string]$Action = "help",
    [string]$Port = "40028",
    [string]$Method = "localtunnel"
)

function Show-Header {
    Write-Host "🌐 QA MOCKS - GERENCIADOR DE TÚNEL PÚBLICO" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host ""
}

function Show-Help {
    Show-Header
    Write-Host "📋 USO:" -ForegroundColor Yellow
    Write-Host "  .\manage-tunnel.ps1 [ação] [opções]" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 AÇÕES DISPONÍVEIS:" -ForegroundColor Yellow
    Write-Host "  start     - Inicia o túnel público" -ForegroundColor Green
    Write-Host "  stop      - Para o túnel" -ForegroundColor Red
    Write-Host "  status    - Verifica status da API" -ForegroundColor Blue
    Write-Host "  test      - Testa todos os endpoints" -ForegroundColor Magenta
    Write-Host "  help      - Mostra esta ajuda" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⚙️  OPÇÕES:" -ForegroundColor Yellow
    Write-Host "  -Port     - Porta da API (padrão: 40028)" -ForegroundColor White    Write-Host "  -Method   - Método do túnel (cloudflare|localtunnel)" -ForegroundColor White
    Write-Host ""
    Write-Host "📝 EXEMPLOS:" -ForegroundColor Yellow
    Write-Host "  .\manage-tunnel.ps1 start -Method cloudflare" -ForegroundColor Green
    Write-Host "  .\manage-tunnel.ps1 start -Method localtunnel" -ForegroundColor Green
    Write-Host "  .\manage-tunnel.ps1 test" -ForegroundColor Green
    Write-Host "  .\manage-tunnel.ps1 status" -ForegroundColor Green
}

function Test-LocalAPI {
    Write-Host "🔍 Testando API local na porta $Port..." -ForegroundColor Blue
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$Port/status" -Method GET
        Write-Host "✅ API local está respondendo" -ForegroundColor Green
        Write-Host "   Banco conectado: $($response.database_connected)" -ForegroundColor White
        Write-Host "   Modo: $($response.storage_mode)" -ForegroundColor White
        Write-Host "   Total mocks: $($response.total_mocks)" -ForegroundColor White
        return $true
    }
    catch {
        Write-Host "❌ API local não está respondendo na porta $Port" -ForegroundColor Red
        Write-Host "   Execute primeiro: python start_api.py" -ForegroundColor Yellow
        return $false
    }
}

function Start-Tunnel {
    Show-Header
    
    if (-not (Test-LocalAPI)) {
        return
    }
    
    Write-Host "🌐 Iniciando túnel público ($Method)..." -ForegroundColor Blue
    Write-Host ""
    
    if ($Method -eq "localtunnel") {
        Write-Host "📡 Verificando LocalTunnel..." -ForegroundColor Blue
        try {
            # Verifica se localtunnel está instalado
            npm list -g localtunnel *>$null
            if ($LASTEXITCODE -ne 0) {
                Write-Host "📦 Instalando LocalTunnel..." -ForegroundColor Yellow
                npm install -g localtunnel
            }
            
            Write-Host "🚀 Iniciando túnel LocalTunnel na porta $Port..." -ForegroundColor Green
            Write-Host "   Aguarde alguns segundos para obter a URL..." -ForegroundColor Yellow
            Write-Host ""
            
            # Inicia o túnel
            Start-Process powershell -ArgumentList "-NoExit", "-Command", "npx localtunnel --port $Port"
            
            Start-Sleep -Seconds 3
            Write-Host "✅ Túnel iniciado!" -ForegroundColor Green
            Write-Host "🔗 Sua URL pública será mostrada na nova janela" -ForegroundColor Cyan
            
        }
        catch {
            Write-Host "❌ Erro ao iniciar LocalTunnel: $($_.Exception.Message)" -ForegroundColor Red
        }    elseif ($Method -eq "cloudflare") {
        Write-Host "📡 Verificando Cloudflare Tunnel..." -ForegroundColor Blue
        try {
            $cloudflaredVersion = cloudflared version 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "🚀 Iniciando túnel Cloudflare na porta $Port..." -ForegroundColor Green
                Write-Host "   Aguarde alguns segundos para obter a URL..." -ForegroundColor Yellow
                Write-Host ""
                
                # Inicia o túnel
                Start-Process powershell -ArgumentList "-NoExit", "-Command", "cloudflared tunnel --url http://localhost:$Port"
                
                Start-Sleep -Seconds 3
                Write-Host "✅ Túnel Cloudflare iniciado!" -ForegroundColor Green
                Write-Host "🔗 Sua URL pública será mostrada na nova janela" -ForegroundColor Cyan
                Write-Host "📋 A URL será algo como: https://[hash].trycloudflare.com" -ForegroundColor White
            }
            else {
                Write-Host "❌ cloudflared não está instalado" -ForegroundColor Red
                Write-Host "   Instale com: winget install cloudflare.cloudflared" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "❌ Erro ao iniciar cloudflared: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

function Stop-Tunnel {
    Show-Header
    Write-Host "🛑 Parando túneis..." -ForegroundColor Red
    
    # Para processos do LocalTunnel
    Get-Process | Where-Object {$_.ProcessName -like "*node*" -or $_.CommandLine -like "*localtunnel*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    
    # Para processos do ngrok
    Get-Process | Where-Object {$_.ProcessName -like "*ngrok*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Host "✅ Túneis interrompidos" -ForegroundColor Green
}

function Test-AllEndpoints {
    param([string]$BaseUrl = "http://localhost:$Port")
    
    Show-Header
    Write-Host "🧪 TESTANDO TODOS OS ENDPOINTS" -ForegroundColor Magenta
    Write-Host "🔗 URL Base: $BaseUrl" -ForegroundColor Blue
    Write-Host ""
    
    $tests = @(
        @{
            Name = "Status da API"
            Method = "GET"
            Endpoint = "/status"
            Expected = "200"
        },
        @{
            Name = "Listar Mocks"
            Method = "GET" 
            Endpoint = "/mocks"
            Expected = "200"
        },
        @{
            Name = "Documentação da API"
            Method = "GET"
            Endpoint = "/docs"
            Expected = "200"
        },
        @{
            Name = "OpenAPI Schema"
            Method = "GET"
            Endpoint = "/openapi.json"
            Expected = "200"
        }
    )
    
    $passed = 0
    $total = $tests.Count
    
    foreach ($test in $tests) {
        Write-Host "📋 Testando: $($test.Name)" -ForegroundColor Blue
        Write-Host "   $($test.Method) $($test.Endpoint)" -ForegroundColor Gray
        
        try {
            $url = "$BaseUrl$($test.Endpoint)"
            $response = Invoke-WebRequest -Uri $url -Method $test.Method -UseBasicParsing
            
            if ($response.StatusCode -eq $test.Expected) {
                Write-Host "   ✅ PASSOU ($($response.StatusCode))" -ForegroundColor Green
                $passed++
            }
            else {
                Write-Host "   ❌ FALHOU ($($response.StatusCode))" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "   ❌ ERRO: $($_.Exception.Message)" -ForegroundColor Red
        }
        Write-Host ""
    }
    
    Write-Host "📊 RESULTADO FINAL:" -ForegroundColor Yellow
    Write-Host "   ✅ Passou: $passed/$total" -ForegroundColor Green
    Write-Host "   📈 Taxa de sucesso: $([math]::Round(($passed/$total)*100, 2))%" -ForegroundColor Cyan
}

function Show-Status {
    Show-Header
    Write-Host "📊 STATUS DO SISTEMA QA MOCKS" -ForegroundColor Blue
    Write-Host ""
    
    # Testa API local
    Write-Host "🔍 API Local (porta $Port):" -ForegroundColor Yellow
    if (Test-LocalAPI) {
        $apiStatus = "🟢 ONLINE"
    } else {
        $apiStatus = "🔴 OFFLINE"
    }
    Write-Host "   Status: $apiStatus" -ForegroundColor White
    
    Write-Host ""
    
    # Verifica processos de túnel
    Write-Host "🌐 Túneis Ativos:" -ForegroundColor Yellow
    $tunnelProcesses = @()
    
    # LocalTunnel
    $ltProcesses = Get-Process | Where-Object {$_.CommandLine -like "*localtunnel*" -or $_.ProcessName -like "*node*"} -ErrorAction SilentlyContinue
    if ($ltProcesses) {
        $tunnelProcesses += "LocalTunnel"
    }
    
    # ngrok
    $ngrokProcesses = Get-Process | Where-Object {$_.ProcessName -like "*ngrok*"} -ErrorAction SilentlyContinue
    if ($ngrokProcesses) {
        $tunnelProcesses += "ngrok"
    }
    
    if ($tunnelProcesses.Count -gt 0) {
        Write-Host "   🟢 Ativos: $($tunnelProcesses -join ', ')" -ForegroundColor Green
    } else {
        Write-Host "   🔴 Nenhum túnel ativo" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "💡 COMANDOS ÚTEIS:" -ForegroundColor Cyan
    Write-Host "   .\manage-tunnel.ps1 start    # Iniciar túnel" -ForegroundColor White
    Write-Host "   .\manage-tunnel.ps1 test     # Testar endpoints" -ForegroundColor White
    Write-Host "   .\manage-tunnel.ps1 stop     # Parar túneis" -ForegroundColor White
}

# Execução principal
switch ($Action.ToLower()) {
    "start" { Start-Tunnel }
    "stop" { Stop-Tunnel }
    "status" { Show-Status }
    "test" { Test-AllEndpoints }
    "help" { Show-Help }
    default { Show-Help }
}

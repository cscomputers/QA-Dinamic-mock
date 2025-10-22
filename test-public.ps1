# Script para testar a API QA Mocks via URL pública
# Testará todos os endpoints usando a URL atual do LocalTunnel

param(
    [string]$PublicUrl = "https://eager-hairs-turn.loca.lt"
)

function Show-Header {
    Write-Host "🧪 TESTE COMPLETO DA API QA MOCKS PÚBLICA" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "🔗 URL: $PublicUrl" -ForegroundColor Blue
    Write-Host ""
}

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Endpoint,
        [hashtable]$Body = $null,
        [string]$ContentType = "application/json"
    )
    
    Write-Host "📋 $Name" -ForegroundColor Yellow
    Write-Host "   $Method $Endpoint" -ForegroundColor Gray
    
    try {
        $url = "$PublicUrl$Endpoint"
        $headers = @{
            "User-Agent" = "QA-Mocks-Tester/1.0"
        }
        
        if ($Body) {
            $bodyJson = $Body | ConvertTo-Json -Depth 10
            Write-Host "   📤 Body: $bodyJson" -ForegroundColor DarkGray
            $response = Invoke-RestMethod -Uri $url -Method $Method -Body $bodyJson -ContentType $ContentType -Headers $headers
        } else {
            $response = Invoke-RestMethod -Uri $url -Method $Method -Headers $headers
        }
        
        Write-Host "   ✅ SUCESSO ($Method $Endpoint)" -ForegroundColor Green
        
        # Mostra resposta formatada
        if ($response) {
            $responseJson = $response | ConvertTo-Json -Depth 5
            Write-Host "   📥 Resposta: $responseJson" -ForegroundColor DarkGreen
        }
        
        return $response
    }
    catch {
        Write-Host "   ❌ ERRO: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            Write-Host "   📄 Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        }
        return $null
    }
    Write-Host ""
}

Show-Header

Write-Host "🔍 1. TESTANDO STATUS DA API" -ForegroundColor Magenta
Write-Host "-" * 40
$status = Test-Endpoint -Name "Status do Sistema" -Method "GET" -Endpoint "/status"

Write-Host "📋 2. TESTANDO LISTAGEM DE MOCKS" -ForegroundColor Magenta  
Write-Host "-" * 40
$mocks = Test-Endpoint -Name "Listar Todos os Mocks" -Method "GET" -Endpoint "/mocks"

Write-Host "🆕 3. TESTANDO CRIAÇÃO DE MOCK" -ForegroundColor Magenta
Write-Host "-" * 40
$newMock = @{
    uri = "/api/test/public-endpoint"
    http_method = "GET"
    status_code_response = 200
    response = @{
        message = "Teste via túnel público"
        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        tunnel_url = $PublicUrl
    }
}
$createdMock = Test-Endpoint -Name "Criar Mock de Teste" -Method "POST" -Endpoint "/mocks/configurar/endpoint" -Body $newMock

Write-Host "🔍 4. TESTANDO CONSULTA POR ID" -ForegroundColor Magenta
Write-Host "-" * 40
if ($createdMock -and $createdMock.mock_id) {
    $mockDetail = Test-Endpoint -Name "Consultar Mock por ID" -Method "GET" -Endpoint "/mocks/$($createdMock.mock_id)"
}

Write-Host "🎯 5. TESTANDO ENDPOINT MOCKADO" -ForegroundColor Magenta
Write-Host "-" * 40
$mockResponse = Test-Endpoint -Name "Chamar Endpoint Mockado" -Method "GET" -Endpoint "/api/test/public-endpoint"

Write-Host "📚 6. TESTANDO DOCUMENTAÇÃO" -ForegroundColor Magenta
Write-Host "-" * 40
try {
    $docsUrl = "$PublicUrl/docs"
    $docsResponse = Invoke-WebRequest -Uri $docsUrl -UseBasicParsing
    if ($docsResponse.StatusCode -eq 200) {
        Write-Host "   ✅ Documentação acessível em: $docsUrl" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Erro ao acessar documentação: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "📊 RESUMO FINAL" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🔗 URL Pública: $PublicUrl" -ForegroundColor Blue
Write-Host "📖 Documentação: $PublicUrl/docs" -ForegroundColor Blue
Write-Host "🌐 LocalTunnel Dashboard: https://loca.lt" -ForegroundColor Blue
Write-Host ""

if ($status) {
    Write-Host "📊 Status da API:" -ForegroundColor Yellow
    Write-Host "   • Banco conectado: $($status.database_connected)" -ForegroundColor White
    Write-Host "   • Modo de armazenamento: $($status.storage_mode)" -ForegroundColor White
    Write-Host "   • Total de mocks: $($status.total_mocks)" -ForegroundColor White
}

Write-Host ""
Write-Host "💡 COMANDOS ÚTEIS:" -ForegroundColor Cyan
Write-Host "   .\test-public.ps1 -PublicUrl 'https://sua-nova-url.loca.lt'" -ForegroundColor White
Write-Host "   .\manage-tunnel.ps1 status" -ForegroundColor White
Write-Host "   .\manage-tunnel.ps1 test" -ForegroundColor White

Write-Host ""
Write-Host "🎉 Teste completo finalizado!" -ForegroundColor Green

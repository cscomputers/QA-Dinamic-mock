#!/usr/bin/env python3
"""
Teste simples de headers customizados no QA Mocks
"""

import requests
import json
import sys

def test_headers_functionality():
    """Testa a funcionalidade de headers customizados."""
    base_url = "http://localhost:40028"
    
    print("🧪 TESTE DE HEADERS CUSTOMIZADOS")
    print("=" * 50)
    
    # Teste 1: Criar mock com headers
    print("1. Criando mock com headers customizados...")
    mock_data = {
        "uri": "/api/test-headers",
        "http_method": "GET",
        "status_code_response": 200,
        "response": {
            "message": "Teste de headers",
            "success": True
        },
        "headers": {
            "X-Custom-Header": "Test-Value",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/mocks/configurar/endpoint", json=mock_data)
        if response.status_code == 200:
            result = response.json()
            mock_id = result["criadas"][0]["id"]
            print(f"✅ Mock criado com ID: {mock_id}")
        else:
            print(f"❌ Erro ao criar mock: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False
    
    # Teste 2: Verificar mock criado
    print("\n2. Verificando mock criado...")
    try:
        response = requests.get(f"{base_url}/mocks/{mock_id}")
        if response.status_code == 200:
            mock_details = response.json()
            if "headers" in mock_details:
                print("✅ Mock contém headers:")
                for header, value in mock_details["headers"].items():
                    print(f"   {header}: {value}")
            else:
                print("❌ Mock não contém headers")
                return False
        else:
            print(f"❌ Erro ao consultar mock: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    # Teste 3: Chamar endpoint mockado e verificar headers
    print("\n3. Testando resposta do endpoint mockado...")
    try:
        response = requests.get(f"{base_url}/api/test-headers")
        if response.status_code == 200:
            print("✅ Endpoint respondeu com sucesso!")
            print("📋 Headers recebidos:")
            for header, value in response.headers.items():
                if header.lower().startswith('x-custom') or header.lower() == 'cache-control':
                    print(f"   ✅ {header}: {value}")
            
            # Verifica se headers customizados estão presentes
            if 'X-Custom-Header' in response.headers:
                print("✅ Header customizado X-Custom-Header presente!")
            else:
                print("❌ Header customizado X-Custom-Header ausente")
                return False
                
        else:
            print(f"❌ Endpoint retornou status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    # Teste 4: Limpeza
    print("\n4. Limpando mock de teste...")
    try:
        response = requests.delete(f"{base_url}/mocks/{mock_id}")
        if response.status_code == 200:
            print("✅ Mock removido com sucesso!")
        else:
            print(f"⚠️ Aviso: Erro ao remover mock: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Aviso: Erro ao remover mock: {e}")
    
    return True

def main():
    """Função principal."""
    print("🚀 Iniciando teste de headers...")
    
    # Verifica se API está rodando
    try:
        response = requests.get("http://localhost:40028/status", timeout=5)
        print(f"✅ API está respondendo (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ API não está respondendo: {e}")
        print("💡 Execute: python start.py")
        return 1
    
    # Executa o teste
    if test_headers_functionality():
        print("\n🎉 TESTE DE HEADERS CONCLUÍDO COM SUCESSO!")
        print("✅ Funcionalidade de headers customizados está funcionando!")
        return 0
    else:
        print("\n❌ TESTE DE HEADERS FALHOU!")
        print("⚠️ Verifique os logs acima para mais detalhes")
        return 1

if __name__ == "__main__":
    sys.exit(main())

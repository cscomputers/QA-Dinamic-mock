#!/usr/bin/env python3
"""
Teste simples e direto de headers
"""

import requests
import json

def test_headers_simple():
    base_url = "http://localhost:40028"
    
    print("🧪 TESTE SIMPLES DE HEADERS")
    print("=" * 40)
    
    # Criar mock com headers
    print("1. Criando mock com headers...")
    mock_data = {
        "uri": "/test/headers/simple",
        "http_method": "GET", 
        "status_code_response": 200,
        "response": {"message": "Headers test"},
        "headers": {
            "X-Test-Header": "Success",
            "Cache-Control": "no-cache"
        }
    }
    
    try:
        r = requests.post(f"{base_url}/mocks/configurar/endpoint", json=mock_data)
        mock_id = r.json()["criadas"][0]["id"]
        print(f"✅ Mock criado: {mock_id}")
        
        # Testar endpoint
        print("2. Testando endpoint...")
        response = requests.get(f"{base_url}/test/headers/simple")
        print(f"✅ Status: {response.status_code}")
        
        # Verificar headers
        print("3. Verificando headers...")
        if "X-Test-Header" in response.headers:
            print(f"✅ X-Test-Header: {response.headers['X-Test-Header']}")
        else:
            print("❌ X-Test-Header não encontrado")
            
        if "Cache-Control" in response.headers:
            print(f"✅ Cache-Control: {response.headers['Cache-Control']}")
        else:
            print("❌ Cache-Control não encontrado")
            
        print("\n🎉 Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_headers_simple()

#!/usr/bin/env python3
"""
Script de teste para o sistema de mocks híbrido
Execute este script para testar as funcionalidades do sistema
"""

import requests
import json
import time

BASE_URL = "http://localhost:40028"

def test_status():
    """Testa o endpoint de status"""
    print("=== Testando Status do Sistema ===")
    response = requests.get(f"{BASE_URL}/status")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_create_mocks():
    """Testa criação de mocks"""
    print("=== Testando Criação de Mocks ===")
    
    # Mock simples
    mock1 = {
        "uri": "/users/:id",
        "http_method": "GET",
        "status_code_response": 200,
        "response": {
            "id": "id",
            "name": "Usuario Teste",
            "email": "user@test.com"
        }
    }
    
    # Mock com resposta dinâmica
    mock2 = {
        "uri": "/orders/:orderId/status",
        "http_method": "GET", 
        "status_code_response": 200,
        "response": {
            "orderId": "orderId",
            "status": "completed",
            "message": "Pedido processado com sucesso"
        }
    }
    
    # Criando múltiplos mocks
    mocks = [mock1, mock2]
    
    response = requests.post(f"{BASE_URL}/mocks", json=mocks)
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    return [mock['id'] for mock in result.get('criadas', [])]

def test_list_mocks():
    """Testa listagem de mocks"""
    print("=== Testando Listagem de Mocks ===")
    response = requests.get(f"{BASE_URL}/mocks")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_get_mock(mock_id):
    """Testa consulta de mock específico"""
    print(f"=== Testando Consulta do Mock {mock_id} ===")
    response = requests.get(f"{BASE_URL}/mocks/{mock_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_mock_calls():
    """Testa as chamadas aos mocks criados"""
    print("=== Testando Chamadas aos Mocks ===")
    
    # Teste do mock /users/:id
    print("Testando GET /users/123")
    response = requests.get(f"{BASE_URL}/users/123")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Teste do mock /orders/:orderId/status
    print("Testando GET /orders/456/status")
    response = requests.get(f"{BASE_URL}/orders/456/status")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_update_mock(mock_id):
    """Testa atualização de mock"""
    print(f"=== Testando Atualização do Mock {mock_id} ===")
    
    update_data = {
        "status_code_response": 201,
        "response": {
            "id": "id",
            "name": "Usuario Atualizado",
            "email": "updated@test.com",
            "updated": True
        }
    }
    
    response = requests.put(f"{BASE_URL}/mocks/{mock_id}", json=update_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_delete_mock(mock_id):
    """Testa remoção de mock"""
    print(f"=== Testando Remoção do Mock {mock_id} ===")
    response = requests.delete(f"{BASE_URL}/mocks/{mock_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes do sistema de mocks híbrido\n")
    
    try:
        # Testa status inicial
        test_status()
        
        # Cria mocks
        mock_ids = test_create_mocks()
        print()
        
        if not mock_ids:
            print("❌ Erro: Nenhum mock foi criado. Verifique se o servidor está rodando.")
            return
        
        # Lista mocks
        test_list_mocks()
        
        # Consulta mock específico
        if len(mock_ids) > 0:
            test_get_mock(mock_ids[0])
        
        # Testa chamadas aos mocks
        test_mock_calls()
        
        # Atualiza um mock
        if len(mock_ids) > 0:
            test_update_mock(mock_ids[0])
            
            # Testa a chamada após atualização
            print("Testando GET /users/123 após atualização")
            response = requests.get(f"{BASE_URL}/users/123")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print()
        
        # Remove um mock
        if len(mock_ids) > 1:
            test_delete_mock(mock_ids[1])
        
        # Status final
        test_status()
        
        print("✅ Todos os testes concluídos com sucesso!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor.")
        print("Certifique-se de que o servidor está rodando em http://localhost:40028")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
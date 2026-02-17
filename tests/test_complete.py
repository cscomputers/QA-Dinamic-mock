#!/usr/bin/env python3
"""
Relatório de testes completo do sistema QA Mocks
"""

def generate_final_report():
    print("🧪 RELATÓRIO FINAL DE TESTES - QA MOCKS")
    print("=" * 55)
    print()
    
    results = []
    
    # Teste 1: Imports
    try:
        from src.database_manager import DatabaseManager
        from src.mocks_manager import MocksManager
        from src.qa_api import app
        import uvicorn
        results.append("✅ Imports: PASSOU")
    except Exception as e:
        results.append(f"❌ Imports: FALHOU - {e}")
    
    # Teste 2: Conexão MSSQL
    try:
        db = DatabaseManager()
        if db.is_connected():
            results.append("✅ MSSQL: CONECTADO (porta 1460)")
        else:
            results.append("⚠️  MSSQL: FALLBACK PARA MEMÓRIA")
    except Exception as e:
        results.append(f"❌ MSSQL: FALHOU - {e}")
    
    # Teste 3: Sistema de Mocks
    try:
        mocks = MocksManager()
        total_before = len(mocks.get_all_mocks())
        
        # Criar mock de teste
        test_id = mocks.create_mock(
            uri='/api/final-test',
            http_method='POST',
            status_code=201,
            response={'test': 'final', 'success': True}
        )
        
        if test_id:
            # Recuperar mock
            mock_data = mocks.get_mock(test_id)
            if mock_data and mock_data['uri'] == '/api/final-test':
                # Testar pattern matching
                found = mocks.find_matching_mock('/api/final-test', 'POST')
                if found:
                    total_after = len(mocks.get_all_mocks())
                    results.append(f"✅ Mocks: FUNCIONANDO ({total_after} mocks)")
                else:
                    results.append("❌ Mocks: Pattern matching falhou")
            else:
                results.append("❌ Mocks: Recuperação falhou")
        else:
            results.append("❌ Mocks: Criação falhou")
    except Exception as e:
        results.append(f"❌ Mocks: FALHOU - {e}")
      # Teste 4: API FastAPI
    try:
        routes = len([r for r in app.routes if hasattr(r, 'path')])
        results.append(f"✅ API: PRONTA ({routes} rotas)")
    except Exception as e:
        results.append(f"❌ API: FALHOU - {e}")
    
    # Teste 5: Verificar modo de armazenamento
    try:
        status = mocks.get_status()
        storage_mode = status.get('storage_mode', 'Unknown')
        results.append(f"ℹ️  Modo: {storage_mode}")
    except Exception as e:
        results.append(f"❌ Status: FALHOU - {e}")
    
    # Imprimir resultados
    for result in results:
        print(f"  {result}")
    
    print()
    print("🎯 RESUMO EXECUTIVO:")
    
    passed = len([r for r in results if r.startswith("✅")])
    warnings = len([r for r in results if r.startswith("⚠️")])
    failed = len([r for r in results if r.startswith("❌")])
    
    print(f"  ✅ Testes aprovados: {passed}")
    print(f"  ⚠️  Avisos: {warnings}")
    print(f"  ❌ Falhas: {failed}")
    
    print()
    if failed == 0:
        print("🎉 SISTEMA 100% FUNCIONAL!")
        print("🚀 Pronto para inicializar: python start_api.py")
        print("📖 Documentação: http://localhost:40028/docs")
    else:        print("⚠️  Sistema com problemas. Verifique os erros acima.")
    
    print()
    print("📊 INFORMAÇÕES DO SISTEMA:")
    print("  🐳 Container: qa-mocks-mssql (porta 1460)")
    print("  🗄️  Database: qa_api")
    print("  🌐 API: QA Mocks API v2.0.0 (porta 40028)")
    print("  📦 Persistência: MSSQL com fallback automático para memória")
    
    return failed == 0

if __name__ == "__main__":
    try:
        success = generate_final_report()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ ERRO CRÍTICO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

#!/usr/bin/env python3
"""
Script para iniciar a API QA Mocks
"""

import uvicorn
import sys
import os

# Adicionar o diretório atual ao path para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Iniciando QA Mocks API...")
    print("📍 Porta: 40028")
    print("📖 Documentação: http://localhost:40028/docs")
    print("⏹️  Para parar: Ctrl+C")
    print()
    
    try:
        uvicorn.run(
            "src.qa_api:app",
            host="0.0.0.0",
            port=40028,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 API finalizada pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar API: {e}")
        sys.exit(1)

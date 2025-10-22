from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Union, List, Dict, Any
import re
import logging
from src.mocks_manager import MocksManager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="QA Mocks API",
    description="Sistema de mocks com persistência híbrida (Banco de Dados + Memória)",
    version="2.0.0",
    swagger_ui_parameters={"deepLinking": False}
)

# Inicializa o gerenciador de mocks
mocks_manager = MocksManager()

@app.post("/mocks/configurar/endpoint")
async def criar_mocks(config: Union[Dict[str, Any], List[Dict[str, Any]]]):
    """Cria um ou vários mocks, atribuindo ID automático."""
    if isinstance(config, dict):
        configs = [config]
    elif isinstance(config, list):
        configs = config
    else:
        raise HTTPException(status_code=400, detail="Envie um objeto ou uma lista de objetos")

    criados = []
    erros = []

    for idx, item in enumerate(configs):
        uri = item.get("uri")
        method = item.get("http_method", "GET").upper()
        status_code = item.get("status_code_response", 200)
        response_body = item.get("response")

        if not uri or response_body is None:
            erros.append({"index": idx, "erro": "Campos obrigatórios faltando"})
            continue

        try:
            mock_id = mocks_manager.create_mock(uri, method, status_code, response_body)
            criados.append({"id": mock_id, "uri": uri, "http_method": method})
        except ValueError as ve:
            logger.error(f"Duplicidade ao criar mock {idx}: {ve}")
            erros.append({"index": idx, "erro": str(ve)})
        except Exception as e:
            logger.error(f"Erro ao criar mock {idx}: {e}")
            erros.append({"index": idx, "erro": str(e)})

    # Se houve erro de duplicidade, retorna 409
    if any('Já existe um mock' in err.get('erro', '') for err in erros):
        raise HTTPException(status_code=409, detail={"criadas": criados, "erros": erros})
    return {"message": "Mocks criados", "criadas": criados, "erros": erros}

@app.get("/mocks")
async def listar_mocks():
    """Lista todos os mocks (sem response)."""
    mocks_list = mocks_manager.get_all_mocks()
    return {"mocks": mocks_list}

@app.get("/mocks/{mock_id}")
async def consultar_mock(mock_id: str):
    """Consulta detalhes de um mock pelo ID."""
    mock_data = mocks_manager.get_mock(mock_id)
    if not mock_data:
        raise HTTPException(status_code=404, detail=f"Mock {mock_id} não encontrado")
    
    return {
        "id": mock_id,
        "uri": mock_data["uri"],
        "http_method": mock_data["http_method"],
        "status_code": mock_data["status_code"],
        "response": mock_data["response"]
    }

@app.put("/mocks/{mock_id}")
async def editar_mock(mock_id: str, config: Dict[str, Any]):
    """Edita um mock existente pelo ID, incluindo alteração de URI e método."""
    if not mocks_manager.mock_exists(mock_id):
        raise HTTPException(status_code=404, detail=f"Mock {mock_id} não encontrado")

    status_code = config.get("status_code_response")
    response_body = config.get("response")
    uri = config.get("uri")
    http_method = config.get("http_method")

    success = mocks_manager.update_mock(mock_id, status_code, response_body, uri, http_method)

    if not success:
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar mock")

    return {"message": f"Mock {mock_id} atualizado com sucesso"}

@app.delete("/mocks/{mock_id}")
async def remover_mock(mock_id: str):
    """Remove um mock pelo ID."""
    if not mocks_manager.mock_exists(mock_id):
        raise HTTPException(status_code=404, detail=f"Mock {mock_id} não encontrado")
    
    success = mocks_manager.delete_mock(mock_id)
    if not success:
        raise HTTPException(status_code=500, detail="Erro interno ao remover mock")
    
    return {"message": f"Mock {mock_id} removido com sucesso"}

@app.delete("/mocks")
async def limpar_mocks():
    """Remove todos os mocks."""
    success = mocks_manager.delete_all_mocks()
    if not success:
        raise HTTPException(status_code=500, detail="Erro interno ao limpar mocks")
    
    return {"message": "Todos os mocks foram removidos"}

@app.get("/status")
async def get_status():
    """Retorna o status do sistema de mocks."""
    return mocks_manager.get_status()

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(full_path: str, request: Request):
    """Captura todas as chamadas e retorna a resposta configurada."""
    path = "/" + full_path
    method = request.method.upper()

    # Procura por um mock correspondente
    mock_match = mocks_manager.find_matching_mock(path, method)
    
    if mock_match:
        # Path variables do padrão da URI
        variables = mock_match["variables"]
        
        # Query params
        variables.update(dict(request.query_params))
        
        # Body variables
        try:
            body = await request.json()
            if isinstance(body, dict):
                variables.update(body)
        except:
            pass

        # Substitui placeholders no response
        def replace_vars(obj):
            if isinstance(obj, str) and obj in variables:
                return variables[obj]
            if isinstance(obj, dict):
                return {k: replace_vars(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [replace_vars(v) for v in obj]
            return obj

        final_response = replace_vars(mock_match["response"])

        return JSONResponse(
            status_code=int(mock_match["status_code"]),
            content=final_response
        )

    return JSONResponse(
        status_code=404,
        content={"erro": f"Nenhuma resposta configurada para {method} {path}"}
    )
    
    # Para rodar: python -m uvicorn src.qa_api:app --host 0.0.0.0 --port 40028 --reload
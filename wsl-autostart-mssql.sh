#!/bin/bash

# Script de inicialização automática para MSSQL Container
# Este script deve ser executado automaticamente no login do WSL

CONTAINER_NAME="qa-mocks-mssql"
PROJECT_PATH="/mnt/d/Desenv/QA-Dinamic-mock"
LOG_FILE="$HOME/.qa-mocks-autostart.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

check_docker_service() {
    if ! pgrep -x "dockerd" > /dev/null; then
        log_message "Iniciando serviço Docker..."
        sudo service docker start
        sleep 3
    fi
}

check_container_status() {
    if docker ps -q --filter "name=$CONTAINER_NAME" | grep -q .; then
        log_message "Container $CONTAINER_NAME já está rodando"
        return 0
    elif docker ps -aq --filter "name=$CONTAINER_NAME" | grep -q .; then
        log_message "Container $CONTAINER_NAME existe mas está parado. Iniciando..."
        docker start "$CONTAINER_NAME"
        return $?
    else
        log_message "Container $CONTAINER_NAME não existe. Criando..."
        return 1
    fi
}

start_container() {
    cd "$PROJECT_PATH" || {
        log_message "ERRO: Não foi possível acessar $PROJECT_PATH"
        return 1
    }
    
    if docker-compose up -d; then
        log_message "Container iniciado com sucesso"
        return 0
    else
        log_message "ERRO: Falha ao iniciar container"
        return 1
    fi
}

main() {
    log_message "=== Iniciando verificação automática do MSSQL Container ==="
    
    # Verificar se o Docker está instalado
    if ! command -v docker &> /dev/null; then
        log_message "Docker não está instalado. Execute o setup primeiro."
        exit 1
    fi
    
    # Iniciar serviço Docker se necessário
    check_docker_service
    
    # Verificar status do container
    if ! check_container_status; then
        # Container não existe, criar usando docker-compose
        start_container
    fi
    
    # Verificar se está funcionando
    sleep 5
    if docker ps -q --filter "name=$CONTAINER_NAME" | grep -q .; then
        # Testar conexão SQL
        if docker exec "$CONTAINER_NAME" /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'QAMocks2024!' -Q 'SELECT 1' -C >/dev/null 2>&1; then
            log_message "✓ MSSQL Container está rodando e respondendo na porta 1460"
        else
            log_message "⚠ MSSQL Container está rodando mas ainda não está respondendo"
        fi
    else
        log_message "✗ Falha ao iniciar MSSQL Container"
    fi
    
    log_message "=== Verificação concluída ==="
}

# Executar apenas se chamado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

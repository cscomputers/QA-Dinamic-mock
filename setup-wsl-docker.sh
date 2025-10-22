#!/bin/bash

# Script de configuração completa para MSSQL no WSL
# Execute este script uma vez para configurar tudo

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTOSTART_SCRIPT="$SCRIPT_DIR/wsl-autostart-mssql.sh"

echo "🐳 Configurando MSSQL Container no WSL..."

# Verificar se está no WSL
if ! grep -qi "microsoft\|wsl" /proc/version 2>/dev/null; then
    echo "❌ Este script deve ser executado no WSL"
    exit 1
fi

# Função para adicionar usuário ao grupo docker sem sudo
add_user_to_docker_group() {
    if ! groups $USER | grep -q docker; then
        echo "📋 Adicionando usuário ao grupo docker..."
        sudo usermod -aG docker $USER
        echo "✅ Usuário adicionado ao grupo docker"
        echo "⚠️  Você precisa fazer logout/login ou executar: newgrp docker"
    else
        echo "✅ Usuário já está no grupo docker"
    fi
}

# Verificar e instalar Docker
install_docker() {
    if command -v docker &> /dev/null; then
        echo "✅ Docker já está instalado"
        docker --version
    else
        echo "📦 Instalando Docker..."
        
        # Atualizar pacotes
        sudo apt-get update
        
        # Instalar dependências
        sudo apt-get install -y \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        
        # Adicionar chave GPG oficial do Docker
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        
        # Adicionar repositório do Docker
        echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
            $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Instalar Docker
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        
        echo "✅ Docker instalado com sucesso"
    fi
}

# Verificar e instalar docker-compose
install_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        echo "✅ docker-compose já está instalado"
        docker-compose --version
    else
        echo "📦 Instalando docker-compose..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        echo "✅ docker-compose instalado com sucesso"
    fi
}

# Configurar inicialização automática
setup_autostart() {
    echo "⚙️  Configurando inicialização automática..."
    
    # Tornar o script executável
    chmod +x "$AUTOSTART_SCRIPT"
    
    # Adicionar ao .bashrc se não estiver lá
    BASHRC_LINE="# Auto-start MSSQL Container for QA Mocks"
    BASHRC_CALL="bash '$AUTOSTART_SCRIPT' &"
    
    if ! grep -q "$BASHRC_LINE" ~/.bashrc; then
        echo "" >> ~/.bashrc
        echo "$BASHRC_LINE" >> ~/.bashrc
        echo "$BASHRC_CALL" >> ~/.bashrc
        echo "✅ Inicialização automática configurada no .bashrc"
    else
        echo "✅ Inicialização automática já está configurada"
    fi
}

# Configurar sudoers para comandos Docker sem senha
setup_docker_sudo() {
    echo "🔐 Configurando permissões Docker..."
    
    SUDOERS_FILE="/etc/sudoers.d/docker-service"
    SUDOERS_CONTENT="$USER ALL=(ALL) NOPASSWD: /usr/sbin/service docker start, /usr/sbin/service docker stop, /usr/sbin/service docker restart"
    
    if [ ! -f "$SUDOERS_FILE" ]; then
        echo "$SUDOERS_CONTENT" | sudo tee "$SUDOERS_FILE" > /dev/null
        echo "✅ Permissões Docker configuradas"
    else
        echo "✅ Permissões Docker já estão configuradas"
    fi
}

# Criar arquivo .env se não existir
setup_env_file() {
    ENV_FILE="$SCRIPT_DIR/.env"
    if [ ! -f "$ENV_FILE" ]; then
        echo "📝 Criando arquivo .env..."
        cp "$SCRIPT_DIR/.env.example" "$ENV_FILE"
        echo "✅ Arquivo .env criado a partir do .env.example"
    else
        echo "✅ Arquivo .env já existe"
    fi
}

# Testar configuração
test_setup() {
    echo "🧪 Testando configuração..."
    
    # Iniciar serviço Docker
    sudo service docker start
    
    # Aguardar um pouco
    sleep 3
    
    # Testar docker sem sudo
    if docker ps &> /dev/null; then
        echo "✅ Docker funcionando sem sudo"
    else
        echo "⚠️  Docker ainda requer sudo. Execute: newgrp docker"
    fi
}

# Executar configuração
main() {
    echo "🚀 Iniciando configuração..."
    
    install_docker
    install_docker_compose
    add_user_to_docker_group
    setup_docker_sudo
    setup_env_file
    setup_autostart
    test_setup
    
    echo ""
    echo "🎉 Configuração concluída!"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Execute: newgrp docker (ou faça logout/login)"
    echo "2. Execute: ./manage-mssql.ps1 setup (no PowerShell)"
    echo "3. Ou execute: bash wsl-autostart-mssql.sh (no WSL)"
    echo ""
    echo "🔗 O container estará disponível em: localhost:1460"
    echo "🔑 Credenciais: sa / QAMocks2024!"
}

main "$@"

pipeline {
    agent any

    stages {
        stage('Criar .env') {
            steps {
                withCredentials([
                    string(credentialsId: 'RESEND_API_KEY', variable: 'RESEND_API_KEY'),
                    string(credentialsId: 'SECRET_KEY', variable: 'SECRET_KEY')
                ]) {
                    sh '''#!/bin/bash
                        cat > .env << ENVFILE
# Database
DATABASE_PATH=dados.db

# Logging
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30

# Email (Resend.com)
RESEND_API_KEY=${RESEND_API_KEY}
RESEND_FROM_EMAIL=noreply@cachoeiro.es
RESEND_FROM_NAME="Default Web App"

# App
APP_NAME=DefaultWebApp
BASE_URL=http://localhost:8400
SECRET_KEY=${SECRET_KEY}
TIMEZONE=America/Sao_Paulo
RUNNING_MODE=Production
RELOAD=False

# Fotos de Perfil
FOTO_PERFIL_TAMANHO_MAX=256
FOTO_MAX_UPLOAD_BYTES=5242880

# Senha
PASSWORD_MIN_LENGTH=8
PASSWORD_MAX_LENGTH=128

# Interface
TOAST_AUTO_HIDE_DELAY_MS=5000

# === Rate Limiting ===

# Autenticação
RATE_LIMIT_LOGIN_MAX=5
RATE_LIMIT_LOGIN_MINUTOS=5
RATE_LIMIT_CADASTRO_MAX=3
RATE_LIMIT_CADASTRO_MINUTOS=10
RATE_LIMIT_ESQUECI_SENHA_MAX=1
RATE_LIMIT_ESQUECI_SENHA_MINUTOS=1

# Upload de Foto de Perfil
RATE_LIMIT_UPLOAD_FOTO_MAX=5
RATE_LIMIT_UPLOAD_FOTO_MINUTOS=10

# Alteração de Senha
RATE_LIMIT_ALTERAR_SENHA_MAX=5
RATE_LIMIT_ALTERAR_SENHA_MINUTOS=15

# Formulários GET
RATE_LIMIT_FORM_GET_MAX=60
RATE_LIMIT_FORM_GET_MINUTOS=1

# Chat - Mensagens
RATE_LIMIT_CHAT_MESSAGE_MAX=30
RATE_LIMIT_CHAT_MESSAGE_MINUTOS=1

# Chat - Salas
RATE_LIMIT_CHAT_SALA_MAX=10
RATE_LIMIT_CHAT_SALA_MINUTOS=10

# Chat - Busca de Usuários
RATE_LIMIT_BUSCA_USUARIOS_MAX=30
RATE_LIMIT_BUSCA_USUARIOS_MINUTOS=1

# Chat - Listagens
RATE_LIMIT_CHAT_LISTAGEM_MAX=60
RATE_LIMIT_CHAT_LISTAGEM_MINUTOS=1

# Chamados - Criação
RATE_LIMIT_CHAMADO_CRIAR_MAX=5
RATE_LIMIT_CHAMADO_CRIAR_MINUTOS=30

# Chamados - Respostas (Usuário)
RATE_LIMIT_CHAMADO_RESPONDER_MAX=10
RATE_LIMIT_CHAMADO_RESPONDER_MINUTOS=10

# Chamados - Respostas (Admin)
RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MAX=20
RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MINUTOS=5

# Admin - Download de Backups
RATE_LIMIT_BACKUP_DOWNLOAD_MAX=5
RATE_LIMIT_BACKUP_DOWNLOAD_MINUTOS=10

# Páginas Públicas
RATE_LIMIT_PUBLIC_MAX=100
RATE_LIMIT_PUBLIC_MINUTOS=1

# Páginas de Exemplos
RATE_LIMIT_EXAMPLES_MAX=100
RATE_LIMIT_EXAMPLES_MINUTOS=1

# Server
HOST=0.0.0.0
PORT=8400
ENVFILE
                        chmod 600 .env
                        echo "Arquivo .env criado com sucesso!"
                        ls -la .env
                    '''
                }
            }
        }

        stage('Build Docker') {
            steps {
                sh 'docker compose build'
            }
        }

        stage('Deploy') {
            steps {
                sh 'docker compose up -d'
            }
        }
    }

    post {
        success {
            echo '✅ Deploy realizado com sucesso!'
        }
        failure {
            echo '❌ Falha no deploy. Verifique os logs.'
        }
        always {
            echo 'Pipeline finalizado.'
        }
    }
}

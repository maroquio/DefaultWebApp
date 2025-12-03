# DefaultWebApp - Boilerplate FastAPI Completo

> Boilerplate profissional e educacional para desenvolvimento rápido de aplicações web modernas em Python, com componentes reutilizáveis, validação robusta e exemplos práticos.

## Visao Geral

**DefaultWebApp** é um template completo de aplicação web que elimina a necessidade de "começar do zero". Ele fornece toda a estrutura base e componentes reutilizáveis para você focar no que realmente importa: **desenvolver as funcionalidades específicas do seu projeto**.

### Por que usar este boilerplate?

- **Sistema de autenticação completo** - Login, cadastro, perfis de usuário, recuperação de senha
- **Sistema de chamados/tickets** - Abertura, acompanhamento e resposta de chamados de suporte
- **Chat em tempo real** - Comunicação entre usuários via SSE (Server-Sent Events)
- **Componentes UI reutilizáveis** - Modais, formulários, galerias, tabelas responsivas
- **Validação robusta** - 15+ validadores prontos (CPF, CNPJ, email, telefone, etc.)
- **Tratamento de erros centralizado** - Sistema inteligente que elimina ~70% do código repetitivo
- **Máscaras de input** - CPF, CNPJ, telefone, valores monetários, datas, placas de veículo
- **Sistema de fotos** - Upload, crop, redimensionamento automático
- **28+ temas prontos** - Bootswatch themes para customização instantânea
- **Sistema de backups** - Backup e restauração do banco de dados via interface admin
- **Auditoria de logs** - Visualização de logs do sistema com filtros por data e nível
- **Configurações dinâmicas** - Gerenciamento de configurações via banco de dados com cache
- **Rate limiting** - Proteção contra abuso em todas as rotas sensíveis
- **Páginas de exemplo** - 9 exemplos completos de layouts e funcionalidades
- **Padrão CRUD** - Template documentado para criar novas entidades rapidamente
- **Logger profissional** - Sistema de logs com rotação automática
- **Email integrado** - Envio de emails transacionais (Resend.com)
- **Flash messages e toasts** - Feedback visual automático para o usuário
- **Testes configurados** - Estrutura completa de testes com pytest (90%+ cobertura)
- **Seed data** - Sistema de dados iniciais em JSON
- **Segurança** - Rate limiting, security headers, hash de senhas, proteção SQL injection

## Instalação Rápida

### Pré-requisitos
- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/maroquio/DefaultWebApp
   cd DefaultWebApp
   ```

2. **Crie um ambiente virtual**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   ```bash
   # Copie o arquivo de exemplo
   cp .env.example .env

   # Edite o arquivo .env com suas configurações
   # Pelo menos altere o SECRET_KEY para produção
   ```

5. **Execute a aplicação**
   ```bash
   python main.py
   ```

6. **Acesse no navegador**
   ```
   http://localhost:8400
   ```

7. **Explore os exemplos**
   ```
   http://localhost:8400/exemplos
   ```

## Usuários Padrão

O sistema vem com usuários pré-cadastrados para facilitar os testes:

| Perfil | E-mail | Senha | Descrição |
|--------|--------|-------|-----------|
| **Administrador** | administrador@email.com | 1234aA@# | Acesso administrativo completo |
| **Cliente** | cliente@email.com | 1234aA@# | Usuário com perfil Cliente |
| **Vendedor** | vendedor@email.com | 1234aA@# | Usuário com perfil Vendedor |

> **Importante**: Altere essas senhas em ambiente de produção!

## Funcionalidades Principais

### Sistema de Autenticação

- **Login/Logout** com sessões seguras
- **Cadastro de usuários** com validação de senha forte
- **Recuperação de senha** por email
- **Perfis de usuário** (Admin, Cliente, Vendedor - extensível)
- **Proteção de rotas** por perfil com decorator `@requer_autenticacao()`
- **Verificação defensiva** - Todas as rotas autenticadas verificam `usuario_logado` antes de executar
- **Gerenciamento de usuários** (CRUD completo para admins)

### Sistema de Chamados (Tickets)

Sistema completo de suporte ao usuário:

- **Abertura de chamados** - Usuários podem abrir chamados com título, descrição e prioridade
- **Acompanhamento** - Histórico completo de interações em cada chamado
- **Respostas** - Usuários e admins podem trocar mensagens
- **Status** - Aberto, Em Análise, Fechado
- **Prioridades** - Baixa, Média, Alta, Urgente
- **Notificações** - Contador de mensagens não lidas
- **Exclusão** - Usuários podem excluir chamados próprios (apenas se abertos e sem resposta admin)

**Rotas de usuário:**
- `/chamados/listar` - Lista chamados do usuário
- `/chamados/cadastrar` - Abre novo chamado
- `/chamados/{id}/visualizar` - Detalhes e histórico
- `/chamados/{id}/responder` - Adiciona resposta
- `/chamados/{id}/excluir` - Exclui chamado

**Rotas administrativas:**
- `/admin/chamados/listar` - Lista todos os chamados
- `/admin/chamados/{id}/responder` - Responde e altera status
- `/admin/chamados/{id}/fechar` - Fecha chamado
- `/admin/chamados/{id}/reabrir` - Reabre chamado fechado

### Chat em Tempo Real

Sistema de chat entre usuários usando Server-Sent Events (SSE):

- **Conversas privadas** - Chat 1:1 entre usuários
- **Tempo real** - Mensagens entregues instantaneamente via SSE
- **Histórico** - Mensagens persistidas no banco de dados
- **Status de leitura** - Marcação de mensagens como lidas
- **Contador de não lidas** - Badge com total de mensagens não lidas
- **Busca de usuários** - Autocomplete para iniciar conversa
- **Widget integrado** - Chat disponível em todas as páginas autenticadas

**Rotas (API JSON):**
- `/chat/stream` - SSE para receber mensagens em tempo real
- `/chat/salas/criar` - Cria ou obtém sala de chat
- `/chat/conversas` - Lista conversas do usuário
- `/chat/salas/{id}/mensagens` - Lista mensagens de uma sala
- `/chat/salas/{id}/enviar` - Envia mensagem
- `/chat/salas/{id}/lidas` - Marca mensagens como lidas
- `/chat/usuarios/buscar` - Busca usuários para chat
- `/chat/nao-lidas/total` - Conta mensagens não lidas

### Área Administrativa

**Gerenciamento de Usuários** (`/admin/usuarios/`)
- Listagem com todos os usuários
- Cadastro de novos usuários
- Edição de dados (nome, email, perfil)
- Exclusão de usuários

**Configurações do Sistema** (`/admin/configuracoes`)
- Gerenciamento de configurações por categoria
- Edição em lote com salvamento único
- Cache automático para performance
- Rate limiters configuráveis

**Temas Visuais** (`/admin/tema`)
- 28+ temas Bootswatch disponíveis
- Preview visual de cada tema
- Aplicação instantânea

**Auditoria de Logs** (`/admin/auditoria`)
- Visualização de logs por data
- Filtro por nível (INFO, WARNING, ERROR, etc.)
- Exibição formatada com destaque de níveis

**Backups** (`/admin/backups/`)
- Listagem de backups existentes
- Criação de novos backups
- Restauração com backup automático do estado atual
- Download de arquivos de backup
- Exclusão de backups antigos

### Componentes UI Reutilizáveis

#### Templates Components (use `{% include %}`)

**Modal de Confirmação** (`components/modal_confirmacao.html`)
```javascript
abrirModalConfirmacao({
    url: '/rota/excluir/1',
    mensagem: 'Tem certeza?',
    detalhes: '<div>Detalhes aqui</div>'
});
```

**Modal de Crop de Imagem** (`components/modal_corte_imagem.html`)
- Integrado com Cropper.js
- Upload via drag & drop
- Redimensionamento automático

**Chat Widget** (`components/chat_widget.html`)
- Widget de chat integrado
- Lista de conversas
- Envio/recebimento de mensagens em tempo real

**Galeria de Fotos** (`components/galeria_fotos.html`)
```jinja
{% from 'components/galeria_fotos.html' import galeria_fotos %}
{{ galeria_fotos(images, gallery_id='gallery1') }}
```

#### Macros de Formulário

Biblioteca completa em `macros/form_fields.html`:

```jinja
{% from 'macros/form_fields.html' import input_text, input_email, input_password,
   input_date, input_decimal, textarea, select, checkbox, radio %}

{# Campos de texto com validação #}
{{ input_text('nome', 'Nome Completo', value=nome, required=True, error=erros.get('nome')) }}

{# Email com validação #}
{{ input_email('email', 'E-mail', value=email, required=True) }}

{# Senha com toggle de visibilidade #}
{{ input_password('senha', 'Senha', required=True) }}

{# Valores monetários/decimais #}
{{ input_decimal('preco', 'Preço', prefix='R$ ', decimal_places=2) }}

{# Select dropdown #}
{{ select('categoria', 'Categoria', options=categorias, value=categoria_atual) }}
```

### Máscaras de Input Automáticas

Sistema completo de máscaras em `static/js/mascara-input.js`:

```html
<!-- CPF com máscara automática -->
<input data-mask="CPF" name="cpf" data-unmask="true">

<!-- CNPJ -->
<input data-mask="CNPJ" name="cnpj">

<!-- Telefone com 9 dígitos -->
<input data-mask="TELEFONE" name="telefone">

<!-- CEP -->
<input data-mask="CEP" name="cep">

<!-- Valores monetários (formato brasileiro) -->
<input data-decimal
       data-decimal-places="2"
       data-decimal-prefix="R$ "
       data-show-thousands="true"
       name="preco">
```

**Máscaras disponíveis:** CPF, CNPJ, TELEFONE, TELEFONE_FIXO, CEP, DATA, HORA, DATA_HORA, PLACA_ANTIGA, PLACA_MERCOSUL, CARTAO, CVV, VALIDADE_CARTAO

### Validadores Reutilizáveis

15+ validadores prontos em `dtos/validators.py`:

```python
from dtos.validators import (
    validar_email,
    validar_senha_forte,
    validar_cpf,
    validar_cnpj,
    validar_telefone_br,
    validar_cep,
    validar_data,
    validar_inteiro_positivo,
    validar_decimal_positivo
)

class ProdutoDTO(BaseModel):
    nome: str
    email: str
    cpf: str
    preco: float

    _validar_email = field_validator('email')(validar_email())
    _validar_cpf = field_validator('cpf')(validar_cpf())
    _validar_preco = field_validator('preco')(validar_decimal_positivo())
```

### Sistema de Notificações

**Flash Messages** (backend → frontend):
```python
from util.flash_messages import informar_sucesso, informar_erro, informar_aviso, informar_info

informar_sucesso(request, "Operação realizada com sucesso!")
informar_erro(request, "Erro ao processar.")
informar_aviso(request, "Atenção!")
informar_info(request, "Informação importante.")
```

**Toast Programático** (JavaScript):
```javascript
window.App.Toasts.show('Operação realizada!', 'success');
window.App.Toasts.show('Erro ao salvar.', 'danger');
```

### Rate Limiting

Proteção contra abuso configurável por rota:

- Login e cadastro
- Criação/resposta de chamados
- Envio de mensagens no chat
- Alteração de senha
- Upload de foto
- Operações administrativas
- Download de backups

Configurações ajustáveis via banco de dados em `/admin/configuracoes`.

## Estrutura do Projeto

```
DefaultWebApp/
├── data/                    # Dados seed em JSON
│   └── usuarios_seed.json
│
├── dtos/                    # DTOs Pydantic para validação
│   ├── validators.py       # 15+ validadores reutilizáveis
│   ├── usuario_dto.py
│   ├── chamado_dto.py
│   ├── chamado_interacao_dto.py
│   └── ...
│
├── model/                   # Modelos de entidades (dataclasses)
│   ├── usuario_model.py
│   ├── usuario_logado_model.py
│   ├── chamado_model.py
│   ├── chamado_interacao_model.py
│   ├── chat_sala_model.py
│   ├── chat_mensagem_model.py
│   ├── chat_participante_model.py
│   └── configuracao_model.py
│
├── repo/                    # Repositórios de acesso a dados
│   ├── usuario_repo.py
│   ├── chamado_repo.py
│   ├── chamado_interacao_repo.py
│   ├── chat_sala_repo.py
│   ├── chat_mensagem_repo.py
│   ├── chat_participante_repo.py
│   └── configuracao_repo.py
│
├── routes/                  # Rotas organizadas por módulo
│   ├── auth_routes.py           # Login, cadastro, recuperação
│   ├── usuario_routes.py        # Dashboard e perfil do usuário
│   ├── chamados_routes.py       # Chamados do usuário
│   ├── chat_routes.py           # API do chat (SSE)
│   ├── admin_usuarios_routes.py # CRUD de usuários
│   ├── admin_chamados_routes.py # Gerenciamento de chamados
│   ├── admin_configuracoes_routes.py # Configurações e temas
│   ├── admin_backups_routes.py  # Backup e restauração
│   ├── public_routes.py         # Páginas públicas
│   └── examples_routes.py       # Exemplos práticos
│
├── sql/                     # Comandos SQL
│   ├── usuario_sql.py
│   ├── chamado_sql.py
│   ├── chat_sql.py
│   └── configuracao_sql.py
│
├── static/                  # Arquivos estáticos
│   ├── css/
│   │   ├── bootstrap.min.css
│   │   ├── bootswatch/     # 28+ temas prontos
│   │   └── custom.css
│   ├── js/
│   │   ├── toasts.js
│   │   ├── mascara-input.js    # Máscaras de input
│   │   ├── widget-chat.js      # Widget do chat
│   │   ├── cortador-imagem.js  # Crop de imagens
│   │   └── ...
│   └── img/
│       └── usuarios/        # Fotos de perfil
│
├── templates/               # Templates Jinja2
│   ├── base_publica.html   # Base para páginas públicas
│   ├── base_privada.html   # Base para páginas autenticadas
│   ├── dashboard.html      # Dashboard do usuário
│   ├── auth/               # Login, cadastro, recuperação
│   ├── perfil/             # Perfil do usuário
│   ├── chamados/           # Páginas de chamados
│   ├── admin/              # Área administrativa
│   │   ├── usuarios/
│   │   ├── chamados/
│   │   ├── configuracoes/
│   │   ├── backups/
│   │   ├── tema.html
│   │   └── auditoria.html
│   ├── components/         # Componentes reutilizáveis
│   │   ├── modal_confirmacao.html
│   │   ├── modal_corte_imagem.html
│   │   ├── chat_widget.html
│   │   └── ...
│   ├── macros/             # Macros de formulário
│   ├── exemplos/           # 9 páginas de exemplo
│   └── errors/             # Páginas de erro (404, 429, 500)
│
├── util/                    # Utilitários
│   ├── auth_decorator.py   # Decorator de autenticação
│   ├── perfis.py           # Enum de perfis
│   ├── db_util.py          # Gerenciamento de conexão
│   ├── security.py         # Hash de senhas
│   ├── backup_util.py      # Funções de backup
│   ├── email_service.py    # Envio de emails
│   ├── foto_util.py        # Sistema de fotos
│   ├── exceptions.py       # Exceções customizadas
│   ├── exception_handlers.py # Handlers globais
│   ├── flash_messages.py   # Flash messages
│   ├── logger_config.py    # Logger profissional
│   ├── rate_limiter.py     # Rate limiting dinâmico
│   ├── config_cache.py     # Cache de configurações
│   ├── permission_helpers.py # Helpers de permissão
│   └── ...
│
├── tests/                   # Testes automatizados
│   ├── conftest.py         # Fixtures do pytest
│   └── test_*.py           # 90%+ cobertura
│
├── logs/                    # Logs da aplicação (criado automaticamente)
│
├── .env.example             # Exemplo de variáveis de ambiente
├── BLOG.md                  # Tutorial passo a passo para criar o projeto
├── main.py                  # Arquivo principal
├── requirements.txt
└── README.md
```

## Tecnologias Utilizadas

### Backend
- **FastAPI 0.115+** - Framework web moderno e rápido
- **Uvicorn** - Servidor ASGI de alta performance
- **Pydantic 2.0+** - Validação de dados com type hints
- **Passlib + Bcrypt** - Hash de senhas seguro
- **SSE (Server-Sent Events)** - Chat em tempo real

### Frontend
- **Jinja2** - Engine de templates
- **Bootstrap 5.3** - Framework CSS responsivo
- **Bootstrap Icons** - Biblioteca de ícones
- **Bootswatch** - 28+ temas prontos
- **JavaScript vanilla** - Sem dependências pesadas
- **Cropper.js** - Crop de imagens

### Banco de Dados
- **SQLite3** - Banco de dados embutido
- **SQL Puro** - Sem ORM para máximo controle

### Comunicação
- **Resend** - Envio de e-mails transacionais

### Desenvolvimento
- **Python-dotenv** - Gerenciamento de variáveis de ambiente
- **Pytest** - Framework de testes (90%+ cobertura)
- **Logging** - Sistema de logs profissional com rotação

## Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```env
# Banco de Dados
DATABASE_PATH=dados.db

# Aplicação
APP_NAME=SeuProjeto
SECRET_KEY=sua_chave_secreta_super_segura_aqui  # gere em https://generate-secret.now.sh/64
BASE_URL=http://localhost:8400
TIMEZONE=America/Sao_Paulo
RUNNING_MODE=Development

# Servidor
HOST=127.0.0.1
PORT=8400
RELOAD=True

# Logging
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30

# E-mail (Resend.com)
RESEND_API_KEY=seu_api_key_aqui  # gere em https://resend.com/
RESEND_FROM_EMAIL=noreply@seudominio.com
RESEND_FROM_NAME="Seu Projeto"

# Fotos
FOTO_PERFIL_TAMANHO_MAX=256
FOTO_MAX_UPLOAD_BYTES=5242880

# Senha
PASSWORD_MIN_LENGTH=8
PASSWORD_MAX_LENGTH=128
```

Veja o arquivo `.env.example` para a lista completa de variáveis, incluindo rate limits configuráveis.

## Testes

Execute os testes com pytest:

```bash
# Todos os testes
pytest

# Com verbose
pytest -v

# Com cobertura
pytest --cov=. --cov-report=html

# Teste específico
pytest tests/test_auth_routes.py
pytest tests/test_chat_routes.py
```

## Segurança

### Implementações Atuais
- Senhas com hash bcrypt
- Sessões com chave secreta
- Rate limiting em todas as rotas sensíveis
- Validação de força de senha
- Security headers (X-Frame-Options, etc.)
- Proteção contra SQL injection (prepared statements)
- Validação de dados com Pydantic
- XSS protection via Jinja2 auto-escaping
- Verificação defensiva de `usuario_logado` em todas as rotas autenticadas
- Whitelist de temas para prevenção de Path Traversal
- Validação de propriedade de recursos (usuário só acessa seus próprios dados)

### Checklist para Produção
- [ ] Alterar `SECRET_KEY` para valor único e seguro
- [ ] Alterar senhas padrão dos usuários
- [ ] Configurar HTTPS/SSL
- [ ] Configurar firewall
- [ ] Backup regular do banco de dados
- [ ] Monitoramento de logs
- [ ] Configurar CSRF tokens

## Documentação Adicional

- **[BLOG.md](BLOG.md)** - Tutorial completo para criar o projeto do zero, passo a passo
- **[/exemplos](http://localhost:8400/exemplos)** - 9 exemplos práticos funcionais na aplicação

## Licença

Este projeto é um boilerplate educacional livre para uso.

---

**Desenvolvido para acelerar o desenvolvimento de aplicações web com Python e FastAPI**

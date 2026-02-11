# DefaultWebApp - Boilerplate FastAPI Completo

> Boilerplate educacional para desenvolvimento rapido de aplicacoes web em Python. Fornece autenticacao, gerenciamento de usuarios, chat em tempo real, sistema de chamados, backups, validacao robusta e componentes UI reutilizaveis — tudo pronto para voce focar nas funcionalidades do seu projeto.

## Glossario Rapido

Se voce esta comecando, estes termos aparecem ao longo do documento:

| Termo | O que significa |
|-------|-----------------|
| **Boilerplate** | Projeto-base pronto para ser reutilizado como ponto de partida |
| **CRUD** | Create, Read, Update, Delete — as 4 operacoes basicas de qualquer cadastro |
| **DTO** | Data Transfer Object — objeto que valida dados recebidos de formularios |
| **API** | Interface que permite comunicacao entre sistemas (ex: frontend e backend) |
| **SSE** | Server-Sent Events — tecnologia para enviar dados do servidor ao navegador em tempo real |
| **CSRF** | Cross-Site Request Forgery — ataque que tenta enviar requisicoes falsas; o projeto ja protege contra isso |
| **ORM** | Mapeamento objeto-relacional (este projeto **nao** usa ORM; usa SQL puro para voce aprender SQL) |
| **Rate Limiting** | Limite de requisicoes por tempo — impede que um usuario abuse do sistema |
| **Seed Data** | Dados iniciais inseridos automaticamente no banco ao iniciar a aplicacao |
| **Hash** | Transformacao irreversivel de uma senha para armazena-la com seguranca |
| **Middleware** | Codigo que intercepta todas as requisicoes antes de chegarem nas rotas |
| **Template** | Arquivo HTML com trechos dinamicos que o servidor preenche antes de enviar ao navegador |
| **Dataclass** | Classe Python simplificada para representar entidades (ex: Usuario, Chamado) |

## Por que usar este boilerplate?

- **Sistema de autenticacao completo** — Login, cadastro, perfis de usuario, recuperacao de senha
- **Sistema de chamados/tickets** — Abertura, acompanhamento e resposta de chamados de suporte
- **Chat em tempo real** — Comunicacao entre usuarios via SSE (Server-Sent Events)
- **Componentes UI reutilizaveis** — Modais, formularios, galerias, tabelas responsivas
- **Validacao robusta** — 15+ validadores prontos (CPF, CNPJ, email, telefone, etc.)
- **Tratamento de erros centralizado** — Sistema que elimina codigo repetitivo de validacao
- **Mascaras de input** — CPF, CNPJ, telefone, valores monetarios, datas, placas de veiculo
- **Sistema de fotos** — Upload, crop e redimensionamento automatico
- **27 temas visuais** — Temas Bootswatch para customizacao instantanea
- **Sistema de backups** — Backup e restauracao do banco de dados via interface admin
- **Auditoria de logs** — Visualizacao de logs do sistema com filtros
- **Configuracoes dinamicas** — Gerenciamento de configuracoes via banco de dados
- **Rate limiting** — Protecao contra abuso em rotas sensiveis
- **9 paginas de exemplo** — Layouts e funcionalidades prontas em `/exemplos`
- **Padrao CRUD documentado** — Template para criar novas entidades rapidamente
- **Logger profissional** — Logs com rotacao automatica diaria
- **Email integrado** — Envio de emails transacionais via Resend.com
- **Testes configurados** — Estrutura completa com pytest (unitarios, integracao e E2E)
- **Docker** — Dockerfile e docker-compose prontos para deploy
- **Seguranca** — CSRF, rate limiting, security headers, hash de senhas, protecao SQL injection

## Instalacao Rapida

### Pre-requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone o repositorio**
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

3. **Instale as dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variaveis de ambiente**
   ```bash
   cp .env.example .env
   ```
   Edite o arquivo `.env` — pelo menos altere `SECRET_KEY` e `APP_NAME`.

5. **Execute a aplicacao**
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

## Usuarios Padrao

O sistema vem com usuarios pre-cadastrados para testes:

| Perfil | E-mail | Senha | Descricao |
|--------|--------|-------|-----------|
| **Administrador** | padrao@administrador.com | 1234aA@# | Acesso administrativo completo |
| **Cliente** | padrao@cliente.com | 1234aA@# | Usuario com perfil Cliente |
| **Vendedor** | padrao@vendedor.com | 1234aA@# | Usuario com perfil Vendedor |

> **Importante**: Altere essas senhas em ambiente de producao!

## Funcionalidades Principais

### Sistema de Autenticacao

- Login/Logout com sessoes seguras
- Cadastro de usuarios com validacao de senha forte
- Recuperacao de senha por email
- Perfis de usuario (Administrador, Cliente, Vendedor — extensivel)
- Protecao de rotas por perfil com decorator `@requer_autenticacao()`
- Gerenciamento de usuarios (CRUD completo para admins)

### Sistema de Chamados (Tickets)

Sistema de suporte ao usuario com:

- Abertura de chamados com titulo, descricao e prioridade
- Historico completo de interacoes em cada chamado
- Troca de mensagens entre usuarios e admins
- 4 status: **Aberto**, **Em Analise**, **Resolvido**, **Fechado**
- 4 prioridades: **Baixa**, **Media**, **Alta**, **Urgente**
- Contador de mensagens nao lidas
- Exclusao de chamados proprios (apenas se abertos e sem resposta admin)

**Rotas de usuario** (prefixo `/chamados`):

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/chamados/listar` | Lista chamados do usuario |
| GET/POST | `/chamados/cadastrar` | Abre novo chamado |
| GET | `/chamados/{id}/visualizar` | Detalhes e historico |
| POST | `/chamados/{id}/responder` | Adiciona resposta |
| POST | `/chamados/{id}/excluir` | Exclui chamado |

**Rotas administrativas** (prefixo `/admin/chamados`):

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/admin/chamados/listar` | Lista todos os chamados |
| GET/POST | `/admin/chamados/{id}/responder` | Responde e altera status |
| POST | `/admin/chamados/{id}/fechar` | Fecha chamado |
| POST | `/admin/chamados/{id}/reabrir` | Reabre chamado fechado |

### Chat em Tempo Real

Sistema de chat entre usuarios usando Server-Sent Events (SSE):

- Conversas privadas 1:1 entre usuarios
- Mensagens entregues instantaneamente via SSE
- Historico persistido no banco de dados
- Marcacao de mensagens como lidas
- Badge com total de mensagens nao lidas
- Busca de usuarios para iniciar conversa
- Widget de chat integrado em todas as paginas autenticadas

**Rotas** (prefixo `/chat`):

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/chat/stream` | Stream SSE para receber mensagens em tempo real |
| POST | `/chat/salas` | Cria ou obtem sala de chat |
| GET | `/chat/conversas` | Lista conversas do usuario |
| GET | `/chat/mensagens/{sala_id}` | Lista mensagens de uma sala |
| POST | `/chat/mensagens` | Envia mensagem |
| POST | `/chat/mensagens/lidas/{sala_id}` | Marca mensagens como lidas |
| GET | `/chat/usuarios/buscar` | Busca usuarios para chat |
| GET | `/chat/mensagens/nao-lidas/total` | Conta mensagens nao lidas |

### Area Administrativa

**Gerenciamento de Usuarios** (`/admin/usuarios/`) — Listagem, cadastro, edicao e exclusao de usuarios.

**Configuracoes do Sistema** (`/admin/configuracoes`) — Gerenciamento de configuracoes organizadas em 4 abas: Frequencia de Requisicoes, Interface, Aplicacao e Fotos. Todas as alteracoes sao aplicadas imediatamente sem reiniciar o servidor.

**Temas Visuais** (`/admin/tema`) — 27 temas Bootswatch com preview visual e aplicacao instantanea.

**Auditoria de Logs** (`/admin/auditoria`) — Visualizacao de logs por data com filtro por nivel (INFO, WARNING, ERROR, etc.).

**Backups** (`/admin/backups/`) — Criacao, listagem, download, restauracao e exclusao de backups do banco de dados. A restauracao cria automaticamente um backup de seguranca do estado atual.

### Componentes UI Reutilizaveis

O projeto inclui uma biblioteca de componentes prontos para uso nos seus templates:

**Componentes** (use com `{% include %}`):
- **Modal de Confirmacao** — Dialogo de confirmacao para operacoes de exclusao
- **Modal de Alerta** — Substituto moderno para `alert()` do JavaScript
- **Modal de Crop de Imagem** — Upload e recorte de fotos com Cropper.js
- **Galeria de Fotos** — Macro para exibicao de galerias com thumbnails
- **Chat Widget** — Widget de chat integrado
- **Indicador de Senha** — Feedback visual de forca da senha

**Macros de Formulario** (use com `{% from ... import ... %}`):
- Campos de texto, email, senha, data, decimal
- Textarea, select, checkbox, radio
- Todos com suporte a label, texto de ajuda e mensagens de erro

**Macros Adicionais**: Botoes de acao, badges de status, estados vazios.

Veja todos os componentes em acao acessando `http://localhost:8400/exemplos`.

### Mascaras de Input

Mascaras disponiveis: **CPF**, **CNPJ**, **TELEFONE**, **TELEFONE_FIXO**, **CEP**, **DATA**, **HORA**, **DATA_HORA**, **PLACA_ANTIGA**, **PLACA_MERCOSUL**, **CARTAO**, **CVV**, **VALIDADE_CARTAO**.

Tambem ha mascara para valores decimais no formato brasileiro (virgula decimal, separador de milhares com ponto, prefixo configuravel como "R$ ").

Exemplos praticos de uso em `http://localhost:8400/exemplos/demo-campos-formulario`.

### Validadores Reutilizaveis

15+ validadores prontos em `dtos/validators.py` para uso em DTOs Pydantic:

- **Texto**: string obrigatoria, comprimento, numero minimo de palavras, nome de pessoa
- **Email**: validacao de formato
- **Senha**: forca da senha, confirmacao de senhas
- **Documentos brasileiros**: CPF, CNPJ, telefone, CEP
- **Datas**: data valida, data futura, data passada
- **Numeros**: inteiro positivo, decimal positivo
- **Arquivos**: extensao, tamanho
- **Enums**: validacao contra enums do dominio

### Sistema de Notificacoes

- **Flash messages** (backend): Mensagens de sucesso, erro, aviso e informacao via `util/flash_messages.py`
- **Toasts** (frontend): Notificacoes visuais automaticas via `static/js/toasts.js`
- **Modais de alerta** (frontend): Substituto moderno para `alert()` via `static/js/modal-alerta.js`

### Rate Limiting

Protecao contra abuso configuravel por rota, incluindo: login, cadastro, chamados, chat, upload de foto, alteracao de senha, operacoes administrativas e paginas publicas. Todas as configuracoes sao ajustaveis via banco de dados em `/admin/configuracoes` sem necessidade de reiniciar o servidor.

## Estrutura do Projeto

```
DefaultWebApp/
├── data/                        # Dados seed em JSON
│   └── usuarios_seed.json
│
├── docs/                        # Documentacao adicional
│   └── TESTES_E2E.md           # Tutorial de testes E2E com Playwright
│
├── dtos/                        # DTOs Pydantic para validacao
│   ├── validators.py           # 15+ validadores reutilizaveis
│   ├── auth_dto.py
│   ├── usuario_dto.py
│   ├── perfil_dto.py
│   ├── chamado_dto.py
│   ├── chamado_interacao_dto.py
│   ├── chat_dto.py
│   └── configuracao_dto.py
│
├── model/                       # Modelos de entidades (dataclasses)
│   ├── usuario_model.py
│   ├── usuario_logado_model.py
│   ├── chamado_model.py
│   ├── chamado_interacao_model.py
│   ├── chat_sala_model.py
│   ├── chat_participante_model.py
│   ├── chat_mensagem_model.py
│   └── configuracao_model.py
│
├── repo/                        # Repositorios de acesso a dados
│   ├── usuario_repo.py
│   ├── chamado_repo.py
│   ├── chamado_interacao_repo.py
│   ├── chat_sala_repo.py
│   ├── chat_participante_repo.py
│   ├── chat_mensagem_repo.py
│   ├── configuracao_repo.py
│   └── indices_repo.py         # Gerenciamento de indices do banco
│
├── routes/                      # Rotas organizadas por modulo
│   ├── auth_routes.py               # Login, cadastro, recuperacao
│   ├── usuario_routes.py            # Dashboard e perfil do usuario
│   ├── chamados_routes.py           # Chamados do usuario
│   ├── chat_routes.py               # Chat em tempo real (SSE)
│   ├── admin_usuarios_routes.py     # CRUD de usuarios (admin)
│   ├── admin_chamados_routes.py     # Gerenciamento de chamados (admin)
│   ├── admin_configuracoes_routes.py # Configuracoes, temas e auditoria
│   ├── admin_backups_routes.py      # Backup e restauracao (admin)
│   ├── public_routes.py             # Paginas publicas
│   └── examples_routes.py          # Exemplos praticos
│
├── sql/                         # Comandos SQL (prepared statements)
│   ├── usuario_sql.py
│   ├── chamado_sql.py
│   ├── chamado_interacao_sql.py
│   ├── chat_sala_sql.py
│   ├── chat_participante_sql.py
│   ├── chat_mensagem_sql.py
│   ├── configuracao_sql.py
│   └── indices_sql.py          # Definicoes de indices
│
├── static/                      # Arquivos estaticos
│   ├── css/
│   │   ├── bootstrap.min.css   # Bootstrap 5.3.8
│   │   ├── bootswatch/         # 27 temas visuais
│   │   ├── custom.css
│   │   └── widget-chat.css
│   ├── js/
│   │   ├── toasts.js               # Notificacoes toast
│   │   ├── modal-alerta.js          # Modais de alerta
│   │   ├── mascara-input.js         # Mascaras de input
│   │   ├── validador-senha.js       # Indicador de forca de senha
│   │   ├── cortador-imagem.js       # Crop de imagens
│   │   ├── manipulador-foto-perfil.js # Handler de foto de perfil
│   │   ├── auxiliares-exclusao.js   # Helpers de exclusao
│   │   └── widget-chat.js          # Widget do chat
│   └── img/
│       ├── usuarios/           # Fotos de perfil dos usuarios
│       ├── bootswatch/         # Previews dos temas
│       ├── site/               # Imagens do site
│       ├── logo.svg
│       └── user.jpg            # Foto padrao de usuario
│
├── templates/                   # Templates Jinja2
│   ├── base_publica.html       # Base para paginas publicas
│   ├── base_privada.html       # Base para paginas autenticadas
│   ├── dashboard.html
│   ├── index.html
│   ├── sobre.html
│   ├── auth/                   # Login, cadastro, recuperacao
│   ├── perfil/                 # Perfil do usuario
│   ├── chamados/               # Paginas de chamados
│   ├── admin/                  # Area administrativa
│   │   ├── usuarios/
│   │   ├── chamados/
│   │   ├── configuracoes/
│   │   ├── backups/
│   │   ├── tema.html
│   │   └── auditoria.html
│   ├── components/             # Componentes reutilizaveis
│   ├── macros/                 # Macros de formulario e UI
│   ├── exemplos/               # 9 paginas de exemplo
│   └── errors/                 # Paginas de erro (404, 429, 500)
│
├── util/                        # Utilitarios
│   ├── auth_decorator.py       # Decorator de autenticacao
│   ├── perfis.py               # Enum de perfis de usuario
│   ├── enum_base.py            # Classe base para enums do dominio
│   ├── db_util.py              # Gerenciamento de conexao com banco
│   ├── datetime_util.py        # Data/hora com timezone
│   ├── security.py             # Hash de senhas (bcrypt)
│   ├── senha_util.py           # Validacao de forca de senha
│   ├── csrf_protection.py      # Middleware de protecao CSRF
│   ├── security_headers.py     # Headers de seguranca
│   ├── exceptions.py           # Excecoes customizadas
│   ├── exception_handlers.py   # Handlers globais de excecao
│   ├── validation_util.py      # Processamento de erros de validacao
│   ├── flash_messages.py       # Flash messages
│   ├── template_util.py        # Rendering de templates
│   ├── foto_util.py            # Sistema de fotos de perfil
│   ├── email_service.py        # Envio de emails (Resend.com)
│   ├── backup_util.py          # Backup do banco de dados
│   ├── chat_manager.py         # Gerenciador SSE do chat
│   ├── rate_limiter.py         # Rate limiting dinamico
│   ├── rate_limit_decorator.py # Decorator de rate limit
│   ├── config.py               # Carregamento de configuracoes
│   ├── config_cache.py         # Cache de configuracoes (thread-safe)
│   ├── migrar_config.py        # Migracao de .env para banco
│   ├── seed_data.py            # Dados iniciais automaticos
│   ├── logger_config.py        # Logger com rotacao diaria
│   ├── permission_helpers.py   # Helpers de permissao
│   ├── repository_helpers.py   # Helpers de repositorio
│   └── validation_helpers.py   # Helpers de validacao
│
├── tests/                       # Testes automatizados
│   ├── conftest.py             # Fixtures globais do pytest
│   ├── unit/                   # Testes unitarios
│   ├── integration/            # Testes de integracao
│   │   ├── repos/              #   Repositorios
│   │   ├── routes/             #   Rotas
│   │   └── utils/              #   Utilitarios
│   ├── e2e/                    # Testes end-to-end (Playwright)
│   └── helpers/                # Testes de helpers
│
├── logs/                        # Logs da aplicacao (criado automaticamente)
├── backups/                     # Backups do banco (criado automaticamente)
│
├── .env.example                 # Modelo de variaveis de ambiente
├── BLOG.md                      # Tutorial: criando um Blog com o boilerplate
├── CLAUDE.md                    # Instrucoes para Claude Code
├── Dockerfile                   # Imagem Docker da aplicacao
├── docker-compose.yml           # Orquestracao Docker
├── Jenkinsfile                  # Pipeline CI/CD
├── main.py                      # Arquivo principal da aplicacao
├── pyproject.toml               # Configuracao do projeto Python
├── pytest.ini                   # Configuracao do pytest
├── requirements.txt             # Dependencias Python
└── README.md
```

## Tecnologias Utilizadas

### Backend
- **Python 3.11+** — Linguagem principal
- **FastAPI 0.115** — Framework web moderno e rapido
- **Uvicorn** — Servidor ASGI de alta performance
- **Pydantic 2.9** — Validacao de dados com type hints
- **Passlib + Bcrypt** — Hash seguro de senhas
- **Pillow** — Processamento de imagens (crop, redimensionamento)
- **SSE (Server-Sent Events)** — Chat em tempo real

### Frontend
- **Jinja2** — Engine de templates
- **Bootstrap 5.3.8** — Framework CSS responsivo
- **Bootstrap Icons** — Biblioteca de icones
- **Bootswatch** — 27 temas visuais prontos
- **JavaScript vanilla** — Sem dependencias pesadas de frameworks
- **Cropper.js** — Crop interativo de imagens

### Banco de Dados
- **SQLite3** — Banco de dados embutido (sem necessidade de instalar servidor)
- **SQL Puro** — Sem ORM, para voce aprender SQL de verdade

### Infraestrutura
- **Docker** — Containerizacao para deploy
- **Jenkins** — Pipeline CI/CD
- **Resend** — Envio de emails transacionais

### Desenvolvimento
- **Python-dotenv** — Gerenciamento de variaveis de ambiente
- **Pytest** — Framework de testes (unitarios, integracao e E2E)
- **Playwright** — Testes end-to-end no navegador
- **Logging** — Sistema de logs profissional com rotacao diaria

## Variaveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```env
# Banco de Dados
DATABASE_PATH=dados.db

# Aplicacao
APP_NAME=SeuProjeto
SECRET_KEY=cole_a_chave_de_sessao_aqui   # gere em https://generate-secret.now.sh/64
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

# Email (Resend.com)
RESEND_API_KEY=seu_api_key_aqui          # gere em https://resend.com/
RESEND_FROM_EMAIL=noreply@seudominio.com
RESEND_FROM_NAME="Seu Projeto"

# Fotos de Perfil
FOTO_PERFIL_TAMANHO_MAX=256
FOTO_MAX_UPLOAD_BYTES=5242880

# Senha
PASSWORD_MIN_LENGTH=8
PASSWORD_MAX_LENGTH=128

# Interface
TOAST_AUTO_HIDE_DELAY_MS=5000
```

O arquivo `.env.example` tambem inclui configuracoes de **rate limiting** para cada grupo de rotas (autenticacao, chat, chamados, upload, paginas publicas, etc.). Todas essas configuracoes podem ser ajustadas posteriormente via `/admin/configuracoes` sem reiniciar o servidor.

## Docker

O projeto inclui suporte a Docker para facilitar o deploy:

```bash
# Construir a imagem
docker compose build

# Iniciar o container
docker compose up -d

# Ver logs do container
docker compose logs -f

# Parar o container
docker compose down
```

O container expoe a aplicacao na porta **8400** e inclui health check automatico no endpoint `/health`.

## Testes

O projeto possui uma estrutura organizada de testes:

```bash
# Executar todos os testes
pytest

# Executar apenas testes unitarios
pytest tests/unit/

# Executar apenas testes de integracao
pytest tests/integration/

# Executar testes de rotas especificas
pytest tests/integration/routes/test_auth_routes.py

# Executar testes por marcador
pytest -m unit
pytest -m integration

# Executar com relatorio de cobertura
pytest --cov=. --cov-report=html
```

**Marcadores disponiveis**: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`, `@pytest.mark.auth`, `@pytest.mark.crud`

Para testes end-to-end com Playwright, consulte `docs/TESTES_E2E.md`.

## Seguranca

### Implementacoes Atuais
- Senhas com hash bcrypt
- Sessoes com chave secreta
- Protecao CSRF com tokens em todos os formularios
- Rate limiting em todas as rotas sensiveis
- Validacao de forca de senha
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- Protecao contra SQL injection (prepared statements com `?`)
- Protecao XSS via Jinja2 auto-escaping
- Validacao de propriedade de recursos (usuario so acessa seus proprios dados)
- Whitelist de temas para prevencao de Path Traversal

### Checklist para Producao
- [ ] Alterar `SECRET_KEY` para valor unico e seguro (minimo 32 caracteres)
- [ ] Alterar senhas padrao dos usuarios
- [ ] Configurar HTTPS/SSL
- [ ] Configurar firewall
- [ ] Ativar backup regular do banco de dados
- [ ] Configurar monitoramento de logs
- [ ] Alterar `RUNNING_MODE` para `Production`

## Como Criar Seu Proprio Projeto

Este boilerplate foi feito para ser o ponto de partida do seu projeto. Siga estes passos:

### 1. Clone e renomeie

```bash
git clone https://github.com/maroquio/DefaultWebApp MeuProjeto
cd MeuProjeto
rm -rf .git
git init
```

### 2. Configure o ambiente

```bash
python3 -m venv .venv
source .venv/bin/activate    # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
```

Edite o `.env` e altere pelo menos:
- `APP_NAME` — Nome do seu projeto
- `SECRET_KEY` — Gere uma chave unica em https://generate-secret.now.sh/64

### 3. Altere os usuarios seed

Edite `data/usuarios_seed.json` com os usuarios iniciais do seu projeto. Altere emails e senhas.

### 4. Crie suas entidades

Para cada nova funcionalidade (ex: Produto, Servico, Pedido), siga esta sequencia de arquivos:

1. **Model** (`model/`) — Dataclass representando a entidade
2. **SQL** (`sql/`) — Queries SQL como constantes
3. **Repository** (`repo/`) — Funcoes de acesso ao banco
4. **DTO** (`dtos/`) — Validacao com Pydantic
5. **Routes** (`routes/`) — Rotas HTTP (GET/POST)
6. **Templates** (`templates/`) — Paginas HTML
7. **Registrar em `main.py`** — Adicionar tabela e router

Para um tutorial pratico completo deste processo, veja o **BLOG.md** que guia a criacao de um blog com categorias e artigos usando este boilerplate.

## Solucao de Problemas Comuns

**"Porta 8400 ja em uso"**
Outra aplicacao esta usando a porta. Altere `PORT` no `.env` para outro valor (ex: 8401) ou encerre o processo que esta usando a porta.

**"ModuleNotFoundError: No module named 'fastapi'"**
O ambiente virtual nao esta ativado. Execute `source .venv/bin/activate` (Linux/Mac) ou `.venv\Scripts\activate` (Windows) antes de rodar a aplicacao.

**"database is locked"**
O banco SQLite so permite uma escrita por vez. Feche outras conexoes ao banco (como o SQLite Browser) e tente novamente.

**"TemplateNotFound"**
Verifique se o caminho do template esta correto e relativo a pasta `templates/`. Confira se o arquivo realmente existe nesse caminho.

**"Erro ao enviar email"**
Configure `RESEND_API_KEY` no `.env` com uma chave valida do Resend.com. Para desenvolvimento sem email, os links de recuperacao de senha aparecem nos logs (`logs/`).

**"Foto de perfil nao aparece"**
Verifique se a pasta `static/img/usuarios/` existe e tem permissao de escrita. O sistema cria uma foto padrao automaticamente ao cadastrar um usuario.

## Documentacao Adicional

- **[BLOG.md](BLOG.md)** — Tutorial pratico: criando um Blog completo usando este boilerplate como base
- **[docs/TESTES_E2E.md](docs/TESTES_E2E.md)** — Tutorial de testes end-to-end com Playwright
- **[tests/README.md](tests/README.md)** — Guia completo de testes (convencoes, fixtures, exemplos)
- **[/exemplos](http://localhost:8400/exemplos)** — 9 paginas de exemplo com componentes, layouts e funcionalidades

## Links Uteis

- [FastAPI - Documentacao Oficial](https://fastapi.tiangolo.com/)
- [Bootstrap 5 - Documentacao](https://getbootstrap.com/docs/5.3/)
- [Pydantic - Documentacao](https://docs.pydantic.dev/)
- [SQLite - Documentacao](https://www.sqlite.org/docs.html)
- [Jinja2 - Documentacao](https://jinja.palletsprojects.com/)
- [Bootswatch - Temas](https://bootswatch.com/)
- [Cropper.js](https://fengyuanchen.github.io/cropperjs/)
- [Resend - Servico de Email](https://resend.com/docs)

## Licenca

Este projeto e um boilerplate educacional livre para uso.

---

**Desenvolvido para o ensino de desenvolvimento web com Python e FastAPI**

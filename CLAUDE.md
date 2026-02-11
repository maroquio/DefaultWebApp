# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**DefaultWebApp** is a FastAPI-based web application boilerplate for rapid development of web applications in Portuguese. It's a complete educational template with authentication, user management, profile photos with crop functionality, reusable validation system, exception handling, support ticket system (chamados), real-time chat via SSE, database backup management, CSRF protection, and example CRUD implementations using Python 3.10+, FastAPI, Jinja2 templates, Bootstrap 5.3.8, and SQLite without ORM (pure SQL).

## Running the Application

### Development Mode (with hot reload)
```bash
python main.py
```

The application will start on the configured HOST and PORT (default: http://0.0.0.0:8400)

### Running Tests
```bash
pytest                              # Run all tests with verbose output
pytest tests/unit/                  # Run unit tests
pytest tests/integration/           # Run integration tests
pytest tests/e2e/                   # Run end-to-end tests
pytest tests/e2e/test_auth.py       # Run specific test file
pytest -k test_login                # Run tests matching pattern
pytest -m auth                      # Run tests with specific marker
```

### Type Checking
```bash
python3 -m mypy .
```

### Database Operations
```bash
sqlite3 database.db       # Access database directly
sqlite3 database.db ".tables"  # List tables
sqlite3 database.db "SELECT * FROM usuario;"  # Query data
```

## Architecture

This project follows a **layered architecture** with clear separation of concerns:

```
Routes (HTTP) → DTOs (Validation) → Repositories → SQL → Database
                        ↓
              Templates ← Flash Messages
                        ↓
              Static Assets (CSS/JS)
```

### Core Layers

1. **Routes** (`routes/`): Handle HTTP requests/responses, use decorators for auth and rate limiting
2. **DTOs** (`dtos/`): Pydantic models for input validation using Field() and field_validator
3. **Models** (`model/`): Python dataclasses representing domain entities
4. **Repositories** (`repo/`): Database access layer with CRUD operations
5. **SQL** (`sql/`): Isolated SQL query definitions as constants (prepared statements with `?` placeholders)
6. **Templates** (`templates/`): Jinja2 HTML templates with Bootstrap 5.3.8
7. **Utilities** (`util/`): Cross-cutting concerns (auth, logging, email, photos, CSRF, rate limiting, etc.)
8. **Static Assets** (`static/`): CSS, JavaScript, images

### Important Patterns

**Authentication Flow:**
- Session-based authentication using FastAPI's SessionMiddleware
- The `@requer_autenticacao()` decorator protects routes and automatically injects `usuario_logado: UsuarioLogado` into kwargs
- Use `@requer_autenticacao([Perfil.ADMIN.value])` to restrict by profile
- Session management functions in `util/auth_decorator.py`: `criar_sessao()`, `destruir_sessao()`, `obter_usuario_logado()`, `esta_logado()`
- **ALWAYS use `UsuarioLogado` dataclass** for type hints of `usuario_logado` parameter (see below)

**Database Connection:**
- Always use `with get_connection() as conn:` context manager from `util/db_util.py`
- Connection automatically commits on success, rolls back on exception, and closes
- `conn.row_factory = sqlite3.Row` is set for dict-like access to results
- Use `cursor.lastrowid` to get inserted ID, `cursor.rowcount` to check affected rows

**User Profiles (Roles):**
- **NEVER use string literals** for profiles (e.g., "admin", "cliente")
- **ALWAYS use** `Perfil` enum from `util/perfis.py`: `Perfil.ADMIN.value`, `Perfil.CLIENTE.value`, `Perfil.VENDEDOR.value`
- `Perfil` inherits from `EnumEntidade` base class (`util/enum_base.py`)
- To add new profiles: edit only `util/perfis.py` Enum definition
- Helper methods: `Perfil.valores()`, `Perfil.nomes()`, `Perfil.existe(valor)`, `Perfil.from_valor(valor)`, `Perfil.validar(valor)`, `Perfil.obter_por_nome(nome)`, `Perfil.para_opcoes_select()`

**EnumEntidade Base Class** (`util/enum_base.py`):
- Base class for all domain enums (`Perfil`, `StatusChamado`, `PrioridadeChamado`, etc.)
- Inherits from `str, Enum` for direct string comparison
- Provides reusable methods: `valores()`, `nomes()`, `existe()`, `from_valor()`, `validar()`, `obter_por_nome()`, `para_opcoes_select()`
- When creating new domain enums, always inherit from `EnumEntidade`

**UsuarioLogado Dataclass:**
- **ALWAYS use** `UsuarioLogado` dataclass for `usuario_logado` parameter in routes
- Import from `model.usuario_logado_model`: `from model.usuario_logado_model import UsuarioLogado`
- **NEVER use dict access** like `usuario_logado["id"]` - use attribute access `usuario_logado.id`
- Immutable dataclass (`frozen=True`) with fields: `id`, `nome`, `email`, `perfil`
- Helper methods:
  - `is_admin()`: Check if user is admin
  - `is_cliente()`: Check if user is cliente
  - `is_vendedor()`: Check if user is vendedor
  - `tem_perfil(*perfis)`: Check if user has any of the given profiles
- Session serialization: stored as dict in session, reconstructed on retrieval
- Example route pattern:
  ```python
  from model.usuario_logado_model import UsuarioLogado

  @router.get("/rota")
  @requer_autenticacao()
  async def minha_rota(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
      assert usuario_logado is not None
      usuario_id = usuario_logado.id  # Correct
      if usuario_logado.is_admin():   # Correct
          ...
  ```

**Timezone e Data/Hora:**
- **NEVER use `datetime.now()` directly** - always use `agora()` from `util/datetime_util.py`
- **CRITICAL: NEVER use `.strftime()` when storing to database** - pass datetime object directly
  - WRONG: `cursor.execute("INSERT INTO table (data) VALUES (?)", (agora().strftime('%Y-%m-%d %H:%M:%S'),))`
  - CORRECT: `cursor.execute("INSERT INTO table (data) VALUES (?)", (agora(),))`
  - `.strftime()` should be used ONLY for display purposes
- System timezone configured in `.env` via `TIMEZONE` (default: `America/Sao_Paulo`)
- Import with `from util.datetime_util import agora, hoje`
- Available functions:
  - `agora()`: Returns current datetime with timezone (replaces `datetime.now()`)
  - `hoje()`: Returns current date in timezone (replaces `date.today()`)
  - `converter_para_timezone(dt, tz)`: Convert datetime between timezones
  - `datetime_para_string_iso(dt)`: Convert to ISO 8601 string
  - `string_iso_para_datetime(iso_string)`: Parse ISO 8601 string

**How Timezone Works (Database Storage):**
- **Storage Strategy**: Datetime values are stored in the database as **UTC naive** (without timezone offset)
  - Example in DB: `2025-10-28 00:40:35.685153` (no -03:00 suffix)
  - This is the standard approach used by Django, Rails, and other frameworks
- **Write Process** (`adapt_datetime` in `util/db_util.py`):
  1. Receives datetime object with timezone from Python code
  2. Converts to UTC
  3. Removes timezone info (stores as "naive")
  4. Format: `YYYY-MM-DD HH:MM:SS.mmmmmm`
- **Read Process** (`convert_datetime` in `util/db_util.py`):
  1. Reads naive UTC datetime from database
  2. Adds UTC timezone
  3. Converts to application timezone (America/Sao_Paulo)
  4. Returns timezone-aware datetime to Python code
- **Result**: Application code ALWAYS works with timezone-aware datetime objects, but database stores simple UTC values
- **Benefits**: Simple database format, easy timezone changes, compatible with external SQLite tools
- SQLite TIMESTAMP columns are automatically converted when annotated with `[timestamp]` syntax
- Templates use filters `formatar_data`, `formatar_data_hora`, `formatar_data_as_hora`, `formatar_hora` for display

**Flash Messages:**
- Use `informar_sucesso(request, "message")` and `informar_erro(request, "message")` from `util/flash_messages.py`
- Messages are automatically displayed in templates via base template
- Also available: `informar_aviso()` and `informar_info()`

**Logging:**
- Logger is pre-configured in `util/logger_config.py` with daily rotation
- Import with `from util.logger_config import logger`
- Use `logger.info()`, `logger.warning()`, `logger.error()`, `logger.debug()`
- Log files are created with date in the name from the start: `logs/app.YYYY.MM.DD.log` (e.g., `logs/app.2025.10.16.log`)
- Each day gets its own log file automatically at midnight
- Retention period configurable via `LOG_RETENTION_DAYS` (default: 30 days)
- Old logs are automatically deleted after retention period

**Exception Handling:**
- Centralized exception handlers in `util/exception_handlers.py`
- Four handlers registered in `main.py`:
  1. `http_exception_handler`: HTTP exceptions (401, 403, 404, 500)
  2. `validation_exception_handler`: Pydantic RequestValidationError (422)
  3. `form_validation_exception_handler`: Custom `ErroValidacaoFormulario`
  4. `generic_exception_handler`: All uncaught exceptions
- Custom error pages: `templates/errors/404.html`, `templates/errors/429.html`, `templates/errors/500.html`
- Development mode (`RUNNING_MODE=Development`) shows detailed error info
- Production mode shows user-friendly messages and logs details
- Use `IS_DEVELOPMENT` from `util/config` to check current mode

**Form Validation Errors (ErroValidacaoFormulario):**
- **ALWAYS use** `ErroValidacaoFormulario` for DTO validation errors in routes that render templates
- This exception centralizes error handling and eliminates code duplication
- Import from `util.exceptions`: `from util.exceptions import ErroValidacaoFormulario`
- Pattern for routes with form validation:
  ```python
  from util.exceptions import ErroValidacaoFormulario

  @router.post("/cadastrar")
  async def post_cadastrar(request: Request, campo: str = Form()):
      # Armazena dados do formulario
      dados_formulario = {"campo": campo}

      try:
          dto = AlgumaDTO(campo=campo)
          # logica de negocio...
      except ValidationError as e:
          raise ErroValidacaoFormulario(
              validation_error=e,
              template_path="pasta/template.html",  # Caminho relativo a templates/
              dados_formulario=dados_formulario,    # Dados para reexibir
              campo_padrao="campo",                 # Para erros de @model_validator
              mensagem_flash="Mensagem customizada" # Opcional
          )
  ```
- The global handler (`form_validation_exception_handler`) automatically:
  - Processes validation errors using `processar_erros_validacao()`
  - Displays flash message to user
  - Renders template with `dados` and `erros` in context
  - Logs the validation error for debugging
- For templates that need extra context (like select options), add to `dados_formulario`:
  ```python
  dados_formulario["perfis"] = Perfil.valores()  # For select dropdowns
  dados_formulario["usuario"] = usuario          # For displaying user info
  ```

**CSRF Protection:**
- Implemented via `MiddlewareProtecaoCSRF` middleware in `util/csrf_protection.py`
- Session-based token generation and validation
- Protected methods: POST, PUT, PATCH, DELETE
- Exempt paths: `/health`, `/api/`
- Constant-time token comparison to prevent timing attacks
- Template usage: `{{ csrf_input(request) }}` generates hidden input field
- Token functions: `gerar_token_csrf()`, `obter_token_csrf(request)`, `validar_token_csrf(request, token)`

**Rate Limiting:**
- Two rate limiter classes in `util/rate_limiter.py`:
  - `RateLimiter`: Static (values fixed at initialization)
  - `DynamicRateLimiter`: **Recommended** - Reads values from `config_cache` on each check, no server restart needed
- Decorator `@com_rate_limit(limiter, mensagem_erro)` in `util/rate_limiter.py` - Raises HTTPException 429
- Decorator `@aplicar_rate_limit(limiter, mensagem_erro, redirect_url)` in `util/rate_limit_decorator.py` - Redirects or returns JSON
- Helper: `obter_identificador_cliente(request)` extracts client IP (supports X-Forwarded-For, X-Real-IP)
- Global registry: `RegistroLimiters` for monitoring all limiters

**Permission Helpers** (`util/permission_helpers.py`):
- `verificar_propriedade(entity, usuario_id, request)`: Check if user owns an entity
- `verificar_propriedade_ou_admin(entity, usuario_logado, request)`: Check ownership OR admin
- `verificar_perfil(usuario_perfil, perfis_permitidos, request)`: Check profile-based access
- `verificar_multiplas_condicoes(condicoes, request, operador="AND")`: Complex permission logic

**Repository Helpers** (`util/repository_helpers.py`):
- `obter_ou_404(entity, request, mensagem, redirect_url)`: Returns entity or RedirectResponse if None
- `obter_lista_ou_vazia(lista, request)`: Guarantees list (never None)
- `validar_inteiro_positivo(valor, request, nome_campo)`: Validates positive integer (for IDs)
- `executar_operacao_repo(operacao, request, mensagem_erro)`: Wraps repo operations with error handling

**Validation Helpers** (`util/validation_helpers.py`):
- `verificar_email_disponivel(email, usuario_id_atual)`: Check email availability (returns tuple)
- `email_existe(email)`: Simple email existence check (returns bool)

**PRG Pattern (Post-Redirect-Get):**
- After POST operations, always return `RedirectResponse(url, status_code=status.HTTP_303_SEE_OTHER)`
- This prevents duplicate submissions on browser refresh

## DTO Validation System

**Reusable Validators** (`dtos/validators.py`):
- Import validators: `from dtos.validators import validar_email, validar_senha_forte, validar_cpf, etc.`
- Use with `field_validator` decorator in Pydantic models
- Available validators:
  - **Text**: `validar_string_obrigatoria()`, `validar_comprimento()`, `validar_texto_minimo_palavras()`, `validar_nome_pessoa()`
  - **Email**: `validar_email()`
  - **Password**: `validar_senha_forte()`, `validar_senhas_coincidem()`
  - **Brazilian**: `validar_cpf()`, `validar_cnpj()`, `validar_telefone_br()`, `validar_cep()`
  - **Dates**: `validar_data()`, `validar_data_futura()`, `validar_data_passada()`
  - **Numbers**: `validar_inteiro_positivo()`, `validar_decimal_positivo()`
  - **Files**: `validar_extensao_arquivo()`, `validar_tamanho_arquivo()`
  - **Enums**: `validar_tipo()` (validates against `EnumEntidade` subclasses)

**Example Usage:**
```python
from pydantic import BaseModel, field_validator
from dtos.validators import validar_email, validar_senha_forte

class UsuarioDTO(BaseModel):
    email: str
    senha: str

    _validar_email = field_validator('email')(validar_email())
    _validar_senha = field_validator('senha')(validar_senha_forte())
```

## Profile Photo System

**Photo Management** (`util/foto_util.py`):
- User photos stored in `static/img/usuarios/` with format `{id:06d}.jpg`
- Automatic photo creation on user registration (copies from `static/img/user.jpg`)
- Functions available:
  - `obter_caminho_foto_usuario(id)`: Get photo URL for templates
  - `obter_path_absoluto_foto(id)`: Get absolute filesystem path
  - `criar_foto_padrao_usuario(id)`: Create default photo for new user
  - `salvar_foto_cropada_usuario(id, base64_data)`: Save cropped photo from frontend
  - `foto_existe(id)`: Check if user photo exists
  - `obter_tamanho_foto(id)`: Get photo file size

**Frontend Integration:**
- JavaScript module: `static/js/cortador-imagem.js` (uses Cropper.js)
- Handler: `static/js/manipulador-foto-perfil.js`
- Modal component: `templates/components/modal_corte_imagem.html`
- Images automatically resized to `FOTO_PERFIL_TAMANHO_MAX` (default: 256px)
- Supports drag & drop, file selection, and crop with preview

## Support Ticket System (Chamados)

Complete support ticket system for user-admin communication:

**Models** (`model/chamado_model.py`, `model/chamado_interacao_model.py`):
- `Chamado`: Support ticket with title, status, priority, user ownership
- `ChamadoInteracao`: Ticket response/interaction messages
- `StatusChamado` enum: `Aberto`, `Em Analise`, `Resolvido`, `Fechado`
- `PrioridadeChamado` enum: `Baixa`, `Media`, `Alta`, `Urgente`

**User Routes** (`routes/chamados_routes.py`, prefix: `/chamados`):
- Users can create, view, respond to, and delete their own tickets
- Ownership verification via `verificar_propriedade()`

**Admin Routes** (`routes/admin_chamados_routes.py`, prefix: `/admin/chamados`):
- Admins can list all tickets, respond, and change status
- Admin-only access via `@requer_autenticacao([Perfil.ADMIN.value])`

## Real-Time Chat System

Private 1-to-1 messaging system using Server-Sent Events (SSE):

**Models** (`model/chat_sala_model.py`, `model/chat_participante_model.py`, `model/chat_mensagem_model.py`):
- `ChatSala`: Chat room (private, identified by `menor_id_maior_id` format)
- `ChatParticipante`: Room participant
- `ChatMensagem`: Individual message

**Chat Manager** (`util/chat_manager.py`):
- `GerenciadorChat` class manages SSE connections
- Singleton instance: `gerenciador_chat`
- Methods: `conectar()`, `desconectar()`, `broadcast_para_sala()`, `esta_conectado()`, `obter_estatisticas()`

**Routes** (`routes/chat_routes.py`, prefix: `/chat`):
- `GET /chat/stream`: SSE event stream
- `GET /chat/salas`: List chat rooms
- `POST /chat/salas`: Create chat room
- `POST /chat/enviar`: Send message
- `GET /chat/buscar-usuarios`: Search users for new conversations
- `GET /chat/conversas`: List conversations

**Frontend**:
- Widget: `templates/components/chat_widget.html`
- JavaScript: `static/js/widget-chat.js`
- CSS: `static/css/widget-chat.css`

## Database Backup System

**Backup Utilities** (`util/backup_util.py`):
- `criar_backup(automatico=False)`: Create database backup
- `listar_backups()`: List all available backups (returns `BackupInfo` objects)
- `restaurar_backup(nome_arquivo)`: Restore from backup with integrity validation and automatic rollback
- `excluir_backup(nome_arquivo)`: Delete a backup file
- `obter_info_backup(nome_arquivo)`: Get backup details
- Path traversal protection and filename validation
- Automatic pre-restore safety backup

**Admin Routes** (`routes/admin_backups_routes.py`, prefix: `/admin/backups`):
- Create, list, download, restore, and delete backups
- Admin-only access

## Templates and Frontend

### Template Structure

**Base Templates:**
- `base_publica.html`: Base for public pages (marketing, landing pages)
- `base_privada.html`: Base for authenticated user pages

**Public Pages:**
- `index.html`: Landing page
- `sobre.html`: About page
- `dashboard.html`: Authenticated user dashboard

**Error Pages:**
- `errors/404.html`: Not found error page
- `errors/429.html`: Rate limit exceeded error page
- `errors/500.html`: Server error page

**Auth Pages:**
- `auth/login.html`, `auth/cadastro.html`, `auth/esqueci_senha.html`, `auth/redefinir_senha.html`

**User Profile Pages:**
- `perfil/visualizar.html`, `perfil/editar.html`, `perfil/alterar-senha.html`

**Support Ticket Pages:**
- `chamados/listar.html`, `chamados/cadastrar.html`, `chamados/visualizar.html`

**Admin Pages:**
- `admin/usuarios/listar.html`, `admin/usuarios/cadastro.html`, `admin/usuarios/editar.html`: User management
- `admin/configuracoes/listar.html`: System configuration (4 tabs)
- `admin/backups/listar.html`: Database backup management
- `admin/chamados/listar.html`, `admin/chamados/responder.html`: Ticket management
- `admin/tema.html`: Theme selector
- `admin/auditoria.html`: Log viewer

**Components** (Reusable UI components - use `{% include %}`):
- `components/modal_confirmacao.html`: Confirmation modal for delete operations
  - Use `abrirModalConfirmacao({url, mensagem, detalhes})` function
  - Automatically displays confirmation dialog with optional details
- `components/modal_alerta.html`: Alert modal for messages (replaces alert())
  - Use: `window.App.Modal.show(mensagem, tipo, titulo, detalhes)`
  - Shortcuts: `window.App.Modal.showError()`, `window.App.Modal.showWarning()`, `window.App.Modal.showInfo()`, `window.App.Modal.showSuccess()`
  - Types: 'danger', 'warning', 'info', 'success'
- `components/modal_corte_imagem.html`: Image crop modal with Cropper.js
- `components/galeria_fotos.html`: Photo gallery macro with thumbnails
  - Use macro: `{% from 'components/galeria_fotos.html' import galeria_fotos %}`
  - Call with: `{{ galeria_fotos(images, gallery_id='myGallery') }}`
- `components/chat_widget.html`: Real-time chat interface widget
- `components/navbar_user_dropdown.html`: User menu dropdown in navbar
- `components/indicador_senha.html`: Password strength indicator
- `components/alerta_erro.html`: Error display component
- `components/rate_limit_field.html`: Rate limit config fields (paired max/minutos with live preview)

**Macros** (Reusable template functions - use `{% from ... import ... %}`):
- `macros/form_fields.html`: Complete form field macro library
  - `input_text()`, `input_email()`, `input_password()`, `input_date()`, `input_decimal()`
  - `textarea()`, `select()`, `checkbox()`, `radio()`
  - All macros support: label, help text, error messages, Bootstrap styling
- `macros/action_buttons.html`: Action button macros (edit, delete, view, etc.)
- `macros/badges.html`: Badge/status indicator macros
- `macros/empty_states.html`: Empty state display macros

### Example Pages

Complete working examples at `/exemplos`:

- **`exemplos/index.html`**: Examples gallery homepage
- **`exemplos/demo_campos_formulario.html`**: Form fields macro demonstration
- **`exemplos/grade_cartoes.html`**: Responsive card grid
- **`exemplos/lista_tabela.html`**: Data table with actions
- **`exemplos/bootswatch.html`**: Theme selector with 28+ themes
- **`exemplos/detalhes_produto.html`**: E-commerce product page
- **`exemplos/detalhes_servico.html`**: Professional service page
- **`exemplos/detalhes_perfil.html`**: User profile page
- **`exemplos/detalhes_imovel.html`**: Real estate property page

### JavaScript Modules

All JavaScript modules are fully documented and production-ready:

**`static/js/toasts.js`** - Toast Notification System:
- Automatic display of flash messages from backend
- Bootstrap 5 toast components
- Functions: `window.App.Toasts.show(mensagem, tipo)`
- Types: `success`, `danger`, `warning`, `info`
- Auto-dismiss after configurable delay

**`static/js/modal-alerta.js`** - Modal Alert System (replaces alert()):
- Modern replacement for JavaScript `alert()` and `confirm()`
- Functions:
  - `window.App.Modal.show(mensagem, tipo, titulo, detalhes)`: Main function
  - `window.App.Modal.showError()`, `window.App.Modal.showWarning()`, `window.App.Modal.showInfo()`, `window.App.Modal.showSuccess()`
- **NEVER use native `alert()`, `confirm()` or `prompt()` - always use modals**

**`static/js/mascara-input.js`** - Input Masking System:
- **InputMask Class**: Pattern-based input masking
  - Pattern syntax: `0` = digit, `A` = uppercase letter, `a` = lowercase letter, any other = literal
  - Pre-defined masks in `InputMask.MASKS`: CPF, CNPJ, TELEFONE, TELEFONE_FIXO, CEP, DATA, HORA, DATA_HORA, PLACA_ANTIGA, PLACA_MERCOSUL, CARTAO, CVV, CVV4, VALIDADE_CARTAO
  - Usage: `<input data-mask="CPF" data-unmask="true">`
- **DecimalMask Class**: Decimal/monetary value formatting (Brazilian format)
  - Usage: `<input data-decimal data-decimal-places="2" data-decimal-prefix="R$ ">`
  - Static methods: `DecimalMask.format(value, options)`, `DecimalMask.parse(value, options)`

**`static/js/validador-senha.js`** - Password Strength Feedback (Visual Only):
- **IMPORTANT**: Provides ONLY visual feedback, does NOT validate or block form submission
- Visual strength indicator with progress bar
- Color-coded strength levels (weak, medium, strong)
- **Validation is done server-side via Pydantic DTOs**

**`static/js/cortador-imagem.js`** - Image Crop System:
- Powered by Cropper.js library
- Features: drag & drop, file selection, interactive crop, zoom, rotate, aspect ratio lock (1:1)
- Returns base64 encoded cropped image

**`static/js/manipulador-foto-perfil.js`** - Profile Photo Handler:
- Integration between image cropper and profile photo system
- Handles photo upload flow, AJAX save, success/error feedback

**`static/js/auxiliares-exclusao.js`** - Delete Confirmation Helpers:
- Helper functions for delete operations with modal confirmation

**`static/js/widget-chat.js`** - Chat Widget:
- SSE connection management and real-time message display
- Chat room navigation and message sending

### CSS Assets

**Bootstrap 5.3.8:**
- `static/css/bootstrap.min.css`: Core Bootstrap framework (local copy)

**Bootswatch Themes** (`static/css/bootswatch/`):
- Complete collection of 28+ free Bootstrap themes
- Preview at `/exemplos/bootswatch`

**Custom Styles:**
- `static/css/custom.css`: Project-specific custom styles
- `static/css/widget-chat.css`: Chat widget styles

## Creating a New CRUD

Follow this exact sequence (detailed guide in `docs/CRIAR_CRUD.md`):

1. **Model** (`model/entidade_model.py`): Create dataclass with type hints. Use `EnumEntidade` for status/type enums.
2. **SQL** (`sql/entidade_sql.py`): Define SQL queries as constants (CRIAR_TABELA, INSERIR, OBTER_TODOS, OBTER_POR_ID, ATUALIZAR, EXCLUIR)
3. **Repository** (`repo/entidade_repo.py`): Implement CRUD functions, include `_row_to_entidade()` converter
4. **DTOs** (`dtos/entidade_dto.py`):
   - Create Pydantic models for validation (CriarDTO and AlterarDTO)
   - Use validators from `dtos/validators.py` when possible
5. **Routes** (`routes/entidade_routes.py`):
   - Create APIRouter with prefix
   - Implement GET/POST pairs: listar, cadastrar, alterar, excluir
   - Use `@requer_autenticacao()` decorator
   - Use `ErroValidacaoFormulario` for validation errors
   - Use `DynamicRateLimiter` for rate limiting
   - Use permission helpers for ownership checks
6. **Templates** (`templates/entidade/`):
   - Create listar.html, cadastrar.html, alterar.html, excluir.html
   - Use form field macros from `macros/form_fields.html`
   - Use `components/modal_confirmacao.html` for delete operations
   - Include `{{ csrf_input(request) }}` in all forms
7. **Register in main.py**:
   - Import repository
   - Add to `TABELAS` list for table creation
   - Import and add router to `ROUTERS` list

## Configuration

**Environment Variables (.env):**
- `DATABASE_PATH`: SQLite database file path (default: database.db)
- `APP_NAME`: Application name shown in UI and logs
- `SECRET_KEY`: Session secret (MUST change in production, min 32 chars)
- `HOST`, `PORT`: Server configuration (default: 0.0.0.0:8400)
- `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, `RESEND_FROM_NAME`: Email service (Resend.com)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `LOG_RETENTION_DAYS`: Number of days to keep log files (default: 30)
- `BASE_URL`: Application base URL for emails
- `FOTO_PERFIL_TAMANHO_MAX`: Max photo size in pixels (default: 256)
- `FOTO_MAX_UPLOAD_BYTES`: Max upload file size (default: 5MB)
- `RUNNING_MODE`: Development or Production (affects error display)
- `TIMEZONE`: Application timezone (default: America/Sao_Paulo)
- `VERSION`: Application version (default: 1.0.0)
- `PASSWORD_MIN_LENGTH`, `PASSWORD_MAX_LENGTH`: Password constraints
- `TOAST_AUTO_HIDE_DELAY_MS`: Toast auto-dismiss delay (default: 5000ms)

All configuration is loaded via `util/config.py` using python-dotenv.

**Hybrid Configuration System:**
- Configuration cascade: Database (if exists) -> .env file -> Hardcoded default
- Runtime-editable configs stored in `configuracao` table
- Managed via admin interface at `/admin/configuracoes` with **4 organized tabs**:
  - **Frequencia de Requisicoes**: All rate limiting configs grouped
  - **Interface**: UI configs (toast delay, etc)
  - **Aplicacao**: App name, email settings
  - **Fotos**: Photo upload and size configs
- Cached for performance using `util/config_cache.py` (`ConfigCache` class)
  - Thread-safe with `threading.RLock()`
  - Methods: `obter()`, `obter_int()`, `obter_bool()`, `obter_float()`, `obter_multiplos()`, `limpar()`, `limpar_chave()`
- **Rate limiters are DYNAMIC**: Changes apply immediately without server restart via `DynamicRateLimiter`
- Config migration: `util/migrar_config.py` migrates .env values to database on startup

## Seed Data

- Seed data files in JSON format in `data/` directory
- Loaded automatically on startup via `util/seed_data.py`
- Default users created from `data/usuarios_seed.json`:
  - admin@sistema.com / Admin@123 (Administrador)
  - joao@email.com / Joao@123 (Cliente)
  - maria@email.com / Maria@123 (Cliente)

## Testing

**Test Structure (organized by type):**
- `tests/conftest.py`: Global fixtures
- `tests/unit/`: Unit tests (config_cache, DTOs, datetime, enums, rate limiter, validators, etc.)
- `tests/integration/`: Integration tests (chat manager, config system, CSRF, migrations)
- `tests/e2e/`: End-to-end tests (auth flows with Playwright)
- `tests/helpers/`: Test helper functions (permission, repository, validation helpers)

**Fixtures in `tests/conftest.py`:**
- `client`: TestClient with clean session per test
- `usuario_teste`, `admin_teste`: Test user data
- `cliente_autenticado`, `admin_autenticado`: Pre-authenticated clients
- `criar_usuario`, `fazer_login`: Helper functions
- Test database automatically uses temporary file

**Test markers:** `@pytest.mark.auth`, `@pytest.mark.crud`, `@pytest.mark.integration`, `@pytest.mark.unit`

## Important Files

### Core Application
- `main.py`: Application entry point, router/middleware registration, table creation, exception handlers

### Utilities
- `util/auth_decorator.py`: Authentication/authorization logic
- `util/perfis.py`: **Single source of truth** for user profiles (inherits `EnumEntidade`)
- `util/enum_base.py`: **Base class** for all domain enums (`EnumEntidade`)
- `util/db_util.py`: Database connection management
- `util/security.py`: Password hashing with bcrypt
- `util/senha_util.py`: Password strength validation
- `util/email_service.py`: Email sending via Resend.com API
- `util/template_util.py`: Template rendering helpers with auto-injected context (filters, globals, CSRF)
- `util/foto_util.py`: Profile photo management (create, save, crop)
- `util/exceptions.py`: **Custom exceptions** including `ErroValidacaoFormulario` for centralized error handling
- `util/exception_handlers.py`: **Global exception handlers** for HTTP, validation, form, and generic errors
- `util/validation_util.py`: **Error processing utilities** for DTO validation errors
- `util/csrf_protection.py`: **CSRF middleware** and token management
- `util/security_headers.py`: Security headers middleware
- `util/flash_messages.py`: Flash message helpers
- `util/logger_config.py`: Logging configuration with rotation
- `util/config.py`: Configuration loading from .env with security validation
- `util/config_cache.py`: Runtime configuration caching (thread-safe `ConfigCache`)
- `util/seed_data.py`: Automatic seed data loading
- `util/migrar_config.py`: Migration of .env configs to database
- `util/rate_limiter.py`: **Rate limiting** with `RateLimiter`, `DynamicRateLimiter`, `RegistroLimiters`, `@com_rate_limit`
- `util/rate_limit_decorator.py`: **Rate limit decorator** `@aplicar_rate_limit` with proxy-aware IP detection
- `util/permission_helpers.py`: **Permission checking** (ownership, profile, multi-condition)
- `util/repository_helpers.py`: **Repository helpers** (obter_ou_404, validation, error handling)
- `util/validation_helpers.py`: **Validation helpers** (email availability checking)
- `util/backup_util.py`: **Database backup** management (create, restore, validate, delete)
- `util/chat_manager.py`: **SSE connection manager** for real-time chat (`GerenciadorChat`)
- `util/datetime_util.py`: Timezone-aware datetime handling

### DTOs
- `dtos/validators.py`: **Reusable validation functions** for all DTOs
- `dtos/auth_dto.py`: Login, register, password reset validation
- `dtos/usuario_dto.py`: User creation/update validation
- `dtos/perfil_dto.py`: Profile validation
- `dtos/chamado_dto.py`: Support ticket validation
- `dtos/chamado_interacao_dto.py`: Ticket interaction validation
- `dtos/chat_dto.py`: Chat room and message validation
- `dtos/configuracao_dto.py`: Configuration validation

### Models
- `model/usuario_model.py`: User entity
- `model/usuario_logado_model.py`: **UsuarioLogado dataclass** (frozen, immutable)
- `model/chamado_model.py`: Support ticket with `StatusChamado` and `PrioridadeChamado` enums
- `model/chamado_interacao_model.py`: Ticket interaction
- `model/chat_sala_model.py`: Chat room
- `model/chat_participante_model.py`: Chat participant
- `model/chat_mensagem_model.py`: Chat message
- `model/configuracao_model.py`: System configuration

### SQL
- `sql/usuario_sql.py`, `sql/configuracao_sql.py`, `sql/chamado_sql.py`, `sql/chamado_interacao_sql.py`
- `sql/chat_sala_sql.py`, `sql/chat_participante_sql.py`, `sql/chat_mensagem_sql.py`
- `sql/indices_sql.py`: Database index definitions for performance optimization

### Repositories
- `repo/usuario_repo.py`, `repo/configuracao_repo.py`, `repo/chamado_repo.py`, `repo/chamado_interacao_repo.py`
- `repo/chat_sala_repo.py`, `repo/chat_participante_repo.py`, `repo/chat_mensagem_repo.py`
- `repo/indices_repo.py`: Database index management

### Routes
- `routes/auth_routes.py`: Login, register, password recovery
- `routes/usuario_routes.py`: User dashboard, profile management, photo upload, password change
- `routes/chamados_routes.py`: User support tickets (prefix: `/chamados`)
- `routes/chat_routes.py`: Real-time chat system (prefix: `/chat`)
- `routes/admin_usuarios_routes.py`: Admin user management (prefix: `/admin/usuarios`)
- `routes/admin_configuracoes_routes.py`: Admin system configuration (prefix: `/admin`)
- `routes/admin_backups_routes.py`: Admin database backups (prefix: `/admin/backups`)
- `routes/admin_chamados_routes.py`: Admin ticket management (prefix: `/admin/chamados`)
- `routes/public_routes.py`: Public pages (/, /index, /sobre)
- `routes/examples_routes.py`: Example pages showcase (prefix: `/exemplos`)

## Reusable Components Quick Reference

### Backend (Python)
- **Validators**: `from dtos.validators import validar_email, validar_cpf`
- **Form Validation Errors**: `from util.exceptions import ErroValidacaoFormulario`
- **Flash Messages**: `from util.flash_messages import informar_sucesso, informar_erro`
- **Photos**: `from util.foto_util import obter_caminho_foto_usuario`
- **Auth**: `from util.auth_decorator import requer_autenticacao`
- **Profiles**: `from util.perfis import Perfil`
- **Logged User**: `from model.usuario_logado_model import UsuarioLogado`
- **Rate Limiting**: `from util.rate_limiter import DynamicRateLimiter, com_rate_limit`
- **Permissions**: `from util.permission_helpers import verificar_propriedade, verificar_propriedade_ou_admin`
- **Repo Helpers**: `from util.repository_helpers import obter_ou_404, validar_inteiro_positivo`
- **Email Check**: `from util.validation_helpers import verificar_email_disponivel`
- **Enums**: `from util.enum_base import EnumEntidade`
- **CSRF**: `{{ csrf_input(request) }}` in templates
- **Config Cache**: `from util.config_cache import config`

### Frontend (Templates)
- **Form Fields**: `{% from 'macros/form_fields.html' import input_text %}`
- **Action Buttons**: `{% from 'macros/action_buttons.html' import ... %}`
- **Badges**: `{% from 'macros/badges.html' import ... %}`
- **Empty States**: `{% from 'macros/empty_states.html' import ... %}`
- **Rate Limit Fields**: `{% from 'components/rate_limit_field.html' import rate_limit_field %}`
- **Confirmation Modal**: `{% include 'components/modal_confirmacao.html' %}`
- **Photo Gallery**: `{% from 'components/galeria_fotos.html' import galeria_fotos %}`
- **Chat Widget**: `{% include 'components/chat_widget.html' %}`

### Frontend (JavaScript)
- **Toasts**: `window.App.Toasts.show('Mensagem', 'success')`
- **Modals**: `window.App.Modal.showError('Mensagem')`, `window.App.Modal.showWarning()`, `window.App.Modal.showInfo()`, `window.App.Modal.showSuccess()`
- **Input Masks**: `<input data-mask="CPF">`
- **Decimal Masks**: `<input data-decimal data-decimal-prefix="R$ ">`
- **Photo Cropper**: Use `modal_corte_imagem.html` component

## Common Gotchas

1. **Router Registration Order**: In `main.py`, register `public_router` and `examples_router` LAST to avoid catching all routes with "/"
2. **SQL Injection Prevention**: ALWAYS use `?` placeholders in SQL, NEVER string concatenation
3. **Boolean in SQLite**: Store as INTEGER (0/1), convert with `bool(row["campo"])` and `1 if valor else 0`
4. **Profile Constants**: Import and use `Perfil` enum from `util/perfis.py`, never hardcode strings
5. **Session Serialization**: Session data must be JSON-serializable (no complex objects)
6. **DTO Validation Errors**: **ALWAYS use** `ErroValidacaoFormulario` for form validation errors in routes. This centralizes error handling and eliminates code duplication. Example:
   ```python
   from util.exceptions import ErroValidacaoFormulario

   try:
       dto = CadastroDTO(...)
   except ValidationError as e:
       raise ErroValidacaoFormulario(
           validation_error=e,
           template_path="auth/cadastro.html",
           dados_formulario={"email": email, "nome": nome},
           campo_padrao="confirmar_senha"
       )
   ```
   **Why:** The global `form_validation_exception_handler` automatically processes errors using `processar_erros_validacao()`, displays flash messages, and renders templates with proper error context.
7. **Template Rendering**: Use `criar_templates()` from `util/template_util.py`
8. **Photo Paths**: Use `obter_caminho_foto_usuario(id)` for templates, `obter_path_absoluto_foto(id)` for filesystem
9. **Validators Import**: Always import from `dtos/validators.py`, don't reimplement common validations
10. **Development vs Production**: Check `IS_DEVELOPMENT` to conditionally show/hide debug info
11. **Client-Side Validation**: **NEVER validate forms with JavaScript alerts or prevent submission**. Use server-side validation via DTOs and display errors in fields. JavaScript should provide ONLY visual feedback.
12. **User Messages**: **NEVER use** `alert()`, `confirm()`, or `prompt()`. Always use:
    - `window.App.Modal.show()` / `window.App.Modal.showError()` / `window.App.Modal.showWarning()` / `window.App.Modal.showInfo()` for user messages
    - `abrirModalConfirmacao()` for confirmations (delete, etc.)
    - `window.App.Toasts.show()` for non-critical notifications
13. **Input Masks**: Use `data-mask` attribute for automatic initialization, or `InputMask.MASKS` constants programmatically
14. **Decimal Formatting**: DecimalMask uses Brazilian format (comma decimal, dot thousands) by default
15. **CSRF Tokens**: Always include `{{ csrf_input(request) }}` in all POST/PUT/DELETE forms
16. **Domain Enums**: Always inherit from `EnumEntidade` (from `util/enum_base.py`), never use plain `Enum`
17. **Lazy Imports**: Used in `chamado_repo` to avoid circular dependencies with `chamado_interacao_repo`

## Code Style

- Python dataclasses for models (use `@dataclass` decorator)
- Type hints everywhere (from `typing` import Optional, List, etc.)
- SQL constant names in UPPERCASE
- Docstrings for all functions (especially in repositories)
- Private functions prefixed with `_` (e.g., `_row_to_entidade`)
- Import order: stdlib -> third-party -> local (DTOs -> Models -> Repos -> Utils)
- Use reusable validators from `dtos/validators.py`
- Use form field macros from `templates/macros/form_fields.html`
- Use reusable components from `templates/components/`
- Domain enums inherit from `EnumEntidade`

## Security Notes

- Passwords hashed with bcrypt via `util/security.py`
- Password validation rules in `util/senha_util.py`
- Rate limiting applied via `DynamicRateLimiter` on all routes
- Security headers configured via `util/security_headers.py`
- SQL injection protected via prepared statements
- XSS protection via Jinja2 auto-escaping
- CSRF protection via `MiddlewareProtecaoCSRF` middleware with session-based tokens
- SECRET_KEY validated on startup (minimum 32 chars in production)
- User photos stored with predictable names (consider adding access control in production)
- Path traversal protection in backup system

## Health Check

The application includes a health check endpoint at `/health` that returns:
```json
{"status": "healthy"}
```

Use this for monitoring, load balancers, or container orchestration.

## Learning Resources

Browse working examples at `/exemplos` to see:
- Complete form implementations
- Responsive layouts
- Data tables with actions
- Detail pages for different entities
- Theme customization
- All reusable components in action

Each example page includes code snippets and implementation notes.

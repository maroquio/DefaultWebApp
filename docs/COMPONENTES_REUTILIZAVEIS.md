# Componentes Reutilizáveis - DefaultWebApp

Este documento cataloga todos os componentes reutilizáveis disponíveis no projeto, incluindo macros de templates, componentes, helpers backend e módulos JavaScript.

## 📋 Índice

1. [Macros de Template](#macros-de-template)
   - [Form Fields](#form-fields)
   - [Badges](#badges)
   - [Action Buttons](#action-buttons)
   - [Empty States](#empty-states)
2. [Componentes de Template](#componentes-de-template)
   - [Rate Limit Field](#rate-limit-field)
   - [Modal Alerta](#modal-alerta)
   - [Modal Confirmação](#modal-confirmação)
   - [Modal Corte Imagem](#modal-corte-imagem)
   - [Indicador de Senha](#indicador-de-senha)
   - [Galeria de Fotos](#galeria-de-fotos)
   - [Navbar User Dropdown](#navbar-user-dropdown)
   - [Chat Widget](#chat-widget)
3. [Helpers Backend](#helpers-backend)
   - [Rate Limiting](#rate-limiting)
   - [Repository Helpers](#repository-helpers)
   - [Permission Helpers](#permission-helpers)
   - [Validation Util](#validation-util)
   - [Validation Helpers](#validation-helpers)
   - [DTO Validators](#dto-validators)
4. [Módulos JavaScript](#módulos-javascript)
   - [Toasts](#toasts)
   - [Modal Alerta JS](#modal-alerta-js)
   - [Input Mask](#input-mask)
   - [Password Validator](#password-validator)
   - [Image Cropper](#image-cropper)
   - [Perfil Photo Handler](#perfil-photo-handler)
   - [Chat Widget JS](#chat-widget-js)
   - [Delete Helpers](#delete-helpers)

---

## Macros de Template

### Form Fields

**Arquivo:** `templates/macros/form_fields.html`

Macro universal para criar campos de formulário com Bootstrap 5 e validação integrada.

#### Importação

```jinja2
{% from 'macros/form_fields.html' import field %}
```

#### Macro Principal: `field()`

Macro universal que renderiza diferentes tipos de campos de formulário com validação, máscaras e eventos.

**Parâmetros principais:**
- `name` (str): Nome do campo
- `label` (str): Label do campo
- `type` (str): Tipo do campo (text, email, password, textarea, select, radio, checkbox, decimal, date, etc.)
- `value` (any): Valor inicial
- `placeholder` (str): Placeholder
- `required` (bool): Campo obrigatório
- `disabled` (bool): Campo desabilitado
- `readonly` (bool): Campo somente leitura
- `options` (dict): Opções para select/radio
- `help_text` (str): Texto de ajuda
- `class_extra` (str): Classes CSS adicionais
- `wrapper_class` (str): Classes CSS para o wrapper

**Parâmetros de máscara:**
- `mask` (str): Máscara de entrada (ex: 'CPF', '000.000.000-00')
- `unmask` (bool): Remover máscara ao enviar

**Parâmetros de campo decimal:**
- `decimal_places` (int): Casas decimais (padrão: 2)
- `show_thousands` (bool): Separador de milhares (padrão: true)
- `allow_negative` (bool): Permitir negativos
- `decimal_prefix` (str): Prefixo (ex: 'R$ ')
- `decimal_suffix` (str): Sufixo (ex: ' kg')

**Parâmetros de eventos JavaScript:**
- `oninput`, `onchange`, `onblur`, `onfocus`, `onkeyup`, `onkeydown`, `onpaste`

**Parâmetros de radio:**
- `radio_style` (str): 'default' ou 'buttons' (botões estilizados)
- `radio_layout` (str): 'vertical' ou 'horizontal'
- `radio_icons` (dict): Ícones Bootstrap Icons para cada opção

**Parâmetros de checkbox:**
- `checkbox_style` (str): 'default' ou 'switch'

**Parâmetros de input com botão:**
- `append_icon` (str): Ícone Bootstrap Icons
- `append_button_onclick` (str): JavaScript ao clicar no botão

#### Exemplos de Uso

**Campo de texto simples:**
```jinja2
{{ field(name='nome', label='Nome completo', type='text', required=true) }}
```

**Campo de email:**
```jinja2
{{ field(name='email', label='E-mail', type='email', required=true) }}
```

**Campo de senha com toggle de visibilidade:**
```jinja2
{{ field(
    name='senha',
    label='Senha',
    type='password',
    append_icon='bi-eye',
    append_button_onclick='togglePassword(this)'
) }}
```

**Textarea:**
```jinja2
{{ field(
    name='descricao',
    label='Descrição',
    type='textarea',
    rows=5,
    help_text='Máximo de 500 caracteres'
) }}
```

**Select:**
```jinja2
{{ field(
    name='perfil',
    label='Perfil',
    type='select',
    options={'admin': 'Administrador', 'cliente': 'Cliente', 'vendedor': 'Vendedor'},
    required=true
) }}
```

**Radio buttons (estilo padrão):**
```jinja2
{{ field(
    name='prioridade',
    label='Prioridade',
    type='radio',
    options={'urgente': 'Urgente', 'alta': 'Alta', 'media': 'Média', 'baixa': 'Baixa'},
    radio_layout='horizontal'
) }}
```

**Radio buttons (estilo botões com ícones):**
```jinja2
{{ field(
    name='tipo_pagamento',
    label='Forma de Pagamento',
    type='radio',
    options={'cartao': 'Cartão', 'boleto': 'Boleto', 'pix': 'PIX'},
    radio_style='buttons',
    radio_icons={'cartao': 'bi-credit-card', 'boleto': 'bi-upc', 'pix': 'bi-phone'}
) }}
```

**Checkbox (switch):**
```jinja2
{{ field(
    name='ativo',
    label='Usuário ativo',
    type='checkbox',
    checkbox_style='switch'
) }}
```

**Campo com máscara de CPF:**
```jinja2
{{ field(
    name='cpf',
    label='CPF',
    type='text',
    mask='CPF',
    unmask=true
) }}
```

**Campo decimal (moeda):**
```jinja2
{{ field(
    name='preco',
    label='Preço',
    type='decimal',
    decimal_prefix='R$ ',
    decimal_places=2,
    show_thousands=true
) }}
```

**Campo de data:**
```jinja2
{{ field(
    name='data_nascimento',
    label='Data de Nascimento',
    type='date',
    required=true
) }}
```

#### Integração com Validação

O macro `field()` automaticamente:
- Exibe erros de validação do dicionário `erros` (se existir no contexto)
- Recupera valores do dicionário `dados` (se existir no contexto)
- Adiciona classe `is-invalid` quando há erro
- Renderiza mensagem de erro abaixo do campo

**Exemplo completo com validação:**
```jinja2
{# No template #}
{{ field(
    name='email',
    label='E-mail',
    type='email',
    required=true
) }}

{# Na rota (backend) #}
try:
    dto = CadastroDTO(email=email)
except ValidationError as e:
    raise FormValidationError(
        validation_error=e,
        template_path="cadastro.html",
        dados_formulario={"email": email},
        campo_padrao="email"
    )
```

---

### Badges

**Arquivo:** `templates/macros/badges.html`

Macros para renderizar badges com cores e estilos consistentes.

#### Importação

```jinja2
{% from 'macros/badges.html' import badge_status_chamado, badge_prioridade, badge_perfil, badge_mensagens_nao_lidas, badge, badge_booleano %}
```

#### Macros Disponíveis

##### `badge_status_chamado(status)`
Badge para status de chamados.

**Cores:**
- Aberto → `bg-primary` (azul)
- Em Análise → `bg-info` (ciano)
- Resolvido → `bg-success` (verde)
- Fechado → `bg-secondary` (cinza)

```jinja2
{{ badge_status_chamado(chamado.status) }}
```

##### `badge_prioridade(prioridade)`
Badge para prioridades.

**Cores:**
- Urgente → `bg-danger` (vermelho)
- Alta → `bg-warning` (amarelo)
- Média → `bg-info` (ciano)
- Baixa → `bg-secondary` (cinza)

```jinja2
{{ badge_prioridade(chamado.prioridade) }}
```

##### `badge_perfil(perfil)`
Badge para perfis de usuário.

**Cores:**
- Administrador → `bg-danger` (vermelho)
- Vendedor → `bg-warning` (amarelo)
- Cliente → `bg-info` (ciano)

```jinja2
{{ badge_perfil(usuario.perfil) }}
```

##### `badge_mensagens_nao_lidas(count)`
Badge para contador de mensagens não lidas (exibe apenas se count > 0).

```jinja2
{{ badge_mensagens_nao_lidas(chamado.mensagens_nao_lidas) }}
```

##### `badge(texto, cor='secondary', icon=none)`
Badge genérico customizável.

```jinja2
{{ badge('Novo', 'success', 'star-fill') }}
{{ badge('Pendente', 'warning') }}
```

##### `badge_booleano(valor, texto_true='Sim', texto_false='Não', cor_true='success', cor_false='secondary')`
Badge para valores booleanos.

```jinja2
{{ badge_booleano(usuario.ativo, 'Ativo', 'Inativo') }}
```

---

### Action Buttons

**Arquivo:** `templates/macros/action_buttons.html`

Macros para renderizar botões de ação com estilos e acessibilidade consistentes.

#### Importação

```jinja2
{% from 'macros/action_buttons.html' import btn_icon, btn_group_crud, btn_text, btn_voltar %}
```

#### Macros Disponíveis

##### `btn_group_crud(entity_id, entity_name, base_url, delete_function='', show_view=false, show_edit=true, show_delete=true, extra_buttons='', size='sm')`

Grupo de botões CRUD padrão.

**Exemplo básico:**
```jinja2
{{ btn_group_crud(
    usuario.id,
    'usuário ' ~ usuario.nome,
    '/admin/usuarios',
    "excluirUsuario(%d, '%s', '%s', '%s')"|format(
        usuario.id,
        usuario.nome|replace("'", "\\'"),
        usuario.email,
        usuario.perfil
    )
) }}
```

**Com botões extras:**
```jinja2
{{ btn_group_crud(
    chamado.id,
    'chamado #' ~ chamado.id,
    '/chamados',
    "excluirChamado(%d)"|format(chamado.id),
    extra_buttons=btn_icon('/chamados/' ~ chamado.id ~ '/mensagens', 'chat', 'info', 'Mensagens')
) }}
```

##### `btn_icon(url, icon, variant='primary', title='', aria_label='', size='sm', onclick='', extra_classes='')`

Botão com ícone (link ou button).

```jinja2
{{ btn_icon('/tarefas/editar/1', 'pencil', 'primary', 'Editar', size='md') }}
{{ btn_icon('#', 'trash', 'danger', 'Excluir', onclick='excluir(1)') }}
```

##### `btn_text(url, texto, icon='', variant='primary', size='md', onclick='', extra_classes='')`

Botão com texto e ícone opcional.

```jinja2
{{ btn_text('/tarefas/cadastrar', 'Nova Tarefa', 'plus-circle', 'success') }}
```

##### `btn_voltar(url, texto='Voltar', variant='secondary', size='md')`

Botão de voltar/cancelar padronizado.

```jinja2
{{ btn_voltar('/tarefas/listar') }}
{{ btn_voltar('/admin/usuarios/listar', 'Cancelar') }}
```

---

### Empty States

**Arquivo:** `templates/macros/empty_states.html`

Macros para renderizar mensagens de estado vazio.

#### Importação

```jinja2
{% from 'macros/empty_states.html' import empty_state, empty_search_result, empty_filtered_result, empty_permission_denied %}
```

#### Macros Disponíveis

##### `empty_state(title, message, action_url='', action_text='', icon='info-circle', variant='info', show_icon=true)`

Estado vazio genérico.

```jinja2
{{ empty_state(
    'Nenhuma tarefa cadastrada',
    'Você ainda não possui tarefas. Clique no botão abaixo para começar!',
    action_url='/tarefas/cadastrar',
    action_text='Cadastrar Primeira Tarefa',
    icon='clipboard-x'
) }}
```

##### `empty_search_result(search_term='', back_url='')`

Estado vazio para resultados de busca.

```jinja2
{{ empty_search_result('Python', '/tarefas/listar') }}
```

##### `empty_filtered_result(filter_description='', clear_url='')`

Estado vazio para listagens filtradas.

```jinja2
{{ empty_filtered_result('Status: Aberto', '/chamados/listar') }}
```

##### `empty_permission_denied(message='', back_url='')`

Estado para acesso negado.

```jinja2
{{ empty_permission_denied('Você não tem permissão para visualizar estes dados.', '/home') }}
```

---

## Componentes de Template

### Rate Limit Field

**Arquivo:** `templates/components/rate_limit_field.html`

Componente para renderizar campos de configuração de rate limit com preview em tempo real.

#### Importação

```jinja2
{% from 'components/rate_limit_field.html' import rate_limit_field %}
```

#### Uso

```jinja2
{{ rate_limit_field(
    prefixo='rate_limit_login',
    label='Login',
    max_atual=5,
    minutos_atuais=5,
    max_recomendado=5,
    minutos_recomendados=5,
    descricao='Limite de tentativas de login por IP',
    erros=erros
) }}
```

**Funcionalidades:**
- Renderiza par de campos (max requisições + minutos)
- Preview dinâmico do limite configurado
- Valores recomendados com tooltip
- Integração com erros de validação
- Atualização em tempo real ao digitar

---

### Modal Alerta

**Arquivo:** `templates/components/modal_alerta.html`

Modal genérico para exibir alertas (substitui `alert()` nativo).

#### Uso

```jinja2
{% include 'components/modal_alerta.html' %}
```

**JavaScript (veja seção [Modal Alerta JS](#modal-alerta-js)):**
```javascript
exibirModalAlerta('Mensagem', 'danger', 'Título');
exibirErro('Arquivo muito grande!');
exibirAviso('Tem certeza?');
exibirInfo('Operação concluída');
exibirSucesso('Salvo com sucesso!');
```

---

### Modal Confirmação

**Arquivo:** `templates/components/modal_confirmacao.html`

Modal para confirmação de ações destrutivas (como exclusões).

#### Uso

```jinja2
{% include 'components/modal_confirmacao.html' %}
```

**JavaScript:**
```javascript
abrirModalConfirmacao({
    url: '/usuarios/excluir/1',
    mensagem: 'Deseja excluir este usuário?',
    detalhes: {'Nome': 'João Silva', 'Email': 'joao@email.com'}
});
```

---

### Modal Corte Imagem

**Arquivo:** `templates/components/modal_corte_imagem.html`

Modal com Cropper.js para corte de imagens (fotos de perfil).

#### Uso

```jinja2
{% include 'components/modal_corte_imagem.html' %}
```

**JavaScript (veja seção [Image Cropper](#image-cropper)):**
- Upload via drag & drop ou botão
- Crop interativo com preview
- Zoom e rotação
- Retorna base64 da imagem cortada

---

### Indicador de Senha

**Arquivo:** `templates/components/indicador_senha.html`

Indicador visual de força de senha com lista de requisitos.

#### Parâmetros

- `show_special` (bool): Mostrar requisito de caractere especial (padrão: false)
- `strength_bar_id` (str): ID da barra de progresso
- `strength_text_id` (str): ID do texto de força
- `match_message_id` (str): ID da mensagem de coincidência
- `req_*_id` (str): IDs dos requisitos individuais
- `wrapper_class` (str): Classes CSS adicionais

#### Uso

```jinja2
{% include 'components/indicador_senha.html' %}
```

**Com parâmetros customizados:**
```jinja2
{% set show_special = true %}
{% include 'components/indicador_senha.html' %}
```

**Requer JavaScript:** `static/js/password-validator.js`

---

### Galeria de Fotos

**Arquivo:** `templates/components/galeria_fotos.html`

Galeria de fotos com imagem principal e miniaturas navegáveis.

#### Importação

```jinja2
{% from 'components/galeria_fotos.html' import galeria_fotos %}
```

#### Uso

```jinja2
{% set images = [
    {'url': '/static/img/produto1.jpg', 'alt': 'Foto 1'},
    {'url': '/static/img/produto2.jpg', 'alt': 'Foto 2'},
    {'url': '/static/img/produto3.jpg', 'alt': 'Foto 3'}
] %}

{{ galeria_fotos(images, gallery_id='produtoGallery') }}
```

**Funcionalidades:**
- Imagem principal em destaque
- Miniaturas clicáveis
- Navegação por teclado (Enter/Space)
- Transições suaves
- Totalmente acessível

---

### Navbar User Dropdown

**Arquivo:** `templates/components/navbar_user_dropdown.html`

Dropdown de usuário para navbar com foto de perfil.

#### Uso

```jinja2
{% include 'components/navbar_user_dropdown.html' %}
```

**Funcionalidades:**
- Foto de perfil circular
- Fallback automático se foto não existir
- Links para Dashboard, Perfil e Logout
- Totalmente responsivo

---

### Chat Widget

**Arquivo:** `templates/components/chat_widget.html`

Widget de chat em tempo real (estilo WhatsApp Web).

#### Uso

```jinja2
{% include 'components/chat_widget.html' %}
```

**Funcionalidades:**
- Botão flutuante retrátil
- Badge com contador de não lidas
- Lista de conversas com busca
- Área de mensagens
- Envio com Enter (Shift+Enter para quebra de linha)
- Atualização em tempo real via SSE

**Requer JavaScript:** `static/js/chat-widget.js`

---

## Helpers Backend

### Rate Limiting

**Arquivo:** `util/rate_limit_decorator.py`

Decorator para aplicar rate limiting de forma centralizada.

#### Importação

```python
from util.rate_limit_decorator import aplicar_rate_limit, aplicar_rate_limit_async
from util.rate_limiter import RateLimiter
```

#### Uso

**1. Criar limiter (nível de módulo):**

```python
tarefa_criar_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="tarefa_criar"
)
```

**2. Aplicar decorator:**

```python
@router.post("/cadastrar")
@aplicar_rate_limit(
    limiter=tarefa_criar_limiter,
    mensagem_erro="Muitas tentativas. Aguarde 1 minuto.",
    redirect_url="/tarefas/listar"
)
@requer_autenticacao()
async def post_cadastrar(request: Request, ...):
    # Lógica da rota SEM código de rate limiting
    pass
```

**Para APIs (retorna JSON):**

```python
@router.post("/api/tasks")
@aplicar_rate_limit_async(
    limiter=api_limiter,
    mensagem_erro="API rate limit exceeded"
)
async def create_task(request: Request, ...):
    pass
```

#### Benefícios

- ✅ Elimina ~100 linhas de código duplicado
- ✅ Logging automático de tentativas bloqueadas
- ✅ Flash messages automáticos
- ✅ Suporte a redirecionamento ou JSON

---

### Repository Helpers

**Arquivo:** `util/repository_helpers.py`

Funções auxiliares para operações comuns com repositórios.

#### Importação

```python
from util.repository_helpers import obter_ou_404, obter_lista_ou_vazia, validar_inteiro_positivo, executar_operacao_repo
```

#### Funções Disponíveis

##### `obter_ou_404(entity, request, mensagem, redirect_url, log_erro=True)`

Verifica se entidade existe e redireciona se não existir.

```python
@router.get("/editar/{id}")
@requer_autenticacao()
async def get_editar(request: Request, id: int, usuario_logado: dict):
    # Obter usuário ou retornar 404
    usuario = obter_ou_404(
        usuario_repo.obter_por_id(id),
        request,
        "Usuário não encontrado",
        "/admin/usuarios/listar"
    )
    if isinstance(usuario, RedirectResponse):
        return usuario

    # Usuario existe, pode usar
    return templates.TemplateResponse("editar.html", {...})
```

##### `obter_lista_ou_vazia(lista, request=None, mensagem_aviso=None, log_aviso=False)`

Garante que lista nunca seja None.

```python
tarefas = obter_lista_ou_vazia(
    tarefa_repo.obter_por_usuario(usuario_id),
    request,
    "Nenhuma tarefa encontrada"
)
# tarefas sempre será list, mesmo que vazia
```

##### `validar_inteiro_positivo(valor, request, nome_campo="ID", redirect_url="/")`

Valida IDs antes de passar para repository.

```python
id_valido = validar_inteiro_positivo(
    id,
    request,
    "ID do usuário",
    "/admin/usuarios/listar"
)
if isinstance(id_valido, RedirectResponse):
    return id_valido
```

##### `executar_operacao_repo(operacao, request, mensagem_erro, redirect_url, log_exception=True)`

Executa operação com tratamento de erros.

```python
resultado = executar_operacao_repo(
    lambda: usuario_repo.inserir(usuario),
    request,
    "Erro ao cadastrar usuário",
    "/admin/usuarios/listar"
)
if isinstance(resultado, RedirectResponse):
    return resultado
```

#### Benefícios

- ✅ Elimina ~60 linhas de código duplicado
- ✅ Tratamento de erros consistente
- ✅ Mensagens e logs padronizados

---

### Permission Helpers

**Arquivo:** `util/permission_helpers.py`

Funções para verificação de permissões e propriedade.

#### Importação

```python
from util.permission_helpers import verificar_propriedade, verificar_propriedade_ou_admin, verificar_perfil, verificar_multiplas_condicoes
```

#### Funções Disponíveis

##### `verificar_propriedade(entity, usuario_id, request, mensagem_erro, redirect_url, campo_usuario='usuario_id', log_tentativa=True)`

Verifica se usuário é proprietário da entidade.

```python
@router.post("/tarefas/excluir/{id}")
@requer_autenticacao()
async def post_excluir(request: Request, id: int, usuario_logado: dict):
    tarefa = obter_ou_404(...)
    if isinstance(tarefa, RedirectResponse):
        return tarefa

    # Verificar propriedade
    if not verificar_propriedade(
        tarefa,
        usuario_logado["id"],
        request,
        "Você não pode excluir esta tarefa",
        "/tarefas/listar"
    ):
        return RedirectResponse("/tarefas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Usuário é dono, pode excluir
    tarefa_repo.excluir(id)
```

##### `verificar_propriedade_ou_admin(entity, usuario_logado, request, mensagem_erro, redirect_url, campo_usuario='usuario_id', log_tentativa=True)`

Verifica se usuário é proprietário OU admin.

```python
# Admin pode editar qualquer recurso, dono também pode
if not verificar_propriedade_ou_admin(
    chamado,
    usuario_logado,
    request,
    "Você não pode editar este chamado",
    "/chamados/listar"
):
    return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)
```

##### `verificar_perfil(usuario_perfil, perfis_permitidos, request, mensagem_erro, redirect_url, log_tentativa=True)`

Verifica se perfil está na lista permitida.

```python
from util.perfis import Perfil

if not verificar_perfil(
    usuario_logado["perfil"],
    [Perfil.ADMIN.value, Perfil.VENDEDOR.value],
    request,
    "Apenas administradores e vendedores podem acessar",
    "/home"
):
    return RedirectResponse("/home", status_code=status.HTTP_303_SEE_OTHER)
```

**Nota:** Considere usar `@requer_autenticacao([perfis])` ao invés desta função.

##### `verificar_multiplas_condicoes(condicoes, request, mensagem_erro_padrao, redirect_url, operador='AND')`

Verifica múltiplas condições com operador lógico.

```python
# AND: todas devem passar
if not verificar_multiplas_condicoes([
    (chamado.usuario_id == usuario_logado["id"], "Não é seu chamado"),
    (chamado.status != "Fechado", "Chamado já está fechado")
], request, redirect_url="/chamados/listar"):
    return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

# OR: pelo menos uma deve passar
if not verificar_multiplas_condicoes([
    (tarefa.usuario_id == usuario_logado["id"], "Não é sua tarefa"),
    (usuario_logado["perfil"] == Perfil.ADMIN.value, "Não é administrador")
], request, redirect_url="/tarefas/listar", operador="OR"):
    return RedirectResponse("/tarefas/listar", status_code=status.HTTP_303_SEE_OTHER)
```

#### Benefícios

- ✅ Elimina ~30 linhas de código duplicado
- ✅ Verificações de segurança consistentes
- ✅ Logging automático de tentativas negadas

---

### Validation Util

**Arquivo:** `util/validation_util.py`

Utilitários para processamento de erros de validação Pydantic.

#### Importação

```python
from util.validation_util import processar_erros_validacao
```

#### Função Principal

##### `processar_erros_validacao(e: ValidationError, campo_padrao: str = "geral") -> dict[str, str]`

Processa erros de validação Pydantic de forma segura.

**Funcionalidades:**
- Lida com erros de `@field_validator` (têm loc não-vazia)
- Lida com erros de `@model_validator` (têm loc vazia)
- Remove prefixo "Value error, " das mensagens
- Retorna dicionário campo → mensagem

```python
try:
    dto = CadastroDTO(email="invalido", senha="123", confirmar_senha="456")
except ValidationError as e:
    erros = processar_erros_validacao(e, campo_padrao="confirmar_senha")
    # erros = {"email": "E-mail inválido", "confirmar_senha": "As senhas não coincidem"}
```

**Uso recomendado:** Use `FormValidationError` ao invés de chamar diretamente.

---

### Validation Helpers

**Arquivo:** `util/validation_helpers.py`

Helpers de validação reutilizáveis para regras de negócio.

#### Importação

```python
from util.validation_helpers import verificar_email_disponivel, email_existe
```

#### Funções Disponíveis

##### `verificar_email_disponivel(email: str, usuario_id_atual: Optional[int] = None) -> tuple[bool, Optional[str]]`

Verifica se um e-mail está disponível para uso.

```python
# Verificar em cadastro (sem usuário atual)
disponivel, msg = verificar_email_disponivel("novo@email.com")
if not disponivel:
    raise ValueError(msg)  # "Este e-mail já está cadastrado"

# Verificar em edição (com usuário atual)
disponivel, msg = verificar_email_disponivel("usuario@email.com", usuario_id=5)
# Retorna True se email pertence ao usuário 5 ou não existe
```

**Retorno:**
- `(True, None)`: Email disponível
- `(False, "mensagem")`: Email indisponível com mensagem de erro

##### `email_existe(email: str) -> bool`

Verifica simplesmente se um e-mail existe no sistema.

```python
if email_existe("admin@sistema.com"):
    print("Email já cadastrado")
```

---

### DTO Validators

**Arquivo:** `dtos/validators.py`

Validadores reutilizáveis para campos de DTOs Pydantic.

#### Importação

```python
from dtos.validators import (
    validar_email, validar_senha_forte, validar_cpf, validar_cnpj,
    validar_telefone_br, validar_cep, validar_data, validar_data_futura,
    validar_data_passada, validar_inteiro_positivo, validar_decimal_positivo,
    validar_extensao_arquivo, validar_tamanho_arquivo,
    validar_string_obrigatoria, validar_comprimento,
    validar_texto_minimo_palavras
)
```

#### Categorias de Validadores

**Texto:**
- `validar_string_obrigatoria(nome_campo, tamanho_minimo, tamanho_maximo, truncar)` - String obrigatória com limites
- `validar_comprimento(tamanho_minimo, tamanho_maximo, truncar)` - Valida comprimento (permite vazia)
- `validar_texto_minimo_palavras(min_palavras, tamanho_maximo, nome_campo)` - Texto com mínimo de palavras

**Email e Senha:**
- `validar_email()` - Validação completa de e-mail
- `validar_senha_forte(min_length, require_uppercase, require_lowercase, require_digit, require_special)` - Validação de força de senha
- `validar_senhas_coincidem(senha_field, confirmar_senha_field)` - Validação de confirmação de senha (usar com `@model_validator`)

**Documentos Brasileiros:**
- `validar_cpf(permitir_vazio)` - Validação de CPF com dígito verificador
- `validar_cnpj(permitir_vazio)` - Validação de CNPJ com dígito verificador
- `validar_telefone_br(permitir_vazio)` - Validação de telefone brasileiro
- `validar_cep(permitir_vazio)` - Validação de CEP

**Datas:**
- `validar_data()` - Validação de data
- `validar_data_futura(campo_nome)` - Data deve ser futura
- `validar_data_passada(campo_nome)` - Data deve ser passada

**Números:**
- `validar_inteiro_positivo(nome_campo)` - Inteiro maior que zero
- `validar_decimal_positivo(nome_campo)` - Decimal maior que zero

**Arquivos:**
- `validar_extensao_arquivo(extensoes_permitidas)` - Validação de extensão
- `validar_tamanho_arquivo(tamanho_maximo_mb)` - Validação de tamanho

#### Exemplo de Uso

```python
from pydantic import BaseModel, field_validator, model_validator
from dtos.validators import (
    validar_email, validar_senha_forte, validar_cpf,
    validar_senhas_coincidem, validar_string_obrigatoria
)

class UsuarioCadastroDTO(BaseModel):
    nome: str
    email: str
    cpf: str
    senha: str
    confirmar_senha: str

    # Validadores de campo individual
    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=3, tamanho_maximo=100)
    )
    _validar_email = field_validator('email')(validar_email())
    _validar_cpf = field_validator('cpf')(validar_cpf())
    _validar_senha = field_validator('senha')(validar_senha_forte())

    # Validador de modelo (múltiplos campos)
    _validar_confirmacao = model_validator(mode='after')(
        validar_senhas_coincidem('senha', 'confirmar_senha')
    )
```

---

## Módulos JavaScript

### Toasts

**Arquivo:** `static/js/toasts.js`

Sistema de notificações toast com Bootstrap 5.

**Já incluído em:** `templates/base_privada.html`

#### Funções Disponíveis

##### `mostrarToast(mensagem, tipo = 'info')`

Exibe um toast na tela.

```javascript
mostrarToast('Operação realizada com sucesso!', 'success');
mostrarToast('Erro ao processar', 'danger');
mostrarToast('Atenção: limite de armazenamento', 'warning');
mostrarToast('Nova mensagem recebida', 'info');
```

**Tipos:** `success`, `danger`, `warning`, `info`

**API moderna (namespace):**
```javascript
window.App.Toasts.show('Mensagem', 'success');
```

**API legacy (retrocompatibilidade):**
```javascript
window.exibirToast('Mensagem', 'success');
```

#### Integração Automática

O módulo automaticamente exibe toasts para flash messages do backend:

```python
# Backend
informar_sucesso(request, "Tarefa criada com sucesso!")

# Frontend - toast aparece automaticamente
```

#### Configuração

Delay de auto-hide configurável via variável global:
```javascript
window.TOAST_AUTO_HIDE_DELAY_MS = 5000; // 5 segundos (padrão)
```

---

### Modal Alerta JS

**Arquivo:** `static/js/modal-alerta.js`

Sistema de modal de alerta (substitui `alert()` nativo).

**Já incluído em:** `templates/base_privada.html`

**Requer componente:** `templates/components/modal_alerta.html`

#### Funções Disponíveis

##### `exibirModalAlerta(mensagem, tipo = 'info', titulo = null, detalhes = null)`

Exibe modal de alerta com estilo Bootstrap.

```javascript
// Erro
exibirModalAlerta('Arquivo muito grande!', 'danger', 'Erro de Upload');

// Aviso
exibirModalAlerta('Tem certeza que deseja sair?', 'warning', 'Atenção');

// Info
exibirModalAlerta('Operação concluída com sucesso!', 'success');

// Com detalhes
exibirModalAlerta(
    'Validação falhou',
    'danger',
    'Erro',
    'Campo email é obrigatório'
);
```

**Tipos:** `danger`, `warning`, `info`, `success`

##### Atalhos para tipos específicos

```javascript
exibirErro('Mensagem de erro', 'Título', 'Detalhes');
exibirAviso('Mensagem de aviso');
exibirInfo('Mensagem informativa');
exibirSucesso('Operação bem-sucedida!');
```

**API moderna (namespace):**
```javascript
window.App.Modal.show('Mensagem', 'danger');
window.App.Modal.showError('Erro!');
window.App.Modal.showWarning('Atenção!');
window.App.Modal.showInfo('Info');
window.App.Modal.showSuccess('Sucesso!');
```

#### Características

- Modal-only (não fecha clicando fora, apenas botão OK ou ESC)
- Cores e ícones Bootstrap
- Acessível (ARIA labels, foco automático)
- Segurança (usa textContent para prevenir XSS)

**NUNCA use `alert()`, `confirm()` ou `prompt()` nativos - sempre use modais!**

---

### Input Mask

**Arquivo:** `static/js/input-mask.js`

Sistema de máscaras de digitação reutilizável.

**Já incluído em:** `templates/base_privada.html`

#### Classes Disponíveis

##### `InputMask`

Máscara baseada em padrões.

**Padrões de máscara:**
- `0` = dígito numérico (0-9)
- `A` = letra maiúscula (A-Z)
- `a` = letra minúscula (a-z)
- Qualquer outro = literal (inserido automaticamente)

**Máscaras pré-definidas:**
```javascript
InputMask.MASKS = {
    CPF: '000.000.000-00',
    CNPJ: '00.000.000/0000-00',
    TELEFONE: '(00) 00000-0000',
    TELEFONE_FIXO: '(00) 0000-0000',
    CEP: '00000-000',
    DATA: '00/00/0000',
    HORA: '00:00',
    DATA_HORA: '00/00/0000 00:00',
    PLACA_ANTIGA: 'AAA-0000',
    PLACA_MERCOSUL: 'AAA-0A00',
    CARTAO: '0000 0000 0000 0000',
    CVV: '000',
    CVV4: '0000',
    VALIDADE_CARTAO: '00/00'
}
```

**Uso com data attributes (automático):**
```html
<input data-mask="CPF" data-unmask="true">
<input data-mask="000.000.000-00">
```

**Uso programático:**
```javascript
const input = document.getElementById('cpf');
new InputMask(input, InputMask.MASKS.CPF, {unmask: true});

// Ou usando função helper
applyMask('cpf-field', 'CPF');
```

##### `DecimalMask`

Máscara para valores decimais/monetários (formato brasileiro).

**Opções:**
- `decimal_places`: Casas decimais (padrão: 2)
- `show_thousands`: Separador de milhares (padrão: true)
- `allow_negative`: Permitir negativos (padrão: false)
- `prefix`: Prefixo (ex: "R$ ")
- `suffix`: Sufixo (ex: " kg")

**Uso com data attributes:**
```html
<input data-decimal
       data-decimal-places="2"
       data-decimal-prefix="R$ "
       data-show-thousands="true">
```

**Uso programático:**
```javascript
const input = document.getElementById('preco');
new DecimalMask(input, {
    decimal_places: 2,
    prefix: 'R$ ',
    show_thousands: true
});
```

**Métodos estáticos:**
```javascript
// Formatar número para string
DecimalMask.format(1234.56, {prefix: 'R$ ', decimal_places: 2});
// Retorna: "R$ 1.234,56"

// Parsear string para número
DecimalMask.parse('R$ 1.234,56', {prefix: 'R$ '});
// Retorna: 1234.56
```

#### Integração com Macros

O macro `field()` tem suporte integrado a máscaras:

```jinja2
{# Campo com máscara de CPF #}
{{ field(name='cpf', label='CPF', mask='CPF', unmask=true) }}

{# Campo decimal (moeda) #}
{{ field(
    name='preco',
    label='Preço',
    type='decimal',
    decimal_prefix='R$ ',
    decimal_places=2
) }}
```

---

### Password Validator

**Arquivo:** `static/js/password-validator.js`

Validador visual de força de senha (NÃO valida no backend).

**Já incluído em:** `templates/base_privada.html`

**Requer componente:** `templates/components/indicador_senha.html`

#### Classe PasswordValidator

```javascript
const validator = new PasswordValidator('senha', 'confirmar_senha', options);
```

**Opções:**
- `showSpecialRequirement`: Mostrar requisito de caractere especial (padrão: false)
- `strengthBarId`: ID da barra de progresso
- `strengthTextId`: ID do texto de força
- `matchMessageId`: ID da mensagem de coincidência
- IDs dos requisitos individuais

#### Métodos

```javascript
validator.getPasswordStrength();  // 0-4
validator.doPasswordsMatch();     // true/false
```

#### Uso Automático

```html
<!-- Senha -->
{{ field(name='senha', label='Senha', type='password', id='senha') }}

<!-- Confirmar senha -->
{{ field(name='confirmar_senha', label='Confirmar Senha', type='password', id='confirmar_senha') }}

<!-- Indicador visual -->
{% include 'components/indicador_senha.html' %}

<script>
// Inicializar validador
new PasswordValidator('senha', 'confirmar_senha');
</script>
```

**IMPORTANTE:** Este módulo fornece apenas feedback visual. A validação real é feita no backend via DTOs.

---

### Image Cropper

**Arquivo:** `static/js/image-cropper.js`

Sistema de corte de imagens com Cropper.js.

**Já incluído em:** `templates/base_privada.html`

**Requer componente:** `templates/components/modal_corte_imagem.html`

#### Classe ImageCropper

```javascript
const cropper = new ImageCropper('modal-id', options);
```

**Opções:**
- `aspectRatio`: Proporção (padrão: 1 para quadrado)
- `viewMode`: Modo de visualização Cropper.js
- `maxWidth`: Largura máxima da imagem final
- `maxHeight`: Altura máxima da imagem final
- `quality`: Qualidade JPEG (0-1)

#### Funcionalidades

- Upload via drag & drop ou botão
- Crop interativo com preview
- Zoom in/out
- Rotação left/right
- Retorna base64 da imagem cortada

#### Exemplo de Uso

```javascript
const cropper = new ImageCropper('modalCorteImagem', {
    aspectRatio: 1,
    maxWidth: 256,
    maxHeight: 256
});

cropper.on('crop', (base64Image) => {
    // Fazer algo com a imagem cortada
    console.log('Imagem cortada:', base64Image);
});
```

---

### Perfil Photo Handler

**Arquivo:** `static/js/perfil-photo-handler.js`

Handler para upload de foto de perfil (integração entre cropper e backend).

**Já incluído em:** Páginas de perfil

#### Funcionalidades

- Integração com Image Cropper
- Upload AJAX para backend
- Feedback com toasts
- Recarga automática após sucesso
- Tratamento de erros

#### Uso

```javascript
// Inicialização automática se elementos estiverem presentes
// Requer:
// - Botão #btn-alterar-foto
// - Modal #modalCorteImagem
// - Campo hidden #usuario-id
```

---

### Chat Widget JS

**Arquivo:** `static/js/chat-widget.js`

Sistema de chat em tempo real com SSE (Server-Sent Events).

**Já incluído em:** `templates/base_privada.html`

**Requer componente:** `templates/components/chat_widget.html`

#### Funcionalidades

- Conexão SSE para atualizações em tempo real
- Lista de conversas com busca
- Área de mensagens estilo WhatsApp
- Scroll infinito (carregar mais mensagens antigas)
- Badge com contador de não lidas
- Marcar como lida automaticamente
- Envio com Enter (Shift+Enter para quebra)

#### Funções Globais

```javascript
toggleChatWidget()           // Alterna entre retraído/expandido
abrirConversa(sala_id)       // Abre conversa específica
enviarMensagem(event)        // Envia mensagem
carregarMaisConversas()      // Carrega mais conversas
```

#### Eventos SSE

O widget escuta eventos do endpoint `/chat/stream`:
- `nova_mensagem`: Nova mensagem recebida
- `mensagem_lida`: Mensagem marcada como lida
- Outros eventos personalizados

---

### Delete Helpers

**Arquivo:** `static/js/delete-helpers.js`

Módulo para confirmação de exclusão com modal customizável.

**Já incluído em:** `templates/base_privada.html`

#### Funções Disponíveis

##### `confirmarExclusao(config)`

Função genérica para confirmação de exclusão.

**Parâmetros:**
- `id` (number): ID da entidade
- `nome` (string): Nome/identificador
- `urlBase` (string): URL base (ex: '/admin/usuarios')
- `entidade` (string): Nome da entidade (ex: 'usuário', 'tarefa')
- `camposDetalhes` (object): Campos a exibir no modal
- `mensagem` (string, opcional): Mensagem customizada
- `urlExclusao` (string, opcional): URL completa de exclusão

**Exemplo básico:**
```javascript
confirmarExclusao({
    id: 1,
    nome: 'João Silva',
    urlBase: '/admin/usuarios',
    entidade: 'usuário'
});
```

**Exemplo com detalhes:**
```javascript
confirmarExclusao({
    id: 1,
    nome: 'João Silva',
    urlBase: '/admin/usuarios',
    entidade: 'usuário',
    camposDetalhes: {
        'Nome': 'João Silva',
        'Email': 'joao@email.com',
        'Perfil': '<span class="badge bg-danger">Administrador</span>'
    }
});
```

##### Helpers Específicos

**`excluirUsuario(id, nome, email, perfil, urlBase='/admin/usuarios')`**

```javascript
excluirUsuario(1, 'João Silva', 'joao@email.com', 'Administrador');
```

**`excluirTarefa(id, titulo, status, urlBase='/tarefas')`**

```javascript
excluirTarefa(1, 'Implementar feature X', 'Pendente');
```

**`excluirChamado(id, titulo, status, prioridade, urlBase='/chamados')`**

```javascript
excluirChamado(1, 'Bug no login', 'Aberto', 'Alta');
```

#### Benefícios

- ✅ Elimina ~200 linhas de JavaScript duplicado
- ✅ Modais consistentes em todo o sistema
- ✅ Escape automático de HTML (segurança)
- ✅ Fácil customização de campos

---

## Resumo de Impacto

### Código Eliminado

- **Templates**: ~500+ linhas (form fields + badges + buttons + empty states + componentes)
- **JavaScript**: ~400+ linhas (toasts + modals + masks + validators + delete confirmations + chat)
- **Python Routes**: ~200+ linhas (rate limiting + repository helpers + permission helpers + validation)
- **Total**: **~1100+ linhas** de código duplicado eliminadas

### Arquivos de Componentes

**Macros de Template (4):**
- `templates/macros/form_fields.html` ⭐ **NOVO**
- `templates/macros/badges.html`
- `templates/macros/action_buttons.html`
- `templates/macros/empty_states.html`

**Componentes de Template (8):**
- `templates/components/rate_limit_field.html` ⭐ **NOVO**
- `templates/components/modal_alerta.html` ⭐ **NOVO**
- `templates/components/modal_confirmacao.html`
- `templates/components/modal_corte_imagem.html`
- `templates/components/indicador_senha.html` ⭐ **NOVO**
- `templates/components/galeria_fotos.html` ⭐ **NOVO**
- `templates/components/navbar_user_dropdown.html` ⭐ **NOVO**
- `templates/components/chat_widget.html` ⭐ **NOVO**

**JavaScript (8):**
- `static/js/toasts.js` ⭐ **NOVO**
- `static/js/modal-alerta.js` ⭐ **NOVO**
- `static/js/input-mask.js` ⭐ **NOVO**
- `static/js/password-validator.js` ⭐ **NOVO**
- `static/js/image-cropper.js` ⭐ **NOVO**
- `static/js/perfil-photo-handler.js` ⭐ **NOVO**
- `static/js/chat-widget.js` ⭐ **NOVO**
- `static/js/delete-helpers.js`

**Python Helpers (6):**
- `util/rate_limit_decorator.py`
- `util/repository_helpers.py`
- `util/permission_helpers.py`
- `util/validation_util.py` ⭐ **NOVO**
- `util/validation_helpers.py` ⭐ **NOVO**
- `dtos/validators.py` ⭐ **NOVO**

### Benefícios Gerais

✅ **Consistência**: Todos os formulários, botões e modais têm aparência e comportamento uniformes

✅ **Manutenibilidade**: Mudanças em um lugar propagam para toda a aplicação

✅ **Produtividade**: Desenvolvimento de novos CRUDs é 3-5x mais rápido

✅ **Qualidade**: Validações, máscaras e tratamento de erros padronizados

✅ **Acessibilidade**: Componentes com ARIA labels, navegação por teclado, foco automático

✅ **Segurança**: Escape de HTML, proteção XSS, validações consistentes

✅ **UX**: Feedback visual consistente (toasts, modais, indicadores de progresso)

---

## Guias Relacionados

- **Criar novo CRUD**: `docs/CRIAR_CRUD.md`
- **Migrar código existente**: `docs/GUIA_MIGRACAO.md`
- **Projeto completo**: `CLAUDE.md`

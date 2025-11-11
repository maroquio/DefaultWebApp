# Componentes Reutilizáveis - DefaultWebApp

Este documento cataloga **todos os componentes reutilizáveis** disponíveis no projeto, incluindo macros de templates, componentes, CSS utilities, módulos JavaScript e helpers backend.

## 📋 Índice

1. [Quick Reference](#quick-reference)
2. [Macros de Template](#macros-de-template)
   - [Form Fields](#form-fields)
   - [Badges](#badges)
   - [Action Buttons](#action-buttons)
   - [Empty States](#empty-states)
3. [Componentes de Template](#componentes-de-template)
   - [Rate Limit Field](#rate-limit-field)
   - [Modal Alerta](#modal-alerta)
   - [Modal Confirmação](#modal-confirmação)
   - [Modal Corte Imagem](#modal-corte-imagem)
   - [Indicador de Senha](#indicador-de-senha)
   - [Galeria de Fotos](#galeria-de-fotos)
   - [Navbar User Dropdown](#navbar-user-dropdown)
   - [Chat Widget](#chat-widget)
   - [Alerta Erro](#alerta-erro)
4. [CSS Utilities](#css-utilities)
   - [Custom CSS](#custom-css)
   - [Chat Widget CSS](#chat-widget-css)
5. [Módulos JavaScript](#módulos-javascript)
   - [Toasts](#toasts)
   - [Modal Alerta JS](#modal-alerta-js)
   - [Input Mask](#input-mask)
   - [Password Validator](#password-validator)
   - [Image Cropper](#image-cropper)
   - [Perfil Photo Handler](#perfil-photo-handler)
   - [Chat Widget JS](#chat-widget-js)
   - [Delete Helpers](#delete-helpers)
6. [Core Utilities Backend](#core-utilities-backend)
   - [Form Validation Error](#form-validation-error)
   - [Auth Decorator](#auth-decorator)
   - [Flash Messages](#flash-messages)
   - [DateTime Util](#datetime-util)
   - [Perfis (Roles)](#perfis-roles)
   - [Template Util](#template-util)
   - [Security](#security)
   - [Senha Util](#senha-util)
   - [CSRF Protection](#csrf-protection)
   - [Foto Util](#foto-util)
7. [Validation Helpers Backend](#validation-helpers-backend)
   - [Validation Util](#validation-util)
   - [Validation Helpers](#validation-helpers)
   - [DTO Validators](#dto-validators)
8. [Repository & Permission Helpers Backend](#repository--permission-helpers-backend)
   - [Rate Limiting](#rate-limiting)
   - [Repository Helpers](#repository-helpers)
   - [Permission Helpers](#permission-helpers)
9. [Resumo de Impacto](#resumo-de-impacto)

---

## Quick Reference

Referência rápida dos imports mais comuns:

### Backend (Python)

```python
# Validação de formulários
from util.exceptions import FormValidationError
from dtos.validators import validar_email, validar_cpf, validar_senha_forte
from util.validation_util import processar_erros_validacao

# Autenticação e autorização
from util.auth_decorator import requer_autenticacao, criar_sessao, destruir_sessao
from util.perfis import Perfil

# Flash messages
from util.flash_messages import informar_sucesso, informar_erro, informar_aviso, informar_info

# Data e hora (NUNCA use datetime.now() diretamente!)
from util.datetime_util import agora, hoje

# Fotos de perfil
from util.foto_util import obter_caminho_foto_usuario, salvar_foto_cropada_usuario

# Segurança
from util.security import criar_hash_senha, verificar_senha
from util.csrf_protection import get_csrf_token

# Templates
from util.template_util import criar_templates

# Rate limiting
from util.rate_limit_decorator import aplicar_rate_limit
from util.rate_limiter import DynamicRateLimiter

# Repository helpers
from util.repository_helpers import obter_ou_404, obter_lista_ou_vazia

# Permission helpers
from util.permission_helpers import verificar_propriedade, verificar_perfil
```

### Frontend (Templates)

```jinja2
{# Form Fields - Macro universal de campos #}
{% from 'macros/form_fields.html' import field %}
{{ field(name='email', label='E-mail', type='email', required=true) }}

{# Badges #}
{% from 'macros/badges.html' import badge_perfil, badge_booleano %}

{# Action Buttons #}
{% from 'macros/action_buttons.html' import btn_group_crud, btn_voltar %}

{# Empty States #}
{% from 'macros/empty_states.html' import empty_state %}

{# Rate Limit Field #}
{% from 'components/rate_limit_field.html' import rate_limit_field %}

{# Galeria de Fotos #}
{% from 'components/galeria_fotos.html' import galeria_fotos %}

{# Componentes (include) #}
{% include 'components/modal_alerta.html' %}
{% include 'components/modal_confirmacao.html' %}
{% include 'components/modal_corte_imagem.html' %}
{% include 'components/indicador_senha.html' %}
{% include 'components/alerta_erro.html' %}
```

### Frontend (JavaScript)

```javascript
// Toasts (notificações não-críticas)
window.App.Toasts.show('Mensagem', 'success');
mostrarToast('Mensagem', 'success'); // API legacy

// Modal Alerta (substitui alert())
window.App.Modal.showError('Erro!');
window.App.Modal.showWarning('Atenção!');
window.App.Modal.showSuccess('Sucesso!');
exibirErro('Erro!'); // API legacy

// Modal Confirmação (exclusões)
abrirModalConfirmacao({url: '/delete/1', mensagem: 'Confirma?'});

// Input Masks
<input data-mask="CPF" data-unmask="true">
<input data-decimal data-decimal-prefix="R$ ">

// Delete Helpers
confirmarExclusao({id: 1, nome: 'Item', urlBase: '/items', entidade: 'item'});
```

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

Widget de chat em tempo real (estilo WhatsApp Web) **totalmente funcional**.

#### Uso

```jinja2
{% include 'components/chat_widget.html' %}
```

**Status:** ✅ **Sistema completo com backend implementado**

**Frontend:**
- Componente HTML incluído em `base_privada.html`
- CSS incluído em `base_privada.html`
- JavaScript incluído em `base_privada.html`

**Backend:**
- Routes: `routes/chat_routes.py` com 10 endpoints
- Models: `chat_sala_model.py`, `chat_mensagem_model.py`, `chat_participante_model.py`
- Repositories: `chat_sala_repo.py`, `chat_mensagem_repo.py`, `chat_participante_repo.py`
- DTOs: `chat_dto.py` com validação
- ChatManager: `util/chat_manager.py` para broadcast SSE
- Rate limiting: 4 limiters específicos

**Funcionalidades:**
- ✅ Botão flutuante retrátil
- ✅ Badge com contador de não lidas
- ✅ Lista de conversas com busca e paginação
- ✅ Área de mensagens estilo WhatsApp
- ✅ Envio com Enter (Shift+Enter para quebra de linha)
- ✅ Atualização em tempo real via SSE (`/chat/stream`)
- ✅ Criar/obter salas de chat
- ✅ Marcar mensagens como lidas
- ✅ Buscar usuários para conversa
- ✅ Scroll infinito (carregar mensagens antigas)

**Requer JavaScript:** `static/js/chat-widget.js`

---

### Alerta Erro

**Arquivo:** `templates/components/alerta_erro.html`

Componente simples para exibir erros gerais (campo `erros.geral`).

#### Uso

```jinja2
{% include 'components/alerta_erro.html' %}
```

**Funcionalidade:**
- Exibe automaticamente se `erros.geral` existir no contexto
- Usa `alert alert-danger` do Bootstrap
- Útil para erros que não se aplicam a um campo específico

**Exemplo no backend:**
```python
erros = {"geral": "Erro ao processar sua solicitação. Tente novamente."}
return templates.TemplateResponse("pagina.html", {"erros": erros, ...})
```

---

## CSS Utilities

### Custom CSS

**Arquivo:** `static/css/custom.css`

CSS customizado com utility classes reutilizáveis para o projeto.

#### Variáveis CSS

```css
:root {
    --primary-color: #0d6efd;
    --secondary-color: #6c757d;
    --success-color: #198754;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
    --info-color: #0dcaf0;
    --light-color: #f8f9fa;
    --dark-color: #212529;
}
```

#### Utility Classes Disponíveis

**Hover Effects:**
```css
.shadow-hover /* Sombra ao passar mouse */
```

**Font Sizes:**
```css
.fs-hero      /* Fonte gigante (15rem) - para códigos de erro */
.fs-small     /* Fonte pequena (0.85rem) */
```

**Resize:**
```css
.resize-none  /* Desabilita resize de textarea */
```

**Object Position:**
```css
.object-top   /* Posiciona imagem no topo */
```

**Error Pages:**
```css
.error-code      /* Estilo do código de erro (404, 500) */
.error-heading   /* Título da página de erro */
.error-container /* Container da página de erro */
.error-traceback /* Container de traceback com scroll */
```

**Theme Selection:**
```css
.tema-card-btn         /* Card de seleção de tema */
.tema-card-btn:hover   /* Hover effect nos cards */
.tema-card-btn.tema-selected /* Tema selecionado */
```

**Toast:**
```css
.toast-offset  /* Margem inferior para toasts */
```

**Preview:**
```css
.preview-120   /* Preview de imagem 120x120px */
```

**Separators:**
```css
.hr-separator  /* HR com largura máxima 200px */
```

**Text Truncation:**
```css
.line-clamp-3  /* Trunca texto após 3 linhas com ... */
```

#### Exemplos de Uso

```html
<!-- Card com hover effect -->
<div class="card shadow-hover">
    <div class="card-body">Conteúdo</div>
</div>

<!-- Código de erro (404, 500) -->
<div class="error-container">
    <h1 class="error-code text-primary">404</h1>
    <h2 class="error-heading">Página não encontrada</h2>
</div>

<!-- Texto truncado -->
<p class="line-clamp-3">
    Lorem ipsum dolor sit amet, consectetur adipiscing elit...
</p>

<!-- Preview de imagem -->
<div class="preview-120">
    <img src="/foto.jpg" class="img-fluid">
</div>
```

---

### Chat Widget CSS

**Arquivo:** `static/css/chat-widget.css`

Estilos específicos para o componente de chat widget **totalmente funcional**.

**Status:** ✅ **Em uso no sistema de chat**

#### Funcionalidades

- Animações de slide-in/slide-out
- Estilos de conversas (lista, itens)
- Bolhas de mensagem (enviadas/recebidas)
- Badge de não lidas
- Botão flutuante
- Responsividade

**Integração:** Este CSS está incluído em `base_privada.html` (linha 18) e é utilizado pelo sistema de chat em tempo real totalmente funcional.

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

**API moderna (namespace):**
```javascript
window.App.InputMask.Mask         // Classe InputMask
window.App.InputMask.apply()      // Aplicar máscara
window.App.InputMask.disconnect() // Remover máscara
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

**API moderna (namespace):**
```javascript
window.App.InputMask.DecimalMask  // Classe DecimalMask
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

**API moderna (namespace):**
```javascript
window.App.Password.Validator     // Classe PasswordValidator
window.App.Password.toggle()      // Toggle visibilidade de senha
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

Sistema de chat em tempo real com SSE (Server-Sent Events) **totalmente funcional**.

**Status:** ✅ **Sistema completo e operacional**

**Incluído em:** `templates/base_privada.html` (linha 147)

**Requer componente:** `templates/components/chat_widget.html`

#### Backend Integrado

**Routes:** `routes/chat_routes.py` com endpoints:
- `GET /chat/stream` - SSE para mensagens em tempo real
- `POST /chat/salas` - Criar/obter sala de chat
- `GET /chat/conversas` - Listar conversas
- `GET /chat/mensagens/{sala_id}` - Listar mensagens
- `POST /chat/mensagens` - Enviar mensagem
- `POST /chat/mensagens/lidas/{sala_id}` - Marcar como lidas
- `GET /chat/usuarios/buscar` - Buscar usuários
- `GET /chat/mensagens/nao-lidas/total` - Contador total
- `GET /chat/health` - Health check

#### Funcionalidades

- ✅ Conexão SSE para atualizações em tempo real
- ✅ Lista de conversas com busca e paginação
- ✅ Área de mensagens estilo WhatsApp
- ✅ Scroll infinito (carregar mensagens antigas)
- ✅ Badge com contador de mensagens não lidas
- ✅ Marcar mensagens como lidas automaticamente
- ✅ Envio com Enter (Shift+Enter para quebra)
- ✅ Botão flutuante retrátil
- ✅ Rate limiting em todas as operações
- ✅ Autorização (apenas participantes)

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
- `atualizar_contador`: Atualizar contador de não lidas
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

## Core Utilities Backend

### Form Validation Error

**Arquivo:** `util/exceptions.py`

Exceção customizada para centralizar tratamento de erros de validação de formulários DTO.

#### Importação

```python
from util.exceptions import FormValidationError
from pydantic import ValidationError
```

#### Classe `FormValidationError`

Encapsula um `ValidationError` do Pydantic com informações para renderizar página de erro.

**Atributos:**
- `validation_error`: ValidationError original do Pydantic
- `template_path`: Caminho do template (relativo a templates/)
- `dados_formulario`: Dict com dados para reexibir no formulário
- `campo_padrao`: Campo para erros sem loc específico (de @model_validator)
- `mensagem_flash`: Mensagem de erro para toast

#### Uso

```python
@router.post("/cadastrar")
async def post_cadastrar(request: Request, email: str = Form(), senha: str = Form()):
    # Armazena dados do formulário
    dados_formulario = {"email": email}

    try:
        dto = CadastroDTO(email=email, senha=senha)
        # ... lógica de negócio
    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="auth/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="senha",
            mensagem_flash="Há campos com erros de validação."
        )
```

#### Benefícios

- ✅ Handler global processa automaticamente e renderiza template
- ✅ Exibe flash message automaticamente
- ✅ Passa `dados` e `erros` para o template
- ✅ Logging automático
- ✅ Elimina ~50 linhas de try/except duplicadas por rota

**IMPORTANTE:** Use APENAS em rotas que renderizam templates. Para APIs JSON, use ValidationError diretamente.

---

### Auth Decorator

**Arquivo:** `util/auth_decorator.py`

Sistema de autenticação e autorização baseado em decorator.

#### Importação

```python
from util.auth_decorator import (
    requer_autenticacao,
    criar_sessao,
    destruir_sessao,
    obter_usuario_logado,
    esta_logado
)
```

#### Funções Disponíveis

##### `requer_autenticacao(perfis_permitidos=None)`

Decorator para proteger rotas com autenticação/autorização.

**Parâmetros:**
- `perfis_permitidos` (List[str], opcional): Lista de perfis que podem acessar

**Funcionalidades:**
- Verifica se usuário está logado
- Verifica se perfil está na lista permitida
- Injeta `usuario_logado` nos kwargs da função
- Redireciona para `/login` se não autenticado
- Redireciona com erro se não autorizado

**Exemplos:**

```python
from util.perfis import Perfil

# Qualquer usuário autenticado
@router.get("/dashboard")
@requer_autenticacao()
async def get_dashboard(request: Request, usuario_logado: dict):
    # usuario_logado é injetado automaticamente
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "usuario": usuario_logado
    })

# Apenas administradores
@router.get("/admin/usuarios")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_usuarios(request: Request, usuario_logado: dict):
    # Apenas Perfil.ADMIN pode acessar
    pass

# Múltiplos perfis
@router.get("/vendas")
@requer_autenticacao([Perfil.ADMIN.value, Perfil.VENDEDOR.value])
async def get_vendas(request: Request, usuario_logado: dict):
    # Admin OU Vendedor podem acessar
    pass
```

##### `criar_sessao(request, usuario)`

Cria sessão de usuário logado.

```python
usuario_dict = {
    "id": usuario.id,
    "email": usuario.email,
    "nome": usuario.nome,
    "perfil": usuario.perfil
}
criar_sessao(request, usuario_dict)
```

##### `destruir_sessao(request)`

Destroi sessão (logout).

```python
destruir_sessao(request)
return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
```

##### `obter_usuario_logado(request)`

Obtém usuário logado da sessão (retorna None se não logado).

```python
usuario = obter_usuario_logado(request)
if usuario:
    print(f"Logado como: {usuario['email']}")
```

##### `esta_logado(request)`

Verifica se há usuário logado na sessão.

```python
if esta_logado(request):
    print("Usuário está logado")
```

#### Benefícios

- ✅ Proteção de rotas com uma linha de código
- ✅ Autorização por perfis integrada
- ✅ Logging automático de tentativas não autorizadas
- ✅ Flash messages automáticos
- ✅ Injeção automática de `usuario_logado`

---

### Flash Messages

**Arquivo:** `util/flash_messages.py`

Sistema de mensagens temporárias (flash messages) exibidas uma única vez após ações.

#### Importação

```python
from util.flash_messages import (
    informar_sucesso,
    informar_erro,
    informar_aviso,
    informar_info,
    obter_mensagens
)
```

#### Funções Disponíveis

##### `informar_sucesso(request, mensagem)`

Adiciona mensagem de sucesso (verde).

```python
informar_sucesso(request, "Usuário cadastrado com sucesso!")
return RedirectResponse("/usuarios", status_code=status.HTTP_303_SEE_OTHER)
```

##### `informar_erro(request, mensagem)`

Adiciona mensagem de erro (vermelho).

```python
informar_erro(request, "Não foi possível excluir o usuário.")
return RedirectResponse("/usuarios", status_code=status.HTTP_303_SEE_OTHER)
```

##### `informar_aviso(request, mensagem)`

Adiciona mensagem de aviso (amarelo).

```python
informar_aviso(request, "Este recurso está em manutenção.")
```

##### `informar_info(request, mensagem)`

Adiciona mensagem informativa (azul).

```python
informar_info(request, "Nova versão disponível em breve.")
```

##### `obter_mensagens(request)`

Obtém e limpa mensagens da sessão (uso interno, chamado pelos templates).

```python
mensagens = obter_mensagens(request)
# [{"texto": "Mensagem", "tipo": "sucesso"}, ...]
```

#### Integração com Frontend

As mensagens são automaticamente convertidas em toasts pelo `static/js/toasts.js`:

```python
# Backend
informar_sucesso(request, "Tarefa criada!")

# Frontend - toast aparece automaticamente
```

#### Tipos de Mensagem

- `sucesso` → Toast verde
- `erro` → Toast vermelho
- `aviso` → Toast amarelo
- `info` → Toast azul

#### Benefícios

- ✅ API simples e consistente
- ✅ Integração automática com toasts
- ✅ Mensagens são exibidas apenas uma vez
- ✅ Suporta múltiplas mensagens simultâneas

---

### DateTime Util

**Arquivo:** `util/datetime_util.py`

Utilitários para manipulação de datetime com timezone configurado.

#### Importação

```python
from util.datetime_util import (
    agora,
    hoje,
    converter_para_timezone,
    datetime_para_string_iso,
    string_iso_para_datetime
)
```

#### Funções Disponíveis

##### `agora()`

Retorna datetime atual no timezone configurado (America/Sao_Paulo).

**CRÍTICO:** Use `agora()` ao invés de `datetime.now()` em TODO o código!

```python
from util.datetime_util import agora

# ✅ CORRETO
timestamp = agora()
print(timestamp)  # 2025-10-28 14:30:00-03:00

# ❌ ERRADO - NUNCA FAÇA ISSO
# from datetime import datetime
# timestamp = datetime.now()  # Sem timezone!
```

##### `hoje()`

Retorna date de hoje no timezone configurado.

```python
from util.datetime_util import hoje

data = hoje()
print(data)  # 2025-10-28
```

##### `converter_para_timezone(dt, tz=None)`

Converte datetime para timezone especificado.

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from util.datetime_util import converter_para_timezone

# Converter UTC para timezone da aplicação
utc_time = datetime(2025, 10, 28, 17, 30, tzinfo=ZoneInfo("UTC"))
local_time = converter_para_timezone(utc_time)
print(local_time)  # 2025-10-28 14:30:00-03:00

# Converter para timezone específico
ny_time = converter_para_timezone(local_time, ZoneInfo("America/New_York"))
```

##### `datetime_para_string_iso(dt)`

Converte datetime para string ISO 8601.

```python
from util.datetime_util import agora, datetime_para_string_iso

timestamp = agora()
iso_string = datetime_para_string_iso(timestamp)
print(iso_string)  # 2025-10-28T14:30:00-03:00
```

##### `string_iso_para_datetime(iso_string)`

Converte string ISO 8601 para datetime.

```python
from util.datetime_util import string_iso_para_datetime

dt = string_iso_para_datetime("2025-10-28T14:30:00-03:00")
print(dt)  # 2025-10-28 14:30:00-03:00
```

#### Armazenamento no Banco de Dados

**CRÍTICO:** Ao inserir datetime no banco, NUNCA use `.strftime()`!

```python
from util.datetime_util import agora

# ✅ CORRETO - Passa datetime object diretamente
cursor.execute(
    "INSERT INTO tabela (data_criacao) VALUES (?)",
    (agora(),)
)

# ❌ ERRADO - NUNCA use .strftime() para banco!
# cursor.execute(
#     "INSERT INTO tabela (data_criacao) VALUES (?)",
#     (agora().strftime('%Y-%m-%d %H:%M:%S'),)
# )
```

**Observação:** `.strftime()` deve ser usado APENAS para display em templates, não para storage!

#### Como Funciona

1. **Write (agora() → DB)**: Datetime com timezone → Convertido para UTC → Armazenado como naive
2. **Read (DB → Template)**: Naive UTC → Adiciona UTC timezone → Converte para America/Sao_Paulo
3. **Resultado**: Código sempre trabalha com timezone-aware datetimes

#### Benefícios

- ✅ Consistência de timezone em toda aplicação
- ✅ Storage simples no SQLite (naive UTC)
- ✅ Fácil mudança de timezone (.env)
- ✅ Compatível com ferramentas externas

---

### Perfis (Roles)

**Arquivo:** `util/perfis.py`

Enum centralizado para perfis de usuário - **Single Source of Truth**.

#### Importação

```python
from util.perfis import Perfil
```

#### Enum `Perfil`

Define todos os perfis disponíveis no sistema.

```python
class Perfil(str, Enum):
    ADMIN = "Administrador"
    CLIENTE = "Cliente"
    VENDEDOR = "Vendedor"
```

#### Uso Correto

**✅ SEMPRE use o Enum:**

```python
from util.perfis import Perfil

# Comparação
if usuario.perfil == Perfil.ADMIN.value:
    print("É administrador")

# Autorização
@requer_autenticacao([Perfil.ADMIN.value])

# Cadastro
usuario = Usuario(
    nome="João",
    email="joao@email.com",
    perfil=Perfil.CLIENTE.value
)

# Select options no template
perfis = Perfil.valores()  # ["Administrador", "Cliente", "Vendedor"]
```

**❌ NUNCA use strings literais:**

```python
# ❌ ERRADO - NUNCA FAÇA ISSO
if usuario.perfil == "admin":  # Hardcoded!
    pass

# ❌ ERRADO
@requer_autenticacao(["admin"])  # Hardcoded!

# ❌ ERRADO
perfil = "cliente"  # Hardcoded!
```

#### Métodos Disponíveis

##### `Perfil.valores()`

Retorna lista de todos os valores de perfis.

```python
perfis = Perfil.valores()
# ["Administrador", "Cliente", "Vendedor"]

# Uso em templates (select dropdown)
{{ field(name='perfil', type='select', options=perfis) }}
```

##### `Perfil.existe(valor)`

Verifica se um perfil é válido.

```python
if Perfil.existe("Administrador"):
    print("Perfil válido")

if not Perfil.existe("InvalidoPerfil"):
    print("Perfil inválido")
```

##### `Perfil.from_string(valor)`

Converte string para Enum Perfil.

```python
perfil_enum = Perfil.from_string("Administrador")
print(perfil_enum)  # <Perfil.ADMIN: 'Administrador'>

perfil_enum = Perfil.from_string("invalido")
print(perfil_enum)  # None
```

##### `Perfil.validar(valor)`

Valida perfil ou levanta ValueError.

```python
try:
    perfil = Perfil.validar("Administrador")  # OK
except ValueError as e:
    print(e)

try:
    perfil = Perfil.validar("invalido")  # Raises ValueError
except ValueError as e:
    print(e)  # "Perfil inválido: invalido. Use: Administrador, Cliente, Vendedor"
```

#### Como Adicionar Novo Perfil

1. Edite APENAS `util/perfis.py`
2. Adicione novo valor ao Enum
3. Todo o sistema se adapta automaticamente

```python
class Perfil(str, Enum):
    ADMIN = "Administrador"
    CLIENTE = "Cliente"
    VENDEDOR = "Vendedor"
    GERENTE = "Gerente"  # ✅ Adicione aqui
```

#### Benefícios

- ✅ Single source of truth para perfis
- ✅ Autocomplete no IDE
- ✅ Type checking
- ✅ Fácil refatoração (rename perfil)
- ✅ Impossível usar perfil inexistente

---

### Template Util

**Arquivo:** `util/template_util.py`

Utilitários para templates Jinja2, incluindo filtros e função de criação de templates.

#### Importação

```python
from util.template_util import criar_templates
```

#### Função Principal: `criar_templates(pasta)`

Cria instância de Jinja2Templates com configurações globais.

**Configurações aplicadas:**
- Funções globais: `obter_mensagens()`, `csrf_input()`
- Variáveis globais: `APP_NAME`, `VERSION`, `TOAST_AUTO_HIDE_DELAY_MS`
- Filtros customizados: `data_br`, `format_data`, `format_data_hora`, `foto_usuario`

```python
from util.template_util import criar_templates

# Criar templates para uma rota
templates = criar_templates("templates/usuarios")

# Renderizar
@router.get("/listar")
async def get_listar(request: Request):
    return templates.TemplateResponse("listar.html", {
        "request": request,
        "usuarios": usuarios
    })
```

**Observação:** Sempre usa o diretório raiz `templates` para permitir acesso a base.html e componentes.

#### Filtros de Data

##### `data_br` / `format_data`

Formata datetime para DD/MM/YYYY (sem hora).

```jinja2
{{ usuario.data_cadastro | format_data }}
<!-- Output: 22/10/2025 -->
```

##### `data_hora_br` / `format_data_hora`

Formata datetime para DD/MM/YYYY HH:MM.

```jinja2
{{ tarefa.data_criacao | format_data_hora }}
<!-- Output: 22/10/2025 14:30 -->
```

##### `format_data_as_hora`

Formata datetime para DD/MM/YYYY às HH:MM.

```jinja2
{{ mensagem.data_envio | format_data_as_hora }}
<!-- Output: 22/10/2025 às 14:30 -->
```

##### `format_hora`

Formata datetime para HH:MM (apenas hora).

```jinja2
{{ evento.hora_inicio | format_hora }}
<!-- Output: 14:30 -->
```

#### Filtro de Foto

##### `foto_usuario`

Retorna caminho da foto do usuário.

```jinja2
<img src="{{ usuario.id | foto_usuario }}" alt="Foto">
<!-- Output: /static/img/usuarios/000001.jpg -->
```

#### Funções Globais

##### `obter_mensagens(request)`

Obtém flash messages (usado internamente pelos templates).

```jinja2
{% for msg in obter_mensagens(request) %}
    <!-- Mensagem: {{ msg.texto }} -->
{% endfor %}
```

##### `csrf_input(request)`

Gera input hidden com token CSRF.

```jinja2
<form method="POST">
    {{ csrf_input(request) | safe }}
    <!-- Output: <input type="hidden" name="csrf_token" value="token..."> -->
</form>
```

#### Variáveis Globais

- `APP_NAME`: Nome da aplicação (.env)
- `VERSION`: Versão da aplicação
- `TOAST_AUTO_HIDE_DELAY_MS`: Delay de auto-hide dos toasts

```jinja2
<title>{{ APP_NAME }} - Página</title>
<script>
    window.TOAST_AUTO_HIDE_DELAY_MS = {{ TOAST_AUTO_HIDE_DELAY_MS }};
</script>
```

#### Benefícios

- ✅ Configuração centralizada de templates
- ✅ Filtros padronizados para data/hora
- ✅ Variáveis globais disponíveis em todos templates
- ✅ Integração automática com flash messages e CSRF

---

### Security

**Arquivo:** `util/security.py`

Funções de segurança para hash de senhas com bcrypt.

#### Importação

```python
from util.security import (
    criar_hash_senha,
    verificar_senha,
    gerar_token_redefinicao,
    obter_data_expiracao_token
)
```

#### Funções Disponíveis

##### `criar_hash_senha(senha)`

Cria hash bcrypt da senha.

```python
senha_plana = "MinhaSenh@123"
senha_hash = criar_hash_senha(senha_plana)
print(senha_hash)  # $2b$12$...

# Armazenar no banco
usuario.senha = senha_hash
```

##### `verificar_senha(senha_plana, senha_hash)`

Verifica se senha corresponde ao hash.

```python
senha_digitada = "MinhaSenh@123"
senha_hash_db = usuario.senha

if verificar_senha(senha_digitada, senha_hash_db):
    print("Senha correta!")
else:
    print("Senha incorreta!")
```

##### `gerar_token_redefinicao()`

Gera token seguro para redefinição de senha.

```python
token = gerar_token_redefinicao()
print(token)  # Token URL-safe de 32 bytes

# Armazenar no banco
usuario.token_redefinicao = token
usuario.token_expiracao = obter_data_expiracao_token(horas=1)
```

##### `obter_data_expiracao_token(horas=1)`

Retorna data de expiração do token.

```python
from util.security import obter_data_expiracao_token

expiracao = obter_data_expiracao_token(horas=1)
print(expiracao)  # 2025-10-28 15:30:00-03:00 (1 hora no futuro)

# Ou 24 horas
expiracao_24h = obter_data_expiracao_token(horas=24)
```

#### Exemplo Completo - Login

```python
from util.security import verificar_senha
from util.auth_decorator import criar_sessao

@router.post("/login")
async def post_login(request: Request, email: str = Form(), senha: str = Form()):
    # Buscar usuário
    usuario = usuario_repo.obter_por_email(email)
    if not usuario:
        informar_erro(request, "E-mail ou senha inválidos")
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar senha
    if not verificar_senha(senha, usuario.senha):
        informar_erro(request, "E-mail ou senha inválidos")
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    # Criar sessão
    criar_sessao(request, {
        "id": usuario.id,
        "email": usuario.email,
        "nome": usuario.nome,
        "perfil": usuario.perfil
    })

    return RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)
```

#### Exemplo Completo - Cadastro

```python
from util.security import criar_hash_senha

@router.post("/cadastrar")
async def post_cadastrar(request: Request, nome: str = Form(), senha: str = Form()):
    # Hash da senha
    senha_hash = criar_hash_senha(senha)

    # Criar usuário
    usuario = Usuario(
        nome=nome,
        email=email,
        senha=senha_hash,  # Armazenar hash, NUNCA senha plana!
        perfil=Perfil.CLIENTE.value
    )

    usuario_repo.inserir(usuario)
    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
```

#### Benefícios

- ✅ Hash bcrypt seguro (cost factor 12)
- ✅ Geração de tokens criptograficamente seguros
- ✅ Integração com timezone (expiracao)
- ✅ API simples e consistente

**NUNCA armazene senhas em texto plano no banco de dados!**

---

### Senha Util

**Arquivo:** `util/senha_util.py`

Validação de força de senha no backend.

#### Importação

```python
from util.senha_util import validar_forca_senha, calcular_nivel_senha
```

#### Funções Disponíveis

##### `validar_forca_senha(senha)`

Valida se senha atende requisitos de força.

**Requisitos:**
- Mínimo 8 caracteres (configurável via `PASSWORD_MIN_LENGTH`)
- Máximo 128 caracteres (configurável via `PASSWORD_MAX_LENGTH`)
- Pelo menos uma letra maiúscula
- Pelo menos uma letra minúscula
- Pelo menos um número
- Pelo menos um caractere especial

**Retorno:** `(bool, str)` - (é_válida, mensagem)

```python
from util.senha_util import validar_forca_senha

# Senha válida
valida, msg = validar_forca_senha("MinhaSenha@123")
print(valida, msg)  # True, "Senha válida"

# Senha fraca (sem maiúscula)
valida, msg = validar_forca_senha("minhasenha@123")
print(valida, msg)  # False, "Senha deve conter pelo menos uma letra maiúscula"

# Senha fraca (muito curta)
valida, msg = validar_forca_senha("Ab1@")
print(valida, msg)  # False, "Senha deve ter no mínimo 8 caracteres"
```

##### `calcular_nivel_senha(senha)`

Calcula nível de força da senha.

**Retorno:** `str` - "fraca", "média" ou "forte"

**Critérios:**
- **Fraca** (≤2 pontos): Poucos requisitos atendidos
- **Média** (3-4 pontos): Maioria dos requisitos atendidos
- **Forte** (≥5 pontos): Todos requisitos + comprimento ≥12

```python
from util.senha_util import calcular_nivel_senha

print(calcular_nivel_senha("abc123"))  # "fraca"
print(calcular_nivel_senha("Abc123"))  # "média"
print(calcular_nivel_senha("Abc123@XYZ"))  # "média"
print(calcular_nivel_senha("Abc123@XYZuvw"))  # "forte" (≥12 chars)
```

#### Uso em DTO Validators

```python
from pydantic import BaseModel, field_validator
from util.senha_util import validar_forca_senha

class CadastroDTO(BaseModel):
    senha: str

    @field_validator('senha')
    def validar_senha(cls, v: str) -> str:
        valida, mensagem = validar_forca_senha(v)
        if not valida:
            raise ValueError(mensagem)
        return v
```

#### Configuração

Configure requisitos mínimos/máximos no `.env`:

```env
PASSWORD_MIN_LENGTH=8
PASSWORD_MAX_LENGTH=128
```

#### Benefícios

- ✅ Validação backend consistente
- ✅ Mensagens de erro descritivas
- ✅ Configurável via .env
- ✅ Integração com DTOs Pydantic

**Observação:** O frontend (`password-validator.js`) fornece feedback visual, mas a validação real é feita aqui no backend.

---

### CSRF Protection

**Arquivo:** `util/csrf_protection.py`

Middleware e funções de proteção CSRF (Cross-Site Request Forgery).

#### Importação

```python
from util.csrf_protection import (
    generate_csrf_token,
    get_csrf_token,
    validate_csrf_token,
    CSRFProtectionMiddleware
)
```

#### Funções Disponíveis

##### `generate_csrf_token()`

Gera token CSRF aleatório e seguro.

```python
token = generate_csrf_token()
print(token)  # String hex aleatória de 32 bytes
```

##### `get_csrf_token(request)`

Obtém ou cria token CSRF da sessão.

```python
token = get_csrf_token(request)
# Se não existe na sessão, cria novo automaticamente
```

##### `validate_csrf_token(request, token_from_form)`

Valida token CSRF contra o token da sessão.

```python
token_enviado = await request.form()["csrf_token"]
if validate_csrf_token(request, token_enviado):
    print("Token válido!")
else:
    print("Token inválido!")
```

#### Middleware

##### `CSRFProtectionMiddleware`

Middleware de proteção CSRF (logging).

**Adicionar em main.py:**

```python
from util.csrf_protection import CSRFProtectionMiddleware

app.add_middleware(CSRFProtectionMiddleware)
```

**Observação:** Atualmente o middleware apenas loga requests protegidos. A validação completa deve ser implementada via dependency injection nos handlers.

#### Uso em Templates

O helper `csrf_input()` já está disponível globalmente nos templates:

```jinja2
<form method="POST" action="/cadastrar">
    {{ csrf_input(request) | safe }}
    <!-- Renderiza: <input type="hidden" name="csrf_token" value="..."> -->

    {{ field(name='nome', label='Nome') }}
    <button type="submit">Enviar</button>
</form>
```

#### Configuração

**Constantes:**
- `CSRF_SESSION_KEY`: Chave na sessão (padrão: `_csrf_token`)
- `CSRF_FORM_FIELD`: Nome do campo no formulário (padrão: `csrf_token`)
- `CSRF_HEADER_NAME`: Nome do header (padrão: `X-CSRF-Token`)
- `CSRF_PROTECTED_METHODS`: Métodos protegidos (POST, PUT, PATCH, DELETE)
- `CSRF_EXEMPT_PATHS`: Caminhos isentos (`/health`, `/api/`)

#### Benefícios

- ✅ Proteção contra ataques CSRF
- ✅ Integração automática com templates
- ✅ Tokens baseados em sessão
- ✅ Comparação constant-time (previne timing attacks)
- ✅ Paths configuráveis para isenção

---

### Foto Util

**Arquivo:** `util/foto_util.py`

Utilitários para gerenciamento de fotos de usuários.

#### Importação

```python
from util.foto_util import (
    obter_caminho_foto_usuario,
    obter_path_absoluto_foto,
    criar_foto_padrao_usuario,
    salvar_foto_cropada_usuario,
    foto_existe,
    obter_tamanho_foto
)
```

#### Funções Disponíveis

##### `obter_caminho_foto_usuario(id)`

Retorna caminho da foto para uso em templates.

```python
caminho = obter_caminho_foto_usuario(1)
print(caminho)  # /static/img/usuarios/000001.jpg

# Uso em templates
<img src="{{ obter_caminho_foto_usuario(usuario.id) }}">
```

##### `obter_path_absoluto_foto(id)`

Retorna Path absoluto do arquivo de foto.

```python
from pathlib import Path

path = obter_path_absoluto_foto(1)
print(path)  # static/img/usuarios/000001.jpg (Path object)

# Verificar se existe
if path.exists():
    print("Foto existe")
```

##### `criar_foto_padrao_usuario(id)`

Cria cópia da foto padrão para novo usuário.

```python
# Ao cadastrar usuário
usuario_id = usuario_repo.inserir(usuario)
criar_foto_padrao_usuario(usuario_id)
```

**Funcionalidade:**
- Copia `static/img/user.jpg` para `static/img/usuarios/{id:06d}.jpg`
- Logging automático
- Retorna True se sucesso, False se erro

##### `salvar_foto_cropada_usuario(id, conteudo_base64)`

Salva foto cropada do frontend.

```python
@router.post("/perfil/foto")
async def salvar_foto(request: Request, foto_base64: str = Form()):
    usuario_id = obter_usuario_logado(request)["id"]

    if salvar_foto_cropada_usuario(usuario_id, foto_base64):
        informar_sucesso(request, "Foto atualizada!")
    else:
        informar_erro(request, "Erro ao salvar foto.")

    return RedirectResponse("/perfil", status_code=status.HTTP_303_SEE_OTHER)
```

**Funcionalidade:**
- Decodifica base64
- Remove prefixo `data:image/...;base64,` se existir
- Converte para RGB (remove alpha channel)
- Redimensiona se > `FOTO_PERFIL_TAMANHO_MAX` (mantém aspect ratio)
- Salva como JPG com qualidade 90
- Logging automático

##### `foto_existe(id)`

Verifica se foto do usuário existe.

```python
if foto_existe(1):
    print("Usuário tem foto customizada")
else:
    print("Usuário está usando foto padrão")
```

##### `obter_tamanho_foto(id)`

Retorna tamanho da foto em bytes.

```python
tamanho = obter_tamanho_foto(1)
if tamanho:
    print(f"Tamanho: {tamanho / 1024:.2f} KB")
else:
    print("Foto não existe")
```

#### Configuração

Configure tamanho máximo no `.env`:

```env
FOTO_PERFIL_TAMANHO_MAX=256
```

#### Formato de Arquivo

- Formato: `{id:06d}.jpg` (ex: `000001.jpg`, `000123.jpg`)
- Pasta: `static/img/usuarios/`
- Formato de imagem: JPEG
- Qualidade: 90

#### Benefícios

- ✅ Gerenciamento centralizado de fotos
- ✅ Redimensionamento automático
- ✅ Fallback para foto padrão
- ✅ Logging de operações
- ✅ Conversão automática de formatos

---

## Validation Helpers Backend

### Validation Util

**Arquivo:** `util/validation_util.py`

Utilitários para processamento de erros de validação Pydantic.

#### Importação

```python
from util.validation_util import processar_erros_validacao
```

#### Função Principal

##### `processar_erros_validacao(e: ValidationError, campo_padrao: str = "geral")`

Processa erros de validação Pydantic de forma segura.

**Parâmetros:**
- `e`: ValidationError do Pydantic
- `campo_padrao`: Campo para erros sem loc específico (de @model_validator)

**Retorno:** `dict[str, str]` - Dicionário campo → mensagem

**Funcionalidades:**
- Lida com erros de `@field_validator` (têm loc não-vazia)
- Lida com erros de `@model_validator` (têm loc vazia)
- Remove prefixo "Value error, " das mensagens
- Retorna dicionário campo → mensagem

```python
from pydantic import ValidationError
from util.validation_util import processar_erros_validacao

try:
    dto = CadastroDTO(email="invalido", senha="123", confirmar_senha="456")
except ValidationError as e:
    erros = processar_erros_validacao(e, campo_padrao="confirmar_senha")
    print(erros)
    # {
    #     "email": "E-mail inválido",
    #     "senha": "Senha deve ter no mínimo 8 caracteres",
    #     "confirmar_senha": "As senhas não coincidem"
    # }
```

#### Uso Recomendado

**Não chame diretamente** - use `FormValidationError`:

```python
from util.exceptions import FormValidationError

try:
    dto = CadastroDTO(...)
except ValidationError as e:
    raise FormValidationError(
        validation_error=e,
        template_path="cadastro.html",
        dados_formulario={...},
        campo_padrao="confirmar_senha"
    )
    # O handler global chama processar_erros_validacao() automaticamente
```

#### Benefícios

- ✅ Processa erros de field_validator e model_validator
- ✅ Remove prefixos desnecessários
- ✅ Retorna formato padronizado para templates
- ✅ Usado automaticamente por FormValidationError

---

### Validation Helpers

**Arquivo:** `util/validation_helpers.py`

Helpers de validação reutilizáveis para regras de negócio.

#### Importação

```python
from util.validation_helpers import verificar_email_disponivel, email_existe
```

#### Funções Disponíveis

##### `verificar_email_disponivel(email, usuario_id_atual=None)`

Verifica se e-mail está disponível para uso.

**Parâmetros:**
- `email`: E-mail a verificar
- `usuario_id_atual`: ID do usuário atual (para edição)

**Retorno:** `(bool, Optional[str])` - (disponível, mensagem_erro)

**Exemplos:**

```python
from util.validation_helpers import verificar_email_disponivel

# Verificar em cadastro (sem usuário atual)
disponivel, msg = verificar_email_disponivel("novo@email.com")
if not disponivel:
    raise ValueError(msg)  # "Este e-mail já está cadastrado"

# Verificar em edição (com usuário atual)
disponivel, msg = verificar_email_disponivel("usuario@email.com", usuario_id=5)
# Retorna True se:
# - Email não existe OU
# - Email pertence ao usuário 5
```

##### `email_existe(email)`

Verifica simplesmente se e-mail existe no sistema.

```python
from util.validation_helpers import email_existe

if email_existe("admin@sistema.com"):
    print("Email já cadastrado")
else:
    print("Email disponível")
```

#### Uso em DTOs

```python
from pydantic import BaseModel, field_validator
from util.validation_helpers import verificar_email_disponivel

class CadastroDTO(BaseModel):
    email: str

    @field_validator('email')
    def validar_email_unico(cls, v: str) -> str:
        disponivel, msg = verificar_email_disponivel(v)
        if not disponivel:
            raise ValueError(msg)
        return v
```

```python
class AlterarDTO(BaseModel):
    email: str
    usuario_id: int

    @field_validator('email')
    def validar_email_unico(cls, v: str, values) -> str:
        usuario_id = values.data.get('usuario_id')
        disponivel, msg = verificar_email_disponivel(v, usuario_id)
        if not disponivel:
            raise ValueError(msg)
        return v
```

#### Benefícios

- ✅ Validação de regras de negócio reutilizável
- ✅ Mensagens de erro consistentes
- ✅ Integração com DTOs Pydantic
- ✅ Suporta cadastro e edição

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

#### Benefícios

- ✅ Validadores prontos para uso
- ✅ Mensagens de erro em português
- ✅ Validação de documentos brasileiros
- ✅ Integração perfeita com Pydantic
- ✅ Elimina código duplicado de validação

---

## Repository & Permission Helpers Backend

### Rate Limiting

**Arquivo:** `util/rate_limit_decorator.py`

Decorator para aplicar rate limiting de forma centralizada.

#### Importação

```python
from util.rate_limit_decorator import aplicar_rate_limit, aplicar_rate_limit_async
from util.rate_limiter import RateLimiter, DynamicRateLimiter
```

#### Uso

**1. Criar limiter (nível de módulo):**

```python
# Limiter estático (valores fixos)
tarefa_criar_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="tarefa_criar"
)

# OU limiter dinâmico (lê valores do database)
login_limiter = DynamicRateLimiter(
    config_key_max="rate_limit_login_max",
    config_key_minutos="rate_limit_login_minutos",
    nome="login"
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
- ✅ Rate limits dinâmicos (sem restart de servidor)

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

## Resumo de Impacto

### Código Eliminado

- **Templates**: ~500+ linhas (form fields + badges + buttons + empty states + componentes)
- **JavaScript**: ~400+ linhas (toasts + modals + masks + validators + delete confirmations + chat)
- **Python Routes**: ~200+ linhas (rate limiting + repository helpers + permission helpers + validation)
- **Total**: **~1100+ linhas** de código duplicado eliminadas

### Arquivos de Componentes

**Macros de Template (4):**
- `templates/macros/form_fields.html` ⭐ **MACRO UNIVERSAL**
- `templates/macros/badges.html`
- `templates/macros/action_buttons.html`
- `templates/macros/empty_states.html`

**Componentes de Template (9):**
- `templates/components/rate_limit_field.html`
- `templates/components/modal_alerta.html`
- `templates/components/modal_confirmacao.html`
- `templates/components/modal_corte_imagem.html`
- `templates/components/indicador_senha.html`
- `templates/components/galeria_fotos.html`
- `templates/components/navbar_user_dropdown.html`
- `templates/components/chat_widget.html`
- `templates/components/alerta_erro.html` ⭐ **NOVO**

**CSS (2):**
- `static/css/custom.css` ⭐ **NOVO**
- `static/css/chat-widget.css` ⭐ **NOVO**

**JavaScript (8):**
- `static/js/toasts.js`
- `static/js/modal-alerta.js`
- `static/js/input-mask.js`
- `static/js/password-validator.js`
- `static/js/image-cropper.js`
- `static/js/perfil-photo-handler.js`
- `static/js/chat-widget.js`
- `static/js/delete-helpers.js`

**Core Utilities Backend (10):** ⭐ **SEÇÃO NOVA**
- `util/exceptions.py` - FormValidationError
- `util/auth_decorator.py` - @requer_autenticacao()
- `util/flash_messages.py` - informar_*()
- `util/datetime_util.py` - agora(), hoje()
- `util/perfis.py` - Enum Perfil
- `util/template_util.py` - criar_templates()
- `util/security.py` - Hash de senha
- `util/senha_util.py` - Validação de senha
- `util/csrf_protection.py` - Proteção CSRF
- `util/foto_util.py` - Manipulação de fotos

**Validation Helpers Backend (3):**
- `util/validation_util.py`
- `util/validation_helpers.py`
- `dtos/validators.py`

**Repository & Permission Helpers Backend (3):**
- `util/rate_limit_decorator.py`
- `util/repository_helpers.py`
- `util/permission_helpers.py`

### Estatísticas Finais

**Total de Componentes Documentados:** 39

| Categoria | Quantidade | Status |
|-----------|-----------|--------|
| Macros de Template | 4 | ✅ 100% |
| Componentes de Template | 9 | ✅ 100% |
| CSS Utilities | 2 | ✅ 100% |
| Módulos JavaScript | 8 | ✅ 100% |
| Core Utilities Backend | 10 | ✅ 100% |
| Validation Helpers | 3 | ✅ 100% |
| Repository/Permission Helpers | 3 | ✅ 100% |
| **TOTAL** | **39** | **✅ 100%** |

### Benefícios Gerais

✅ **Consistência**: Todos os formulários, botões e modais têm aparência e comportamento uniformes

✅ **Manutenibilidade**: Mudanças em um lugar propagam para toda a aplicação

✅ **Produtividade**: Desenvolvimento de novos CRUDs é 3-5x mais rápido

✅ **Qualidade**: Validações, máscaras e tratamento de erros padronizados

✅ **Acessibilidade**: Componentes com ARIA labels, navegação por teclado, foco automático

✅ **Segurança**: Escape de HTML, proteção XSS, validações consistentes

✅ **UX**: Feedback visual consistente (toasts, modais, indicadores de progresso)

✅ **Backend**: Helpers centralizam lógica comum (auth, validation, permissions, rate limiting)

✅ **DRY Principle**: Elimina duplicação massiva de código

---

## Guias Relacionados

- **Criar novo CRUD**: `docs/CRIAR_CRUD.md`
- **Migrar código existente**: `docs/GUIA_MIGRACAO.md`
- **Projeto completo**: `CLAUDE.md`

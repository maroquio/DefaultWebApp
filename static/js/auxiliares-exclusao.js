/**
 * Auxiliares de Exclusao
 *
 * Modulo para auxiliar na confirmacao de exclusao de entidades com modal de confirmacao.
 * Elimina codigo JavaScript duplicado em templates de listagem.
 *
 * Dependencias:
 * - Bootstrap 5 (para modais)
 * - components/modal_confirmacao.html (deve estar incluido no template)
 * - modal-alerta.js (funcao abrirModalConfirmacao)
 *
 * @version 1.0.0
 * @author DefaultWebApp
 */

/**
 * Confirma exclusao de uma entidade com modal de confirmacao customizavel
 *
 * @param {Object} config - Configuracao da confirmacao
 * @param {number} config.id - ID da entidade a ser excluida
 * @param {string} config.nome - Nome/identificador principal da entidade
 * @param {string} config.urlBase - URL base para exclusao (ex: '/admin/usuarios')
 * @param {string} [config.entidade='item'] - Nome da entidade (ex: 'usuario', 'chamado')
 * @param {Object} [config.camposDetalhes={}] - Objeto com campos a exibir (chave: label, valor: conteudo HTML)
 * @param {string} [config.mensagem=null] - Mensagem customizada (null = usa mensagem padrao)
 * @param {string} [config.urlExclusao=null] - URL completa de exclusao (null = usa urlBase + id + '/excluir')
 *
 * @example
 * // Uso basico
 * confirmarExclusao({
 *     id: 1,
 *     nome: 'Joao Silva',
 *     urlBase: '/admin/usuarios',
 *     entidade: 'usuario'
 * });
 *
 * @example
 * // Uso com detalhes customizados
 * confirmarExclusao({
 *     id: 1,
 *     nome: 'Joao Silva',
 *     urlBase: '/admin/usuarios',
 *     entidade: 'usuario',
 *     camposDetalhes: {
 *         'Nome': 'Joao Silva',
 *         'Email': 'joao@email.com',
 *         'Perfil': '<span class="badge bg-danger">Administrador</span>'
 *     }
 * });
 *
 * @example
 * // Uso com URL customizada
 * confirmarExclusao({
 *     id: 1,
 *     nome: 'Tarefa #1',
 *     urlExclusao: '/categorias/excluir/1',
 *     entidade: 'categoria',
 *     camposDetalhes: {
 *         'Titulo': 'Implementar funcionalidade X',
 *         'Status': '<span class="badge bg-primary">Pendente</span>'
 *     }
 * });
 */
function confirmarExclusao(config) {
    // Validacao de parametros obrigatorios
    if (!config.id) {
        console.error('confirmarExclusao: parametro "id" e obrigatorio');
        return;
    }

    // Extracao de parametros com valores padrao
    const {
        id,
        nome = 'item',
        urlBase = '',
        entidade = 'item',
        camposDetalhes = {},
        mensagem = null,
        urlExclusao = null
    } = config;

    // Construir URL de exclusao
    const url = urlExclusao || `${urlBase}/excluir/${id}`;

    // Validar URL
    if (!url || url === '/excluir/' + id) {
        console.error('confirmarExclusao: URL de exclusao invalida. Forneca "urlBase" ou "urlExclusao"');
        return;
    }

    // Construir HTML dos detalhes se houver campos
    let detalhesHtml = '';
    if (Object.keys(camposDetalhes).length > 0) {
        detalhesHtml = `
            <div class="card bg-light mt-3">
                <div class="card-body">
                    <table class="table table-sm table-borderless mb-0">
        `;

        // Adicionar cada campo a tabela
        for (const [label, valor] of Object.entries(camposDetalhes)) {
            detalhesHtml += `
                        <tr>
                            <th scope="row" width="30%">${label}:</th>
                            <td>${valor}</td>
                        </tr>
            `;
        }

        detalhesHtml += `
                    </table>
                </div>
            </div>
        `;
    }

    // Mensagem padrao ou customizada
    const mensagemFinal = mensagem || `Tem certeza que deseja excluir ${entidade === 'item' ? 'este' : 'este(a)'} <strong>${entidade}</strong>?`;

    // Abrir modal de confirmacao
    abrirModalConfirmacao({
        url: url,
        mensagem: mensagemFinal,
        detalhes: detalhesHtml
    });
}

/**
 * Funcao auxiliar para escapar HTML em strings
 * Previne injecao de HTML nao intencional
 *
 * @param {string} texto - Texto a ser escapado
 * @returns {string} Texto com caracteres HTML escapados
 *
 * @example
 * escaparHtml('<script>alert("xss")</script>');
 * // Retorna: "&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;"
 */
function escaparHtml(texto) {
    const div = document.createElement('div');
    div.textContent = texto;
    return div.innerHTML;
}

/**
 * Confirma exclusao de usuario (helper especifico)
 *
 * @param {number} id - ID do usuario
 * @param {string} nome - Nome do usuario
 * @param {string} email - Email do usuario
 * @param {string} perfil - Perfil do usuario
 * @param {string} [urlBase='/admin/usuarios'] - URL base
 *
 * @example
 * excluirUsuario(1, 'Joao Silva', 'joao@email.com', 'Administrador');
 */
function excluirUsuario(id, nome, email, perfil, urlBase = '/admin/usuarios') {
    // Determinar cor do badge baseado no perfil
    let corBadge = 'info';
    if (perfil === 'Administrador') {
        corBadge = 'danger';
    } else if (perfil === 'Vendedor') {
        corBadge = 'warning text-dark';
    }

    confirmarExclusao({
        id: id,
        nome: nome,
        urlBase: urlBase,
        entidade: 'usuario',
        camposDetalhes: {
            'Nome': escaparHtml(nome),
            'Email': escaparHtml(email),
            'Perfil': `<span class="badge bg-${corBadge}">${escaparHtml(perfil)}</span>`
        }
    });
}

/**
 * Confirma exclusao de chamado (helper especifico)
 *
 * @param {number} id - ID do chamado
 * @param {string} titulo - Titulo do chamado
 * @param {string} status - Status do chamado
 * @param {string} prioridade - Prioridade do chamado
 * @param {string} [urlBase='/chamados'] - URL base
 *
 * @example
 * excluirChamado(1, 'Bug no login', 'Aberto', 'Alta');
 */
function excluirChamado(id, titulo, status, prioridade, urlBase = '/chamados') {
    // Determinar cor do badge de status
    let corStatus = 'secondary';
    if (status === 'Aberto') {
        corStatus = 'primary';
    } else if (status === 'Em Analise') {
        corStatus = 'info';
    } else if (status === 'Resolvido') {
        corStatus = 'success';
    }

    // Determinar cor do badge de prioridade
    let corPrioridade = 'secondary';
    if (prioridade === 'Urgente') {
        corPrioridade = 'danger';
    } else if (prioridade === 'Alta') {
        corPrioridade = 'warning text-dark';
    } else if (prioridade === 'Media') {
        corPrioridade = 'info';
    }

    confirmarExclusao({
        id: id,
        nome: `#${id}`,
        urlBase: urlBase,
        entidade: 'chamado',
        camposDetalhes: {
            'Titulo': escaparHtml(titulo),
            'Status': `<span class="badge bg-${corStatus}">${escaparHtml(status)}</span>`,
            'Prioridade': `<span class="badge bg-${corPrioridade}">${escaparHtml(prioridade)}</span>`
        }
    });
}

/**
 * Inicializar namespace global do app
 */
window.App = window.App || {};
window.App.Exclusao = window.App.Exclusao || {};

/**
 * API publica do modulo Exclusao
 */
window.App.Exclusao.confirmar = confirmarExclusao;
window.App.Exclusao.escaparHtml = escaparHtml;
window.App.Exclusao.excluirUsuario = excluirUsuario;
window.App.Exclusao.excluirChamado = excluirChamado;

// Exportar funcoes para uso global
window.confirmarExclusao = confirmarExclusao;
window.excluirUsuario = excluirUsuario;
window.excluirChamado = excluirChamado;

window.escaparHtml = escaparHtml;

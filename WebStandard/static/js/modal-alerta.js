/**
 * Sistema de Modal de Alerta Bootstrap
 * Substitui alert() nativo por modais Bootstrap bonitos e acessíveis
 */

/**
 * Exibe um modal de alerta com estilo Bootstrap
 *
 * @param {string} mensagem - Mensagem principal a ser exibida
 * @param {string} tipo - Tipo do alerta: 'danger', 'warning', 'info', 'success' (padrão: 'info')
 * @param {string|null} titulo - Título do modal (se null, usa título padrão baseado no tipo)
 * @param {string|null} detalhes - Texto ou HTML adicional para detalhes (opcional)
 */
function exibirModalAlerta(mensagem, tipo = 'info', titulo = null, detalhes = null) {
    // Validar tipo
    const tiposValidos = ['danger', 'warning', 'info', 'success'];
    if (!tiposValidos.includes(tipo)) {
        console.warn(`Tipo inválido: ${tipo}. Usando 'info' como padrão.`);
        tipo = 'info';
    }

    // Configuração de cada tipo
    const config = {
        danger: {
            titulo: 'Erro',
            icone: 'bi-exclamation-circle-fill',
            headerClass: 'bg-danger text-white',
            btnClass: 'btn-danger',
            btnCloseClass: 'btn-close-white'
        },
        warning: {
            titulo: 'Atenção',
            icone: 'bi-exclamation-triangle-fill',
            headerClass: 'bg-warning',
            btnClass: 'btn-warning',
            btnCloseClass: ''
        },
        info: {
            titulo: 'Informação',
            icone: 'bi-info-circle-fill',
            headerClass: 'bg-info text-white',
            btnClass: 'btn-info',
            btnCloseClass: 'btn-close-white'
        },
        success: {
            titulo: 'Sucesso',
            icone: 'bi-check-circle-fill',
            headerClass: 'bg-success text-white',
            btnClass: 'btn-success',
            btnCloseClass: 'btn-close-white'
        }
    };

    const cfg = config[tipo];

    // Obter elementos do DOM
    const modal = document.getElementById('modalAlerta');
    const header = document.getElementById('modalAlertaHeader');
    const tituloTexto = document.getElementById('modalAlertaTituloTexto');
    const icone = document.getElementById('modalAlertaIcone');
    const mensagemEl = document.getElementById('modalAlertaMensagem');
    const detalhesEl = document.getElementById('modalAlertaDetalhes');
    const btnOk = document.getElementById('modalAlertaBtnOk');
    const btnClose = document.getElementById('modalAlertaBtnClose');

    if (!modal) {
        console.error('Modal de alerta não encontrado! Certifique-se de incluir modal_alerta.html no template.');
        console.error(`Mensagem não exibida: ${mensagem}`);
        return;
    }

    // Resetar classes do header
    header.className = 'modal-header';
    header.classList.add(...cfg.headerClass.split(' '));

    // Configurar ícone
    icone.className = 'bi';
    icone.classList.add(cfg.icone, 'me-2');

    // Configurar título
    tituloTexto.textContent = titulo || cfg.titulo;

    // Configurar mensagem
    mensagemEl.textContent = mensagem;

    // Configurar detalhes (se fornecidos)
    // SEGURANÇA: Usar textContent em vez de innerHTML para prevenir XSS
    if (detalhes) {
        detalhesEl.textContent = detalhes;
        detalhesEl.classList.remove('d-none');
    } else {
        detalhesEl.textContent = '';
        detalhesEl.classList.add('d-none');
    }

    // Configurar botão OK
    btnOk.className = 'btn';
    btnOk.classList.add(cfg.btnClass);

    // Configurar botão close
    btnClose.className = 'btn-close';
    if (cfg.btnCloseClass) {
        btnClose.classList.add(cfg.btnCloseClass);
    }

    // Exibir modal
    const bsModal = new bootstrap.Modal(modal, {
        backdrop: 'static',  // Não fecha ao clicar fora
        keyboard: true       // Permite fechar com ESC
    });
    bsModal.show();

    // Focar no botão OK quando modal abrir (acessibilidade)
    modal.addEventListener('shown.bs.modal', function () {
        btnOk.focus();
    }, { once: true });
}

/**
 * Atalhos para tipos específicos
 */
function exibirErro(mensagem, titulo = null, detalhes = null) {
    exibirModalAlerta(mensagem, 'danger', titulo, detalhes);
}

function exibirAviso(mensagem, titulo = null, detalhes = null) {
    exibirModalAlerta(mensagem, 'warning', titulo, detalhes);
}

function exibirInfo(mensagem, titulo = null, detalhes = null) {
    exibirModalAlerta(mensagem, 'info', titulo, detalhes);
}

function exibirSucesso(mensagem, titulo = null, detalhes = null) {
    exibirModalAlerta(mensagem, 'success', titulo, detalhes);
}

/**
 * Inicializar namespace global do app
 */
window.App = window.App || {};
window.App.Modal = window.App.Modal || {};

/**
 * API pública do módulo Modal
 */
window.App.Modal.show = exibirModalAlerta;
window.App.Modal.showError = exibirErro;
window.App.Modal.showWarning = exibirAviso;
window.App.Modal.showInfo = exibirInfo;
window.App.Modal.showSuccess = exibirSucesso;

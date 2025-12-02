/**
 * Sistema de Toasts Bootstrap
 * Lê mensagens do JSON e exibe como toasts Bootstrap 5
 */

document.addEventListener('DOMContentLoaded', function() {
    // Obter mensagens do script JSON
    const mensagensElement = document.getElementById('mensagens-data');

    if (!mensagensElement) {
        return;
    }

    try {
        const mensagens = JSON.parse(mensagensElement.textContent || '[]');

        // Mapeamento de tipos de mensagem para classes Bootstrap
        const tipoMap = {
            'sucesso': 'success',
            'erro': 'danger',
            'aviso': 'warning',
            'info': 'info'
        };

        // Exibir cada mensagem
        mensagens.forEach(msg => {
            const tipoBootstrap = tipoMap[msg.tipo] || 'info';
            mostrarToast(msg.texto, tipoBootstrap);
        });
    } catch (e) {
        console.error('Erro ao processar mensagens:', e);
    }
});

/**
 * Exibe um toast na tela
 * @param {string} mensagem - Texto da mensagem
 * @param {string} tipo - Tipo do toast (success, danger, warning, info)
 */
function mostrarToast(mensagem, tipo = 'info') {
    const container = document.getElementById('toast-container');

    if (!container) {
        console.error('Container de toasts não encontrado');
        return;
    }

    // Gerar ID único para o toast
    const id = 'toast-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);

    // Criar elemento do toast
    const toastElement = document.createElement('div');
    toastElement.className = `toast align-items-center text-bg-${tipo} border-0`;
    toastElement.setAttribute('role', 'alert');
    toastElement.setAttribute('aria-live', 'assertive');
    toastElement.setAttribute('aria-atomic', 'true');
    toastElement.id = id;

    // Ícones para cada tipo
    const icones = {
        'success': '<i class="bi bi-check-circle-fill me-2"></i>',
        'danger': '<i class="bi bi-exclamation-circle-fill me-2"></i>',
        'warning': '<i class="bi bi-exclamation-triangle-fill me-2"></i>',
        'info': '<i class="bi bi-info-circle-fill me-2"></i>'
    };

    const icone = icones[tipo] || '';

    toastElement.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${icone}${mensagem}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto"
                    data-bs-dismiss="toast" aria-label="Fechar"></button>
        </div>
    `;

    // Adicionar ao container
    container.appendChild(toastElement);

    // Obter delay configurado ou usar padrão de 5s
    const delay = window.TOAST_AUTO_HIDE_DELAY_MS || 5000;

    // Inicializar e mostrar toast (auto-dismiss)
    const bsToast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: delay
    });

    bsToast.show();

    // Remover elemento do DOM após ser escondido
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

/**
 * Inicializar namespace global do app
 */
window.App = window.App || {};
window.App.Toasts = window.App.Toasts || {};

/**
 * API pública do módulo Toasts
 */
window.App.Toasts.show = mostrarToast;

/**
 * ValidadorSenha - Sistema de feedback visual de senha
 *
 * Funcionalidades:
 * - Toggle de visibilidade de senha
 * - Medidor de forca de senha
 * - Atualizacao visual de requisitos
 * - Feedback visual de senhas coincidentes
 *
 * IMPORTANTE: Este componente fornece APENAS feedback visual.
 * A validacao real e feita server-side atraves de DTOs Pydantic.
 * NAO bloqueia envio do formulario com alerts.
 */

class ValidadorSenha {
    /**
     * @param {Object} config - Configuracao do validador
     * @param {string} config.passwordFieldId - ID do campo de senha
     * @param {string} config.confirmPasswordFieldId - ID do campo de confirmacao (opcional)
     * @param {string} config.strengthBarId - ID da barra de progresso (opcional)
     * @param {string} config.strengthTextId - ID do texto de forca (opcional)
     * @param {string} config.matchMessageId - ID da mensagem de coincidencia (opcional)
     * @param {Object} config.requirements - IDs dos elementos de requisitos (opcional)
     * @param {number} config.minLength - Tamanho minimo da senha (padrao: 8)
     * @param {boolean} config.showStrength - Exibir medidor de forca (padrao: false)
     * @param {boolean} config.showRequirements - Exibir requisitos visuais (padrao: false)
     * @param {Function} config.onValidate - Callback customizado de validacao (opcional)
     */
    constructor(config) {
        this.config = {
            minLength: 8,
            showStrength: false,
            showRequirements: false,
            ...config
        };

        this.passwordField = document.getElementById(this.config.passwordFieldId);
        this.confirmPasswordField = this.config.confirmPasswordFieldId
            ? document.getElementById(this.config.confirmPasswordFieldId)
            : null;

        if (!this.passwordField) {
            console.error(`Campo de senha com ID "${this.config.passwordFieldId}" nao encontrado`);
            return;
        }

        this.init();
    }

    init() {
        // Configurar eventos de forca de senha
        if (this.config.showStrength) {
            this.strengthBar = document.getElementById(this.config.strengthBarId);
            this.strengthText = document.getElementById(this.config.strengthTextId);

            if (this.strengthBar && this.strengthText) {
                this.passwordField.addEventListener('input', () => this.verificarForcaSenha());
            }
        }

        // Configurar eventos de senha coincidente
        if (this.confirmPasswordField && this.config.matchMessageId) {
            this.matchMessage = document.getElementById(this.config.matchMessageId);

            if (this.matchMessage) {
                this.confirmPasswordField.addEventListener('input', () => this.verificarSenhasCoincidentes());
            }
        }
    }

    /**
     * Verifica a forca da senha e atualiza indicadores visuais
     */
    verificarForcaSenha() {
        const password = this.passwordField.value;
        let strength = 0;
        let color = 'danger';
        let text = 'Muito fraca';

        // Verificar requisitos
        const requirements = {
            length: password.length >= this.config.minLength,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        // Atualizar indicadores visuais de requisitos
        if (this.config.showRequirements && this.config.requirements) {
            this.atualizarIndicadoresRequisitos(requirements);
        }

        // Calcular forca (20% para cada requisito)
        if (requirements.length) strength += 20;
        if (requirements.uppercase) strength += 20;
        if (requirements.lowercase) strength += 20;
        if (requirements.number) strength += 20;
        if (requirements.special) strength += 20;

        // Definir texto e cor baseado na forca
        if (strength >= 80) {
            color = 'success';
            text = 'Forte';
        } else if (strength >= 60) {
            color = 'info';
            text = 'Media';
        } else if (strength >= 40) {
            color = 'warning';
            text = 'Fraca';
        }

        // Atualizar barra de progresso
        if (this.strengthBar) {
            this.strengthBar.style.width = strength + '%';
            this.strengthBar.className = 'progress-bar bg-' + color;
        }

        // Atualizar texto de forca
        if (this.strengthText) {
            this.strengthText.textContent = text;
            this.strengthText.className = 'text-' + color;
        }

        return { strength, requirements };
    }

    /**
     * Atualiza indicadores visuais de requisitos de senha
     * SEGURANCA: Usa createElement em vez de innerHTML para prevenir XSS
     */
    atualizarIndicadoresRequisitos(requirements) {
        const reqMap = {
            length: this.config.requirements.length,
            uppercase: this.config.requirements.uppercase,
            lowercase: this.config.requirements.lowercase,
            number: this.config.requirements.number,
            special: this.config.requirements.special
        };

        Object.keys(reqMap).forEach(key => {
            const elementId = reqMap[key];
            if (!elementId) return;

            const element = document.getElementById(elementId);
            if (!element) return;

            const isMet = requirements[key];

            // Extrair texto original (sem icones)
            const originalText = element.textContent
                .replace(/✓ /g, '')
                .replace(/<i.*?<\/i>/g, '')
                .trim();

            // Limpar conteudo atual
            element.innerHTML = '';

            if (isMet) {
                // Criar icone de sucesso usando createElement
                const icon = document.createElement('i');
                icon.className = 'bi bi-check-circle-fill';
                element.appendChild(icon);

                // Adicionar espaco e texto
                element.appendChild(document.createTextNode(' ' + originalText));
                element.classList.add('text-success');
            } else {
                // Apenas texto, sem icone
                element.textContent = originalText;
                element.classList.remove('text-success');
            }
        });
    }

    /**
     * Verifica se as senhas coincidem
     * SEGURANCA: Usa createElement em vez de innerHTML para prevenir XSS
     */
    verificarSenhasCoincidentes() {
        if (!this.confirmPasswordField || !this.matchMessage) return true;

        const password = this.passwordField.value;
        const confirmPassword = this.confirmPasswordField.value;

        if (confirmPassword.length === 0) {
            this.matchMessage.textContent = '';
            return true;
        }

        // Limpar conteudo anterior
        this.matchMessage.innerHTML = '';

        // Criar span wrapper
        const span = document.createElement('span');

        if (password === confirmPassword) {
            // Senhas coincidem - feedback positivo
            span.className = 'text-success';

            const icon = document.createElement('i');
            icon.className = 'bi bi-check-circle';
            span.appendChild(icon);

            span.appendChild(document.createTextNode(' As senhas coincidem'));
            this.matchMessage.appendChild(span);
            return true;
        } else {
            // Senhas nao coincidem - feedback negativo
            span.className = 'text-danger';

            const icon = document.createElement('i');
            icon.className = 'bi bi-x-circle';
            span.appendChild(icon);

            span.appendChild(document.createTextNode(' As senhas nao coincidem'));
            this.matchMessage.appendChild(span);
            return false;
        }
    }

    /**
     * Retorna informacoes sobre a forca da senha (para uso programatico)
     * @returns {Object} Objeto com forca (0-100) e requisitos atendidos
     */
    obterForcaSenha() {
        const password = this.passwordField.value;
        let strength = 0;

        // Verificar requisitos
        const requirements = {
            length: password.length >= this.config.minLength,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        // Calcular forca (20% para cada requisito)
        if (requirements.length) strength += 20;
        if (requirements.uppercase) strength += 20;
        if (requirements.lowercase) strength += 20;
        if (requirements.number) strength += 20;
        if (requirements.special) strength += 20;

        return {
            strength,
            requirements,
            isStrong: strength >= 80,
            isMedium: strength >= 60,
            isWeak: strength < 60
        };
    }

    /**
     * Retorna se as senhas coincidem (para uso programatico)
     * @returns {boolean} True se senhas coincidem ou nao ha confirmacao
     */
    senhasCoincidentes() {
        if (!this.confirmPasswordField) return true;

        const password = this.passwordField.value;
        const confirmPassword = this.confirmPasswordField.value;

        return password === confirmPassword;
    }
}

/**
 * Funcao global para toggle de visibilidade de senha
 * @param {string} fieldId - ID do campo de senha
 */
function alternarVisibilidadeSenha(fieldId) {
    const field = document.getElementById(fieldId);
    const icon = document.getElementById('icon_' + fieldId);

    if (!field) {
        console.error(`Campo com ID "${fieldId}" nao encontrado`);
        return;
    }

    if (field.type === 'password') {
        field.type = 'text';
        if (icon) {
            icon.classList.remove('bi-eye');
            icon.classList.add('bi-eye-slash');
        }
    } else {
        field.type = 'password';
        if (icon) {
            icon.classList.remove('bi-eye-slash');
            icon.classList.add('bi-eye');
        }
    }
}

/**
 * Inicializar namespace global do app
 */
window.App = window.App || {};
window.App.Senha = window.App.Senha || {};

/**
 * API publica do modulo Senha
 */
window.App.Senha.Validador = ValidadorSenha;
window.App.Senha.alternarVisibilidade = alternarVisibilidadeSenha;

// Expor classe e funcao no escopo global
window.ValidadorSenha = ValidadorSenha;
window.alternarVisibilidadeSenha = alternarVisibilidadeSenha;

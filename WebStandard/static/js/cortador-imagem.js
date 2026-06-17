/**
 * Cortador de Imagem
 *
 * Sistema reutilizavel de crop de imagens usando Cropper.js
 */

// Armazenar instancias do Cropper para cada modal
const instanciasCortador = {};

/**
 * Prepara uma imagem para o modal SEM inicializar o Cropper
 * Util para pre-carregar antes de abrir o modal
 *
 * @param {string} modalId - ID do modal
 * @param {File} file - Arquivo de imagem
 * @param {number} maxFileSizeMB - Tamanho maximo em MB (default: 5)
 * @returns {Promise} - Resolve quando a imagem estiver carregada
 */
function prepararImagemParaModal(modalId, file, maxFileSizeMB = 5) {
    return new Promise((resolve, reject) => {
        const uploadSection = document.getElementById(`upload-section-${modalId}`);
        const cropperContainer = document.getElementById(`cropper-container-${modalId}`);
        const cropperImage = document.getElementById(`cropper-image-${modalId}`);
        const cropperImageArea = document.getElementById(`cropper-image-area-${modalId}`);
        const btnSubmit = document.getElementById(`btn-submit-${modalId}`);

        if (!file) {
            reject('Nenhum arquivo fornecido');
            return;
        }

        // Validar tamanho
        const maxBytes = maxFileSizeMB * 1024 * 1024;
        if (file.size > maxBytes) {
            reject(`Arquivo muito grande! Tamanho maximo: ${maxFileSizeMB}MB`);
            return;
        }

        // Validar tipo
        if (!file.type.startsWith('image/')) {
            reject('Por favor, selecione um arquivo de imagem valido.');
            return;
        }

        // Ler arquivo
        const reader = new FileReader();
        reader.onload = function(event) {
            // Ocultar secao de upload e mostrar cropper
            if (uploadSection) uploadSection.classList.add('d-none');
            if (cropperContainer) cropperContainer.classList.remove('d-none');
            if (btnSubmit) btnSubmit.disabled = false;

            // Definir imagem no cropper
            cropperImage.src = event.target.result;

            // Pre-calcular e aplicar altura ideal ANTES do modal abrir
            // Usar estimativa baseada em viewport ja que o modal ainda nao esta visivel
            const viewportHeight = window.innerHeight;
            const estimatedHeight = Math.max(200, Math.min(600, viewportHeight * 0.5));
            cropperImageArea.style.height = `${estimatedHeight}px`;

            // Aguardar a imagem carregar completamente
            cropperImage.onload = function() {
                resolve();
            };
            cropperImage.onerror = function() {
                reject('Erro ao carregar a imagem');
            };
        };
        reader.onerror = function() {
            reject('Erro ao ler o arquivo');
        };
        reader.readAsDataURL(file);
    });
}

/**
 * Inicializa o Cropper no modal (deve ser chamado apos o modal estar visivel)
 *
 * @param {string} modalId - ID do modal
 * @param {number} aspectRatio - Proporcao do crop (default: 1.0)
 * @param {Function} onReady - Callback chamado quando o cropper estiver pronto (opcional)
 */
function inicializarCortadorNoModal(modalId, aspectRatio = 1.0, onReady = null) {
    const cropperImage = document.getElementById(`cropper-image-${modalId}`);
    const previewImage = document.getElementById(`preview-${modalId}`);

    if (!cropperImage || !cropperImage.src) {
        console.error(`Imagem nao preparada para o modal ${modalId}`);
        return;
    }

    // Destruir cropper anterior se existir
    if (instanciasCortador[modalId]) {
        instanciasCortador[modalId].destroy();
    }

    // Inicializar Cropper.js
    instanciasCortador[modalId] = new Cropper(cropperImage, {
        aspectRatio: aspectRatio,
        viewMode: 1,  // Permite crop box crescer ate os limites do container
        dragMode: 'move',
        autoCropArea: 0.8,  // Area inicial de 80% para dar espaco para expansao
        restore: false,
        guides: true,
        center: true,
        highlight: false,
        cropBoxMovable: true,
        cropBoxResizable: true,
        toggleDragModeOnDblclick: false,
        minContainerWidth: 200,  // Container minimo
        minContainerHeight: 200,
        ready: function() {
            // Ajustar tamanho baseado nas dimensoes reais do modal agora visivel
            ajustarTamanhoContainerCortador(modalId);
            // Chamar callback se fornecido
            if (onReady && typeof onReady === 'function') {
                onReady();
            }
        },
        crop: function(event) {
            // Atualizar preview em tempo real
            if (previewImage) atualizarPreview(modalId, previewImage);
        }
    });
}

/**
 * Carrega uma imagem de um arquivo File e inicializa o cropper
 * Funcao publica que pode ser chamada externamente
 *
 * @param {string} modalId - ID do modal
 * @param {File} file - Arquivo de imagem
 * @param {number} aspectRatio - Proporcao do crop (default: 1.0)
 * @param {number} maxFileSizeMB - Tamanho maximo em MB (default: 5)
 * @param {Function} onReady - Callback chamado quando o cropper estiver pronto (opcional)
 */
function carregarImagemDeArquivo(modalId, file, aspectRatio = 1.0, maxFileSizeMB = 5, onReady = null) {
    const uploadSection = document.getElementById(`upload-section-${modalId}`);
    const cropperContainer = document.getElementById(`cropper-container-${modalId}`);
    const cropperImage = document.getElementById(`cropper-image-${modalId}`);
    const previewImage = document.getElementById(`preview-${modalId}`);
    const btnSubmit = document.getElementById(`btn-submit-${modalId}`);

    if (!file) return;

    // Validar tamanho
    const maxBytes = maxFileSizeMB * 1024 * 1024;
    if (file.size > maxBytes) {
        window.App.Modal.showError(
            `O arquivo selecionado e muito grande. Tamanho maximo permitido: ${maxFileSizeMB}MB.`,
            'Arquivo Muito Grande'
        );
        return;
    }

    // Validar tipo
    if (!file.type.startsWith('image/')) {
        window.App.Modal.showError(
            'Por favor, selecione um arquivo de imagem valido (JPG, PNG, GIF, etc.).',
            'Tipo de Arquivo Invalido'
        );
        return;
    }

    // Ler arquivo
    const reader = new FileReader();
    reader.onload = function(event) {
        // Ocultar secao de upload e mostrar cropper
        if (uploadSection) uploadSection.classList.add('d-none');
        if (cropperContainer) cropperContainer.classList.remove('d-none');
        if (btnSubmit) btnSubmit.disabled = false;

        // Definir imagem no cropper
        cropperImage.src = event.target.result;

        // Destruir cropper anterior se existir
        if (instanciasCortador[modalId]) {
            instanciasCortador[modalId].destroy();
        }

        // Inicializar Cropper.js
        instanciasCortador[modalId] = new Cropper(cropperImage, {
            aspectRatio: aspectRatio,
            viewMode: 1,  // Permite crop box crescer ate os limites do container
            dragMode: 'move',
            autoCropArea: 0.8,  // Area inicial de 80% para dar espaco para expansao
            restore: false,
            guides: true,
            center: true,
            highlight: false,
            cropBoxMovable: true,
            cropBoxResizable: true,
            toggleDragModeOnDblclick: false,
            minContainerWidth: 200,  // Container minimo
            minContainerHeight: 200,
            ready: function() {
                // Aguardar 100ms para garantir que o DOM foi atualizado
                setTimeout(() => {
                    ajustarTamanhoContainerCortador(modalId);
                    // Chamar callback se fornecido
                    if (onReady && typeof onReady === 'function') {
                        onReady();
                    }
                }, 100);
            },
            crop: function(event) {
                // Atualizar preview em tempo real
                if (previewImage) atualizarPreview(modalId, previewImage);
            }
        });
    };
    reader.readAsDataURL(file);
}

/**
 * Inicializa o cropper para um modal especifico
 */
function inicializarCortadorImagem(modalId, aspectRatio = 1.0, maxFileSizeMB = 5) {
    const inputFile = document.getElementById(`input-${modalId}`);
    const uploadSection = document.getElementById(`upload-section-${modalId}`);
    const cropperContainer = document.getElementById(`cropper-container-${modalId}`);
    const cropperImage = document.getElementById(`cropper-image-${modalId}`);
    const previewImage = document.getElementById(`preview-${modalId}`);
    const btnSubmit = document.getElementById(`btn-submit-${modalId}`);
    const fotoBase64Input = document.getElementById(`foto-base64-${modalId}`);
    const form = document.getElementById(`form-${modalId}`);

    if (!cropperContainer || !cropperImage) {
        console.error(`Elementos do modal ${modalId} nao encontrados`);
        return;
    }

    // Evento: Selecao de arquivo (apenas se input file existir)
    if (inputFile) {
        inputFile.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                carregarImagemDeArquivo(modalId, file, aspectRatio, maxFileSizeMB);
            }
        });
    }

    // Evento: Submit do formulario
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            if (!instanciasCortador[modalId]) {
                window.App.Modal.showWarning('Por favor, selecione uma imagem antes de salvar.', 'Nenhuma Imagem Selecionada');
                return;
            }

            // Obter canvas da imagem cropada
            const canvas = instanciasCortador[modalId].getCroppedCanvas({
                maxWidth: 1000,
                maxHeight: 1000,
                fillColor: '#fff',
                imageSmoothingEnabled: true,
                imageSmoothingQuality: 'high'
            });

            // Converter para base64 (JPEG com qualidade 90)
            const base64 = canvas.toDataURL('image/jpeg', 0.9);

            // Definir no campo hidden
            fotoBase64Input.value = base64;

            // Submeter formulario
            form.submit();
        });
    }

    // Evento: Reset ao fechar modal
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        modalElement.addEventListener('hidden.bs.modal', function() {
            resetarCortador(modalId, uploadSection, cropperContainer, inputFile, btnSubmit);
        });
    }
}

/**
 * Calcula a altura disponivel para a area de imagem do cropper
 * Mede os elementos reais do DOM para precisao
 */
function calcularAlturaImagemCortador(modalId) {
    // Obter elementos
    const modalElement = document.getElementById(modalId);
    const modalHeader = modalElement?.querySelector('.modal-header');
    const modalBody = modalElement?.querySelector('.modal-body');
    const controlsArea = document.getElementById(`cropper-controls-area-${modalId}`);

    if (!modalElement || !modalHeader || !modalBody || !controlsArea) {
        console.warn(`Elementos do modal ${modalId} nao encontrados para calculo de altura`);
        return 300; // Valor padrao de fallback
    }

    // Medir alturas reais
    const viewportHeight = window.innerHeight;
    const headerHeight = modalHeader.offsetHeight;
    const controlsHeight = controlsArea.offsetHeight;

    // Pegar padding do modal-body
    const bodyStyles = window.getComputedStyle(modalBody);
    const bodyPaddingTop = parseFloat(bodyStyles.paddingTop) || 0;
    const bodyPaddingBottom = parseFloat(bodyStyles.paddingBottom) || 0;

    // Margem de seguranca para espacamentos internos e scroll
    const safetyMargin = 100;

    // Calcular altura disponivel
    const availableHeight = viewportHeight - headerHeight - controlsHeight - bodyPaddingTop - bodyPaddingBottom - safetyMargin;

    // Aplicar limites: minimo 200px, maximo 600px
    const finalHeight = Math.max(200, Math.min(600, availableHeight));

    return finalHeight;
}

/**
 * Ajusta o tamanho do container do cropper dinamicamente
 */
function ajustarTamanhoContainerCortador(modalId) {
    const cropperImageArea = document.getElementById(`cropper-image-area-${modalId}`);
    if (!cropperImageArea) return;

    // Calcular altura usando medicao real dos elementos
    const calculatedHeight = calcularAlturaImagemCortador(modalId);

    // Aplicar altura calculada
    cropperImageArea.style.height = `${calculatedHeight}px`;

    // Forcar o cropper a recalcular suas dimensoes
    if (instanciasCortador[modalId]) {
        instanciasCortador[modalId].resize();
    }
}

/**
 * Atualiza o preview da imagem cropada
 */
function atualizarPreview(modalId, previewImage) {
    if (!instanciasCortador[modalId]) return;

    const canvas = instanciasCortador[modalId].getCroppedCanvas({
        width: 120,
        height: 120,
        imageSmoothingEnabled: true,
        imageSmoothingQuality: 'high'
    });

    if (canvas) {
        previewImage.src = canvas.toDataURL('image/jpeg', 0.9);
    }
}

/**
 * Reseta o cropper para estado inicial
 */
function resetarCortador(modalId, uploadSection, cropperContainer, inputFile, btnSubmit) {
    // Destruir cropper
    if (instanciasCortador[modalId]) {
        instanciasCortador[modalId].destroy();
        delete instanciasCortador[modalId];
    }

    // Resetar UI para estado inicial
    if (uploadSection) uploadSection.classList.remove('d-none');
    if (cropperContainer) cropperContainer.classList.add('d-none');
    if (inputFile) inputFile.value = '';
    if (btnSubmit) btnSubmit.disabled = true;
}

/**
 * Auto-inicializacao de modais com configuracao
 */
document.addEventListener('DOMContentLoaded', function() {
    // Procurar por todas as configuracoes de modal no window
    for (const key in window) {
        if (key.startsWith('config_modal')) {
            const config = window[key];
            if (config && config.modalId) {
                inicializarCortadorImagem(
                    config.modalId,
                    config.aspectRatio || 1.0,
                    config.maxFileSizeMB || 5
                );
            }
        }
    }

    // Ajustar tamanho do cropper quando a janela for redimensionada (com debounce)
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            for (const modalId in instanciasCortador) {
                if (instanciasCortador[modalId]) {
                    ajustarTamanhoContainerCortador(modalId);
                }
            }
        }, 150);
    });
});

/**
 * Inicializar namespace global do app
 */
window.App = window.App || {};
window.App.CortadorImagem = window.App.CortadorImagem || {};

/**
 * API publica do modulo CortadorImagem
 */
window.App.CortadorImagem.instancias = instanciasCortador;
window.App.CortadorImagem.prepararImagem = prepararImagemParaModal;
window.App.CortadorImagem.inicializarNoModal = inicializarCortadorNoModal;
window.App.CortadorImagem.carregarDeArquivo = carregarImagemDeArquivo;
window.App.CortadorImagem.inicializar = inicializarCortadorImagem;
window.App.CortadorImagem.calcularAltura = calcularAlturaImagemCortador;
window.App.CortadorImagem.ajustarContainer = ajustarTamanhoContainerCortador;
window.App.CortadorImagem.atualizarPreview = atualizarPreview;
window.App.CortadorImagem.resetar = resetarCortador;

// Expor funcoes no escopo global
window.instanciasCortador = instanciasCortador;
window.prepararImagemParaModal = prepararImagemParaModal;
window.inicializarCortadorNoModal = inicializarCortadorNoModal;
window.carregarImagemDeArquivo = carregarImagemDeArquivo;
window.inicializarCortadorImagem = inicializarCortadorImagem;
window.calcularAlturaImagemCortador = calcularAlturaImagemCortador;
window.ajustarTamanhoContainerCortador = ajustarTamanhoContainerCortador;
window.atualizarPreview = atualizarPreview;
window.resetarCortador = resetarCortador;

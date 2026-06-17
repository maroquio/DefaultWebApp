/**
 * Chat Widget - Sistema de chat em tempo real com SSE
 * Estilo WhatsApp Web: lista de conversas à esquerda, mensagens à direita
 */

const chatWidget = (() => {
    // Estado do widget
    let eventSource = null;
    let conversaAtual = null;
    let conversasOffset = 0;
    let debounceTimer = null;
    let mensagensOffset = 0;
    let carregandoMensagens = false;
    let todasMensagensCarregadas = false;

    // Elementos do DOM
    const elementos = {
        button: null,
        panel: null,
        badge: null,
        userSearch: null,
        searchSuggestions: null,
        conversationsList: null,
        messagesContainer: null,
        messageInput: null,
        messageForm: null
    };

    /**
     * Inicializa o widget
     */
    function init() {
        // Cachear elementos do DOM
        elementos.button = document.getElementById('chat-widget-button');
        elementos.panel = document.getElementById('chat-widget-panel');
        elementos.badge = document.getElementById('chat-badge');
        elementos.userSearch = document.getElementById('chat-user-search');
        elementos.searchSuggestions = document.getElementById('chat-search-suggestions');
        elementos.conversationsList = document.getElementById('chat-conversations-list');
        elementos.messagesContainer = document.getElementById('chat-messages-container');
        elementos.messageInput = document.getElementById('chat-message-input');
        elementos.messageForm = document.getElementById('chat-message-form');

        // Conectar SSE
        conectarSSE();

        // Carregar conversas iniciais
        carregarConversas(0);

        // Atualizar contador de não lidas
        atualizarContadorNaoLidas();

        // Event listeners
        elementos.userSearch.addEventListener('input', handleBuscaUsuario);
        elementos.messageInput.addEventListener('keydown', handleMessageInputKeydown);
        elementos.messagesContainer.addEventListener('scroll', handleScrollMensagens);
    }

    /**
     * Conecta ao stream SSE
     */
    function conectarSSE() {
        eventSource = new EventSource('/chat/stream');

        eventSource.onmessage = (event) => {
            const mensagem = JSON.parse(event.data);
            processarMensagemSSE(mensagem);
        };

        eventSource.onerror = (error) => {
            console.error('[Chat SSE] Erro na conexão:', error);
            // EventSource reconecta automaticamente
        };
    }

    /**
     * Processa mensagem recebida via SSE
     */
    function processarMensagemSSE(mensagem) {
        if (mensagem.tipo === 'nova_mensagem') {
            // Se for da conversa atual, adicionar na tela
            if (conversaAtual && mensagem.sala_id === conversaAtual.sala_id) {
                renderizarMensagem(mensagem.mensagem, false);

                // Scroll para o final para mostrar nova mensagem
                elementos.messagesContainer.scrollTop = elementos.messagesContainer.scrollHeight;

                // Marcar como lida automaticamente
                marcarComoLidas(mensagem.sala_id);
            }

            // Atualizar lista de conversas
            carregarConversas(0);

            // Atualizar contador
            atualizarContadorNaoLidas();
        } else if (mensagem.tipo === 'atualizar_contador') {
            // Atualizar contador de não lidas
            atualizarContadorNaoLidas();
        }
    }

    /**
     * Carrega lista de conversas
     */
    async function carregarConversas(offset) {
        try {
            const response = await fetch(`/chat/conversas?limit=12&offset=${offset}`);
            const conversas = await response.json();

            if (offset === 0) {
                elementos.conversationsList.innerHTML = '';
                conversasOffset = 0;
            }

            renderizarConversas(conversas);
            conversasOffset += conversas.length;

        } catch (error) {
            console.error('[Chat] Erro ao carregar conversas:', error);
        }
    }

    /**
     * Renderiza lista de conversas
     */
    function renderizarConversas(conversas) {
        conversas.forEach(conversa => {
            const item = document.createElement('div');
            item.className = 'chat-conversation-item p-2 border-bottom d-flex align-items-center';
            item.setAttribute('data-sala-id', conversa.sala_id);

            if (conversaAtual && conversaAtual.sala_id === conversa.sala_id) {
                item.classList.add('active');
            }

            // Foto do usuário
            const foto = document.createElement('img');
            foto.src = conversa.outro_usuario.foto_url;
            foto.alt = conversa.outro_usuario.nome;
            foto.className = 'rounded-circle me-2';
            foto.style.width = '40px';
            foto.style.height = '40px';
            foto.style.objectFit = 'cover';

            // Conteúdo
            const content = document.createElement('div');
            content.className = 'flex-grow-1 overflow-hidden';

            const nome = document.createElement('div');
            nome.className = 'fw-bold small text-truncate';
            nome.textContent = conversa.outro_usuario.nome;

            const ultimaMensagem = document.createElement('div');
            ultimaMensagem.className = 'text-muted small text-truncate';
            ultimaMensagem.textContent = conversa.ultima_mensagem
                ? conversa.ultima_mensagem.mensagem
                : 'Sem mensagens';

            content.appendChild(nome);
            content.appendChild(ultimaMensagem);

            // Badge de não lidas
            if (conversa.nao_lidas > 0) {
                const badge = document.createElement('span');
                badge.className = 'badge bg-danger rounded-pill ms-2';
                badge.textContent = conversa.nao_lidas;
                item.appendChild(foto);
                item.appendChild(content);
                item.appendChild(badge);
            } else {
                item.appendChild(foto);
                item.appendChild(content);
            }

            // Click handler
            item.addEventListener('click', () => abrirChat(conversa));

            elementos.conversationsList.appendChild(item);
        });
    }

    /**
     * Handle busca de usuário com debounce
     */
    function handleBuscaUsuario(e) {
        const termo = e.target.value.trim();

        // Limpar timer anterior
        if (debounceTimer) {
            clearTimeout(debounceTimer);
        }

        if (termo.length < 2) {
            elementos.searchSuggestions.style.display = 'none';
            return;
        }

        // Debounce de 300ms
        debounceTimer = setTimeout(() => {
            buscarUsuarios(termo);
        }, 300);
    }

    /**
     * Busca usuários
     */
    async function buscarUsuarios(termo) {
        try {
            const response = await fetch(`/chat/usuarios/buscar?q=${encodeURIComponent(termo)}`);
            const usuarios = await response.json();

            renderizarSugestoesUsuarios(usuarios);

        } catch (error) {
            console.error('[Chat] Erro ao buscar usuários:', error);
        }
    }

    /**
     * Renderiza sugestões de usuários
     */
    function renderizarSugestoesUsuarios(usuarios) {
        elementos.searchSuggestions.innerHTML = '';

        if (usuarios.length === 0) {
            elementos.searchSuggestions.style.display = 'none';
            return;
        }

        usuarios.forEach(usuario => {
            const item = document.createElement('div');
            item.className = 'chat-user-suggestion p-2 d-flex align-items-center';

            const foto = document.createElement('img');
            foto.src = usuario.foto_url;
            foto.alt = usuario.nome;
            foto.className = 'rounded-circle me-2';
            foto.style.width = '32px';
            foto.style.height = '32px';
            foto.style.objectFit = 'cover';

            const content = document.createElement('div');
            content.className = 'flex-grow-1';

            const nome = document.createElement('div');
            nome.className = 'fw-bold small';
            nome.textContent = usuario.nome;

            const email = document.createElement('div');
            email.className = 'text-muted';
            email.style.fontSize = '0.75rem';
            email.textContent = usuario.email;

            content.appendChild(nome);
            content.appendChild(email);

            item.appendChild(foto);
            item.appendChild(content);

            // Click handler
            item.addEventListener('click', () => {
                criarOuAbrirSala(usuario);
                elementos.userSearch.value = '';
                elementos.searchSuggestions.style.display = 'none';
            });

            elementos.searchSuggestions.appendChild(item);
        });

        elementos.searchSuggestions.style.display = 'block';
    }

    /**
     * Cria ou abre sala com usuário
     */
    async function criarOuAbrirSala(usuario) {
        try {
            const formData = new FormData();
            formData.append('outro_usuario_id', usuario.id);

            const response = await fetch('/chat/salas', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Erro ao criar sala');
            }

            const data = await response.json();
            const salaId = data.sala_id;

            // Recarregar conversas
            await carregarConversas(0);

            // Abrir chat
            abrirChat({
                sala_id: salaId,
                outro_usuario: usuario,
                ultima_mensagem: null,
                nao_lidas: 0
            });

        } catch (error) {
            console.error('[Chat] Erro ao criar/abrir sala:', error);
            window.App.Modal.showError('Erro ao iniciar conversa');
        }
    }

    /**
     * Abre um chat específico
     */
    async function abrirChat(conversa) {
        conversaAtual = conversa;

        // Resetar estado de paginação
        mensagensOffset = 0;
        todasMensagensCarregadas = false;

        // Marcar como ativa na lista
        document.querySelectorAll('.chat-conversation-item').forEach(item => {
            if (item.getAttribute('data-sala-id') === conversa.sala_id) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        // Carregar mensagens iniciais
        await carregarMensagens(conversa.sala_id, true);

        // Marcar como lidas
        await marcarComoLidas(conversa.sala_id);

        // Focar input
        elementos.messageInput.focus();
    }

    /**
     * Carrega mensagens de uma sala
     * @param {string} salaId - ID da sala
     * @param {boolean} inicial - Se é o carregamento inicial (limpa container)
     */
    async function carregarMensagens(salaId, inicial = false) {
        if (carregandoMensagens || todasMensagensCarregadas) {
            return;
        }

        carregandoMensagens = true;

        try {
            const limit = 24;
            const response = await fetch(`/chat/mensagens/${salaId}?limit=${limit}&offset=${mensagensOffset}`);
            const mensagens = await response.json();

            // Se retornou menos que o limite, não há mais mensagens
            if (mensagens.length < limit) {
                todasMensagensCarregadas = true;
            }

            if (inicial) {
                elementos.messagesContainer.innerHTML = '';
                mensagensOffset = 0;
            }

            // Salvar posição de scroll antes de adicionar
            const alturaAntes = elementos.messagesContainer.scrollHeight;
            const scrollAntes = elementos.messagesContainer.scrollTop;

            // Renderizar mensagens na ordem (mais antigas primeiro)
            if (inicial) {
                // Carregamento inicial: adicionar no final
                mensagens.forEach(msg => renderizarMensagem(msg, false));

                // Scroll para o final (mensagens mais recentes)
                elementos.messagesContainer.scrollTop = elementos.messagesContainer.scrollHeight;
            } else {
                // Carregamento paginado: adicionar no início (prepend)
                // Inverter ordem para adicionar corretamente
                for (let i = mensagens.length - 1; i >= 0; i--) {
                    renderizarMensagem(mensagens[i], true);
                }

                // Manter posição de scroll relativa
                const alturaDepois = elementos.messagesContainer.scrollHeight;
                elementos.messagesContainer.scrollTop = scrollAntes + (alturaDepois - alturaAntes);
            }

            mensagensOffset += mensagens.length;

        } catch (error) {
            console.error('[Chat] Erro ao carregar mensagens:', error);
        } finally {
            carregandoMensagens = false;
        }
    }

    /**
     * Renderiza uma mensagem
     * @param {Object} msg - Objeto da mensagem
     * @param {boolean} prepend - Se true, adiciona no início; se false, adiciona no final
     */
    function renderizarMensagem(msg, prepend = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'd-flex mb-2';

        const isEnviada = msg.usuario_id === parseInt(document.body.dataset.usuarioId || '0');

        if (isEnviada) {
            msgDiv.classList.add('justify-content-end');
        }

        const bolha = document.createElement('div');
        bolha.className = isEnviada ? 'chat-message-sent p-2' : 'chat-message-received p-2';

        const texto = document.createElement('div');
        texto.innerHTML = aplicarFormatacaoMarkdown(msg.mensagem);

        const hora = document.createElement('div');
        hora.className = 'text-end mt-1 small';
        hora.style.fontSize = '0.7rem';
        hora.style.opacity = '0.7';
        hora.textContent = formatarHora(msg.data_envio);

        bolha.appendChild(texto);
        bolha.appendChild(hora);
        msgDiv.appendChild(bolha);

        if (prepend) {
            // Adicionar no início (mensagens antigas)
            elementos.messagesContainer.insertBefore(msgDiv, elementos.messagesContainer.firstChild);
        } else {
            // Adicionar no final (mensagens novas)
            elementos.messagesContainer.appendChild(msgDiv);
        }
    }

    /**
     * Escapa HTML de forma segura usando DOM (previne XSS)
     * Usa o próprio browser para garantir escaping correto
     */
    function escapeHtml(texto) {
        const div = document.createElement('div');
        div.textContent = texto;
        return div.innerHTML;
    }

    /**
     * Aplica formatação markdown lite
     * Seguro contra XSS: escapa HTML antes de aplicar formatação
     */
    function aplicarFormatacaoMarkdown(texto) {
        // Escapar HTML usando DOM (mais seguro que regex)
        texto = escapeHtml(texto);

        // ***texto*** = negrito + itálico
        texto = texto.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');

        // **texto** = negrito
        texto = texto.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

        // *texto* = itálico
        texto = texto.replace(/\*(.+?)\*/g, '<em>$1</em>');

        // Quebras de linha
        texto = texto.replace(/\n/g, '<br>');

        return texto;
    }

    /**
     * Formata timestamp para hora
     */
    function formatarHora(timestamp) {
        const data = new Date(timestamp);
        return data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    }

    /**
     * Handle scroll no container de mensagens
     * Carrega mais mensagens quando o usuário rola até o topo
     */
    function handleScrollMensagens(e) {
        const container = e.target;

        // Se scroll está próximo do topo (menos de 50px do topo)
        if (container.scrollTop < 50 && conversaAtual && !carregandoMensagens && !todasMensagensCarregadas) {
            carregarMensagens(conversaAtual.sala_id, false);
        }
    }

    /**
     * Handle keydown no input de mensagem
     */
    function handleMessageInputKeydown(e) {
        // Enter sem Shift = enviar
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            elementos.messageForm.dispatchEvent(new Event('submit'));
        }
        // Shift+Enter = quebra de linha (comportamento padrão do textarea)
    }

    /**
     * Envia mensagem
     */
    async function enviarMensagem(event) {
        event.preventDefault();

        if (!conversaAtual) {
            return;
        }

        const mensagem = elementos.messageInput.value.trim();
        if (!mensagem) {
            return;
        }

        try {
            const formData = new FormData();
            formData.append('sala_id', conversaAtual.sala_id);
            formData.append('mensagem', mensagem);

            const response = await fetch('/chat/mensagens', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Erro ao enviar mensagem');
            }

            // Limpar input
            elementos.messageInput.value = '';

            // Mensagem será adicionada via SSE

        } catch (error) {
            console.error('[Chat] Erro ao enviar mensagem:', error);
            window.App.Modal.showError('Erro ao enviar mensagem');
        }
    }

    /**
     * Marca mensagens como lidas
     */
    async function marcarComoLidas(salaId) {
        try {
            await fetch(`/chat/mensagens/lidas/${salaId}`, {
                method: 'POST'
            });

            // Atualizar contador
            atualizarContadorNaoLidas();

        } catch (error) {
            console.error('[Chat] Erro ao marcar como lidas:', error);
        }
    }

    /**
     * Atualiza contador de não lidas
     */
    async function atualizarContadorNaoLidas() {
        try {
            const response = await fetch('/chat/mensagens/nao-lidas/total');
            const data = await response.json();

            const total = data.total;

            if (total > 0) {
                elementos.badge.textContent = total > 99 ? '99+' : total;
                elementos.badge.style.display = 'inline-block';
            } else {
                elementos.badge.style.display = 'none';
            }

        } catch (error) {
            console.error('[Chat] Erro ao atualizar contador:', error);
        }
    }


    /**
     * Destrói o widget
     */
    function destruir() {
        if (eventSource) {
            eventSource.close();
        }
    }

    // Cleanup ao sair da página
    window.addEventListener('beforeunload', destruir);

    // API pública
    return {
        init,
        destruir,
        enviarMensagem,
        carregarMaisConversas: () => carregarConversas(conversasOffset)
    };
})();

// Expor globalmente
window.chatWidget = chatWidget;

/**
 * Funções globais chamadas pelo HTML
 */

function toggleChatWidget() {
    const panel = document.getElementById('chat-widget-panel');
    const button = document.getElementById('chat-widget-button');

    if (panel.style.display === 'none' || !panel.style.display) {
        panel.style.display = 'block';
        panel.classList.add('show');
        button.style.display = 'none';

        // Pedir permissão de notificações (futuro)
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    } else {
        panel.style.display = 'none';
        panel.classList.remove('show');
        button.style.display = 'flex';
    }
}

function carregarMaisConversas() {
    window.chatWidget.carregarMaisConversas();
}

function enviarMensagem(event) {
    window.chatWidget.enviarMensagem(event);
}

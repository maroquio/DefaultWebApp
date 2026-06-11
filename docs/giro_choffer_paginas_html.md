# Giro Choffer — Lista de páginas HTML necessárias

Este documento reúne as páginas HTML recomendadas para implementar a aplicação **Giro Choffer**, com base nos requisitos funcionais, perfis de usuário, diferenciais e casos de uso descritos na documentação do projeto.

A aplicação é uma plataforma logística para conectar **empresas/transportadoras** e **motoristas autônomos**, centralizando publicação de cargas, busca de fretes, comunicação, pagamentos, histórico de viagens, avaliações e administração da plataforma.

---

## 1. Páginas públicas

| Página HTML | Nome sugerido | Descrição |
|---|---|---|
| Página inicial | `public/home.html` | Apresentação do Giro Choffer, explicação da proposta, chamadas para cadastro de motorista e empresa, benefícios da plataforma, diferenciais, botão de login, botão de criação de conta e seção de newsletter. Atende ao RF1 e RF5. |
| Como funciona | `public/como_funciona.html` | Explicação em etapas: empresa publica carga, motorista encontra frete compatível, comunicação ocorre pela plataforma, pagamento/negociação é centralizado e a viagem é avaliada. |
| Planos | `public/planos.html` | Comparação dos planos Free, Starter e Pro, com preço, quantidade de gestores, limite de cargas publicadas por mês, recursos disponíveis e botão para assinar. |
| Termos de uso | `public/termos.html` | Regras de uso da plataforma, responsabilidades de motoristas e empresas, regras de conduta, bloqueio, suspensão e banimento. |
| Política de privacidade | `public/privacidade.html` | Explicação sobre coleta, uso e proteção dos dados pessoais, especialmente por envolver CPF, CNPJ, dados de veículos, cargas, viagens e pagamentos. |
| Newsletter | `public/newsletter.html` | Página simples para inscrição de e-mail, confirmação de inscrição e mensagens de validação. Pode ser integrada à home, mas também pode existir separadamente. |

---

## 2. Páginas de autenticação e cadastro

| Página HTML | Nome sugerido | Descrição |
|---|---|---|
| Login | `auth/login.html` | Formulário de e-mail e senha, botão de entrada, links para criar conta e recuperar senha. Deve servir para motorista, empresa e administrador. Atende ao RF6, RF14 e RF24. |
| Escolha do tipo de conta | `auth/escolher_perfil.html` | Tela para o usuário escolher se deseja se cadastrar como **motorista** ou **empresa/transportadora**. Atende ao RF3. |
| Validação de CPF/CNPJ | `auth/validar_documento.html` | Campo para CPF ou CNPJ, validação inicial e mensagens de erro. Para empresas, deve usar a integração com BrasilAPI. Atende ao RF4. |
| Cadastro de motorista | `auth/cadastro_motorista.html` | Formulário com nome, CPF, telefone, e-mail, senha, dados do veículo, tipo de carroceria, capacidade de carga, rotas de interesse e documentos necessários. |
| Cadastro de empresa/transportadora | `auth/cadastro_empresa.html` | Formulário com CNPJ, razão social, nome fantasia, responsável, telefone, e-mail corporativo, senha, endereço e dados de cobrança. Deve usar consulta de CNPJ e CEP. |
| Recuperação de senha | `auth/recuperar_senha.html` | Formulário para informar e-mail e solicitar link/token de recuperação. Atende ao RF7 e RF15. |
| Redefinição de senha | `auth/redefinir_senha.html` | Campos para nova senha e confirmação da nova senha. |
| Confirmação de cadastro | `auth/confirmar_cadastro.html` | Mensagem orientando o usuário a confirmar o e-mail ou aguardar verificação, se aplicável. |
| Verificação de conta | `auth/verificacao_conta.html` | Página para envio de documentos ou solicitação de verificação de identidade/cadastro. Está alinhada ao caso de uso “Solicitar Verificação”, presente no diagrama do perfil usuário. |

---

## 3. Páginas comuns para usuários autenticados

Estas páginas servem para motorista, empresa/transportadora e administrador, com ajustes conforme o perfil.

| Página HTML | Nome sugerido | Descrição |
|---|---|---|
| Dashboard geral do usuário | `usuario/dashboard.html` | Página de redirecionamento ou painel inicial com atalhos conforme o perfil logado. |
| Meu perfil | `usuario/perfil.html` | Dados cadastrais, telefone, e-mail, documento, endereço, status da conta e opção de editar dados. Atende ao caso de uso “Alterar Dados de Perfil”. |
| Editar perfil | `usuario/editar_perfil.html` | Formulário para atualização dos dados do usuário. |
| Alterar senha | `usuario/alterar_senha.html` | Campos para senha atual, nova senha e confirmação. |
| Notificações | `usuario/notificacoes.html` | Lista de alertas sobre novas cargas, mensagens, aceite de motorista, alterações de status, pagamentos e avaliações. |
| Chamados de suporte | `usuario/chamados.html` | Lista de chamados abertos pelo usuário, status e respostas da administração. |
| Abrir chamado | `usuario/abrir_chamado.html` | Formulário para relatar problemas, dúvidas, denúncias ou dificuldades de uso. |
| Detalhe do chamado | `usuario/detalhe_chamado.html` | Conversa entre usuário e suporte, histórico de respostas e situação do chamado. |

---

## 4. Área do motorista

O motorista precisa buscar cargas, visualizar detalhes, aceitar carga, conversar com a empresa, atualizar status da viagem, consultar histórico, ganhos e avaliações.

| Página HTML | Nome sugerido | Descrição |
|---|---|---|
| Dashboard do motorista | `motorista/dashboard.html` | Resumo com cargas compatíveis, viagens em andamento, ganhos do mês, média de avaliações e notificações recentes. |
| Mural de cargas disponíveis | `motorista/cargas.html` | Lista de cargas disponíveis compatíveis com o veículo/carroceria do motorista, busca por palavras-chave e filtros por origem/destino. Atende ao RF8, RF9 e RF10. |
| Detalhes da carga | `motorista/detalhe_carga.html` | Origem, destino, data, valor do frete, tipo de carga, tags, tipo de veículo exigido, empresa responsável, botão para aceitar carga e botão para enviar mensagem. |
| Aceitar carga | `motorista/aceitar_carga.html` | Página ou modal de confirmação antes de aceitar o frete, mostrando responsabilidades, valor e dados essenciais da carga. |
| Minhas viagens | `motorista/viagens.html` | Lista de viagens aceitas, em andamento, concluídas ou canceladas. |
| Detalhes da viagem | `motorista/detalhe_viagem.html` | Dados completos da carga, empresa, rota, status atual, mensagens, pagamento e botão para atualizar status. |
| Atualizar status da viagem | `motorista/atualizar_status.html` | Interface simples, com botões grandes, para marcar etapas como “aceita”, “a caminho da coleta”, “coletada”, “em trânsito”, “entregue” e “finalizada”. |
| Histórico de viagens | `motorista/historico_viagens.html` | Viagens concluídas, datas, empresas, rotas, valores recebidos e avaliações. Atende ao RF11. |
| Ganhos do mês | `motorista/ganhos.html` | Total financeiro do mês vigente, viagens pagas, pendentes, canceladas e gráfico/resumo dos ganhos. Atende ao RF12. |
| Minhas avaliações | `motorista/avaliacoes.html` | Média de notas, comentários recebidos das empresas e histórico de avaliações. Atende ao RF13. |
| Meu veículo | `motorista/veiculo.html` | Dados do veículo cadastrado: tipo, placa, capacidade, tipo de carroceria, documentos e status de validação. |
| Editar veículo | `motorista/editar_veiculo.html` | Formulário para atualização dos dados do veículo, importante para o match de cargas. |
| Rotas de interesse | `motorista/rotas.html` | Cadastro de cidades, estados ou trajetos preferenciais, inclusive rota de retorno. Relaciona-se ao diferencial de foco na rota de retorno. |
| Modo estrada | `motorista/modo_estrada.html` | Versão de alta legibilidade para uso rápido, com contraste forte, fontes grandes e botões simplificados, alinhada ao diferencial de “Modo Estrada”. |

---

## 5. Área da empresa/transportadora

A empresa deve publicar cargas, editar, excluir, agendar, consultar métricas, buscar motoristas, enviar mensagens, aceitar/rejeitar motoristas e avaliar o serviço.

| Página HTML | Nome sugerido | Descrição |
|---|---|---|
| Dashboard da empresa | `empresa/dashboard.html` | Resumo com cargas publicadas, cargas aguardando motorista, viagens em andamento, motoristas favoritos, visualizações e tempo médio de aceite. |
| Minhas cargas | `empresa/cargas.html` | Lista das cargas criadas pela empresa, com status, origem, destino, data, valor, visualizações e ações de editar, cancelar ou excluir. |
| Publicar nova carga | `empresa/nova_carga.html` | Formulário com origem, destino, data, valor do frete, tipo de veículo/carroceria, descrição, peso, volume e tags como “Carga Frágil” ou “Refrigerada”. Atende ao RF16, RF17 e RF18. |
| Editar carga | `empresa/editar_carga.html` | Formulário para alterar informações de uma carga ainda com status “Aguardando Motorista”. Atende ao RF20. |
| Detalhes da carga | `empresa/detalhe_carga.html` | Dados completos da carga, motoristas interessados, motorista aceito, mensagens, visualizações, status e ações disponíveis. |
| Agendar publicação | `empresa/agendar_carga.html` | Tela para definir data e hora futuras para uma carga aparecer no mural dos motoristas. Atende ao RF19. |
| Cargas agendadas | `empresa/cargas_agendadas.html` | Lista de cargas com publicação futura, permitindo editar ou cancelar o agendamento. |
| Excluir/cancelar carga | `empresa/cancelar_carga.html` | Confirmação antes de excluir ou cancelar carga que ainda não foi aceita. Atende ao RF21. |
| Métricas das cargas | `empresa/metricas_cargas.html` | Total de visualizações por carga, tempo médio para aceite, desempenho das publicações e relatórios básicos. Atende ao RF22 e RF23. |
| Buscar motoristas | `empresa/buscar_motoristas.html` | Busca de motoristas por localização, tipo de veículo, carroceria, avaliação, disponibilidade e rotas de interesse. |
| Perfil do motorista | `empresa/detalhe_motorista.html` | Dados públicos do motorista, veículo, capacidade, tipo de carroceria, média de avaliações, histórico resumido e botão para enviar mensagem ou solicitar motorista. |
| Motoristas favoritos | `empresa/motoristas_favoritos.html` | Lista de motoristas marcados como favoritos pela empresa. |
| Solicitações de motoristas | `empresa/solicitacoes_motoristas.html` | Lista de motoristas interessados ou solicitados para cargas, com opções de aceitar ou rejeitar. |
| Avaliar motorista | `empresa/avaliar_motorista.html` | Formulário para nota e comentário após conclusão do frete. |
| Relatórios | `empresa/relatorios.html` | Relatórios de cargas, viagens, valores, motoristas contratados, visualizações e tempo de aceite. |
| Plano e assinatura | `empresa/plano.html` | Plano atual, limite de publicações, quantidade de gestores, cobranças, botão de upgrade/downgrade e acesso ao pagamento. |

---

## 6. Comunicação, contratação e pagamento

| Página HTML | Nome sugerido | Descrição |
|---|---|---|
| Lista de conversas | `chat/conversas.html` | Lista de conversas entre motoristas e empresas, associadas a cargas ou viagens. |
| Conversa | `chat/conversa.html` | Chat contextualizado com identificação da carga, mensagens, anexos simples e histórico da negociação. |
| Checkout do plano | `pagamento/checkout_plano.html` | Resumo do plano escolhido, valor, dados da empresa e integração com Mercado Pago. |
| Resultado do pagamento | `pagamento/resultado.html` | Confirmação de pagamento aprovado, pendente ou recusado. |
| Pagamentos de frete | `pagamento/fretes.html` | Lista de pagamentos relacionados a fretes, adiantamentos, valores pendentes e liquidações. |
| Detalhe do pagamento do frete | `pagamento/detalhe_frete.html` | Dados do pagamento de uma viagem específica: valor, status, data, motorista, empresa e comprovante. |
| Avaliação do frete | `avaliacoes/avaliar_frete.html` | Página para motorista avaliar empresa e/ou empresa avaliar motorista após conclusão da viagem. |
| Avaliações recebidas | `avaliacoes/recebidas.html` | Lista de avaliações recebidas pelo usuário logado. |

---

## 7. Área administrativa

O administrador precisa gerenciar usuários, suspender/banir contas, criar/editar/inativar categorias logísticas, moderar avaliações, verificar usuários, responder chamados e acessar dashboard geral.

| Página HTML | Nome sugerido | Descrição |
|---|---|---|
| Dashboard administrativo | `admin/dashboard.html` | Indicadores gerais: total de motoristas, empresas, cargas, viagens, pagamentos, avaliações, chamados e usuários pendentes de verificação. |
| Usuários | `admin/usuarios.html` | Lista completa de motoristas e empresas, com filtros por perfil, status, documento, cidade e data de cadastro. Atende ao RF25. |
| Detalhes do usuário | `admin/detalhe_usuario.html` | Dados completos do usuário, documento, status, histórico de viagens/cargas, avaliações, chamados e ações administrativas. |
| Suspender usuário | `admin/suspender_usuario.html` | Tela/modal de confirmação com campo de justificativa para suspender conta. Atende ao RF26. |
| Banir usuário | `admin/banir_usuario.html` | Tela/modal de confirmação com justificativa para banimento permanente. Atende ao RF27. |
| Verificações pendentes | `admin/verificacoes.html` | Lista de usuários que solicitaram verificação, com documentos e dados para análise. |
| Detalhes da verificação | `admin/detalhe_verificacao.html` | Página para aprovar ou reprovar a verificação de motorista ou empresa. |
| Categorias logísticas | `admin/categorias.html` | Lista de categorias globais, como tipos de carroceria, tipos de veículo e tags de carga. Atende ao RF28 e RF29. |
| Nova categoria logística | `admin/nova_categoria.html` | Formulário para criar nova categoria. |
| Editar categoria logística | `admin/editar_categoria.html` | Formulário para editar ou inativar categoria existente. |
| Moderação de avaliações | `admin/avaliacoes.html` | Lista de avaliações e comentários trocados entre usuários. Atende ao RF30. |
| Detalhe/moderação de avaliação | `admin/moderar_avaliacao.html` | Permite editar, ocultar ou excluir comentários inadequados. Atende ao RF31. |
| Chamados de suporte | `admin/chamados.html` | Lista de chamados abertos pelos usuários, com status, prioridade e responsável. |
| Responder chamado | `admin/responder_chamado.html` | Tela para ler o chamado, responder e alterar status. |
| Pagamentos e assinaturas | `admin/pagamentos.html` | Lista de pagamentos de planos, status de assinatura, clientes inadimplentes e histórico de transações. |
| Auditoria | `admin/auditoria.html` | Registro de ações críticas: login, alteração de dados, suspensão, banimento, edição de carga e moderação. Relaciona-se ao requisito não funcional de auditabilidade. |
| Logs e monitoramento | `admin/logs.html` | Consulta de logs básicos da aplicação, erros e eventos importantes. Relaciona-se aos requisitos de monitoramento e logs. |

---

## 8. Páginas auxiliares e de erro

| Página HTML | Nome sugerido | Descrição |
|---|---|---|
| Acesso negado | `errors/403.html` | Mensagem informando que o usuário não tem permissão para acessar aquela área. |
| Página não encontrada | `errors/404.html` | Mensagem amigável e botão para voltar à home ou ao dashboard. |
| Erro interno | `errors/500.html` | Mensagem genérica de erro, sem detalhes técnicos. |
| Manutenção | `errors/manutencao.html` | Página para períodos de manutenção programada. |
| Baixa conexão | `public/baixa_conexao.html` | Interface simples avisando que a conexão está instável e oferecendo ações leves. Relaciona-se ao diferencial de otimização para baixa conexão. |
| Confirmação genérica | `shared/confirmacao.html` | Página reutilizável para cadastro realizado, e-mail enviado, pagamento confirmado, chamado aberto etc. |

---

## 9. Templates parciais reutilizáveis

Além das páginas completas, recomenda-se criar componentes Jinja reutilizáveis.

| Template parcial | Finalidade |
|---|---|
| `base.html` | Estrutura base com HTML, head, CSS, scripts e blocos Jinja. |
| `_navbar.html` | Menu superior adaptado ao perfil do usuário. |
| `_footer.html` | Rodapé público da aplicação. |
| `_sidebar_motorista.html` | Menu lateral da área do motorista. |
| `_sidebar_empresa.html` | Menu lateral da área da empresa/transportadora. |
| `_sidebar_admin.html` | Menu lateral da administração. |
| `_mensagens.html` | Exibição de mensagens de sucesso, erro, alerta e informação. |
| `_card_carga.html` | Card reutilizável para exibir cargas no mural, listas e buscas. |
| `_card_motorista.html` | Card reutilizável para exibir motoristas em buscas e favoritos. |
| `_form_carga.html` | Formulário compartilhado para criar, editar e agendar cargas. |
| `_filtros_carga.html` | Filtros por origem, destino, tipo de carroceria, data e valor. |
| `_paginacao.html` | Paginação para listagens longas. |
| `_modal_confirmacao.html` | Modal para confirmar exclusões, cancelamentos, suspensão e banimento. |
| `_status_viagem.html` | Componente visual para exibir o andamento da viagem. |
| `_avaliacao.html` | Componente para exibir nota e comentário de avaliação. |

---

## 10. Lista mínima para uma primeira versão funcional

Para uma primeira entrega viável, recomenda-se priorizar estas páginas:

1. `public/home.html`
2. `public/planos.html`
3. `auth/login.html`
4. `auth/escolher_perfil.html`
5. `auth/validar_documento.html`
6. `auth/cadastro_motorista.html`
7. `auth/cadastro_empresa.html`
8. `auth/recuperar_senha.html`
9. `auth/redefinir_senha.html`
10. `usuario/perfil.html`
11. `usuario/alterar_senha.html`
12. `motorista/dashboard.html`
13. `motorista/cargas.html`
14. `motorista/detalhe_carga.html`
15. `motorista/viagens.html`
16. `motorista/detalhe_viagem.html`
17. `motorista/historico_viagens.html`
18. `motorista/ganhos.html`
19. `motorista/avaliacoes.html`
20. `empresa/dashboard.html`
21. `empresa/cargas.html`
22. `empresa/nova_carga.html`
23. `empresa/editar_carga.html`
24. `empresa/detalhe_carga.html`
25. `empresa/metricas_cargas.html`
26. `empresa/buscar_motoristas.html`
27. `empresa/detalhe_motorista.html`
28. `chat/conversas.html`
29. `chat/conversa.html`
30. `avaliacoes/avaliar_frete.html`
31. `admin/dashboard.html`
32. `admin/usuarios.html`
33. `admin/detalhe_usuario.html`
34. `admin/categorias.html`
35. `admin/avaliacoes.html`
36. `admin/chamados.html`
37. `errors/403.html`
38. `errors/404.html`
39. `errors/500.html`

---

## 11. Observações importantes

- A aplicação deve considerar os perfis: **motorista**, **empresa/transportadora**, **administrador** e **usuário autenticado**.
- O documento menciona, em determinado trecho final, os perfis “Autores, Leitores e Administradores” e também “SimpleBlog”, mas isso parece ser uma inconsistência textual reaproveitada de outro projeto.
- Para implementação, devem ser considerados os requisitos funcionais e os diagramas de casos de uso do Giro Choffer.
- Recomenda-se organizar os templates por pastas, separando páginas públicas, autenticação, área do motorista, área da empresa, área administrativa, comunicação, pagamentos, avaliações, erros e componentes compartilhados.
- Como o projeto usa FastAPI com Jinja, os nomes sugeridos acima seguem uma estrutura compatível com aplicações server-side rendered.

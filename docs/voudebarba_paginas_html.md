# VouDeBarba — Lista de páginas HTML necessárias

Este documento reúne as páginas HTML recomendadas para implementar a aplicação **VouDeBarba — Agendamento de corte em barbearia**, com base no briefing, requisitos funcionais, requisitos não funcionais, diferenciais, integrações e diagramas de casos de uso descritos na documentação do projeto.

A aplicação é uma plataforma web para **agendamento online em barbearias**, permitindo que clientes encontrem barbearias, escolham serviços, selecionem barbeiros, consultem horários disponíveis e confirmem agendamentos. Para a barbearia, o sistema oferece gestão de agenda, barbeiros, atendentes, serviços, clientes, comissões, faturamento, chat, imagens, mapas e planos SaaS.

---

## 1. Páginas públicas

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Página inicial | `public/home.html` | Deve apresentar o VouDeBarba, explicar a proposta da plataforma, destacar agendamento online, facilidade de uso, busca por barbearias, benefícios para clientes e barbearias, botões para login, cadastro e busca de barbearias. Atende ao RF1. |
| Lista de barbearias | `public/barbearias.html` | Deve listar barbearias cadastradas, com nome, foto/logo, endereço, avaliação, distância aproximada, horário de funcionamento, botão para ver detalhes e filtros por cidade, bairro ou proximidade. Atende ao RF1, RF45 e RF46. |
| Busca por proximidade | `public/busca_proximidade.html` | Deve permitir localizar barbearias próximas ao usuário usando mapa e distância. Deve exibir resultado em lista e mapa, usando integração com OpenStreetMap/Leaflet. Atende ao RF45 e RF46. |
| Detalhes da barbearia | `public/detalhe_barbearia.html` | Deve exibir informações completas da barbearia: nome, imagens, endereço, localização em mapa, horários de funcionamento, barbeiros, serviços, preços, formas de pagamento e botão para iniciar agendamento. |
| Serviços da barbearia | `public/servicos_barbearia.html` | Deve listar os serviços disponíveis em uma barbearia, como corte, barba, sobrancelha, combo etc., com duração, preço, descrição e barbeiros que realizam cada serviço. Atende ao RF2. |
| Barbeiros da barbearia | `public/barbeiros_barbearia.html` | Deve exibir barbeiros disponíveis em uma barbearia, com foto, nome, especialidade, serviços oferecidos, horários disponíveis e botão para selecionar profissional. Atende ao RF3. |
| Detalhes do barbeiro | `public/detalhe_barbeiro.html` | Deve mostrar perfil público do barbeiro, foto, serviços oferecidos, agenda de disponibilidade, portfólio de imagens e botão para iniciar agendamento. Atende ao RF3 e RF4. |
| Horários disponíveis | `public/horarios_disponiveis.html` | Deve permitir visualizar os horários disponíveis para um serviço e barbeiro, sem confirmar o agendamento quando o usuário não estiver autenticado. Atende ao RF4 e RF5. |
| Simulação de agendamento | `public/simular_agendamento.html` | Deve permitir ao usuário anônimo percorrer o fluxo de seleção de barbearia, serviço, barbeiro, data e horário, mas impedir a confirmação final sem login. Atende ao RF5 e RF6. |
| Planos | `public/planos.html` | Deve apresentar os planos Sem Barba, Cavanhaque e Barbudo, com mensalidade, limite de agendamentos, módulo financeiro, dashboard e botão para contratação. |
| Como funciona | `public/como_funciona.html` | Deve explicar em etapas: buscar barbearia, escolher serviço, selecionar barbeiro, escolher horário, confirmar agendamento, receber lembrete e comparecer. Também deve explicar benefícios para barbearias. |
| Termos de uso | `public/termos.html` | Deve apresentar regras da plataforma, responsabilidades de clientes, barbearias, barbeiros, cancelamentos, pagamentos, uso de imagens, comportamento e suporte. |
| Política de privacidade | `public/privacidade.html` | Deve explicar como dados pessoais, contatos, localização, imagens, histórico de agendamentos, mensagens e pagamentos são armazenados e protegidos. |
| Contato público | `public/contato.html` | Deve oferecer formulário de contato, e-mail de suporte e informações institucionais da plataforma. |

---

## 2. Autenticação, cadastro e recuperação

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Login | `auth/login.html` | Deve conter formulário com e-mail e senha, links para cadastro e recuperação de senha. Deve atender clientes, barbeiros, atendentes e administradores. Atende ao RF8. |
| Cadastro de usuário/cliente | `auth/cadastro.html` | Deve exigir nome completo, e-mail, senha e telefone, validando formato de e-mail e telefone e garantindo unicidade do e-mail. Atende ao RF7, RF10, RF11 e RF12. |
| Cadastro de barbearia | `auth/cadastro_barbearia.html` | Deve permitir que um responsável cadastre uma barbearia, informando nome, CNPJ/CPF, endereço, CEP, telefone, e-mail, plano desejado, horários básicos e imagens iniciais. Relaciona-se ao suporte a múltiplas barbearias. |
| Escolha de perfil | `auth/escolher_perfil.html` | Deve permitir escolher se o cadastro será como cliente ou responsável por barbearia. |
| Recuperação de senha | `auth/recuperar_senha.html` | Deve permitir solicitar recuperação informando e-mail cadastrado. Atende ao RF9. |
| Redefinição de senha | `auth/redefinir_senha.html` | Deve conter campos para nova senha e confirmação, acessada por token/link enviado por e-mail. |
| Confirmação de cadastro | `auth/confirmar_cadastro.html` | Deve orientar o usuário a verificar e-mail ou concluir cadastro. |
| Logout | `auth/logout.html` | Pode ser uma tela simples informando que a sessão foi encerrada, com botão para login ou página inicial. Atende ao RF38. |

---

## 3. Páginas comuns para usuários autenticados

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Dashboard geral | `usuario/dashboard.html` | Página inicial após login. Deve redirecionar ou exibir atalhos conforme o perfil: cliente, barbeiro, atendente ou administrador/gerenciador. |
| Meu perfil | `usuario/perfil.html` | Deve exibir dados cadastrais do usuário, telefone, e-mail, foto opcional, tipo de perfil e status da conta. |
| Editar perfil | `usuario/editar_perfil.html` | Deve permitir editar dados cadastrais autorizados, como nome, telefone, senha, foto e preferências. Atende ao RF37. |
| Alterar senha | `usuario/alterar_senha.html` | Deve permitir alterar senha informando senha atual, nova senha e confirmação. |
| Notificações | `usuario/notificacoes.html` | Deve listar confirmações de agendamento, lembretes, alterações de horário, cancelamentos, mensagens e avisos da plataforma. |
| Suporte | `usuario/suporte.html` | Deve permitir entrar em contato com o suporte do sistema. Atende ao RF39. |
| Abrir chamado | `usuario/abrir_chamado.html` | Deve permitir registrar problema, dúvida, sugestão ou solicitação de ajuda. |
| Detalhes do chamado | `usuario/detalhe_chamado.html` | Deve mostrar histórico de conversa com suporte, status e respostas. |

---

## 4. Área do cliente

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Dashboard do cliente | `cliente/dashboard.html` | Deve mostrar próximos agendamentos, histórico recente, mensagens, barbearias visitadas/favoritas e atalhos para buscar barbearia ou agendar horário. |
| Buscar barbearia | `cliente/buscar_barbearia.html` | Deve permitir buscar barbearias por nome, cidade, bairro, serviço, barbeiro ou proximidade. Atende ao RF46. |
| Detalhes da barbearia | `cliente/detalhe_barbearia.html` | Deve exibir barbearia com dados completos, mapa, serviços, barbeiros, horários, avaliações e botão para agendar. |
| Selecionar serviço | `cliente/selecionar_servico.html` | Deve listar serviços disponíveis da barbearia escolhida, com preço, duração e descrição. Atende aos casos de uso do cliente. |
| Selecionar barbeiro | `cliente/selecionar_barbeiro.html` | Deve listar barbeiros que executam o serviço selecionado, com foto, disponibilidade e informações básicas. |
| Selecionar horário | `cliente/selecionar_horario.html` | Deve exibir datas e horários disponíveis conforme serviço e barbeiro selecionados. |
| Confirmar agendamento | `cliente/confirmar_agendamento.html` | Deve mostrar resumo do agendamento: barbearia, serviço, barbeiro, data, horário, duração, preço, forma de pagamento e botão de confirmação. Atende ao RF13. |
| Agendamento confirmado | `cliente/agendamento_confirmado.html` | Deve exibir comprovante do agendamento, status, dados do serviço, endereço, instruções e opção de adicionar ao calendário. Relaciona-se ao RF41. |
| Meus agendamentos | `cliente/agendamentos.html` | Deve listar agendamentos futuros e passados, com status, serviço, barbeiro, data e ações. Atende ao RF14. |
| Detalhes do agendamento | `cliente/detalhe_agendamento.html` | Deve exibir todos os dados do agendamento, status, histórico de alterações, mensagens e ações disponíveis. |
| Remarcar agendamento | `cliente/remarcar_agendamento.html` | Deve permitir escolher novo horário dentro da disponibilidade do barbeiro. Atende ao RF15. |
| Cancelar agendamento | `cliente/cancelar_agendamento.html` | Deve permitir cancelar agendamento, informando motivo quando necessário. Atende ao RF16. |
| Histórico de agendamentos | `cliente/historico.html` | Deve listar agendamentos finalizados, cancelados e remarcados. Atende ao RF17. |
| Chat com barbearia | `cliente/chat.html` | Deve permitir conversar com a barbearia ou atendente. Atende ao RF18 e RF19. |
| Barbearias favoritas | `cliente/favoritas.html` | Deve listar barbearias salvas como favoritas, facilitando novos agendamentos. |
| Avaliar atendimento | `cliente/avaliar_atendimento.html` | Deve permitir avaliar barbearia, barbeiro e serviço após atendimento. |
| Pagamentos do cliente | `cliente/pagamentos.html` | Deve listar pagamentos realizados, pendentes ou cancelados, especialmente quando houver pagamento antecipado pelo Mercado Pago. |

---

## 5. Área do atendente

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Dashboard do atendente | `atendente/dashboard.html` | Deve mostrar resumo da agenda do dia, mensagens pendentes, agendamentos próximos, cancelamentos e alertas operacionais. |
| Agenda da barbearia | `atendente/agenda.html` | Deve exibir agenda geral da barbearia, com filtros por barbeiro, data, serviço e status. Atende ao RF22. |
| Agendamentos | `atendente/agendamentos.html` | Deve listar agendamentos da barbearia, permitindo visualizar, remarcar, cancelar e alterar status. Atende ao RF22 e RF23. |
| Detalhes do agendamento | `atendente/detalhe_agendamento.html` | Deve exibir cliente, serviço, barbeiro, horário, status, pagamento, mensagens e histórico de alterações. |
| Novo agendamento | `atendente/novo_agendamento.html` | Deve permitir cadastrar um agendamento manualmente para cliente presencial, por telefone ou WhatsApp. |
| Remarcar agendamento | `atendente/remarcar_agendamento.html` | Deve permitir alterar horário de agendamento conforme disponibilidade dos barbeiros. Atende ao RF23. |
| Cancelar agendamento | `atendente/cancelar_agendamento.html` | Deve permitir cancelar agendamento, registrar motivo e notificar cliente. |
| Mensagens de clientes | `atendente/mensagens.html` | Deve listar conversas abertas por clientes. Atende ao RF20. |
| Responder mensagem | `atendente/responder_mensagem.html` | Deve permitir visualizar e responder mensagens de clientes. Atende ao RF21. |
| Clientes | `atendente/clientes.html` | Deve listar clientes da barbearia, com busca por nome, telefone ou e-mail. |
| Detalhes do cliente | `atendente/detalhe_cliente.html` | Deve exibir dados básicos do cliente, histórico de agendamentos, faltas e mensagens. |
| Notificações e lembretes | `atendente/lembretes.html` | Deve permitir acompanhar ou reenviar confirmações e lembretes de agendamento por e-mail. Relaciona-se ao RF41 e RF42. |

---

## 6. Área do barbeiro

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Dashboard do barbeiro | `barbeiro/dashboard.html` | Deve mostrar agenda do dia, próximos clientes, receita gerada, serviços realizados, notificações e atalhos para disponibilidade. |
| Minha agenda | `barbeiro/agenda.html` | Deve exibir horários do barbeiro, clientes agendados e serviços previstos. Atende ao RF24 e RF25. |
| Detalhes do agendamento | `barbeiro/detalhe_agendamento.html` | Deve exibir dados do cliente, serviço, horário, observações, status e pagamento. |
| Clientes agendados | `barbeiro/clientes_agendados.html` | Deve listar os clientes agendados por período, com contato e serviço marcado. Atende ao RF25. |
| Disponibilidade | `barbeiro/disponibilidade.html` | Deve permitir definir horários disponíveis, pausas, dias de atendimento e bloqueios. Atende ao RF26. |
| Serviços oferecidos | `barbeiro/servicos.html` | Deve permitir visualizar e, se permitido, definir serviços oferecidos pelo barbeiro, preços e duração. Relaciona-se ao caso de uso “Definir serviços oferecidos”. |
| Receita gerada | `barbeiro/receita.html` | Deve mostrar ganhos por dia, semana e mês, serviços realizados e comissão estimada. Atende ao RF27 e ao diferencial de dashboard de faturamento. |
| Comissões | `barbeiro/comissoes.html` | Deve exibir valores de comissão calculados conforme porcentagem definida pelo gerenciador. Relaciona-se ao RF40. |
| Meu perfil profissional | `barbeiro/perfil.html` | Deve permitir editar foto, descrição, especialidades, portfólio, contatos e preferências. |
| Portfólio de imagens | `barbeiro/portfolio.html` | Deve permitir upload e gerenciamento de imagens de cortes e serviços, armazenadas em CDN. Atende ao RF43 e RF44. |

---

## 7. Área do administrador/gerenciador da barbearia

O documento utiliza principalmente o perfil “Administrador” nos diagramas e “Gerenciadores” nos requisitos. Aqui, considera-se o administrador/gerenciador como o responsável pela barbearia.

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Dashboard da barbearia | `admin/dashboard.html` | Deve exibir visão geral conforme plano contratado: agendamentos, faturamento, agenda do dia, serviços mais vendidos, barbeiros, cancelamentos e indicadores. Atende ao RF28. |
| Barbearias | `admin/barbearias.html` | Deve listar barbearias vinculadas ao gerenciador, considerando suporte a múltiplas barbearias. Atende ao RF51. |
| Cadastrar barbearia | `admin/cadastrar_barbearia.html` | Deve permitir cadastrar nova barbearia, incluindo nome, endereço, CEP, telefone, descrição, localização, imagens e horários. Relaciona-se ao caso de uso do administrador. |
| Dados da barbearia | `admin/dados_barbearia.html` | Deve exibir e permitir editar dados da barbearia, como nome, descrição, endereço, mapa, imagens e contatos. Atende ao RF30. |
| Editar barbearia | `admin/editar_barbearia.html` | Deve permitir alterar informações gerais da barbearia. Atende ao RF30. |
| Horários de funcionamento | `admin/horarios_funcionamento.html` | Deve permitir definir horários de abertura, fechamento, pausas, feriados, dias de atendimento e bloqueios. Atende ao RF31 e RF32. |
| Regras operacionais | `admin/regras_operacionais.html` | Deve permitir configurar regras como antecedência mínima, prazo para cancelamento, intervalo entre serviços, tolerância de atraso e política de remarcação. Atende ao RF33. |
| Barbeiros | `admin/barbeiros.html` | Deve listar barbeiros vinculados à barbearia, com status, agenda, serviços e comissão. Atende ao RF29. |
| Cadastrar barbeiro | `admin/cadastrar_barbeiro.html` | Deve permitir cadastrar barbeiro, dados pessoais, contato, serviços, agenda, comissão e relação com barbearia. Atende ao RF29. |
| Detalhes do barbeiro | `admin/detalhe_barbeiro.html` | Deve mostrar informações do barbeiro, agenda, serviços, receita gerada e comissão. |
| Editar barbeiro | `admin/editar_barbeiro.html` | Deve permitir alterar dados do barbeiro, disponibilidade, serviços, comissão e status. |
| Relacionar barbeiro com barbearia | `admin/relacionar_barbeiro.html` | Deve permitir vincular barbeiros a uma ou mais barbearias. Relaciona-se ao diagrama de administrador. |
| Atendentes | `admin/atendentes.html` | Deve listar atendentes da barbearia, com dados, status e permissões. |
| Cadastrar atendente | `admin/cadastrar_atendente.html` | Deve permitir cadastrar atendente para operar agenda e mensagens. |
| Serviços | `admin/servicos.html` | Deve listar serviços da barbearia, com preço, duração, descrição, status e barbeiros associados. |
| Cadastrar serviço | `admin/cadastrar_servico.html` | Deve permitir cadastrar serviço com nome, descrição, preço, duração, categoria e imagem opcional. |
| Editar serviço | `admin/editar_servico.html` | Deve permitir editar dados de serviço e disponibilidade por barbeiro. |
| Agenda geral | `admin/agenda.html` | Deve exibir agenda completa da barbearia, com filtros por barbeiro, serviço, status e período. |
| Agendamentos | `admin/agendamentos.html` | Deve listar agendamentos e permitir ações administrativas de alteração, cancelamento, confirmação e controle. |
| Clientes | `admin/clientes.html` | Deve listar clientes da barbearia, histórico, contato e frequência. |
| Detalhes do cliente | `admin/detalhe_cliente.html` | Deve exibir dados do cliente, histórico de agendamentos, mensagens, faltas e avaliações. |
| Financeiro | `admin/financeiro.html` | Deve apresentar contas a pagar, contas a receber, histórico financeiro e resumo de movimentações, conforme plano. Atende ao RF34, RF35 e RF49. |
| Contas a pagar | `admin/contas_pagar.html` | Deve listar despesas da barbearia, vencimentos, status e categorias. Atende ao RF34. |
| Contas a receber | `admin/contas_receber.html` | Deve listar recebimentos previstos, pagamentos antecipados, serviços prestados e status. Atende ao RF35. |
| Comissões | `admin/comissoes.html` | Deve permitir definir porcentagem de comissão dos barbeiros e visualizar cálculos automáticos. Atende ao RF36 e RF40. |
| Dashboard de faturamento | `admin/faturamento.html` | Deve mostrar ganhos do dia, semana e mês em tempo real, conforme diferencial do projeto. |
| Relatórios | `admin/relatorios.html` | Deve reunir relatórios de agendamentos, clientes, serviços, barbeiros, faturamento, cancelamentos e no-show. |
| Plano e assinatura | `admin/plano.html` | Deve exibir plano atual, limites de agendamento, módulo financeiro, dashboard e opções de upgrade/downgrade. |
| Pagamentos da assinatura | `admin/pagamentos.html` | Deve listar cobranças, status, mensalidades e pagamentos feitos pela barbearia via Mercado Pago. |
| Imagens da barbearia | `admin/imagens.html` | Deve permitir upload, organização e exclusão de imagens da barbearia, portfólio e fotos de serviços. Atende ao RF43 e RF44. |
| Localização e mapa | `admin/localizacao.html` | Deve permitir configurar endereço por CEP, coordenadas, mapa e validação geográfica. Atende ao RF45, RF47 e RF48. |
| Logs de operações | `admin/logs.html` | Deve exibir registros de operações importantes, como agendamentos, alterações, pagamentos, comissões e login. Atende ao RF50. |

---

## 8. Chat, suporte e comunicação

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Lista de conversas | `chat/conversas.html` | Deve listar conversas entre clientes e barbearias, com última mensagem, status e responsável. |
| Conversa | `chat/conversa.html` | Deve exibir mensagens trocadas entre cliente e barbearia, relacionadas ou não a um agendamento. Atende ao RF18, RF19, RF20 e RF21. |
| Enviar mensagem | `chat/enviar.html` | Pode ser página ou componente para envio de mensagem rápida no contexto da barbearia ou agendamento. |
| Chamados de suporte | `suporte/chamados.html` | Deve listar chamados abertos pelo usuário autenticado. |
| Abrir chamado | `suporte/abrir_chamado.html` | Deve permitir abrir chamado para suporte do sistema. Atende ao RF39. |
| Detalhe do chamado | `suporte/detalhe_chamado.html` | Deve exibir histórico de atendimento, mensagens, anexos e status. |
| Central de ajuda | `suporte/ajuda.html` | Deve conter perguntas frequentes sobre cadastro, agendamento, cancelamento, pagamento, planos e uso da plataforma. |

---

## 9. Pagamento e checkout

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Checkout de serviço | `pagamento/checkout_servico.html` | Deve permitir pagamento antecipado do serviço por PIX ou cartão, quando habilitado pela barbearia. Usa Mercado Pago. |
| Resultado do pagamento do serviço | `pagamento/resultado_servico.html` | Deve exibir pagamento aprovado, pendente, recusado ou cancelado e atualizar o status do agendamento. |
| Checkout de assinatura | `pagamento/checkout_assinatura.html` | Deve permitir contratação ou renovação dos planos Sem Barba, Cavanhaque ou Barbudo. |
| Resultado da assinatura | `pagamento/resultado_assinatura.html` | Deve informar status do pagamento da assinatura da barbearia. |
| Histórico de pagamentos | `pagamento/historico.html` | Deve listar pagamentos de serviços e assinaturas, com data, valor, status e comprovantes. |
| Detalhe do pagamento | `pagamento/detalhe.html` | Deve exibir dados completos de uma transação, método, status, valor e referência. |

---

## 10. Mapas, imagens e localização

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Mapa de barbearias | `mapa/barbearias.html` | Deve exibir barbearias em mapa interativo, com marcadores, distância e filtros. Atende ao RF45 e RF46. |
| Configurar localização | `mapa/configurar_localizacao.html` | Deve permitir ao administrador configurar endereço, CEP, coordenadas e validar a localização. Atende ao RF47 e RF48. |
| Galeria da barbearia | `midia/galeria_barbearia.html` | Deve exibir fotos da barbearia, ambiente e serviços. |
| Gerenciar galeria | `midia/gerenciar_galeria.html` | Deve permitir upload, exclusão e organização de imagens em CDN. Atende ao RF43 e RF44. |
| Portfólio do barbeiro | `midia/portfolio_barbeiro.html` | Deve exibir fotos de serviços realizados por um barbeiro. |

---

## 11. Administração da plataforma SaaS

Além da administração de cada barbearia, pode existir uma administração global da plataforma VouDeBarba.

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Dashboard global | `superadmin/dashboard.html` | Deve mostrar número total de barbearias, usuários, agendamentos, receita de assinaturas, planos ativos e alertas. |
| Barbearias cadastradas | `superadmin/barbearias.html` | Deve listar todas as barbearias da plataforma, plano, status e dados de contato. |
| Detalhes da barbearia | `superadmin/detalhe_barbearia.html` | Deve exibir dados completos da barbearia, usuários vinculados, pagamentos e uso da plataforma. |
| Usuários da plataforma | `superadmin/usuarios.html` | Deve listar usuários de todos os perfis, com filtros por perfil, status e barbearia. |
| Planos SaaS | `superadmin/planos.html` | Deve permitir gerenciar planos Sem Barba, Cavanhaque e Barbudo. |
| Assinaturas | `superadmin/assinaturas.html` | Deve listar assinaturas, vencimentos, inadimplência e status de pagamento. |
| Logs globais | `superadmin/logs.html` | Deve exibir logs administrativos e técnicos da plataforma. |
| Relatórios globais | `superadmin/relatorios.html` | Deve mostrar crescimento, uso, receita, cancelamentos e métricas gerais da plataforma. |

---

## 12. Páginas auxiliares e de erro

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Acesso negado | `errors/403.html` | Deve informar que o usuário não tem permissão para acessar a página ou funcionalidade. |
| Página não encontrada | `errors/404.html` | Deve informar que a página não existe e oferecer botões para voltar à home, dashboard ou busca. |
| Erro interno | `errors/500.html` | Deve apresentar mensagem genérica de erro, sem expor detalhes técnicos ao usuário final. |
| Manutenção | `errors/manutencao.html` | Deve informar períodos de manutenção programada. |
| Sessão expirada | `errors/sessao_expirada.html` | Deve informar que a sessão expirou e oferecer link para login. |
| Agendamento indisponível | `errors/agendamento_indisponivel.html` | Deve informar que o horário selecionado não está mais disponível e oferecer retorno à seleção de horário. |
| Pagamento não confirmado | `errors/pagamento_nao_confirmado.html` | Deve informar que o pagamento não foi confirmado e orientar o usuário. |
| Confirmação genérica | `shared/confirmacao.html` | Pode ser usada para cadastro realizado, agendamento confirmado, mensagem enviada, pagamento aprovado e outras operações concluídas. |

---

## 13. Templates parciais reutilizáveis

Além das páginas completas, recomenda-se criar componentes Jinja reutilizáveis.

| Template parcial | Finalidade |
|---|---|
| `base.html` | Estrutura base com HTML, head, CSS, scripts, blocos Jinja e layout geral. |
| `_navbar.html` | Menu superior adaptado para visitante, cliente, barbeiro, atendente, administrador ou superadministrador. |
| `_footer.html` | Rodapé com links institucionais, contato, termos e privacidade. |
| `_sidebar_cliente.html` | Menu lateral da área do cliente. |
| `_sidebar_atendente.html` | Menu lateral da área do atendente. |
| `_sidebar_barbeiro.html` | Menu lateral da área do barbeiro. |
| `_sidebar_admin.html` | Menu lateral da administração da barbearia. |
| `_sidebar_superadmin.html` | Menu lateral da administração global da plataforma. |
| `_mensagens.html` | Exibição de mensagens de sucesso, erro, alerta e informação. |
| `_card_barbearia.html` | Card reutilizável para exibir barbearias em listas e buscas. |
| `_card_barbeiro.html` | Card reutilizável para exibir barbeiros. |
| `_card_servico.html` | Card reutilizável para serviços. |
| `_card_agendamento.html` | Card reutilizável para agendamentos. |
| `_form_barbearia.html` | Formulário compartilhado para cadastro e edição de barbearias. |
| `_form_barbeiro.html` | Formulário compartilhado para cadastro e edição de barbeiros. |
| `_form_servico.html` | Formulário compartilhado para cadastro e edição de serviços. |
| `_form_agendamento.html` | Formulário compartilhado para criação, edição e remarcação de agendamentos. |
| `_filtros_barbearias.html` | Filtros por localidade, serviço, avaliação e proximidade. |
| `_filtros_agendamentos.html` | Filtros por data, barbeiro, serviço, status e cliente. |
| `_status_agendamento.html` | Componente visual para status: solicitado, confirmado, concluído, cancelado, remarcado ou não compareceu. |
| `_status_pagamento.html` | Componente visual para status de pagamento. |
| `_agenda_mini.html` | Mini calendário ou agenda resumida para dashboards. |
| `_mapa_barbearia.html` | Componente para exibir mapa da barbearia. |
| `_modal_confirmacao.html` | Modal para confirmar cancelamento, exclusão, pagamento, remarcação e ações importantes. |
| `_paginacao.html` | Paginação para listagens longas. |
| `_upload_imagem.html` | Componente de upload de imagens para barbearia, barbeiro ou serviço. |

---

## 14. Lista mínima para uma primeira versão funcional

Para uma primeira entrega viável, recomenda-se priorizar estas páginas:

1. `public/home.html`
2. `public/barbearias.html`
3. `public/detalhe_barbearia.html`
4. `public/servicos_barbearia.html`
5. `public/barbeiros_barbearia.html`
6. `public/horarios_disponiveis.html`
7. `public/planos.html`
8. `auth/login.html`
9. `auth/cadastro.html`
10. `auth/cadastro_barbearia.html`
11. `auth/recuperar_senha.html`
12. `auth/redefinir_senha.html`
13. `usuario/perfil.html`
14. `usuario/editar_perfil.html`
15. `cliente/dashboard.html`
16. `cliente/buscar_barbearia.html`
17. `cliente/selecionar_servico.html`
18. `cliente/selecionar_barbeiro.html`
19. `cliente/selecionar_horario.html`
20. `cliente/confirmar_agendamento.html`
21. `cliente/agendamento_confirmado.html`
22. `cliente/agendamentos.html`
23. `cliente/remarcar_agendamento.html`
24. `cliente/cancelar_agendamento.html`
25. `cliente/historico.html`
26. `cliente/chat.html`
27. `atendente/dashboard.html`
28. `atendente/agenda.html`
29. `atendente/agendamentos.html`
30. `atendente/novo_agendamento.html`
31. `atendente/mensagens.html`
32. `barbeiro/dashboard.html`
33. `barbeiro/agenda.html`
34. `barbeiro/disponibilidade.html`
35. `barbeiro/servicos.html`
36. `barbeiro/receita.html`
37. `admin/dashboard.html`
38. `admin/dados_barbearia.html`
39. `admin/horarios_funcionamento.html`
40. `admin/barbeiros.html`
41. `admin/cadastrar_barbeiro.html`
42. `admin/servicos.html`
43. `admin/cadastrar_servico.html`
44. `admin/agenda.html`
45. `admin/agendamentos.html`
46. `admin/clientes.html`
47. `admin/financeiro.html`
48. `admin/comissoes.html`
49. `admin/plano.html`
50. `pagamento/checkout_assinatura.html`
51. `pagamento/resultado_assinatura.html`
52. `chat/conversas.html`
53. `chat/conversa.html`
54. `suporte/abrir_chamado.html`
55. `errors/403.html`
56. `errors/404.html`
57. `errors/500.html`

---

## 15. Observações importantes

- A aplicação deve considerar os perfis principais: **usuário anônimo**, **cliente**, **barbeiro**, **atendente**, **administrador/gerenciador da barbearia** e, se necessário, **superadministrador da plataforma SaaS**.
- O documento cita tecnologias como HTML5/CSS3, Bootstrap, Python, Docker Compose, Git/GitHub e PostgreSQL.
- As integrações previstas justificam páginas e fluxos específicos:
  - **Resend**: confirmação de agendamento, lembretes e recuperação de senha;
  - **Mercado Pago**: pagamento antecipado de serviços e assinatura dos planos;
  - **ViaCEP/BrasilAPI**: preenchimento e validação de endereço;
  - **OpenStreetMap/Leaflet**: localização das barbearias e busca por proximidade;
  - **CDN de imagens**: fotos de barbeiros, barbearias, serviços e portfólio.
- Como o projeto usa uma arquitetura web com templates, os nomes sugeridos seguem uma organização compatível com aplicações server-side rendered, como FastAPI com Jinja.
- A lista mínima prioriza o fluxo principal: buscar barbearia, escolher serviço/barbeiro/horário, confirmar agendamento, gerenciar agenda, configurar barbearia, controlar serviços, ver receita e operar suporte básico.

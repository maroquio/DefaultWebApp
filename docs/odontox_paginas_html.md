# OdontoX — Lista de páginas HTML necessárias

Este documento reúne as páginas HTML recomendadas para implementar a aplicação **OdontoX — Agendamento de Consultas Odontológicas**, com base no briefing, requisitos funcionais, requisitos não funcionais, perfis de usuário, diferenciais e diagramas de casos de uso descritos na documentação do projeto.

A aplicação é uma plataforma web para **consultórios odontológicos e clínicas de pequeno porte**, com foco em **cadastro de pacientes**, **agenda digital**, **agendamento de consultas**, **histórico de atendimentos**, **notificações/lembretes**, **gestão de usuários**, **controle de permissões** e **área do paciente**.

---

## 1. Páginas públicas

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Página inicial da clínica | `public/home.html` | Deve apresentar a clínica ou consultório, os principais serviços, diferenciais do OdontoX, equipe, localização, horários de funcionamento, botão de login, botão de cadastro como paciente e chamada para solicitar agendamento. Atende ao RF11 e RF17. |
| Página institucional | `public/sobre.html` | Deve mostrar a história da clínica, missão, equipe, localização, estrutura e informações institucionais. Atende ao RF15. |
| Serviços e especialidades | `public/servicos.html` | Deve listar especialidades, procedimentos odontológicos oferecidos, descrição resumida de cada serviço e profissionais relacionados, quando aplicável. Atende ao RF17. |
| Equipe de profissionais | `public/equipe.html` | Deve exibir dentistas e profissionais da clínica, com nome, especialidade, breve descrição, foto opcional e horários gerais de atendimento, se públicos. |
| Localização e contato | `public/contato.html` | Deve exibir endereço, mapa, telefone, WhatsApp, e-mail, horário de funcionamento e formulário de contato. Atende ao RF16 e RF17. |
| Solicitação pública de agendamento | `public/solicitar_agendamento.html` | Deve permitir que usuário anônimo envie uma solicitação de consulta, informando nome, CPF, telefone, e-mail, horário preferencial, serviço desejado e observações. A solicitação deve ficar pendente de confirmação pela clínica. Atende ao RF18. |
| Mensagem enviada | `public/mensagem_enviada.html` | Deve confirmar o envio de mensagem ou solicitação à clínica, orientando que a equipe entrará em contato. |
| Planos | `public/planos.html` | Deve apresentar os planos Free, Starter e Pro, com mensalidade, quantidade de usuários, limite de pacientes cadastrados e recursos disponíveis. Útil para a versão SaaS da aplicação. |
| Política de privacidade | `public/privacidade.html` | Deve explicar coleta, uso, armazenamento e proteção dos dados dos pacientes, incluindo dados pessoais, endereço, contato, histórico clínico e registros de atendimento. |
| Termos de uso | `public/termos.html` | Deve apresentar regras de uso da plataforma, responsabilidades da clínica, usuários, pacientes e políticas de cancelamento/agendamento. |

---

## 2. Páginas de autenticação e cadastro

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Login | `auth/login.html` | Deve conter formulário com e-mail e senha, botão de entrada, link para cadastro de paciente e link para recuperação de senha. Deve atender usuários dos perfis administrador, dentista, atendente e paciente. Atende ao RF12. |
| Cadastro de paciente | `auth/cadastro_paciente.html` | Deve permitir que usuário anônimo se cadastre como paciente, informando nome, CPF, data de nascimento, endereço, telefone, e-mail e senha. Deve usar consulta de CEP para preenchimento automático do endereço. Atende ao RF13. |
| Recuperação de senha | `auth/recuperar_senha.html` | Deve permitir solicitar redefinição de senha informando e-mail ou CPF, com envio de instruções por e-mail. Atende ao RF14. |
| Redefinir senha | `auth/redefinir_senha.html` | Deve conter formulário com nova senha e confirmação de senha, acessado por token/link recebido por e-mail. |
| Confirmação de cadastro | `auth/confirmar_cadastro.html` | Deve orientar o paciente a confirmar o cadastro, verificar e-mail ou aguardar aprovação, conforme a regra definida pela clínica. |
| Logout | `auth/logout.html` | Pode ser uma página simples de confirmação de encerramento da sessão, com botão para voltar ao login ou à página inicial. |

---

## 3. Páginas comuns para usuários autenticados

Estas páginas podem ser usadas por administrador, dentista, atendente e paciente, com variações conforme o perfil.

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Dashboard geral | `usuario/dashboard.html` | Página inicial após login. Pode redirecionar automaticamente para o dashboard específico do perfil: administrador, dentista, atendente ou paciente. |
| Meu perfil | `usuario/perfil.html` | Deve exibir dados cadastrais do usuário, foto opcional, telefone, e-mail, status da conta e preferências do sistema. |
| Editar perfil | `usuario/editar_perfil.html` | Deve permitir atualizar dados pessoais permitidos, como telefone, e-mail, endereço e preferências. Para dentistas, pode incluir dados profissionais. |
| Alterar senha | `usuario/alterar_senha.html` | Deve permitir alterar senha informando senha atual, nova senha e confirmação da nova senha. |
| Notificações | `usuario/notificacoes.html` | Deve listar notificações sobre consultas, confirmações, cancelamentos, remarcações, lembretes, comunicados internos e mensagens do sistema. |
| Preferências do sistema | `usuario/preferencias.html` | Deve permitir configurar preferências de notificação, tema visual, idioma, modo de exibição da agenda e outros ajustes simples. |

---

## 4. Área do administrador

O administrador gerencia a clínica, usuários, dentistas, atendentes, pacientes, agenda geral, configurações, permissões e indicadores de uso.

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Dashboard administrativo | `admin/dashboard.html` | Deve exibir indicadores da clínica: número de pacientes, consultas realizadas, cancelamentos, agenda do dia, consultas por período e filtros por profissional. Atende ao RF1. |
| Usuários da plataforma | `admin/usuarios.html` | Deve listar administradores, dentistas, atendentes e pacientes, com filtros por perfil, status e nome. Deve permitir acessar detalhes, editar, desativar ou excluir contas. Atende ao RF2. |
| Detalhes do usuário | `admin/detalhe_usuario.html` | Deve exibir dados completos de um usuário, perfil de acesso, status, histórico básico de uso e ações administrativas. |
| Novo usuário | `admin/novo_usuario.html` | Deve permitir cadastrar usuário interno, selecionando perfil, dados pessoais, e-mail, telefone e permissões. |
| Editar usuário | `admin/editar_usuario.html` | Deve permitir alterar dados e perfil de acesso de um usuário já cadastrado. |
| Dentistas | `admin/dentistas.html` | Deve listar dentistas cadastrados, especialidade, telefone, e-mail, horários de atendimento e status. Atende ao RF3. |
| Cadastrar dentista | `admin/cadastrar_dentista.html` | Deve conter formulário com nome, CPF, especialidade, horários de atendimento, telefone, e-mail e dados profissionais. Atende ao RF3. |
| Detalhes do dentista | `admin/detalhe_dentista.html` | Deve exibir dados profissionais, agenda, consultas, pacientes atendidos, estatísticas e status. |
| Editar dentista | `admin/editar_dentista.html` | Deve permitir alterar dados pessoais, profissionais e horários de atendimento do dentista. |
| Atendentes | `admin/atendentes.html` | Deve listar atendentes cadastrados, função, telefone, e-mail, horários de trabalho e status. Atende ao RF4. |
| Cadastrar atendente | `admin/cadastrar_atendente.html` | Deve conter formulário com nome, CPF, telefone, e-mail, função e horários de trabalho. Atende ao RF4. |
| Detalhes do atendente | `admin/detalhe_atendente.html` | Deve exibir dados do atendente, função, horários, histórico operacional e status. |
| Editar atendente | `admin/editar_atendente.html` | Deve permitir alterar dados cadastrais, função e horários do atendente. |
| Pacientes | `admin/pacientes.html` | Deve listar pacientes, com busca por nome, CPF, telefone ou e-mail. Deve permitir visualizar, cadastrar, editar ou excluir registros. Atende ao RF5. |
| Cadastrar paciente | `admin/cadastrar_paciente.html` | Deve conter formulário completo com nome, CPF, data de nascimento, endereço, telefone, e-mail e informações de saúde. Atende ao RF5. |
| Detalhes do paciente | `admin/detalhe_paciente.html` | Deve exibir dados pessoais, contato, endereço, informações de saúde, consultas, histórico de atendimentos e observações administrativas. |
| Editar paciente | `admin/editar_paciente.html` | Deve permitir atualizar dados cadastrais e informações de saúde do paciente. |
| Agenda geral da clínica | `admin/agenda.html` | Deve exibir agenda de todos os profissionais, com visualização por dia, semana, mês e filtros por dentista. Deve permitir inserir horários, bloqueios, consultas e alterações. Atende ao RF6. |
| Nova consulta | `admin/nova_consulta.html` | Deve permitir registrar consulta vinculando paciente, dentista, data, horário, tipo de atendimento e observações. Atende ao RF7. |
| Detalhes da consulta | `admin/detalhe_consulta.html` | Deve exibir dados da consulta, paciente, dentista, procedimento previsto, status, histórico de alterações e ações de remarcar, cancelar ou concluir. |
| Editar/remarcar consulta | `admin/editar_consulta.html` | Deve permitir alterar data, horário, profissional, status e observações da consulta. Atende ao RF7. |
| Cancelar consulta | `admin/cancelar_consulta.html` | Deve solicitar confirmação e motivo do cancelamento, registrando no histórico. Atende ao RF7. |
| Atendimentos realizados | `admin/atendimentos.html` | Deve listar atendimentos realizados, com filtros por período, dentista, paciente e procedimento. Atende ao RF8. |
| Detalhes do atendimento | `admin/detalhe_atendimento.html` | Deve exibir procedimento realizado, observações clínicas, profissional responsável, paciente e data. Atende ao RF8. |
| Configurações da clínica | `admin/configuracoes_clinica.html` | Deve permitir configurar horários de funcionamento, políticas de cancelamento, intervalos entre consultas e regras gerais. Atende ao RF9. |
| Perfis de acesso | `admin/perfis_acesso.html` | Deve listar perfis de acesso personalizados, suas permissões e usuários associados. Atende ao RF10. |
| Cadastrar perfil de acesso | `admin/cadastrar_perfil.html` | Deve permitir criar novo perfil e definir permissões por funcionalidade e nível de acesso. Atende ao RF10. |
| Editar perfil de acesso | `admin/editar_perfil.html` | Deve permitir alterar permissões, nome e status de um perfil de acesso. Atende ao RF10. |
| Estatísticas de uso | `admin/estatisticas.html` | Deve exibir relatórios e gráficos de pacientes cadastrados, consultas realizadas, cancelamentos, faltas, produtividade e uso da plataforma. |
| Plano e assinatura | `admin/plano.html` | Deve exibir plano atual da clínica, limite de usuários, limite de pacientes, cobrança, status de pagamento e opção de troca de plano. |
| Pagamentos | `admin/pagamentos.html` | Deve exibir histórico de pagamentos da assinatura da clínica, status, valores, vencimentos e integração com Mercado Pago. |

---

## 5. Área do dentista

O dentista acessa sua agenda, pacientes vinculados, histórico clínico, notificações e registra atendimentos.

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Dashboard do dentista | `dentista/dashboard.html` | Deve mostrar resumo do dia, próximas consultas, notificações, status dos atendimentos, pacientes agendados e indicadores básicos. Atende ao RF19. |
| Minha agenda | `dentista/agenda.html` | Deve exibir horários disponíveis, consultas marcadas e detalhes de atendimentos, com filtros por data e status. Atende ao RF20. |
| Detalhes da consulta | `dentista/detalhe_consulta.html` | Deve exibir paciente, horário, tipo de procedimento, observações, status e ações para confirmar, remarcar, cancelar ou registrar atendimento. |
| Consultas por período | `dentista/consultas_periodo.html` | Deve permitir consultar atendimentos por dia, semana, mês ou intervalo personalizado. |
| Meus pacientes | `dentista/pacientes.html` | Deve listar pacientes vinculados aos atendimentos do dentista, exibindo dados básicos e acesso ao histórico clínico. Atende ao RF21. |
| Detalhes do paciente | `dentista/detalhe_paciente.html` | Deve exibir dados básicos, informações de saúde, consultas, histórico clínico e observações do paciente. Atende ao RF21 e RF23. |
| Cadastrar paciente | `dentista/cadastrar_paciente.html` | Deve permitir cadastrar paciente durante atendimento, informando dados pessoais, contato, endereço e informações de saúde. Atende ao RF22. |
| Editar paciente | `dentista/editar_paciente.html` | Deve permitir atualizar dados permitidos do paciente, especialmente informações relevantes para o atendimento. Atende ao RF22. |
| Histórico de atendimentos do paciente | `dentista/historico_paciente.html` | Deve exibir procedimentos realizados, evolução clínica, observações, diagnósticos e registros anteriores. Atende ao RF23. |
| Registrar atendimento | `dentista/registrar_atendimento.html` | Deve permitir registrar procedimento realizado, observações clínicas, diagnóstico, anotações, anexos e recomendações. Atende ao RF24. |
| Atualizar dados da consulta | `dentista/atualizar_consulta.html` | Deve permitir atualizar status, observações e informações de uma consulta. Atende ao RF24, RF25 e RF26. |
| Confirmar consulta realizada | `dentista/confirmar_atendimento.html` | Deve permitir marcar consulta como concluída/atendida, atualizando o status. Atende ao RF25. |
| Remarcar ou cancelar consulta | `dentista/remarcar_cancelar.html` | Deve permitir alterar data/horário ou cancelar consulta, registrando justificativa conforme regras da clínica. Atende ao RF26. |
| Notificações do dentista | `dentista/notificacoes.html` | Deve listar alterações na agenda, consultas novas, cancelamentos, comunicados internos e lembretes. Atende ao RF27. |
| Meu perfil profissional | `dentista/perfil.html` | Deve permitir visualizar e atualizar telefone, e-mail, preferências do sistema e informações profissionais. Atende ao RF28. |
| Estatísticas de atendimento | `dentista/estatisticas.html` | Deve exibir quantidade de consultas, atendimentos concluídos, cancelamentos, faltas e produtividade por período. |

---

## 6. Área do atendente

O atendente opera a rotina da clínica: agenda, cadastro de pacientes, agendamentos, remarcações, cancelamentos, presença, lembretes e solicitações.

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Dashboard operacional | `atendente/dashboard.html` | Deve mostrar situação da clínica, agenda do dia, consultas pendentes, confirmações, cancelamentos e status dos atendimentos. Atende ao RF29. |
| Agenda completa | `atendente/agenda.html` | Deve exibir agenda de todos os dentistas, horários disponíveis, consultas e detalhes. Atende ao RF30 e RF41. |
| Consultas agendadas | `atendente/consultas.html` | Deve listar consultas por data, dentista, paciente e status. |
| Detalhes da consulta | `atendente/detalhe_consulta.html` | Deve exibir dados completos da consulta, paciente, dentista, status, histórico e ações possíveis. |
| Agendar consulta | `atendente/agendar_consulta.html` | Deve permitir vincular paciente, dentista e horário disponível, indicando tipo de atendimento. Atende ao RF33. |
| Remarcar consulta | `atendente/remarcar_consulta.html` | Deve permitir alterar data e horário de consulta previamente agendada, mantendo registro das alterações. Atende ao RF34. |
| Cancelar consulta | `atendente/cancelar_consulta.html` | Deve permitir cancelar consulta, registrar motivo e atualizar status. Atende ao RF35. |
| Registrar presença | `atendente/registrar_presenca.html` | Deve permitir marcar o paciente como presente, ausente ou atrasado. Atende ao RF36. |
| Alterar status da consulta | `atendente/alterar_status_consulta.html` | Deve permitir alterar status como agendado, confirmado, atendido ou cancelado. Atende ao RF37. |
| Pacientes | `atendente/pacientes.html` | Deve listar pacientes e permitir busca rápida por nome, CPF ou telefone. Atende ao RF31 e RF39. |
| Cadastrar paciente | `atendente/cadastrar_paciente.html` | Deve permitir cadastrar paciente com dados pessoais, contato, endereço e informações de saúde. Atende ao RF31. |
| Detalhes do paciente | `atendente/detalhe_paciente.html` | Deve exibir dados essenciais do paciente, histórico resumido, consultas e contato. Atende ao RF40. |
| Editar paciente | `atendente/editar_paciente.html` | Deve permitir atualizar telefone, endereço, e-mail e dados de saúde do paciente. Atende ao RF32. |
| Histórico de consultas | `atendente/historico_consultas.html` | Deve exibir histórico de consultas do paciente ou da clínica, com filtros por período, dentista e status. |
| Disponibilidade dos dentistas | `atendente/disponibilidade_dentistas.html` | Deve listar horários livres dos dentistas e permitir cadastrar bloqueios ou disponibilidades conforme permissão. Atende ao RF41. |
| Solicitações de agendamento | `atendente/solicitacoes_agendamento.html` | Deve listar solicitações públicas ou feitas por pacientes, permitindo confirmar, recusar, remarcar ou solicitar mais informações. Relaciona-se ao RF18 e aos casos de uso do atendente. |
| Moderar solicitação de consulta | `atendente/moderar_solicitacao.html` | Deve exibir detalhes da solicitação e permitir aprovar, ajustar horário, recusar ou transformar em consulta agendada. |
| Enviar lembrete/notificação | `atendente/enviar_notificacao.html` | Deve permitir enviar lembretes de consulta por e-mail, SMS ou WhatsApp, além de avisos importantes. Atende ao RF38. |

---

## 7. Área do paciente

O paciente visualiza seu cadastro, consultas agendadas, histórico, notificações, solicita/remarca/cancela consultas e confirma presença.

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Dashboard do paciente | `paciente/dashboard.html` | Deve mostrar dados resumidos, próximas consultas, histórico recente, notificações e atalhos para solicitar consulta ou atualizar cadastro. Atende ao RF42. |
| Meus dados cadastrais | `paciente/dados.html` | Deve exibir informações pessoais cadastradas, contato, endereço e dados essenciais. Atende ao RF50. |
| Atualizar dados cadastrais | `paciente/editar_dados.html` | Deve permitir atualizar endereço, telefone, e-mail e informações de contato. Atende ao RF47. |
| Minhas consultas agendadas | `paciente/consultas.html` | Deve listar consultas futuras, com data, horário, dentista responsável, serviço e observações. Atende ao RF43. |
| Detalhes da consulta | `paciente/detalhe_consulta.html` | Deve exibir informações completas da consulta, status, dentista, data, horário, observações e ações disponíveis. |
| Solicitar/agendar consulta | `paciente/solicitar_consulta.html` | Deve permitir solicitar ou agendar consulta informando preferência de horário, serviço, observações e contato. A confirmação pode depender da clínica. Atende ao RF45. |
| Remarcar consulta | `paciente/remarcar_consulta.html` | Deve permitir solicitar nova data ou horário, respeitando regras de antecedência da clínica. Atende ao RF46. |
| Cancelar consulta | `paciente/cancelar_consulta.html` | Deve permitir cancelar consulta agendada, com aviso sobre políticas de cancelamento e campo de justificativa. Atende ao RF46. |
| Confirmar presença | `paciente/confirmar_presenca.html` | Deve permitir confirmar presença em consulta agendada, ajudando a organização da clínica. Atende ao RF49. |
| Histórico de consultas | `paciente/historico.html` | Deve listar consultas já realizadas, com data, dentista, procedimento e informações permitidas ao paciente. Atende ao RF44. |
| Notificações do paciente | `paciente/notificacoes.html` | Deve listar confirmações de agendamento, lembretes, remarcações, cancelamentos e mensagens importantes. Atende ao RF48. |

---

## 8. Agenda, consultas e atendimentos — páginas compartilhadas

Algumas páginas podem ser compartilhadas entre administrador, dentista e atendente, variando apenas permissões e ações disponíveis.

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Calendário da agenda | `agenda/calendario.html` | Visualização centralizada da agenda em modo dia, semana e mês, com filtros por profissional, status e tipo de consulta. |
| Grade de horários | `agenda/horarios.html` | Deve exibir horários livres, ocupados e bloqueados dos dentistas. |
| Bloqueios de agenda | `agenda/bloqueios.html` | Deve permitir registrar horários indisponíveis, férias, pausas e intervalos. |
| Novo bloqueio | `agenda/novo_bloqueio.html` | Formulário para cadastrar indisponibilidade de dentista ou da clínica. |
| Detalhe de consulta compartilhado | `agenda/detalhe_consulta.html` | Página reutilizável para exibição de consulta, com ações condicionadas ao perfil logado. |
| Linha do tempo da consulta | `agenda/historico_alteracoes.html` | Deve listar mudanças de data, horário, status, cancelamentos, confirmações e responsáveis por cada alteração. |
| Prontuário/histórico clínico | `atendimento/prontuario.html` | Deve reunir histórico clínico, procedimentos, diagnósticos, observações, alergias, hábitos e anexos digitais. |
| Anexos do paciente | `atendimento/anexos.html` | Deve permitir listar e anexar exames, documentos ou imagens, respeitando permissões e segurança. |
| Relatório de produtividade | `relatorios/produtividade.html` | Deve apresentar dados de consultas, atendimentos, cancelamentos, faltas e produção por profissional. |
| Relatório de faltas | `relatorios/faltas.html` | Deve indicar ausências e cancelamentos por período, profissional e paciente. |

---

## 9. Notificações, pagamentos e plano SaaS

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Configuração de lembretes | `notificacoes/configurar_lembretes.html` | Deve permitir configurar quando e como os lembretes serão enviados: e-mail, SMS ou WhatsApp. |
| Histórico de notificações | `notificacoes/historico.html` | Deve listar notificações enviadas, status de envio, destinatário, canal e relação com consulta. |
| Templates de mensagem | `notificacoes/templates.html` | Deve permitir configurar textos padrão para confirmação, lembrete, cancelamento, remarcação e aviso geral. |
| Checkout de assinatura | `pagamento/checkout.html` | Deve apresentar plano escolhido, valor, dados da clínica e integração com Mercado Pago. |
| Resultado do pagamento | `pagamento/resultado.html` | Deve informar se o pagamento foi aprovado, recusado ou está pendente. |
| Histórico de pagamentos | `pagamento/historico.html` | Deve exibir mensalidades, vencimentos, status e comprovantes. |
| Detalhe do pagamento | `pagamento/detalhe.html` | Deve mostrar dados completos de uma cobrança ou pagamento específico. |

---

## 10. Suporte, auditoria e administração técnica

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Chamados de suporte | `suporte/chamados.html` | Deve listar chamados abertos por usuários da clínica, com status, prioridade e assunto. |
| Abrir chamado | `suporte/abrir_chamado.html` | Deve permitir relatar problema, dúvida ou solicitação de melhoria. |
| Detalhe do chamado | `suporte/detalhe_chamado.html` | Deve exibir conversa, respostas, anexos e status do atendimento. |
| Central de ajuda | `suporte/ajuda.html` | Deve conter perguntas frequentes sobre cadastro, agenda, pacientes, notificações e pagamento. |
| Auditoria | `admin/auditoria.html` | Deve registrar ações críticas: login, alteração de paciente, agendamento, cancelamento, exclusão, alteração de permissões e configurações. Relaciona-se ao RNF17. |
| Logs do sistema | `admin/logs.html` | Deve listar eventos técnicos, erros, falhas de integração, tentativas de login e alertas. Relaciona-se ao RNF14. |
| Backup e restauração | `admin/backups.html` | Deve exibir status de backups, datas, opções de download/exportação e informações de recuperação. Relaciona-se ao RNF13. |

---

## 11. Páginas auxiliares e de erro

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Acesso negado | `errors/403.html` | Deve informar que o usuário não tem permissão para acessar a página ou funcionalidade. |
| Página não encontrada | `errors/404.html` | Deve informar que a página não existe e oferecer botões para voltar à home, dashboard ou agenda. |
| Erro interno | `errors/500.html` | Deve apresentar mensagem genérica de erro, sem expor detalhes técnicos ao usuário final. |
| Manutenção | `errors/manutencao.html` | Deve informar períodos de manutenção programada. |
| Sessão expirada | `errors/sessao_expirada.html` | Deve informar que a sessão expirou e oferecer link para login. |
| Confirmação genérica | `shared/confirmacao.html` | Pode ser usada para cadastro realizado, consulta solicitada, mensagem enviada, pagamento confirmado e outras operações concluídas. |

---

## 12. Templates parciais reutilizáveis

Além das páginas completas, recomenda-se criar componentes Jinja reutilizáveis.

| Template parcial | Finalidade |
|---|---|
| `base.html` | Estrutura base com HTML, head, CSS, scripts, blocos Jinja e layout geral. |
| `_navbar.html` | Menu superior adaptado para usuário anônimo, paciente, dentista, atendente ou administrador. |
| `_footer.html` | Rodapé com links institucionais, contato, termos e privacidade. |
| `_sidebar_admin.html` | Menu lateral da área administrativa. |
| `_sidebar_dentista.html` | Menu lateral da área do dentista. |
| `_sidebar_atendente.html` | Menu lateral da área do atendente. |
| `_sidebar_paciente.html` | Menu lateral da área do paciente. |
| `_mensagens.html` | Exibição de mensagens de sucesso, erro, alerta e informação. |
| `_card_paciente.html` | Card reutilizável para exibir dados resumidos de pacientes. |
| `_card_dentista.html` | Card reutilizável para exibir profissionais. |
| `_card_consulta.html` | Card reutilizável para exibir consulta em listas e dashboards. |
| `_form_paciente.html` | Formulário compartilhado para cadastro e edição de pacientes. |
| `_form_consulta.html` | Formulário compartilhado para criação, edição e remarcação de consultas. |
| `_form_dentista.html` | Formulário compartilhado para cadastro e edição de dentistas. |
| `_form_atendente.html` | Formulário compartilhado para cadastro e edição de atendentes. |
| `_filtros_consultas.html` | Filtros por data, profissional, paciente e status. |
| `_filtros_pacientes.html` | Filtros e busca por nome, CPF, telefone e e-mail. |
| `_status_consulta.html` | Componente visual para status: agendada, confirmada, atendida, cancelada, ausente ou remarcada. |
| `_paginacao.html` | Paginação para listagens longas. |
| `_modal_confirmacao.html` | Modal para confirmar exclusões, cancelamentos, remarcações e alterações importantes. |
| `_agenda_mini.html` | Mini calendário ou resumo da agenda do dia para dashboards. |
| `_notificacao_item.html` | Item reutilizável para exibir notificações. |

---

## 13. Lista mínima para uma primeira versão funcional

Para uma primeira entrega viável, recomenda-se priorizar estas páginas:

1. `public/home.html`
2. `public/sobre.html`
3. `public/servicos.html`
4. `public/contato.html`
5. `public/solicitar_agendamento.html`
6. `auth/login.html`
7. `auth/cadastro_paciente.html`
8. `auth/recuperar_senha.html`
9. `auth/redefinir_senha.html`
10. `usuario/perfil.html`
11. `usuario/alterar_senha.html`
12. `admin/dashboard.html`
13. `admin/usuarios.html`
14. `admin/dentistas.html`
15. `admin/cadastrar_dentista.html`
16. `admin/atendentes.html`
17. `admin/cadastrar_atendente.html`
18. `admin/pacientes.html`
19. `admin/cadastrar_paciente.html`
20. `admin/detalhe_paciente.html`
21. `admin/agenda.html`
22. `admin/nova_consulta.html`
23. `admin/detalhe_consulta.html`
24. `admin/configuracoes_clinica.html`
25. `dentista/dashboard.html`
26. `dentista/agenda.html`
27. `dentista/pacientes.html`
28. `dentista/detalhe_paciente.html`
29. `dentista/registrar_atendimento.html`
30. `atendente/dashboard.html`
31. `atendente/agenda.html`
32. `atendente/consultas.html`
33. `atendente/agendar_consulta.html`
34. `atendente/pacientes.html`
35. `atendente/cadastrar_paciente.html`
36. `atendente/solicitacoes_agendamento.html`
37. `paciente/dashboard.html`
38. `paciente/dados.html`
39. `paciente/consultas.html`
40. `paciente/solicitar_consulta.html`
41. `paciente/historico.html`
42. `notificacoes/configurar_lembretes.html`
43. `notificacoes/historico.html`
44. `errors/403.html`
45. `errors/404.html`
46. `errors/500.html`

---

## 14. Observações importantes

- A aplicação deve considerar os perfis principais: **usuário anônimo**, **paciente**, **dentista**, **atendente** e **administrador**.
- Como a aplicação lida com dados pessoais e informações de saúde, é importante dar atenção especial a privacidade, LGPD, controle de acesso por perfil, auditoria, criptografia, backup e logs.
- O documento cita integrações com envio de e-mails, consulta de CEP e Mercado Pago, o que justifica páginas e fluxos para confirmação/lembretes de consulta, preenchimento automático de endereço e gerenciamento de assinatura.
- Há trechos finais aparentemente reaproveitados de outro projeto, mencionando “Autores, Leitores e Administradores” e “SimpleBlog”. Para a implementação, devem ser considerados os perfis e requisitos funcionais próprios do OdontoX: administrador, dentista, atendente, paciente e usuário anônimo.
- Como o projeto usa **FastAPI** com **Jinja**, os nomes sugeridos seguem uma estrutura compatível com aplicações server-side rendered.

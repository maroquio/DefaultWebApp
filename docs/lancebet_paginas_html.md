# Lance.BET — Lista de páginas HTML necessárias

Este documento reúne as páginas HTML recomendadas para implementar a aplicação **Lance.BET — Apostas Esportivas**, com base nos requisitos funcionais, requisitos não funcionais, perfis de usuário, diferenciais de funcionalidades e diagramas de casos de uso descritos na documentação do projeto.

A aplicação é uma plataforma web de apostas esportivas, com foco em **segurança**, **gestão de saldo**, **cálculo de odds**, **depósitos e saques**, **histórico de apostas**, **ambiente de teste**, **jogo responsável** e **área administrativa para gerenciamento de eventos, usuários, odds e movimentações financeiras**.

---

## 1. Páginas públicas

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Página inicial | `public/home.html` | Deve apresentar a plataforma Lance.BET, explicar a proposta do serviço, destacar segurança, transparência, simplicidade da interface, principais esportes disponíveis, botões para login e cadastro, aviso de maioridade obrigatória e links para eventos ativos, regras e política de privacidade. Atende aos RF1, RF24, RF25, RF26 e RF27. |
| Lista pública de eventos esportivos | `public/eventos.html` | Deve listar eventos esportivos ativos que podem ser visualizados por usuários anônimos, exibindo esporte, campeonato, equipes/competidores, data, horário e odds principais em modo somente leitura. Atende ao RF2. |
| Detalhes públicos do evento | `public/detalhe_evento.html` | Deve exibir os dados principais de um evento esportivo: modalidade, times ou atletas, data/hora, status, mercados disponíveis e odds visíveis sem permitir apostar enquanto o usuário não estiver autenticado. |
| Como funciona | `public/como_funciona.html` | Deve explicar, em etapas simples, como criar conta, verificar identidade, adicionar saldo, escolher evento, visualizar odds, confirmar aposta, acompanhar resultado e solicitar saque. |
| Regras da plataforma | `public/regras.html` | Deve apresentar regras gerais de uso, funcionamento das apostas, confirmação/cancelamento de apostas, liquidação, resultados oficiais, limites, condutas proibidas, regras de saque e responsabilidades do usuário. Atende aos RF4 e RF16. |
| Política de privacidade e LGPD | `public/privacidade_lgpd.html` | Deve explicar coleta, uso, armazenamento e proteção de dados pessoais, incluindo CPF, e-mail, documentos, transações financeiras, histórico de apostas e dados de verificação de identidade. Atende aos RF3 e RF15. |
| Jogo responsável | `public/jogo_responsavel.html` | Deve conter informações sobre uso responsável da plataforma, riscos associados a apostas, definição de limites, pausa temporária, autoexclusão e canais de orientação. Relaciona-se ao RF42 e ao aviso de maioridade do RF27. |
| Contato e suporte público | `public/contato.html` | Deve apresentar canais de contato, formulário simples de mensagem e informações para suporte antes do cadastro ou login. |

---

## 2. Páginas de autenticação, cadastro e verificação

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Login | `auth/login.html` | Deve conter formulário de CPF ou e-mail e senha, botão de entrada, links para cadastro e recuperação de senha. Deve redirecionar apostador para sua área e administrador para a área administrativa. Atende aos RF7, RF25 e RF44. |
| Cadastro de apostador | `auth/cadastro.html` | Deve conter formulário com dados pessoais obrigatórios, como nome completo, CPF, data de nascimento, e-mail, telefone e senha. Deve incluir confirmação de maioridade e aceite dos termos. Atende aos RF5, RF28 e RF29. |
| Instruções de cadastro | `auth/instrucoes_cadastro.html` | Deve explicar quais dados são necessários, por que a maioridade é obrigatória, como ocorre a verificação de identidade e quais funcionalidades ficam bloqueadas até a liberação da conta. Atende ao RF26. |
| Validação de CPF | `auth/validar_cpf.html` | Deve permitir validar CPF durante o cadastro ou em etapa intermediária, integrando com API externa de CPF. Deve exibir mensagens claras em caso de CPF inválido, inconsistente ou já cadastrado. |
| Verificação de identidade | `auth/verificacao_identidade.html` | Deve solicitar dados e documentos necessários para liberar funcionalidades de aposta, depósito e saque. Deve mostrar o status da verificação: pendente, aprovada ou reprovada. Atende ao RF30. |
| Confirmação de e-mail | `auth/confirmar_email.html` | Deve orientar o usuário a confirmar o e-mail ou exibir mensagem de confirmação concluída. Pode ser usada após cadastro e recuperação de senha. |
| Recuperação de senha | `auth/recuperar_senha.html` | Deve permitir que o apostador informe o e-mail cadastrado para receber instruções de recuperação. Atende ao RF13. |
| Redefinição de senha | `auth/redefinir_senha.html` | Deve conter campos de nova senha e confirmação de senha, acessada por link ou token enviado por e-mail. |
| Logout/encerramento de sessão | `auth/logout.html` | Pode ser uma tela simples de confirmação de sessão encerrada, com botão para voltar à home ou ao login. Atende ao RF43. |

---

## 3. Páginas comuns do apostador

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Dashboard do apostador | `apostador/dashboard.html` | Deve mostrar saldo disponível, atalhos para eventos, apostas em aberto, últimas apostas, notificações, depósitos, saques e limites de jogo responsável. Atende aos RF6 e RF32. |
| Meu perfil | `apostador/perfil.html` | Deve exibir dados cadastrais, status de verificação, CPF parcialmente mascarado, e-mail, telefone e informações permitidas para edição. Atende ao RF31. |
| Editar perfil | `apostador/editar_perfil.html` | Deve permitir editar apenas os dados autorizados, como telefone, e-mail secundário ou preferências de notificação, preservando dados sensíveis sujeitos à verificação. Atende ao RF31. |
| Alterar senha | `apostador/alterar_senha.html` | Deve conter senha atual, nova senha e confirmação da nova senha. |
| Notificações | `apostador/notificacoes.html` | Deve listar avisos de apostas confirmadas, eventos encerrados, resultados, depósitos, saques, alterações de odds antes da confirmação e alertas de segurança. Atende ao RF40. |
| Limites e jogo responsável | `apostador/limites.html` | Deve permitir configurar limites de aposta, limites de depósito, pausa temporária, bloqueios voluntários e mensagens educativas. Atende ao RF42. |
| Suporte do apostador | `apostador/suporte.html` | Deve permitir enviar mensagem ao suporte, acompanhar chamados e tratar problemas de depósito, saque, conta, aposta ou verificação. |

---

## 4. Páginas de eventos e apostas

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Página de apostas | `apostas/eventos.html` | Deve listar eventos disponíveis para aposta, com filtros por esporte, campeonato, data, status e busca textual. Deve mostrar odds atualizadas. Atende ao RF8 e RF38. |
| Detalhes do evento para aposta | `apostas/detalhe_evento.html` | Deve exibir informações completas do evento, mercados de aposta, odds, status, data/hora, regras específicas, estatísticas básicas e botão para selecionar uma aposta. Atende ao RF10, RF11 e RF38. |
| Boletim/cupom de aposta | `apostas/cupom.html` | Deve mostrar seleções feitas pelo apostador, valor apostado, odds aplicadas, retorno potencial, saldo disponível, mensagens de alteração de odds e botão de confirmação. Atende aos RF11, RF37, RF38 e RF53. |
| Confirmação de aposta | `apostas/confirmar.html` | Deve exibir resumo final antes da confirmação: evento, mercado, seleção, valor, odds, retorno potencial e regras. Deve permitir confirmar ou cancelar antes do registro definitivo. Atende aos RF36, RF37 e RF39. |
| Aposta confirmada | `apostas/aposta_confirmada.html` | Deve exibir comprovante da aposta com número/código, data, horário, valor, odds, retorno potencial e status inicial. Atende ao RF39. |
| Apostas em aberto | `apostas/em_aberto.html` | Deve listar apostas ainda não liquidadas, com evento, valor, odds, possível retorno, status do evento e opção de cancelamento apenas quando aplicável. Atende ao RF36. |
| Histórico de apostas reais | `apostas/historico.html` | Deve exibir histórico completo de apostas reais, incluindo evento, data, horário, valor apostado, odds, possível retorno, resultado final e status. Atende ao RF9 e RF41. |
| Histórico de apostas de teste | `apostas/historico_teste.html` | Deve exibir separadamente as apostas feitas no ambiente de teste, sem uso de saldo real. Atende ao RF14 e RF41. |
| Resultados de eventos | `apostas/resultados.html` | Deve listar resultados e status dos eventos esportivos, indicando eventos em andamento, encerrados, cancelados ou liquidados. Atende ao RF10 e RF17. |
| Detalhes da aposta | `apostas/detalhe_aposta.html` | Deve mostrar todos os dados de uma aposta específica, incluindo linha do tempo, odds no momento da aposta, resultado oficial, cálculo do ganho ou perda e comprovante. |

---

## 5. Ambiente de teste

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Página inicial do modo teste | `teste/dashboard.html` | Deve explicar que o modo teste não usa saldo real e serve para simular apostas. Deve exibir saldo fictício, eventos disponíveis e histórico de teste. Atende ao RF14. |
| Eventos do modo teste | `teste/eventos.html` | Deve listar eventos disponíveis para simulação, com odds e filtros semelhantes aos da página real. |
| Cupom de aposta de teste | `teste/cupom.html` | Deve permitir simular valor de aposta, odds e retorno potencial sem movimentação financeira real. |
| Aposta de teste confirmada | `teste/aposta_confirmada.html` | Deve exibir comprovante fictício da aposta simulada. |
| Histórico de teste | `teste/historico.html` | Deve listar todas as apostas simuladas, separadas do histórico de apostas reais. Atende ao RF41. |

---

## 6. Carteira, depósitos, saques e extrato

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Carteira do apostador | `carteira/dashboard.html` | Deve mostrar saldo disponível, saldo bloqueado em apostas abertas, valores pendentes de saque, últimos depósitos e últimas movimentações. Atende ao RF32. |
| Depósito | `carteira/deposito.html` | Deve permitir adicionar saldo por cartão, Pix ou boleto via MercadoPago, mostrando valor, método escolhido, taxas quando houver e instruções de pagamento. Atende ao RF12 e RF34. |
| Status do depósito | `carteira/status_deposito.html` | Deve exibir se o depósito está pendente, aprovado, recusado, expirado ou cancelado. Atende ao RF34. |
| Saque | `carteira/saque.html` | Deve permitir solicitar saque, informando valor, método disponível, dados da conta ou chave Pix, regras e prazo estimado. Atende ao RF12 e RF35. |
| Status do saque | `carteira/status_saque.html` | Deve permitir acompanhar solicitações de saque: pendente, em análise, aprovado, pago, recusado ou cancelado. Atende ao RF35. |
| Extrato financeiro | `carteira/extrato.html` | Deve listar entradas e saídas da conta: depósitos, apostas, ganhos, perdas, estornos, saques e ajustes administrativos. Atende ao RF33. |
| Detalhe da movimentação | `carteira/detalhe_movimentacao.html` | Deve mostrar informações completas de uma transação específica, como tipo, data, valor, status, referência e comprovante. |
| Métodos de pagamento | `carteira/metodos_pagamento.html` | Deve permitir visualizar ou gerenciar métodos de pagamento vinculados, respeitando segurança e conformidade. |
| Comprovante de transação | `carteira/comprovante.html` | Deve exibir recibo de depósito, saque, estorno ou movimentação relevante. |

---

## 7. Área administrativa

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Login administrativo | `admin/login.html` | Deve permitir login do administrador com conta corporativa ou pré-configurada. Atende ao RF44. |
| Dashboard administrativo | `admin/dashboard.html` | Deve mostrar visão geral da plataforma: eventos ativos, apostas em aberto, usuários cadastrados, saldo total, entradas, saídas, saques pendentes, movimentações atípicas e alertas de risco. |
| Gerenciar eventos | `admin/eventos.html` | Deve listar eventos cadastrados, com filtros por esporte, data, status e campeonato, além de ações para editar, encerrar ou validar resultado. Atende aos RF17, RF45, RF46 e RF47. |
| Cadastrar evento | `admin/cadastrar_evento.html` | Deve permitir cadastrar novo evento esportivo, informando modalidade, campeonato, participantes, data/hora, mercados e odds iniciais. Atende ao RF45. |
| Editar evento | `admin/editar_evento.html` | Deve permitir atualizar informações de eventos cadastrados, como horário, status, mercados e dados básicos. Atende ao RF46. |
| Alterar odds | `admin/alterar_odds.html` | Deve permitir alterar odds dos eventos, registrar justificativa e exibir histórico de alterações para controle e auditoria. Atende ao RF18. |
| Encerrar evento | `admin/encerrar_evento.html` | Deve permitir encerrar evento após finalização, bloqueando novas apostas e encaminhando para validação de resultado. Atende ao RF47. |
| Registrar/validar resultado | `admin/validar_resultado.html` | Deve permitir registrar ou validar resultados oficiais dos eventos, disparando a liquidação das apostas vinculadas. Atende ao RF48. |
| Usuários | `admin/usuarios.html` | Deve listar todos os apostadores, com filtros por status, verificação, saldo, data de cadastro e movimentações suspeitas. Atende ao RF19. |
| Detalhes do usuário | `admin/detalhe_usuario.html` | Deve exibir dados cadastrais, status da conta, verificação de identidade, saldo, histórico de apostas, depósitos, saques e ações administrativas. Atende ao RF19. |
| Liberar/bloquear usuário | `admin/bloquear_usuario.html` | Deve permitir liberar ou bloquear usuário, com campo de justificativa e registro de auditoria. Atende ao RF49. |
| Excluir conta de usuário | `admin/excluir_usuario.html` | Deve permitir excluir ou desativar conta de usuário, com confirmação, justificativa e regras de segurança. Atende ao RF20. |
| Histórico geral de apostas | `admin/historico_apostas.html` | Deve listar todas as apostas realizadas na plataforma para controle, monitoramento e análise operacional. Atende ao RF23. |
| Detalhes de aposta administrativa | `admin/detalhe_aposta.html` | Deve exibir dados completos de uma aposta, incluindo usuário, evento, odds, valor, status, resultado e cálculo de liquidação. |
| Entradas e saídas financeiras | `admin/financeiro.html` | Deve listar entradas e saídas de valores da plataforma, incluindo depósitos, saques, ganhos pagos, perdas, estornos e taxas. Atende ao RF21. |
| Histórico de depósitos | `admin/depositos.html` | Deve listar depósitos realizados pelos usuários, com status, método, valor, data e usuário. Atende ao RF50. |
| Solicitações de saque | `admin/saques.html` | Deve listar e permitir gerenciar solicitações de saque pendentes, aprovadas, recusadas ou pagas. Atende ao RF22 e RF51. |
| Detalhes do saque | `admin/detalhe_saque.html` | Deve exibir dados completos de uma solicitação de saque, histórico, usuário, valor, método, análise e ações de aprovar/recusar. |
| Monitoramento de movimentações atípicas | `admin/monitoramento.html` | Deve destacar usuários com movimentações suspeitas ou atípicas, como valores elevados, muitos saques, alterações frequentes ou comportamento incompatível com o perfil. Atende ao RF52. |
| Gestão de risco | `admin/risco.html` | Deve apoiar a gestão operacional com volume apostado por evento, concentração de apostas, exposição financeira, limite de apostas e alertas de possível prejuízo. Relaciona-se aos objetivos de gestão de risco. |
| Relatórios administrativos | `admin/relatorios.html` | Deve reunir relatórios de usuários, apostas, eventos, movimentações financeiras, resultados e desempenho da plataforma. |
| Auditoria | `admin/auditoria.html` | Deve registrar ações críticas: login administrativo, alteração de odds, validação de resultado, bloqueio de usuário, exclusão de conta, aprovação de saque e ajustes financeiros. Relaciona-se ao RNF17. |
| Logs e monitoramento | `admin/logs.html` | Deve permitir consulta de erros, eventos de sistema, falhas de integração, tentativas de login e alertas de segurança. Relaciona-se ao RNF14. |

---

## 8. Páginas de suporte e comunicação

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Lista de chamados | `suporte/chamados.html` | Deve listar chamados abertos pelo apostador, com status, assunto, data e última resposta. |
| Abrir chamado | `suporte/abrir_chamado.html` | Deve permitir abrir chamado sobre conta, verificação, depósito, saque, aposta, resultado ou problema técnico. |
| Detalhe do chamado | `suporte/detalhe_chamado.html` | Deve exibir conversa entre usuário e suporte, anexos simples, status e histórico de atendimento. |
| Central de ajuda | `suporte/ajuda.html` | Deve conter perguntas frequentes sobre cadastro, verificação, depósitos, saques, apostas, resultados e jogo responsável. |

---

## 9. Páginas auxiliares e de erro

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Acesso negado | `errors/403.html` | Deve informar que o usuário não tem permissão para acessar a página ou funcionalidade. |
| Página não encontrada | `errors/404.html` | Deve informar que a página não existe e oferecer botões para voltar à home, eventos ou dashboard. |
| Erro interno | `errors/500.html` | Deve apresentar mensagem genérica de erro sem expor detalhes técnicos. |
| Manutenção | `errors/manutencao.html` | Deve informar períodos de manutenção ou indisponibilidade programada. |
| Conta não verificada | `errors/conta_nao_verificada.html` | Deve informar que determinadas funcionalidades estão bloqueadas até a verificação de identidade. |
| Saldo insuficiente | `errors/saldo_insuficiente.html` | Deve informar que o saldo disponível não permite confirmar a aposta e oferecer atalho para depósito. |
| Aposta indisponível | `errors/aposta_indisponivel.html` | Deve informar que o evento, mercado ou odd não está mais disponível, possivelmente por encerramento ou alteração. |
| Confirmação genérica | `shared/confirmacao.html` | Pode ser usada para operações concluídas, como cadastro realizado, e-mail enviado, aposta confirmada, depósito solicitado ou chamado aberto. |

---

## 10. Templates parciais reutilizáveis

Além das páginas completas, recomenda-se criar componentes Jinja reutilizáveis.

| Template parcial | Finalidade |
|---|---|
| `base.html` | Estrutura base com HTML, head, CSS, scripts, blocos Jinja e layout geral. |
| `_navbar.html` | Menu superior adaptado para usuário anônimo, apostador ou administrador. |
| `_footer.html` | Rodapé com links para regras, privacidade, jogo responsável e suporte. |
| `_sidebar_apostador.html` | Menu lateral da área do apostador. |
| `_sidebar_admin.html` | Menu lateral da área administrativa. |
| `_mensagens.html` | Exibição de mensagens de sucesso, erro, alerta e informação. |
| `_card_evento.html` | Card reutilizável para exibir eventos esportivos. |
| `_linha_odd.html` | Componente para exibir mercados e odds. |
| `_cupom_aposta.html` | Componente reutilizável do boletim/cupom de aposta. |
| `_saldo_resumo.html` | Componente para exibir saldo disponível, saldo bloqueado e atalhos financeiros. |
| `_status_aposta.html` | Componente visual para status de aposta: aberta, confirmada, ganha, perdida, cancelada ou liquidada. |
| `_status_evento.html` | Componente visual para status de evento: aberto, ao vivo, encerrado, cancelado ou liquidado. |
| `_status_transacao.html` | Componente visual para depósitos e saques. |
| `_form_evento.html` | Formulário compartilhado para cadastrar e editar eventos esportivos. |
| `_form_odds.html` | Formulário para cadastrar ou alterar odds. |
| `_paginacao.html` | Paginação para listagens longas. |
| `_filtros_eventos.html` | Filtros por esporte, campeonato, data e status. |
| `_modal_confirmacao.html` | Modal para confirmar ações como aposta, saque, bloqueio de usuário, encerramento de evento ou exclusão. |
| `_aviso_maioridade.html` | Componente com aviso de obrigatoriedade de maioridade. |
| `_aviso_jogo_responsavel.html` | Componente com alerta e links para limites, pausa e jogo responsável. |

---

## 11. Lista mínima para uma primeira versão funcional

Para uma primeira entrega viável, recomenda-se priorizar estas páginas:

1. `public/home.html`
2. `public/eventos.html`
3. `public/detalhe_evento.html`
4. `public/regras.html`
5. `public/privacidade_lgpd.html`
6. `public/jogo_responsavel.html`
7. `auth/login.html`
8. `auth/cadastro.html`
9. `auth/validar_cpf.html`
10. `auth/verificacao_identidade.html`
11. `auth/recuperar_senha.html`
12. `auth/redefinir_senha.html`
13. `apostador/dashboard.html`
14. `apostador/perfil.html`
15. `apostador/editar_perfil.html`
16. `apostador/limites.html`
17. `apostas/eventos.html`
18. `apostas/detalhe_evento.html`
19. `apostas/cupom.html`
20. `apostas/confirmar.html`
21. `apostas/aposta_confirmada.html`
22. `apostas/em_aberto.html`
23. `apostas/historico.html`
24. `apostas/resultados.html`
25. `teste/dashboard.html`
26. `teste/eventos.html`
27. `teste/cupom.html`
28. `teste/historico.html`
29. `carteira/dashboard.html`
30. `carteira/deposito.html`
31. `carteira/status_deposito.html`
32. `carteira/saque.html`
33. `carteira/status_saque.html`
34. `carteira/extrato.html`
35. `admin/login.html`
36. `admin/dashboard.html`
37. `admin/eventos.html`
38. `admin/cadastrar_evento.html`
39. `admin/editar_evento.html`
40. `admin/alterar_odds.html`
41. `admin/validar_resultado.html`
42. `admin/usuarios.html`
43. `admin/detalhe_usuario.html`
44. `admin/historico_apostas.html`
45. `admin/financeiro.html`
46. `admin/depositos.html`
47. `admin/saques.html`
48. `admin/monitoramento.html`
49. `admin/risco.html`
50. `suporte/abrir_chamado.html`
51. `suporte/chamados.html`
52. `suporte/detalhe_chamado.html`
53. `errors/403.html`
54. `errors/404.html`
55. `errors/500.html`

---

## 12. Observações importantes

- A aplicação deve considerar os perfis principais: **usuário anônimo**, **apostador** e **administrador**.
- Como a aplicação envolve apostas esportivas com dinheiro real, é recomendável dar atenção especial às páginas de **maioridade**, **verificação de identidade**, **jogo responsável**, **limites de aposta**, **privacidade/LGPD**, **auditoria** e **monitoramento de movimentações atípicas**.
- O documento menciona integrações com **MercadoPago**, **apicpf.com** e **Resend.com**, o que justifica páginas e fluxos de pagamento, validação de CPF, recuperação de senha, confirmação de cadastro e notificações por e-mail.
- O documento também menciona inconsistências textuais no final, como referências a “Autores, Leitores e Administradores” e “SimpleBlog”. Para implementação, devem ser considerados os perfis e requisitos funcionais da Lance.BET: usuário anônimo, apostador e administrador.
- Como o projeto usa **FastAPI** com **Jinja**, os nomes sugeridos seguem uma estrutura compatível com aplicações server-side rendered.

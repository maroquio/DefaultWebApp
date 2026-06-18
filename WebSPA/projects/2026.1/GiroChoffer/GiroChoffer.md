# GiroChoffer

## 1\. Diagrama de Entidades e Relacionamentos — DER conceitual

### Entidades principais

| Entidade | Campos principais sugeridos | Papel no sistema |
| --- | --- | --- |
| **Usuario** | id, nome, e-mail, senha, telefone, tipo\_perfil, status, data\_cadastro | Entidade-base para todos os usuários: motorista, empresa/transportadora e administrador. |
| **Motorista** | id, usuario\_id, CPF, CNH, data\_nascimento, média\_avaliação, verificado | Especialização de usuário para quem busca e aceita fretes. |
| **Empresa** | id, usuario\_id, CNPJ, razão\_social, nome\_fantasia, inscrição\_estadual, verificada | Especialização de usuário para quem publica cargas e contrata motoristas. |
| **Administrador** | id, usuario\_id, cargo, nível\_acesso | Usuário interno com permissão de moderação e gestão. |
| **PlanoAssinatura** | id, nome, preço, limite\_cargas\_mês, limite\_gestores, recursos | Define os planos Free, Starter e Pro. |
| **AssinaturaEmpresa** | id, empresa\_id, plano\_id, status, início, fim | Registra o plano contratado por cada empresa. |
| **Pagamento** | id, assinatura\_id, viagem\_id, valor, método, status, gateway\_ref | Registra pagamentos de assinatura e/ou fretes. |
| **Endereco** | id, CEP, logradouro, número, bairro, cidade, UF, latitude, longitude | Usado para endereços de origem/destino das cargas e, opcionalmente, endereço de usuários. |
| **TipoVeiculo** | id, nome, ativo | Categoria de veículo: caminhão, carro, moto etc. |
| **TipoCarroceria** | id, nome, descrição, ativo | Categoria logística: baú, graneleiro, refrigerado, aberto etc. |
| **Veiculo** | id, motorista\_id, tipo\_veiculo\_id, tipo\_carroceria\_id, placa, capacidade\_kg, volume\_m3, ativo | Veículos cadastrados pelo motorista. |
| **RotaInteresse** | id, motorista\_id, origem\_cidade, origem\_UF, destino\_cidade, destino\_UF, raio\_km | Rotas nas quais o motorista tem interesse. |
| **Carga** | id, empresa\_id, origem\_id, destino\_id, tipo\_veiculo\_id, tipo\_carroceria\_id, título, descrição, peso, volume, valor\_frete, data\_coleta, status, agendada\_para | Oferta de carga publicada pela empresa. |
| **TagCarga** | id, nome, ativo | Tags como “Carga Frágil”, “Refrigerada”, “Urgente”. |
| **CargaTag** | carga\_id, tag\_id | Tabela intermediária para relação N:N entre cargas e tags. |
| **VisualizacaoCarga** | id, carga\_id, motorista\_id, visualizada\_em | Registra visualizações para métricas da empresa. |
| **SolicitacaoCarga** | id, carga\_id, motorista\_id, veiculo\_id, origem\_solicitacao, status, criada\_em | Representa candidatura do motorista ou convite da empresa. |
| **Viagem** | id, carga\_id, motorista\_id, veiculo\_id, valor\_fechado, status, início, fim | Frete efetivamente aceito e executado. |
| **HistoricoStatusViagem** | id, viagem\_id, status, observação, alterado\_por, data | Guarda a evolução da viagem: aceita, em trânsito, entregue etc. |
| **Conversa** | id, carga\_id, viagem\_id, empresa\_id, motorista\_id, criada\_em | Canal de comunicação contextualizado por carga/viagem. |
| **Mensagem** | id, conversa\_id, remetente\_id, texto, lida, enviada\_em | Mensagens entre empresa e motorista. |
| **Avaliacao** | id, viagem\_id, avaliador\_id, avaliado\_id, nota, comentário, status\_moderacao, criada\_em | Avaliação após o frete. |
| **FavoritoMotorista** | empresa\_id, motorista\_id, criado\_em | Motoristas favoritados por empresas. |
| **Notificacao** | id, usuario\_id, tipo, título, mensagem, lida, criada\_em | Alertas de novas cargas, candidaturas, mensagens e status. |
| **ChamadoSuporte** | id, usuario\_id, assunto, descrição, status, respondido\_por | Chamados abertos por usuários. |
| **VerificacaoUsuario** | id, usuario\_id, tipo, status, dados\_validados, verificado\_por | Validação de CPF, CNPJ, documentos e conta. |
| **Newsletter** | id, e-mail, status, data\_inscricao | Inscrição de visitantes anônimos na newsletter. |
| **TokenRedefinicaoSenha** | id, usuario\_id, token, expira\_em, usado | Recuperação de senha. |
| **Auditoria** | id, usuario\_id, ação, entidade, entidade\_id, data, ip | Registro de ações críticas para rastreabilidade. |

### Relacionamentos principais

| Relacionamento | Cardinalidade | Explicação |
| --- | --- | --- |
| **Usuario → Motorista** | 1 : 0..1 | Um usuário pode ter perfil de motorista. |
| **Usuario → Empresa** | 1 : 0..1 | Um usuário pode representar uma empresa/transportadora. |
| **Usuario → Administrador** | 1 : 0..1 | Um usuário pode ser administrador. |
| **Empresa → Carga** | 1 : N | Uma empresa publica várias cargas. |
| **Carga → Endereco** | N : 1 origem / N : 1 destino | Cada carga possui endereço de origem e destino. |
| **Motorista → Veiculo** | 1 : N | Um motorista pode cadastrar vários veículos. |
| **Veiculo → TipoVeiculo** | N : 1 | Cada veículo tem um tipo. |
| **Veiculo → TipoCarroceria** | N : 1 | Cada veículo tem uma carroceria. |
| **Carga → TipoVeiculo** | N : 1 | A carga exige um tipo de veículo. |
| **Carga → TipoCarroceria** | N : 1 | A carga exige uma carroceria. |
| **Motorista → RotaInteresse** | 1 : N | O motorista pode indicar várias rotas desejadas. |
| **Carga ↔ TagCarga** | N : N | Uma carga pode ter várias tags; uma tag pode aparecer em várias cargas. |
| **Carga → VisualizacaoCarga** | 1 : N | Cada visualização da carga é registrada. |
| **Motorista → VisualizacaoCarga** | 1 : N | Um motorista pode visualizar várias cargas. |
| **Carga → SolicitacaoCarga** | 1 : N | Vários motoristas podem se candidatar ou serem convidados para uma carga. |
| **Motorista → SolicitacaoCarga** | 1 : N | Um motorista pode se candidatar a várias cargas. |
| **SolicitacaoCarga → Viagem** | 1 : 0..1 | Uma solicitação aceita pode gerar uma viagem. |
| **Carga → Viagem** | 1 : 0..1 | Uma carga gera uma viagem quando contratada. |
| **Viagem → HistoricoStatusViagem** | 1 : N | A viagem mantém histórico de mudanças de status. |
| **Viagem → Avaliacao** | 1 : N | Uma viagem pode gerar avaliação da empresa e do motorista. |
| **Empresa ↔ Motorista** | N : N via FavoritoMotorista | Empresas podem favoritar motoristas. |
| **Conversa → Mensagem** | 1 : N | Uma conversa contém várias mensagens. |
| **Usuario → Notificacao** | 1 : N | Usuários recebem notificações. |
| **Usuario → ChamadoSuporte** | 1 : N | Usuários podem abrir chamados. |
| **PlanoAssinatura → AssinaturaEmpresa** | 1 : N | Um plano pode ser usado por várias empresas. |
| **Empresa → AssinaturaEmpresa** | 1 : N | Uma empresa pode ter histórico de assinaturas. |
| **AssinaturaEmpresa → Pagamento** | 1 : N | Uma assinatura pode gerar vários pagamentos. |
| **Usuario → Auditoria** | 1 : N | Ações relevantes do usuário são auditadas. |

O DER acima cobre os requisitos de cadastro, busca de fretes, filtro por origem/destino, compatibilidade por carroceria, histórico de viagens, ganhos, avaliações, publicação/edição/exclusão de cargas, métricas de visualização, administração de usuários, categorias e moderação. Esses pontos aparecem nos requisitos funcionais do documento, especialmente nos itens relacionados a motorista, empresa e administrador.

---

## 2\. Páginas web necessárias para o aplicativo completo

### Páginas públicas e autenticação

| Página | Descrição |
| --- | --- |
| **Página inicial / Landing page** | Apresenta o Giro Choffer, proposta de valor, vantagens para motoristas e empresas, chamada para cadastro, explicação resumida de como funciona e formulário de newsletter. |
| **Como funciona** | Explica o fluxo da plataforma: empresa publica carga, motorista encontra/candidata-se, empresa aceita, viagem é executada, avaliação é registrada. |
| **Planos e preços** | Mostra planos Free, Starter e Pro, limites de cargas, número de gestores, recursos disponíveis e botão para assinar. |
| **Cadastro — escolha de perfil** | Tela inicial de cadastro em que o visitante escolhe entre Motorista e Empresa/Transportadora. |
| **Cadastro de motorista** | Formulário com dados pessoais, CPF, CNH, telefone, e-mail, senha, dados do primeiro veículo e rotas de interesse. |
| **Cadastro de empresa/transportadora** | Formulário com CNPJ, razão social, nome fantasia, responsável, e-mail corporativo, telefone e endereço. |
| **Validação de CPF/CNPJ** | Etapa de confirmação dos dados informados. Para empresa, pode consultar CNPJ; para motorista, pode validar CPF/documentos de forma simples ou manual. |
| **Login** | Entrada na plataforma com e-mail e senha, redirecionando para o painel adequado ao perfil. |
| **Recuperar senha** | Solicita e-mail para envio de link de redefinição. |
| **Redefinir senha** | Permite criar nova senha a partir de token enviado por e-mail. |
| **Termos de uso e privacidade** | Explica regras da plataforma, tratamento de dados, LGPD, responsabilidades e condições de uso. |

O documento prevê autenticação, recuperação de senha, newsletter e validações de CPF/CNPJ no cadastro, além de integrações com Resend, Mercado Pago, ViaCEP e BrasilAPI.

---

### Área comum do usuário logado

| Página | Descrição |
| --- | --- |
| **Meu perfil** | Permite alterar dados cadastrais, telefone, e-mail, senha, endereço e preferências de notificação. |
| **Notificações** | Lista alertas de novas cargas, candidaturas, mensagens, mudança de status e avaliações. |
| **Mensagens / Chat** | Central de conversas entre motorista e empresa, sempre associadas a uma carga ou viagem. |
| **Abrir chamado** | Formulário para o usuário solicitar suporte ou relatar problema. |
| **Meus chamados** | Lista chamados abertos, status, respostas e histórico de atendimento. |
| **Solicitar verificação** | Permite enviar/solicitar análise de documentos ou validar dados da conta. |
| **Sair** | Encerra a sessão do usuário. |

---

### Área do motorista

| Página | Descrição |
| --- | --- |
| **Dashboard do motorista** | Mostra resumo de cargas compatíveis, viagens em andamento, ganhos do mês, avaliações e notificações recentes. |
| **Buscar cargas / Mural de fretes** | Lista cargas disponíveis com busca por palavra-chave, filtros por origem, destino, tipo de veículo, carroceria, valor e data. |
| **Detalhes da carga** | Exibe origem, destino, distância aproximada, valor, data de coleta, tipo de carroceria exigida, tags, descrição e botão para aceitar/candidatar-se. |
| **Minhas candidaturas / Solicitações** | Mostra cargas às quais o motorista se candidatou e convites recebidos de empresas, com status pendente, aceito ou rejeitado. |
| **Viagem em andamento** | Exibe dados da carga aceita, empresa contratante, rota, contatos, mensagens e botão para atualizar status da viagem. |
| **Atualizar status da viagem** | Tela ou modal para registrar etapas como “aceita”, “em coleta”, “em trânsito”, “entregue” e “concluída”. |
| **Histórico de viagens** | Lista viagens concluídas, canceladas ou recusadas, com filtros por período, empresa, cidade e status. |
| **Ganhos do mês** | Mostra somatório financeiro mensal, viagens pagas, pendentes e valor acumulado. |
| **Minhas avaliações** | Exibe média de notas, comentários recebidos e histórico de avaliações por empresa. |
| **Meus veículos** | Permite cadastrar, editar, remover ou inativar veículos, informando tipo, carroceria, placa e capacidade. |
| **Rotas de interesse** | Permite cadastrar trajetos desejados e rotas de retorno, usadas no match de cargas. |
| **Perfil público do motorista** | Página visualizada por empresas, com dados profissionais, veículos, avaliações, histórico resumido e status de verificação. |

Essas páginas refletem os casos de uso do motorista indicados no documento: buscar cargas, visualizar detalhes, enviar mensagem à empresa, aceitar carga, atualizar status, consultar histórico e avaliações.

---

### Área da empresa / transportadora

| Página | Descrição |
| --- | --- |
| **Dashboard da empresa** | Mostra resumo de cargas publicadas, cargas aguardando motorista, viagens em andamento, candidatos recentes, visualizações e métricas básicas. |
| **Publicar nova carga** | Formulário para cadastrar origem, destino, data, valor, tipo de veículo, tipo de carroceria, descrição, peso, volume e tags. |
| **Agendar publicação de carga** | Permite definir data e hora futura para a oferta aparecer no mural. |
| **Minhas cargas** | Lista cargas da empresa por status: rascunho, agendada, aguardando motorista, em negociação, aceita, em andamento, concluída ou cancelada. |
| **Detalhes da carga publicada** | Exibe todos os dados da carga, visualizações, candidatos, mensagens, status e ações disponíveis. |
| **Editar carga** | Permite alterar dados de uma carga ainda não aceita. |
| **Cancelar/excluir carga** | Permite cancelar ou excluir ofertas que ainda não foram aceitas. |
| **Candidatos da carga** | Lista motoristas interessados, seus veículos, avaliações, rotas e botões para aceitar ou rejeitar. |
| **Buscar motoristas** | Permite procurar motoristas por cidade, rota, tipo de veículo, carroceria, avaliação e disponibilidade. |
| **Solicitar motorista** | Permite enviar convite direto a um motorista para uma carga. |
| **Motoristas favoritos** | Lista motoristas salvos para contratações futuras. |
| **Perfil do motorista** | Exibe dados públicos do motorista, avaliações, veículos, rotas e histórico resumido. |
| **Avaliar motorista** | Página exibida após a conclusão de uma viagem para registrar nota e comentário. |
| **Relatórios e métricas** | Exibe visualizações por carga, tempo médio para aceite, cargas por período, viagens concluídas e desempenho. |
| **Gestores da empresa** | Permite cadastrar usuários gestores vinculados à mesma empresa, respeitando o limite do plano. |
| **Assinatura e pagamentos** | Mostra plano atual, faturas, pagamentos, upgrade/downgrade e status financeiro. |
| **Dados da empresa** | Permite editar informações institucionais, endereço, CNPJ, responsável e dados de contato. |

Essas páginas cobrem os requisitos de publicação de cargas, tags, agendamento, edição, exclusão, visualizações, tempo médio de aceite e ações da transportadora, como buscar, solicitar, aceitar/rejeitar e avaliar motoristas.

---

### Área do administrador

| Página | Descrição |
| --- | --- |
| **Dashboard administrativo** | Visão geral de usuários, empresas, motoristas, cargas, viagens, avaliações, chamados e indicadores da plataforma. |
| **Gerenciar usuários** | Lista motoristas, empresas e administradores, com filtros por status, tipo de perfil, verificação e data de cadastro. |
| **Detalhes do usuário** | Exibe dados cadastrais, documentos, veículos, cargas, viagens, avaliações, chamados e ações administrativas. |
| **Suspender ou banir usuário** | Tela ou modal para alterar status da conta, informando motivo e registrando auditoria. |
| **Verificações pendentes** | Lista usuários/documentos aguardando validação e permite aprovar, rejeitar ou solicitar correção. |
| **Gerenciar categorias logísticas** | CRUD de tipos de veículo, tipos de carroceria e tags globais. |
| **Moderar avaliações** | Lista avaliações e comentários, permitindo ocultar, editar ou excluir conteúdo inadequado. |
| **Gerenciar chamados** | Visualiza chamados abertos, responde usuários, altera status e acompanha histórico. |
| **Gerenciar planos e assinaturas** | Administra planos, empresas assinantes, pagamentos e eventuais bloqueios por inadimplência. |
| **Logs e auditoria** | Exibe ações críticas: login, alteração de carga, aceite de frete, suspensão, moderação e alterações administrativas. |
| **Configurações do sistema** | Ajustes gerais, mensagens automáticas, limites, parâmetros de notificação e integrações. |

O documento prevê que o administrador gerencie contas, categorias logísticas, avaliações, verificações, chamados e dashboard geral.

---

## MVP mais enxuto do Giro Choffer

### 1\. Fluxo essencial do MVP

1. Usuário cria conta como **Empresa** ou **Motorista**.

2. Empresa cadastra uma **carga**.

3. Motorista visualiza a lista de **cargas disponíveis**.

4. Motorista abre os detalhes da carga e clica em **Tenho interesse**.

5. Empresa vê os interessados e escolhe um motorista.

6. Carga muda para **Contratada**.

7. Empresa ou motorista marca a carga como **Concluída**.

Esse fluxo já permite usar o sistema de ponta a ponta.

---

### 2\. Páginas do MVP enxuto

#### Páginas públicas

| Página | Descrição |
| --- | --- |
| **Página inicial** | Explica rapidamente o que é o Giro Choffer, com botões “Sou motorista” e “Sou empresa”. |
| **Cadastro/Login** | Uma única página para entrar ou criar conta. No cadastro, o usuário escolhe o tipo: Motorista ou Empresa. |

---

#### Área da empresa

| Página | Descrição |
| --- | --- |
| **Painel da empresa** | Mostra as cargas publicadas pela empresa, separadas por status: Disponível, Com interessados, Contratada e Concluída. |
| **Nova carga** | Formulário simples para cadastrar origem, destino, tipo de veículo/carroceria, data, descrição e valor do frete. |
| **Detalhes da carga** | Mostra os dados da carga e a lista de motoristas interessados. A empresa pode escolher um motorista. |

---

#### Área do motorista

| Página | Descrição |
| --- | --- |
| **Painel do motorista / Cargas disponíveis** | Lista cargas disponíveis com filtros simples por origem, destino e tipo de carroceria. |
| **Detalhes da carga** | Mostra informações completas da carga e botão **Tenho interesse**. |
| **Minhas cargas** | Lista cargas nas quais o motorista demonstrou interesse, cargas aceitas e cargas concluídas. |

---

#### Página opcional, mas recomendada

| Página | Descrição |
| --- | --- |
| **Meu perfil** | Permite editar dados básicos. Para motorista: nome, telefone e dados do veículo. Para empresa: nome, CNPJ e telefone. |

---

### 3\. Features que ficam no MVP enxuto

| Feature | Entra no MVP? | Observação |
| --- | --- | --- |
| Cadastro de usuário | Sim | Apenas e-mail, senha, nome e tipo de perfil. |
| Perfil Motorista/Empresa | Sim | Bem simples. |
| Cadastro de veículo do motorista | Sim | Apenas tipo de veículo, carroceria e capacidade. |
| Publicação de carga | Sim | Essencial. |
| Lista de cargas disponíveis | Sim | Essencial. |
| Filtro por origem/destino/carroceria | Sim | Match simples, sem algoritmo avançado. |
| Motorista demonstrar interesse | Sim | Substitui chat, candidatura complexa e negociação interna. |
| Empresa escolher motorista | Sim | Fecha o ciclo principal. |
| Status da carga | Sim | Disponível, Contratada, Concluída e Cancelada. |
| Histórico simples | Sim | Pode ser a própria página “Minhas cargas”. |
| Avaliação | Não | Pode ficar para versão 2. |
| Chat | Não | No MVP, o sistema pode liberar telefone/WhatsApp após interesse ou aceite. |
| Pagamento online | Não | Fica fora. |
| Assinatura SaaS | Não | Fica fora. |
| Admin completo | Não | Pode ser feito manualmente no banco ou com uma tela mínima depois. |
| Notificações | Não | Pode começar sem notificação automática; o usuário consulta o painel. |
| Agendamento de carga | Não | Não é essencial. |
| Métricas de visualização | Não | Fica para depois. |
| Favoritar motorista | Não | Fica para depois. |
| Verificação documental avançada | Não | Pode ser manual ou inexistente no MVP. |

---

### 4\. Entidades mínimas do banco para esse MVP

O DER mínimo ficaria assim:

| Entidade | Função |
| --- | --- |
| **Usuario** | Guarda login, senha, nome, e-mail, telefone e tipo de perfil. |
| **Empresa** | Guarda dados específicos da empresa, como CNPJ e nome fantasia. |
| **Motorista** | Guarda dados específicos do motorista. |
| **Veiculo** | Guarda o veículo do motorista. |
| **TipoCarroceria** | Lista fixa de carrocerias possíveis. |
| **Carga** | Carga publicada pela empresa. |
| **InteresseCarga** | Registra que um motorista tem interesse em uma carga. |

#### Relacionamentos mínimos

| Relacionamento | Cardinalidade |
| --- | --- |
| Usuario → Empresa | 1 : 0..1 |
| Usuario → Motorista | 1 : 0..1 |
| Motorista → Veiculo | 1 : N |
| Empresa → Carga | 1 : N |
| Carga → InteresseCarga | 1 : N |
| Motorista → InteresseCarga | 1 : N |
| Carga → Motorista escolhido | N : 0..1 |

---

### 5\. Status mínimos da carga

Para simplificar bastante, a carga pode ter apenas estes status:

| Status | Significado |
| --- | --- |
| **Disponível** | A carga está aberta para motoristas interessados. |
| **Contratada** | A empresa escolheu um motorista. |
| **Concluída** | O frete foi realizado. |
| **Cancelada** | A empresa cancelou a carga. |

---

### 6\. Recorte final recomendado

Eu implementaria apenas estas **7 páginas**:

1. **Página inicial**

2. **Cadastro/Login**

3. **Painel da empresa**

4. **Nova carga**

5. **Detalhes da carga — empresa**

6. **Painel do motorista / Cargas disponíveis**

7. **Detalhes da carga — motorista**

E, se houver tempo, adicionaria:

8. **Meu perfil**

9. **Minhas cargas do motorista**

Esse MVP fica pequeno, viável para desenvolvimento escolar e ainda demonstra claramente o produto funcionando. Ele não tenta ser uma plataforma logística completa; ele valida o ponto principal: **existe uma forma simples de publicar uma carga e encontrar um motorista interessado**.
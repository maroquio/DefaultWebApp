# CAVI — Lista de páginas HTML necessárias

Este documento reúne as páginas HTML recomendadas para implementar a aplicação **CAVI — Compra, aluguel e venda de imóveis**, com base nos requisitos funcionais, perfis de usuário e diferenciais descritos na documentação do projeto.

A aplicação é uma plataforma SaaS para corretores autônomos e pequenas imobiliárias divulgarem imóveis em site próprio, com catálogo público, busca, favoritos, solicitações de anúncio, área do corretor, área do cliente, área administrativa, planos de assinatura e integração com APIs externas.

---

## 1. Páginas públicas

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Página inicial da plataforma | `public/home.html` | Deve apresentar o CAVI, explicar a proposta da plataforma, destacar os benefícios para corretores e pequenas imobiliárias, exibir chamada para assinatura de planos, chamada para busca de imóveis, lista ou cards de corretores cadastrados e informações de qualidade/confiabilidade da aplicação. Atende ao RF1. |
| Lista pública de corretores | `public/corretores.html` | Deve listar corretores e imobiliárias cadastrados, com cards contendo foto ou logotipo, nome, cidade/região, quantidade de imóveis e botão para acessar o site/catálogo do corretor. Pode existir como página separada ou ser incorporada à home. |
| Página pública do corretor/imobiliária | `public/site_corretor.html` | Deve funcionar como o site próprio do corretor ou imobiliária, contendo logotipo, dados de contato, CRECI, descrição profissional, banner, imóveis em destaque e link para o catálogo completo. Relaciona-se ao diferencial de site próprio personalizado. |
| Catálogo de imóveis do corretor | `public/catalogo_imoveis.html` | Deve exibir os imóveis cadastrados por determinado corretor, em cards com imagem, título, tipo, finalidade, bairro/cidade, preço, botão de detalhes, botão de WhatsApp e botão de favoritar quando o cliente estiver autenticado. Atende ao RF2. |
| Busca de imóveis | `public/busca_imoveis.html` | Deve conter formulário de busca e filtros por localização, tipo de imóvel, finalidade, faixa de preço e, se desejado, número de quartos, banheiros e vagas. Deve exibir os resultados em cards. Atende ao RF3 e ao diferencial de filtros avançados. |
| Detalhes do imóvel | `public/detalhe_imovel.html` | Deve apresentar galeria de fotos, título, preço, finalidade, endereço aproximado, descrição, características, dados do corretor, botão de WhatsApp, formulário de interesse/contato e botão de favoritar. Atende ao RF4 e RF9. |
| Página offline/PWA | `public/offline.html` | Deve apresentar uma mensagem amigável quando o usuário estiver sem internet. Pode listar imóveis já visitados e armazenados em cache. Relaciona-se ao diferencial de PWA offline-first. |

---

## 2. Páginas de autenticação, cadastro e pagamento

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Login | `auth/login.html` | Deve conter formulário com e-mail e senha, botão de entrada, link para cadastro como cliente, link para recuperação de senha e link para assinatura como corretor. Atende ao RF6. |
| Cadastro de cliente | `auth/cadastro_cliente.html` | Deve conter formulário com nome completo, CPF, data de nascimento, telefone, e-mail e senha. Atende ao RF5. |
| Recuperação de senha | `auth/recuperar_senha.html` | Deve permitir que o usuário informe o e-mail para receber instruções de recuperação de senha por e-mail ou SMS. Atende ao RF7. |
| Redefinir senha | `auth/redefinir_senha.html` | Deve permitir cadastrar uma nova senha e confirmar a nova senha, geralmente acessada por link/token enviado ao usuário. Complementa o RF7. |
| Página de planos | `public/planos.html` | Deve comparar os planos Junior, Starter e Pro, exibindo mensalidade, limite de autores/usuários, armazenamento, domínio próprio, limite de imóveis e botão para assinar. |
| Assinatura/cadastro de corretor | `auth/cadastro_corretor.html` | Deve conter formulário com nome completo, CPF, data de nascimento, CRECI, telefone, e-mail, senha e escolha do plano. Atende ao RF8. |
| Checkout de pagamento | `pagamento/checkout.html` | Deve apresentar resumo do plano escolhido, valor da assinatura, dados do assinante, forma de pagamento e integração com gateway de pagamento. |
| Resultado do pagamento | `pagamento/resultado.html` | Deve informar se o pagamento foi aprovado, recusado ou está pendente, além de orientar o corretor sobre o próximo passo para acessar a plataforma. |

---

## 3. Páginas comuns para usuários autenticados

Estas páginas podem ser usadas por cliente, corretor e administrador, com variações conforme o perfil do usuário.

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Painel inicial autenticado | `usuario/dashboard.html` | Deve exibir boas-vindas e atalhos diferentes conforme o perfil: cliente, corretor ou administrador. Pode redirecionar automaticamente para o painel específico do perfil. |
| Meu perfil | `usuario/perfil.html` | Deve exibir e permitir editar dados cadastrais do usuário, como nome, CPF, data de nascimento, telefone e e-mail. Para corretores, também deve exibir dados profissionais, como CRECI e informações públicas do site. Atende ao RF14. |
| Alterar senha | `usuario/alterar_senha.html` | Deve conter campos para senha atual, nova senha e confirmação da nova senha. Atende ao RF13. |

---

## 4. Área do cliente

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Favoritos | `cliente/favoritos.html` | Deve listar os imóveis favoritados pelo cliente, com imagem, título, preço, corretor responsável, botão para remover dos favoritos e botão para ver detalhes. Atende ao RF10. |
| Solicitar anúncio de imóvel | `cliente/solicitar_anuncio.html` | Deve permitir que o cliente solicite a um corretor o anúncio de um imóvel para venda ou aluguel. Deve conter dados do imóvel, finalidade, endereço, descrição, preço sugerido, fotos e escolha do corretor. Atende ao RF11. |
| Minhas solicitações de anúncio | `cliente/solicitacoes.html` | Deve listar as solicitações feitas pelo cliente, com status como pendente, aprovada, reprovada ou aguardando correção. |
| Detalhes/correção da solicitação | `cliente/detalhe_solicitacao.html` | Deve mostrar os dados enviados, o parecer do corretor em caso de reprovação e permitir que o cliente corrija uma solicitação reprovada. Atende ao RF12. |

---

## 5. Área do corretor

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Dashboard do corretor | `corretor/dashboard.html` | Deve mostrar resumo com total de imóveis, imóveis visíveis/ocultos, solicitações pendentes, visitas recentes, plano contratado e atalhos para cadastrar imóvel e ver solicitações. |
| Listagem de imóveis cadastrados | `corretor/imoveis.html` | Deve exibir tabela ou cards com os imóveis cadastrados pelo corretor, status visível/oculto, preço, finalidade, data de cadastro e ações de editar, excluir, ocultar ou mostrar. Atende aos RF15, RF17 e RF19. |
| Cadastro de imóvel | `corretor/cadastrar_imovel.html` | Deve conter formulário completo do imóvel, com título, tipo, finalidade, preço, endereço, CEP com busca automática, descrição, características, fotos, status de publicação e opção de destaque. Atende ao RF18. |
| Edição de imóvel | `corretor/editar_imovel.html` | Deve reaproveitar o formulário de cadastro, já preenchido com os dados atuais do imóvel, permitindo alterar informações e fotos. Atende ao RF16. |
| Confirmação de exclusão de imóvel | `corretor/excluir_imovel.html` | Deve apresentar dados básicos do imóvel e solicitar confirmação antes da exclusão. Pode ser implementada como página ou modal. Atende ao RF17. |
| Solicitações de anúncio recebidas | `corretor/solicitacoes.html` | Deve listar solicitações feitas por clientes, com status, nome do cliente, tipo de imóvel, finalidade e botão para analisar. Atende ao RF20. |
| Detalhes da solicitação de anúncio | `corretor/detalhe_solicitacao.html` | Deve apresentar dados completos enviados pelo cliente, fotos, contato do cliente, botões para aprovar ou reprovar e campo para justificativa em caso de reprovação. Atende aos RF21 e RF22. |
| Estatísticas dos imóveis | `corretor/estatisticas.html` | Deve apresentar gráficos ou cards com acessos por imóvel, imóveis mais visualizados, contatos recebidos, favoritos e desempenho geral. Atende ao RF23. |
| Personalização do site | `corretor/personalizar_site.html` | Deve permitir configurar o site próprio do corretor: logotipo, cores, tema, texto de apresentação, WhatsApp, redes sociais, domínio próprio e imóveis em destaque. |
| Plano e assinatura | `corretor/plano.html` | Deve exibir plano atual, limite de imóveis, armazenamento usado, status do pagamento e opções para trocar de plano ou atualizar forma de pagamento. |

---

## 6. Área do administrador

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Dashboard administrativo | `admin/dashboard.html` | Deve apresentar indicadores gerais da plataforma, como número de corretores, clientes, imóveis, assinaturas ativas, pagamentos pendentes e acessos. Atende ao RF26. |
| Listagem de corretores | `admin/corretores.html` | Deve exibir tabela com corretores cadastrados, e-mail, CRECI, plano, status da assinatura, quantidade de imóveis e botão para detalhes. Atende ao RF24. |
| Detalhes do corretor | `admin/detalhe_corretor.html` | Deve mostrar dados completos do corretor, plano contratado, situação de pagamento, imóveis cadastrados, estatísticas básicas e histórico de assinatura. Atende ao RF25 e RF27. |
| Estatísticas da plataforma | `admin/estatisticas.html` | Deve apresentar relatórios gerais de uso da plataforma: acessos, imóveis cadastrados, novos clientes, novos corretores, conversões e crescimento. Atende ao RF26. |
| Pagamentos/assinaturas | `admin/pagamentos.html` | Deve listar pagamentos por corretor, status, vencimento, plano, valor, forma de pagamento e filtros por situação. Atende ao RF27. |

---

## 7. Páginas auxiliares recomendadas

| Página HTML | Nome sugerido do template | Descrição |
|---|---|---|
| Erro 403 — Acesso negado | `errors/403.html` | Deve informar que o usuário não tem permissão para acessar a página solicitada. |
| Erro 404 — Página não encontrada | `errors/404.html` | Deve informar que a página não existe e oferecer botão para voltar à página inicial ou ao catálogo de imóveis. |
| Erro 500 — Erro interno | `errors/500.html` | Deve informar que ocorreu erro interno, sem expor detalhes técnicos ao usuário final. |
| Confirmação genérica | `shared/confirmacao.html` | Pode ser usada para mensagens como cadastro realizado, e-mail enviado, solicitação enviada ou operação concluída. |

---

## 8. Templates parciais reutilizáveis

Estes arquivos não são páginas completas, mas ajudam a evitar repetição de código nos templates Jinja.

| Template parcial | Finalidade |
|---|---|
| `base.html` | Estrutura base com HTML, head, CSS, scripts, blocos Jinja e layout geral. |
| `_navbar.html` | Menu superior da aplicação, com variações para visitante, cliente, corretor e administrador. |
| `_footer.html` | Rodapé com informações institucionais, links úteis e redes sociais. |
| `_mensagens.html` | Exibição de mensagens de sucesso, erro, alerta ou informação. |
| `_card_imovel.html` | Card reutilizável para exibir imóveis em catálogos, favoritos e resultados de busca. |
| `_form_imovel.html` | Formulário reutilizável para cadastro e edição de imóveis. |
| `_paginacao.html` | Componente de paginação para listagens longas. |
| `_filtros_busca.html` | Formulário reutilizável com filtros de busca de imóveis. |
| `_sidebar_corretor.html` | Menu lateral da área do corretor. |
| `_sidebar_admin.html` | Menu lateral da área administrativa. |
| `_modal_confirmacao.html` | Modal genérico para confirmar exclusão, ocultação, aprovação ou reprovação. |

---

## 9. Lista mínima priorizada para a primeira versão funcional

Para iniciar o desenvolvimento de forma pragmática, recomenda-se priorizar as seguintes páginas:

1. `public/home.html`
2. `public/site_corretor.html`
3. `public/catalogo_imoveis.html`
4. `public/detalhe_imovel.html`
5. `auth/login.html`
6. `auth/cadastro_cliente.html`
7. `auth/recuperar_senha.html`
8. `auth/cadastro_corretor.html`
9. `public/planos.html`
10. `pagamento/checkout.html`
11. `usuario/perfil.html`
12. `usuario/alterar_senha.html`
13. `cliente/favoritos.html`
14. `cliente/solicitacoes.html`
15. `cliente/solicitar_anuncio.html`
16. `corretor/dashboard.html`
17. `corretor/imoveis.html`
18. `corretor/cadastrar_imovel.html`
19. `corretor/editar_imovel.html`
20. `corretor/solicitacoes.html`
21. `corretor/detalhe_solicitacao.html`
22. `corretor/estatisticas.html`
23. `admin/dashboard.html`
24. `admin/corretores.html`
25. `admin/detalhe_corretor.html`
26. `admin/pagamentos.html`
27. `errors/403.html`
28. `errors/404.html`
29. `errors/500.html`

---

## 10. Observações importantes

- A aplicação deve considerar os perfis: **usuário anônimo**, **cliente**, **corretor**, **administrador** e **usuário autenticado**.
- O documento menciona, em determinado trecho final, os perfis “Autores, Leitores e Administradores”, mas isso parece ser uma inconsistência textual. Para implementação, devem ser considerados os perfis descritos nos requisitos funcionais e diagramas de casos de uso: cliente, corretor, administrador e anônimo.
- Recomenda-se organizar os templates por pastas, separando claramente páginas públicas, autenticação, área do cliente, área do corretor, área administrativa, páginas de erro e componentes compartilhados.
- Como o projeto usa FastAPI com Jinja, os nomes sugeridos acima já seguem uma estrutura compatível com aplicações server-side rendered.

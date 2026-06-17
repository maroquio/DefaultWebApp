# Relação Mestre-Detalhe (1:N)

Padrão para uma entidade **pai** que possui muitos **filhos**, espelhando o que o projeto já faz
com `Chamado` (pai) → `ChamadoInteracao` (filho). Use quando o usuário descrever algo como
"um pedido tem vários itens", "uma enquete tem várias opções", "um chamado tem várias respostas".

> Leia os arquivos reais antes de gerar: `model/chamado_interacao_model.py`,
> `sql/chamado_interacao_sql.py`, `repo/chamado_interacao_repo.py`,
> `routes/admin_chamados_routes.py` (rota `/{id}/responder`) e
> `templates/admin/chamados/responder.html`. Eles são o gabarito canônico.

## Estrutura

- **Pai** (`pedido`): CRUD completo normal (gere pelo fluxo padrão do SKILL.md).
- **Filho** (`pedido_item`): tem `pedido_id INTEGER NOT NULL` (FK ao pai) +, opcionalmente,
  FKs de referência próprias (ex.: `produto_id`). Normalmente **não** tem telas de listar/editar
  próprias — é gerenciado **dentro da tela de detalhe do pai**.

## 1. Model do filho — `model/pedido_item_model.py`

```python
@dataclass
class PedidoItem:
    id: int
    pedido_id: int                 # FK ao pai
    produto_id: int                # FK de referência (opcional)
    quantidade: int
    preco_unitario: float
    # JOIN (exibição)
    produto_nome: Optional[str] = None
```

## 2. SQL do filho — `sql/pedido_item_sql.py`

```python
CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS pedido_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL DEFAULT 1,
    preco_unitario REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (pedido_id) REFERENCES pedido(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produto(id) ON DELETE RESTRICT
)
"""

# Filtra os filhos de um pai específico — query central do padrão
OBTER_POR_PEDIDO = """
SELECT i.*, p.nome as produto_nome
FROM pedido_item i
INNER JOIN produto p ON i.produto_id = p.id
WHERE i.pedido_id = ?
ORDER BY i.id ASC
"""

INSERIR = """
INSERT INTO pedido_item (pedido_id, produto_id, quantidade, preco_unitario)
VALUES (?, ?, ?, ?)
"""

EXCLUIR = "DELETE FROM pedido_item WHERE id = ?"
CONTAR_POR_PEDIDO = "SELECT COUNT(*) as total FROM pedido_item WHERE pedido_id = ?"
```

`ON DELETE CASCADE` no `pedido_id`: apagar o pai apaga automaticamente os filhos.

## 3. Repository do filho — `repo/pedido_item_repo.py`

Funções principais: `criar_tabela`, `inserir`, `obter_por_pedido(pedido_id)`, `excluir`,
e helpers como `contar_por_pedido(pedido_id)`.

```python
def obter_por_pedido(pedido_id: int) -> list[PedidoItem]:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_PEDIDO, (pedido_id,))
        return [_row_to_item(r) for r in cursor.fetchall()]
```

### Imports circulares
Se o repo do pai precisar do repo do filho **e** vice-versa (ex.: pai calcula total agregando
filhos; filho lê algo do pai), use **lazy import dentro da função** e documente no topo:

```python
"""
NOTA SOBRE IMPORTS CIRCULARES:
obter_por_id() do pai usa lazy import de pedido_item_repo para agregar o total.
Lazy import (import dentro da função) evita import circular — padrão aceito em Python.
"""

def obter_por_id(id: int) -> Optional[Pedido]:
    from repo import pedido_item_repo          # lazy import
    ...
    pedido.total_itens = pedido_item_repo.contar_por_pedido(id)
    return pedido
```

## 4. Rotas — detalhe do pai + adicionar/remover filho

Em vez de telas próprias do filho, adicione no router do **pai** uma rota de **detalhe** que carrega
os filhos, e rotas POST para adicionar/remover filho:

```python
@router.get("/{id}/itens")                       # tela de detalhe do pedido + seus itens
@requer_autenticacao([Perfil.ADMIN.value])
async def get_itens(request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None):
    assert usuario_logado is not None
    pedido = obter_ou_404(pedido_repo.obter_por_id(id), request, "Pedido não encontrado", "/admin/pedidos/listar")
    if isinstance(pedido, RedirectResponse):
        return pedido
    itens = pedido_item_repo.obter_por_pedido(id)
    return templates.TemplateResponse(
        "admin/pedido/itens.html",
        {"request": request, "pedido": pedido, "itens": itens,
         "produtos": produto_repo.obter_todos(), "usuario_logado": usuario_logado},
    )


@router.post("/{id}/itens/adicionar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_adicionar_item(
    request: Request, id: int,
    produto_id: int = Form(...), quantidade: int = Form(...), preco_unitario: str = Form(...),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    assert usuario_logado is not None
    # ...rate limit + DTO de validação do item...
    novo = PedidoItem(id=0, pedido_id=id, produto_id=produto_id,
                      quantidade=quantidade, preco_unitario=float(_normalizar_decimal(preco_unitario)))
    pedido_item_repo.inserir(novo)
    informar_sucesso(request, "Item adicionado!")
    return RedirectResponse(f"/admin/pedidos/{id}/itens", status_code=http_status.HTTP_303_SEE_OTHER)


@router.post("/{id}/itens/{item_id}/excluir")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir_item(request: Request, id: int, item_id: int, usuario_logado: Optional[UsuarioLogado] = None):
    assert usuario_logado is not None
    pedido_item_repo.excluir(item_id)
    informar_sucesso(request, "Item removido!")
    return RedirectResponse(f"/admin/pedidos/{id}/itens", status_code=http_status.HTTP_303_SEE_OTHER)
```

O `pedido_id` do filho vem **da URL** (`{id}`), nunca de campo do formulário — análogo a como
`usuario_id` vem da sessão. O DTO do item valida apenas `produto_id`, `quantidade`, `preco_unitario`.

## 5. Template de detalhe — `templates/admin/pedido/itens.html`

- Cabeçalho com dados do pai (`pedido`).
- Tabela com os filhos (`itens`), cada linha com botão de excluir (POST para `.../{item_id}/excluir`
  via `modal_confirmacao`).
- Formulário inline (no fim da página) para adicionar item: `<select>` de `produtos`,
  campos de quantidade e preço. `{{ csrf_input(request) }}` no form.
- Link "Adicionar Itens" na listagem/edição do pai apontando para `/admin/pedidos/{{ pedido.id }}/itens`.

## 6. Registro
- main.py TABELAS: `pedido` antes de `pedido_item` (FK). E `produto` antes de `pedido_item` se houver FK a produto.
- Índices: `idx_pedido_item_pedido_id` e `idx_pedido_item_produto_id` em `sql/indices_sql.py`.
- ROUTERS: as rotas de item ficam no router do pai (mesmo arquivo `admin_pedido_routes.py`) — nada novo a registrar além do router do pai.

## Resumo das diferenças vs CRUD simples
| Aspecto | CRUD simples | Mestre-detalhe (filho) |
|--------|--------------|------------------------|
| Telas | listar/cadastrar/editar | gerenciado na tela de detalhe do pai |
| FK do pai | — | `{pai}_id` vem da URL, não do form/DTO |
| Query central | `obter_todos` | `obter_por_{pai}({pai}_id)` |
| Exclusão em cascata | — | `ON DELETE CASCADE` no `{pai}_id` |
| Import circular | improvável | use lazy import se pai↔filho se referenciam |

# Usando o Claude Code de graça com modelos da NVIDIA (FCC)

Este tutorial mostra, passo a passo, como usar o **Claude Code** com modelos LLM
gratuitos provisionados pela **NVIDIA NIM**, por meio do projeto
**free-claude-code (FCC)**. Há instruções separadas para **Windows 11**,
**macOS** e **Ubuntu**, além de uma seção de solução de problemas.

> ⚠️ **Aviso:** este não é um recurso oficial da Anthropic. Você estará usando o
> Claude Code conectado a modelos *open-source* (Qwen, GLM, Kimi, MiniMax,
> Nemotron etc.), e **não** ao Claude real. Funciona bem na prática, mas com
> algumas limitações (veja a seção [Limitações](#limitações)).

---

## Sumário

- [Como funciona](#como-funciona)
- [Por que usar a NVIDIA NIM](#por-que-usar-a-nvidia-nim)
- [Pré-requisitos](#pré-requisitos)
- [Passo comum: obter a API key da NVIDIA NIM](#passo-comum-obter-a-api-key-da-nvidia-nim)
- [Windows 11](#windows-11)
- [macOS](#macos)
- [Ubuntu](#ubuntu)
- [Configurar o modelo no Admin UI](#configurar-o-modelo-no-admin-ui)
- [Modelos recomendados](#modelos-recomendados)
- [Usando no VS Code (opcional)](#usando-no-vs-code-opcional)
- [Solução de problemas](#solução-de-problemas)
- [Limitações](#limitações)

---

## Como funciona

O Claude Code "fala" o formato da API da Anthropic, mas a NVIDIA NIM usa o
formato da API da OpenAI. A solução é colocar um **proxy local** no meio, que faz
a tradução entre os dois formatos. O projeto **free-claude-code (FCC)** já faz
essa normalização automaticamente (tool calls, blocos de *thinking*, *streaming*),
no formato que o Claude Code espera.

```
Claude Code CLI  →  Proxy FCC (local)  →  NVIDIA NIM API  →  Modelo (Qwen, GLM, Kimi, Nemotron...)
```

O FCC fornece dois comandos principais:

| Comando      | Função                                                              |
|--------------|--------------------------------------------------------------------|
| `fcc-server` | Inicia o proxy local (Admin UI em `http://127.0.0.1:8082/admin`).  |
| `fcc-claude` | Inicia o Claude Code já apontando para o proxy local.              |

---

## Por que usar a NVIDIA NIM

- Modelos fortes para código disponíveis **gratuitamente**, **sem cartão de crédito**.
- O *tier* gratuito **não expira** — só tem limite de taxa (cerca de **40 requisições/minuto**).
- Bons modelos para programação: **Qwen**, **GLM**, **Kimi K2.5**, **MiniMax M2.5** e **Nemotron**.

---

## Pré-requisitos

O script de instalação do FCC tenta instalar tudo automaticamente. Em geral você
precisa de:

- **Node.js 18+**
- **Python 3.14+**
- **uv** (gerenciador de pacotes Python)
- **Claude Code CLI**

O script `install` cuida de instalar o Claude Code CLI, o Python, o `uv` e o
próprio `free-claude-code` de uma só vez.

---

## Passo comum: obter a API key da NVIDIA NIM

Este passo é igual em todos os sistemas operacionais. Faça antes ou depois da
instalação — você vai precisar da chave ao configurar o Admin UI.

1. Acesse **`build.nvidia.com/settings/api-keys`**.
2. Crie uma conta (gratuito, sem cartão de crédito).
3. Gere uma **API key** — ela começa com `nvapi-...`.
4. **Copie e guarde a chave** — ela só aparece uma vez.

---

## Windows 11

### Passo 1 — Instalar tudo

Abra o **PowerShell como Administrador** e execute:

```powershell
irm "https://github.com/Alishahryar1/free-claude-code/blob/main/scripts/install.ps1?raw=1" | iex
```

Isso instala Node.js, Python 3.14, `uv`, o Claude Code CLI e o `free-claude-code`
automaticamente.

### Passo 2 — Obter a API key da NVIDIA NIM

Veja a seção [Passo comum: obter a API key da NVIDIA NIM](#passo-comum-obter-a-api-key-da-nvidia-nim).

### Passo 3 — Iniciar o proxy

No PowerShell:

```powershell
fcc-server
```

Deve aparecer algo como:

```
INFO:     Admin UI: http://127.0.0.1:8082/admin (local-only)
```

### Passo 4 — Configurar o modelo no Admin UI

Siga a seção [Configurar o modelo no Admin UI](#configurar-o-modelo-no-admin-ui).

### Passo 5 — Rodar o Claude Code

Deixe o `fcc-server` rodando no primeiro terminal. Abra um **segundo PowerShell** e execute:

```powershell
fcc-claude
```

Pronto! O Claude Code funcionará apontando para o proxy local.

### Dica — atalho para abrir tudo de uma vez

Para não precisar abrir dois terminais toda vez, crie um arquivo `claude.bat` na
pasta do seu projeto:

```bat
@echo off
start powershell -Command "fcc-server"
timeout /t 3
fcc-claude
```

Dê um duplo clique no `claude.bat` (ou execute-o no terminal) para iniciar o
servidor e o Claude Code juntos.

---

## macOS

### Passo 1 — Instalar tudo

No Terminal:

```bash
curl -fsSL "https://github.com/Alishahryar1/free-claude-code/blob/main/scripts/install.sh?raw=1" | sh
```

Isso instala automaticamente: Node.js, Python 3.14, `uv`, o Claude Code CLI e o
`free-claude-code`.

Depois, recarregue o PATH (use `~/.zshrc` no macOS moderno, que usa Zsh por padrão):

```bash
source ~/.zshrc
```

### Passo 2 — Obter a API key da NVIDIA NIM

Veja a seção [Passo comum: obter a API key da NVIDIA NIM](#passo-comum-obter-a-api-key-da-nvidia-nim).

### Passo 3 — Iniciar o proxy

```bash
fcc-server
```

Deve aparecer:

```
INFO:     Admin UI: http://127.0.0.1:8082/admin (local-only)
```

### Passo 4 — Configurar o modelo no Admin UI

Siga a seção [Configurar o modelo no Admin UI](#configurar-o-modelo-no-admin-ui).

### Passo 5 — Rodar o Claude Code

Deixe o `fcc-server` rodando no primeiro terminal. Abra um **segundo terminal** e execute:

```bash
fcc-claude
```

### Dica — rodar o servidor em segundo plano

Para não precisar de dois terminais abertos, use o `tmux`:

```bash
# Instala o tmux (caso não tenha; requer Homebrew)
brew install tmux

# Cria uma sessão em segundo plano para o servidor
tmux new-session -d -s fcc 'fcc-server'

# Roda o Claude Code normalmente
fcc-claude
```

Para parar o servidor depois:

```bash
tmux kill-session -t fcc
```

---

## Ubuntu

### Passo 1 — Instalar tudo

No Terminal:

```bash
curl -fsSL "https://github.com/Alishahryar1/free-claude-code/blob/main/scripts/install.sh?raw=1" | sh
```

Isso instala automaticamente: Node.js, Python 3.14, `uv`, o Claude Code CLI e o
`free-claude-code`.

Depois, recarregue o PATH:

```bash
source ~/.bashrc
```

### Passo 2 — Obter a API key da NVIDIA NIM

Veja a seção [Passo comum: obter a API key da NVIDIA NIM](#passo-comum-obter-a-api-key-da-nvidia-nim).

### Passo 3 — Iniciar o proxy

```bash
fcc-server
```

Deve aparecer:

```
INFO:     Admin UI: http://127.0.0.1:8082/admin (local-only)
```

### Passo 4 — Configurar o modelo no Admin UI

Siga a seção [Configurar o modelo no Admin UI](#configurar-o-modelo-no-admin-ui).

### Passo 5 — Rodar o Claude Code

Deixe o `fcc-server` rodando no primeiro terminal. Abra um **segundo terminal** e execute:

```bash
fcc-claude
```

### Dica — rodar o servidor em segundo plano (com root)

```bash
# Instala o tmux se não tiver
sudo apt install tmux -y

# Cria uma sessão em segundo plano para o servidor
tmux new-session -d -s fcc 'fcc-server'

# Roda o Claude Code normalmente
fcc-claude
```

Para parar o servidor depois:

```bash
tmux kill-session -t fcc
```

### Sem permissão de root (ambientes restritos / laboratório)

Boa notícia: **o instalador não precisa de root** — ele coloca tudo na sua pasta
*home* (`~/.local/`, `~/.uv/`, `~/.npm/`). Porém, em ambientes onde o Node.js foi
instalado pelo administrador, o `npm install -g` pode falhar com erro de
permissão (`EACCES`, tentando escrever em `/usr/local/lib`). Nesse caso, instale
o Node.js na sua *home* usando o **nvm**:

**1. Instalar o nvm:**

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
```

**2. Instalar o Node.js via nvm:**

```bash
nvm install --lts
nvm use --lts
```

Verifique se o Node e o npm agora estão na sua *home*:

```bash
which node
which npm
# Deve apontar para algo como /home/seu_usuario/.nvm/versions/node/...
```

**3. Instalar o Claude Code (agora sem precisar de root):**

```bash
npm install -g @anthropic-ai/claude-code
```

**4. Rodar o instalador do FCC novamente:**

```bash
curl -fsSL "https://github.com/Alishahryar1/free-claude-code/blob/main/scripts/install.sh?raw=1" | sh
```

Dessa vez deve passar sem erro de permissão.

**Servidor em segundo plano sem root:** como `apt install tmux` exige root, use o
`screen` (normalmente já instalado):

```bash
# Verifica se tem screen
which screen

# Cria sessão em segundo plano
screen -dmS fcc fcc-server

# Roda o Claude Code
fcc-claude

# Para encerrar o servidor depois
screen -X -S fcc quit
```

---

## Configurar o modelo no Admin UI

Com o `fcc-server` em execução:

1. Abra **`http://127.0.0.1:8082/admin`** no navegador.
2. Cole sua **`NVIDIA_NIM_API_KEY`** (a chave `nvapi-...`).
3. Clique em **Validate** e depois em **Apply**.

O modelo padrão já vem configurado como:

```
nvidia_nim/nvidia/nemotron-3-super-120b-a12b
```

---

## Modelos recomendados

Outros modelos bons para programação que você pode selecionar no Admin UI:

| Modelo                                       |
|----------------------------------------------|
| `nvidia_nim/nvidia/nemotron-3-super-120b-a12b` (padrão) |
| `nvidia_nim/moonshotai/kimi-k2.5`            |
| `nvidia_nim/z-ai/glm5.1`                     |
| `nvidia_nim/minimaxai/minimax-m2.5`          |

---

## Usando no VS Code (opcional)

Você pode usar a extensão do Claude Code no VS Code apontando para o proxy local.

1. Abra as configurações: `Ctrl+,` (Windows/Linux) ou `Cmd+,` (macOS) →
   busque por **`claude-code.environmentVariables`** → **"Edit in settings.json"**.
2. Adicione ao seu `settings.json`:

```json
"claudeCode.environmentVariables": [
  { "name": "ANTHROPIC_BASE_URL", "value": "http://localhost:8082" },
  { "name": "ANTHROPIC_AUTH_TOKEN", "value": "freecc" },
  { "name": "CLAUDE_CODE_AUTO_COMPACT_WINDOW", "value": "190000" }
]
```

Mantenha o `fcc-server` rodando para que a extensão consiga se conectar ao proxy.

---

## Solução de problemas

### Os comandos `fcc-server` / `fcc-claude` não são encontrados

Significa que o diretório de instalação não está no **PATH**.

**Windows (PowerShell):**

```powershell
# Descobre onde o fcc-server está instalado
where.exe fcc-server
```

Se não encontrar, adicione manualmente o diretório ao PATH:

1. Pressione `Win + S` e busque por **"variáveis de ambiente"**.
2. Clique em **"Editar as variáveis de ambiente do sistema"**.
3. Clique em **"Variáveis de Ambiente..."**.
4. Em **"Variáveis do usuário"**, selecione **Path** → **Editar** → **Novo**.
5. Adicione o caminho onde o `fcc-server` está. Geralmente é um destes:
   - `C:\Users\SEU_USUARIO\AppData\Roaming\Python\Python314\Scripts`
   - `C:\Users\SEU_USUARIO\.local\bin`
   - `C:\Users\SEU_USUARIO\.uv\bin`
6. Clique em **OK** em tudo e **feche e reabra** o PowerShell.

Verifique:

```powershell
fcc-server --help
fcc-claude --help
```

**macOS / Ubuntu:**

```bash
which fcc-server
which fcc-claude
```

Se não encontrar, adicione os diretórios ao PATH:

```bash
# Ubuntu (Bash)
echo 'export PATH="$HOME/.local/bin:$HOME/.uv/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# macOS (Zsh)
echo 'export PATH="$HOME/.local/bin:$HOME/.uv/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Erro `npm ERR! code EACCES` ao instalar (Linux/macOS)

O Node.js do sistema foi instalado pelo administrador e o `npm install -g` tenta
escrever em um diretório protegido (`/usr/local/lib`). A solução é instalar o
Node.js na sua *home* via **nvm** — veja
[Sem permissão de root](#sem-permissão-de-root-ambientes-restritos--laboratório).

---

## Limitações

- Você está usando modelos **open-source**, **não** o Claude real.
- Recursos avançados (extended thinking, cadeias complexas de *tool use*, edição
  multi-arquivo) podem ser **menos confiáveis** — depende do modelo escolhido.
- Chat básico, geração de código e edições simples costumam funcionar bem.
- O *tier* gratuito da NVIDIA NIM tem limite de aproximadamente **40 requisições/minuto**.

---

## Referências

- Projeto **free-claude-code**: <https://github.com/Alishahryar1/free-claude-code>
- API keys da NVIDIA NIM: <https://build.nvidia.com/settings/api-keys>
- **nvm** (Node Version Manager): <https://github.com/nvm-sh/nvm>

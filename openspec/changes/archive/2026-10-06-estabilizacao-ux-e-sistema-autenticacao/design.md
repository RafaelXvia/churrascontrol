# Decisões de Design & Arquitetura Técnica — Estabilização de UX e RBAC

## 1. Arquitetura de Interface & Correção da Navbar

### A. Eliminação da Sobreposição do Header Streamlit
No arquivo `ui_components.py`, as seguintes regras CSS serão injetadas:
```css
/* Desativa completamente captura de ponteiro e colapsa a altura do cabeçalho nativo */
header[data-testid="stHeader"],
div[data-testid="stHeader"] {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    pointer-events: none !important;
    visibility: hidden !important;
}

/* Garante que a barra superior customizada esteja na camada superior de interação */
.st-key-cc_nav_desktop,
.st-key-cc_nav_mobile,
.st-key-cc_navbar_container {
    position: relative !important;
    z-index: 9999 !important;
}
```

### B. Navegação Direta e RBAC Dinâmico
- `render_navbar(active_tab: str)` inspecionará o estado de sessão `st.session_state.get("usuario_logado")`.
- Se o usuário autenticado for do cargo `caixa`, os links para `Cardápio`, `Relatórios` e `Colaboradores` não serão renderizados ou serão desabilitados com badge informativo.
- Exibição de badge do usuário conectado (`👤 Nome [Cargo]`) com botão de Logout (`Sair`).
- As páginas restritas (`2_Cardapio.py`, `3_Relatorios.py`, etc.) terão uma checagem de guarda `ui_components.verificar_permissao_acesso(["gerente"])`: caso o usuário tente acessar diretamente pela URL, será exibida uma tela de acesso negado amigável com botão de retorno.

---

## 2. Robustez do Cardápio do Cliente (`5_Cardapio_Cliente.py`)

### A. Sanitização de Valores Nulos
Evitar chamadas diretas como `p.get("descricao").lower()` ou `p.get("categoria").lower()`:
```python
nome_limpo = (p.get("nome") or "").strip()
cat_limpa = (p.get("categoria") or "Geral").strip()
desc_limpa = (p.get("descricao") or "").strip()
img_limpa = p.get("url_imagem") or "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80"
```

### B. Eliminação do Botão Redundante e Card 100% Clicável
- Remover o botão físico `st.button("Adicionar ao Pedido")` que ficava abaixo de cada card.
- O card visual conterá um botão invisível de acionamento ou ancoragem via JavaScript unificado, abrindo diretamente o modal de seleção de quantidade e observações do prato ao ser clicado/tocado em qualquer parte de sua área.
- Armazenar o produto selecionado em `st.session_state["modal_prato_ativo"]` antes de invocar o `@st.dialog`, garantindo que o diálogo não se perca nos reruns.

---

## 3. Sincronização Real do Auto-Refresh no Salão (`1_Salao_e_Mesas.py`)

### A. Fim do Iframe Desconectado
- Remover o arquivo/bloco `components.html` que possuía o contador isolado em JavaScript.
- Utilizar Streamlit nativo com `@st.fragment(run_every=15)` (intervalo operacional de 15 segundos, muito mais adequado para o ritmo de um restaurante que 60 segundos).
- Inserir um indicador visual nativo com a hora exata da última leitura local (`Última leitura: HH:MM:SS`) e um botão `st.button("🔄 Atualizar Salão")` para forçar recarregamento imediato.

---

## 4. Sistema de Autenticação, Usuários e RBAC

### A. Modelo de Dados no SQLite (`churrascontrol.db`)
Nova tabela `colaboradores`:
```sql
CREATE TABLE IF NOT EXISTS colaboradores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    numero TEXT NOT NULL,
    cargo TEXT NOT NULL CHECK(cargo IN ('caixa', 'gerente')),
    primeiro_acesso INTEGER NOT NULL DEFAULT 1 CHECK(primeiro_acesso IN (0, 1)),
    ativo INTEGER NOT NULL DEFAULT 1 CHECK(ativo IN (0, 1)),
    criado_em TEXT NOT NULL,
    atualizado_em TEXT NOT NULL
);
```

### B. Seed Inicial Seguro
Se a tabela estiver vazia, cria o primeiro Gerente Administrador padrão:
- Email: `gerente@churrascontrol.com`
- Senha Inicial: `admin123`
- Cargo: `gerente`
- `primeiro_acesso`: 1 (forçando a troca no primeiro login)

### C. Segurança e Criptografia
- Hash de senhas implementado com `hashlib.sha256` combinado com salt interno fixo do sistema, sem dependências externas pesadas em C que possam quebrar em contêineres mínimos da Discloud.
- Fluxo de login:
  1. O usuário digita email e senha.
  2. Valida hash no banco.
  3. Se `primeiro_acesso == 1`, exibe modal obrigatório de "Definir Nova Senha Pessoal" antes de permitir qualquer ação.
  4. Após a troca, `primeiro_acesso` é setado para `0` e o usuário navega com seu perfil.

### D. Paridade e Sincronização com Xano
- Tabela `user.xs` em `xano/table/` com campos `nome`, `email`, `cargo`, `numero`, `primeiro_acesso`.
- Eventos de criação e atualização de colaboradores enfileirados em `fila_sincronizacao`.

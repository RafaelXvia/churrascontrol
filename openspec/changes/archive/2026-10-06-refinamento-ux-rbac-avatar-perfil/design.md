# Design Técnico: Refinamento UX, Login Moderno, Avatar de Perfil e RBAC Estrito

## 1. Arquitetura de Componentes e Fluxos

### 1.1 Tela de Login Moderna
- Estrutura centrada com card estilizado em CSS: bordas em gradiente sutil, sombreamento profundo, ícone de chama estilizado em SVG com iluminação âmbar.
- Campos de entrada com destaque nos rótulos e foco visual aprimorado.
- Tratamento de erro com feedback em toast e alert visual moderno.

### 1.2 Avatar Circular e Modal de Perfil do Usuário
- Na navbar (desktop e mobile), renderizar um botão circular estilizado com a inicial do colaborador (ex: `G` para Gerente, `R` para Rafael).
- Ao clicar no avatar, acionar `@st.dialog("Meu Perfil & Segurança")`:
  - Seção superior com badge do cargo (`GERENTE` ou `CAIXA`) e identificador.
  - Campos desabilitados (`disabled=True`): Nome, E-mail, Telefone, Cargo.
  - Seção expansível ou dedicada para "Alterar Minha Senha":
    - Senha Atual
    - Nova Senha (mínimo 4 caracteres)
    - Confirmação da Nova Senha
    - Validação de senha atual e atualização atômica no SQLite via `data_manager.atualizar_senha_colaborador`.
  - Botão de logout no rodapé do diálogo.

### 1.3 Cardápio do Cliente — Toque no Card e Eliminação de Conflito de Diálogos
- Substituir o botão separado "Pedir" por um overlay nativo no card: cada card do prato possui um botão invisível sobreposto (`opacity: 0`, `position: absolute`, ocupando 100% da área do card), tornando o toque no card instantâneo sem necessidade de JS frágil.
- Ao clicar no card, adiciona diretamente 1 unidade do prato ao carrinho (`st.session_state[session_key]`) e emite um toast de confirmação.
- O diálogo de seleção redundante (`modal_adicionar_prato`) é descontinuado em favor da adição direta ao cardápio, mantendo apenas o diálogo único do carrinho (`modal_carrinho_mesa`), sanando a exceção `StreamlitInvalidLayoutContextError`.

### 1.4 Ergonomia em Salão e Mesas
- Na listagem de itens da comanda:
  - Diminuir a coluna descritiva e reajustar colunas dos botões para `[5, 2.5, 1.2, 1.2, 1.2]`.
  - Botão de decrementar: `➖` com estilo de botão tátil.
  - Botão de incrementar: `➕` com estilo de botão tátil.
  - Botão de remoção: `✖` com `help="Excluir item da comanda"` evitando qualquer corte de texto.

### 1.5 Gestão e Edição de Colaboradores
- Criar a função `data_manager.editar_colaborador(colab_id, nome, email, numero, cargo, nova_senha=None, primeiro_acesso=None)`.
- Re-criptografar todos os dados sensíveis no SQLite e enfileirar sync com o Xano.
- Em `6_Colaboradores.py`, adicionar botão de edição que abre `@st.dialog("Editar Colaborador")` com todos os campos editáveis pelo Gerente.

### 1.6 Regras Estritas de RBAC para Caixa
- Caixa acessa exclusivamente:
  - `pages/1_Salao_e_Mesas.py`
  - `pages/2_Cardapio.py`
- Em `ui_components.py`:
  - Se `cargo == "caixa"`: Navbar renderiza apenas "Salão & Mesas", "Cardápio" e o Avatar.
- Em `app.py`:
  - Se `usuario["cargo"] == "caixa"`: redireciona imediatamente com `st.switch_page("pages/1_Salao_e_Mesas.py")`.
- Em `3_Relatorios.py` e `6_Colaboradores.py`:
  - Acesso bloqueado para Caixa.

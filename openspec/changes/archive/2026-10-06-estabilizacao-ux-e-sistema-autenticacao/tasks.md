# Lista de Tarefas — Estabilização de UX e Sistema de Autenticação RBAC

## Fase 1: Correção Imediata de UX e Bugs de Interface
- [x] **1.1 Corrigir sobreposição da Navbar em `ui_components.py`**
  - Ocultar e anular `pointer-events` do `header[data-testid="stHeader"]`.
  - Fixar `z-index: 9999` e garantir responsividade sem travamento de hover/clique.
- [x] **1.2 Estabilizar e robustecer Cardápio do Cliente em `pages/5_Cardapio_Cliente.py`**
  - Tratar todos os valores nulos (`descricao`, `categoria`, `url_imagem`) com fallbacks seguros.
  - Remover botão redundante "Adicionar ao Pedido", tornando o card 100% clicável com acionamento estável do modal.
  - Ajustar bounds do `st.number_input` no carrinho para evitar `StreamlitAPIException`.
- [x] **1.3 Sincronizar e aprimorar auto-refresh do Salão em `pages/1_Salao_e_Mesas.py`**
  - Remover iframe com timer JavaScript desconectado.
  - Configurar `@st.fragment(run_every=15)` com indicador nativo da última sincronização e botão manual de refresh.

## Fase 2: Camada de Dados de Autenticação (SQLite + Xano)
- [x] **2.1 Implementar tabela `colaboradores` e funções de autenticação em `data_manager.py`**
  - Criar tabela `colaboradores` com campos `nome`, `email`, `senha_hash`, `numero`, `cargo`, `primeiro_acesso`, `ativo`.
  - Implementar funções: `autenticar_usuario()`, `cadastrar_colaborador()`, `atualizar_senha()`, `listar_colaboradores()`, `excluir_colaborador()`.
  - Inserir seed padrão do primeiro Gerente (`gerente@churrascontrol.com` / `admin123`).
  - Adicionar enfileiramento de eventos na `fila_sincronizacao` para o Xano.
- [x] **2.2 Atualizar schema XanoScript em `xano/table/colaborador.xs`**
  - Definir estrutura em XanoScript com campos de colaboração e papéis `caixa` e `gerente`.

## Fase 3: Camada Visual de Autenticação e RBAC
- [x] **3.1 Criar componente de Login e Troca de Senha de Primeiro Acesso em `ui_components.py`**
  - Formulário elegante de login integrado ao design system escuro do ChurrasControl.
  - Diálogo modal bloqueante para primeiro acesso (obrigando redefinição da senha provisória).
  - Funções de checagem de autorização (`exigir_autenticacao()`, `verificar_permissao_acesso()`).
- [x] **3.2 Integrar RBAC na Navbar em `ui_components.py`**
  - Ocultar abas restritas quando logado como `caixa`.
  - Exibir badge do usuário ativo e botão de Logout.
- [x] **3.3 Proteger páginas existentes contra acesso indevido**
  - Inserir guarda de autenticação em `app.py`, `1_Salao_e_Mesas.py`, `2_Cardapio.py`, `3_Relatorios.py`, `4_Mesas_QRCodes.py`.
  - Manter `5_Cardapio_Cliente.py` aberto para clientes via QR Code sem exigir login de salão.
- [x] **3.4 Criar nova página/módulo de Gerenciamento de Colaboradores**
  - Adicionar tela exclusiva do Gerente para cadastrar novos membros com nome, email, senha inicial, número e cargo (`caixa` ou `gerente`).
  - Listagem dos colaboradores com status de primeiro acesso e opção de desativação/exclusão.

## Fase 4: Testes e Validação Automatizada
- [x] **4.1 Criar nova suíte de testes `tools/test_autenticacao_rbac.py`**
  - Testar hash de senhas, validação de login, primeiro acesso, troca de senha e regras de restrição de cargos.
- [x] **4.2 Executar bateria completa via `tools/run_all.py`**
  - Garantir 100% de aprovação em todas as 6 suítes de testes.

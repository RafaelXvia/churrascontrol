# Proposta de Mudança — Estabilização de UX e Sistema de Autenticação RBAC

## 1. Contexto de Negócio & Problemas Identificados

Durante a operação em ambiente real do **ChurrasControl**, foram diagnosticados 4 gargalos de experiência de uso e a necessidade de governança de segurança operacional:

1. **Intermitência dos Botões da Navbar**: Em determinados momentos, os botões superiores de navegação deixam de responder aos cliques e perdem o estado de hover ("parecem morrer").
   - *Causa Raiz*: O container invisível padrão do Streamlit (`header[data-testid="stHeader"]`) possui altura de ~56px e z-index elevado (999990), sobrepondo a margem superior da barra de navegação e interceptando os eventos de clique do mouse.
2. **Quebra e Erro Vermelho ao Adicionar Certos Itens no Carrinho (Cardápio Cliente)**: Ao adicionar pratos específicos na pré-comanda, ocorre uma falha com alerta vermelho no topo da página.
   - *Causa Raiz*: Atributos com valores `NULL` no banco de dados (ex: `descricao` ou `categoria` nulas) provocam exceção não tratada ao chamar `.lower()` na filtragem/busca. Adicionalmente, chamadas acopladas de `@st.dialog` dentro de `if st.button` e limites rígidos de `st.number_input` (max_value=20) geravam `StreamlitAPIException`.
3. **Redundância de Ação nos Cards do Cardápio**: O botão visual "Adicionar ao Pedido" polui o layout de pratos e gera atrito desnecessário em relação ao comportamento mobile-first esperado de clicar diretamente no card do prato.
4. **Dessincronização do Auto-Refresh no Salão e Mesas**: O timer regressivo em JavaScript dentro de um iframe (`components.html`) operava de forma totalmente desvinculada do ciclo de execução do Streamlit, induzindo o operador ao erro ao reiniciar sem que uma nova leitura do banco de dados ocorresse.
5. **Necessidade de Controle de Acesso Baseado em Perfis (RBAC) e Primeiro Acesso**: Ausência de controle de permissões por operador. Operadores de caixa tinham acesso irrestrito a relatórios financeiros e configurações do cardápio, além de não haver rastreabilidade de logins ou política de troca obrigatória de senha inicial.

---

## 2. Escopo da Solução

### No Escopo:
- **Correção da Navbar**: Ocultação efetiva e anulação de `pointer-events` do `stHeader`, elevação de `z-index` da navbar e adoção de roteamento rápido e responsivo para Desktop e Mobile.
- **Tratamento Robusto de Nulos & Carrinho**: Sanitização de dados de produtos no cardápio do cliente, proteção contra `AttributeError` em buscas e normalização do ciclo de vida dos modais de adição ao pedido via `st.session_state`.
- **Card 100% Clicável**: Eliminação do botão redundante "Adicionar ao Pedido", tornando o card do produto a única e direta área de toque no cardápio do cliente.
- **Auto-Refresh Sincronizado**: Substituição do timer fictício em iframe por componente nativo Streamlit reativo, com atualização automática periódica e botão explícito de "Atualizar Agora".
- **Sistema de Autenticação & Cargos (RBAC)**:
  - Criação da tabela `colaboradores` (ou `usuarios`) no SQLite em modo WAL com hash seguro (`sha256` com salt).
  - Dois cargos estritos:
    - **`gerente`**: Acesso irrestrito a todos os módulos, relatórios, cardápio e tela administrativa de colaboradores.
    - **`caixa`**: Acesso restrito exclusivamente ao **Painel Geral (Home)** e **Salão & Mesas**.
  - **Fluxo de Primeiro Acesso**: Se `primeiro_acesso = 1`, o sistema obriga a redefinição de senha antes de liberar o acesso às telas do sistema.
  - Tela administrativa do Gerente para cadastrar colaboradores (`nome`, `email`, `senha`, `numero`, `cargo`).
  - Atualização do schema e rotas correspondentes em XanoScript (`xano/table/user.xs` e fila de sincronização).
  - Preservação do acesso anônimo no **Cardápio Digital do Cliente** (`pages/5_Cardapio_Cliente.py`), permitindo que clientes na mesa peçam livremente via QR Code.

### Fora do Escopo:
- Autenticação OAuth2 de terceiros (Google/Facebook).
- Alteração da persistência básica do salão (continua SQLite WAL + fila Xano).
- Modificação das pastas de backup (`discloud/`) e pedagógica (`material do professor/`).

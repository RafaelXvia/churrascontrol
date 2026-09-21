# Tasks: Cardápio Visual Unificado & Modais Interativos com Sincronização Xano

- [x] 1. Sincronização e Paridade de Schema Xano
  - [x] 1.1 Implementar `sincronizar_produtos_xano()` em `data_manager.py` para puxar fotos reais do Imgur e produtos do endpoint Xano.
  - [x] 1.2 Atualizar schema de produtos em `produtos` para incluir `url_imagem`, `descricao`, `qtd_disp`, `precisa_produzir` e `disponivel`.
  - [x] 1.3 Adicionar políticas `referrerpolicy="no-referrer"` contra erro 403 Forbidden do Imgur.

- [x] 2. Modais Saltados na Tela (@st.dialog)
  - [x] 2.1 Criar modal `dialog_novo_produto()` para cadastro completo com todos os campos da tabela `PRODUTO`.
  - [x] 2.2 Criar modal `dialog_gerenciar_produto()` com abas de edição e exclusão de produto com confirmação.
  - [x] 2.3 Substituir formulários expansíveis (`st.expander`) e botões textuais por acionamento via modais.

- [x] 3. Unificação Visual & Interação Reativa Sem F5
  - [x] 3.1 Migrar o layout de delivery/cards gastronômicos para a página oficial `pages/2_Cardapio.py`.
  - [x] 3.2 Remover a página duplicada `pages/4_Cardapio_Digital.py`.
  - [x] 3.3 Implementar técnica de Overlay Nativo com botão invisível cobrindo o card para clique instantâneo sem recarregar a tela (sem F5).
  - [x] 3.4 Injetar script delegado para propagação de eventos de clique.

- [x] 4. Limpeza da Navbar e Testes Automatizados
  - [x] 4.1 Remover atalho "Cardápio Digital" da navbar desktop e mobile em `ui_components.py`, mantendo as 4 abas oficiais.
  - [x] 4.2 Adicionar recarregamento automático (`importlib.reload`) em todas as páginas para evitar stale modules.
  - [x] 4.3 Atualizar e validar a suíte de testes (`test_app.py`, `test_cardapio_delivery.py`, `test_security_performance.py`, `test_sqlite_sync.py`).

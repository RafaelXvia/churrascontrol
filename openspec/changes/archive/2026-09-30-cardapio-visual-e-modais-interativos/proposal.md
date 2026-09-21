# Proposal: Cardápio Visual Unificado & Modais Interativos com Sincronização Xano

## 1. Contexto e Motivação
O catálogo de produtos do ChurrasControl anteriormente utilizava uma exibição tradicional em tabela linear com formulários expansíveis (`st.expander`) e botões textuais.
Para elevar a experiência do usuário a um padrão de cardápio digital moderno de restaurante/delivery, o cliente solicitou:
1. **Unificação Visual**: Transformar o cardápio em uma grade interativa de cards gastronômicos modernos com fotos reais de alta definição, badges de preparo (*Na Brasa Viva* vs *Pronta Entrega*) e estoque disponível.
2. **Janelas Modais Saltadas na Tela (`st.dialog`)**:
   - Botão no cabeçalho para `➕ Novo Produto` que abre um modal saltado na tela com todos os atributos da tabela `PRODUTO`.
   - Clique direto em qualquer parte do card do produto para abrir o modal de `⚙️ Gerenciar Produto` (com abas para edição e exclusão segura).
3. **Interação Sem F5 (Zero Page Reload)**: Abertura imediata do modal via WebSocket nativo do Streamlit utilizando técnica de overlay invisível acoplado aos cards.
4. **Sincronização com Xano & Imgur Seguro**:
   - Integração com a API do Xano (`/produto`) para puxar fotos reais e dados cadastrais.
   - Aplicação da diretiva `referrerpolicy="no-referrer"` para viabilizar o carregamento seguro de imagens do Imgur sem bloqueio HTTP 403 Forbidden em ambiente `localhost`.
5. **Limpeza da Navegação**: Remoção de atalhos redundantes na navbar, mantendo estritamente as 4 abas operacionais do sistema.

## 2. Escopo da Alteração
- Modificação em `pages/2_Cardapio.py`: Unificação completa do layout de cards gastronômicos, busca, filtro de categorias em chips (`st.pills`), botão de cadastro em modal e clique no card para gerenciamento.
- Modificação em `data_manager.py`: Inclusão de `sincronizar_produtos_xano()` para sincronização sob demanda dos dados do Xano para o SQLite.
- Remoção de página duplicada `pages/4_Cardapio_Digital.py`.
- Ajustes de `ui_components.py`: Restauração da navbar executiva de 4 seções (*Painel Geral*, *Salão & Mesas*, *Cardápio*, *Relatórios*) e suporte a recarregamento com `importlib.reload`.

## 3. Critérios de Sucesso
- Abertura imediata do modal de edição ao clicar em qualquer ponto do card do prato sem recarregar a tela (sem F5).
- Abertura do modal de cadastro via botão `➕ Novo Produto`.
- Carregamento 100% funcional das fotos reais do Imgur.
- 100% dos testes automatizados (`test_app.py`, `test_cardapio_delivery.py`, etc.) passando com sucesso.

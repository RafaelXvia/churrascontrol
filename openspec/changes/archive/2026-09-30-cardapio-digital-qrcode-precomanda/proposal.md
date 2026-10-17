# Proposta: Cardápio Digital de Mesa via QR Code com Pré-Comanda do Cliente e Baixa Automática de Estoque

## 1. Contexto e Motivação
No modelo operacional do ChurrasControl, o garçom e o operador lançam pedidos manualmente na tela do sistema (*Salão & Mesas*). Para modernizar o atendimento gastronômico e viabilizar autoatendimento ágil:
1. O cliente sentado em uma mesa física (ex: Mesa 6) deve poder escanear um **QR Code exclusivo daquela mesa** com a câmera do celular.
2. O QR Code abre uma **página dedicada de Cardápio Digital do Cliente**, com visualização rica e responsiva (mobile-first), fotos reais, preços, badges de categoria e seletores de pratos.
3. Para evitar que pedidos incompletos ou acidentais poluam a cozinha e o salão, a seleção dos itens vai primeiro para uma **Pré-Comanda local (carrinho do cliente)**.
4. **Somente quando o cliente revisar e clicar em "Confirmar Pedido"**:
   - A comanda da mesa é localizada (ou aberta automaticamente se a mesa estiver livre).
   - Os itens são registrados no SQLite e despachados para a fila de sincronização com o Xano.
   - O pedido surge em tempo real no *Painel Geral* e no *Salão & Mesas*.
   - O estoque (`qtd_disp`) do produto é decrementado automaticamente, e caso atinja 0 unidades, o produto é marcado como esgotado (`disponivel = 0`).

## 2. Escopo da Solução
- **Central Administrativa de QR Codes de Mesas (`pages/4_Mesas_QRCodes.py`)**:
  - Geração visual de cartões com QR Code para cada mesa cadastrada no sistema (ex: Mesas 1 a 10).
  - Exibição de link direto para compartilhamento e visualização rápida.
  - Opção de impressão/exportação dos cartões para disposição nas mesas do salão.
  - **Atualização Reativa Silenciosa com `@st.fragment(run_every=60)`**: Sincronização periódica a cada 60s sem recarregar a página (sem F5), preservando o scroll do usuário.
  - **Timer Regressivo Visual de 60s**: Contador vivo descendo segundo a segundo com reset automático a cada ciclo.
- **Página de Autoatendimento do Cliente (`pages/5_Cardapio_Cliente.py`)**:
  - Leitura de parâmetro de URL (`?mesa=X`).
  - Layout mobile-first responsivo com visualização gastronômica, fotos e filtro rápido de categorias.
  - **Carrinho Flutuante (FAB)**: Botão fixo no canto inferior da tela do celular (`position: fixed`) permitindo acesso rápido à pré-comanda de qualquer altura do scroll.
  - Modal/Gaveta de Pré-Comanda com ajuste de quantidades, observações por item e cálculo de subtotal.
  - Botão de envio "Confirmar Pedido na Cozinha" com trava contra envios duplicados.
- **Salão & Gestão de Comandas (`pages/1_Salao_e_Mesas.py`)**:
  - Controles incrementais ágeis na listagem de itens da comanda (`➕` aumentar, `➖` diminuir e `🗑️` excluir) com ajuste automático proporcional de estoque.
  - Badge de timer regressivo de 60s no cabeçalho e fragmento reativo silencioso `@st.fragment(run_every=60)`.
- **Regra de Negócio de Estoque no `data_manager.py`**:
  - Decrementar `qtd_disp` na confirmação de itens de comanda.
  - Se `qtd_disp <= 0`, atualizar `disponivel = 0` (produto esgotado).
  - Bloquear adição à pré-comanda de produtos marcados como esgotados.
  - Restauração de estoque caso um item seja diminuído ou removido da comanda ou comanda cancelada.
- **Arquitetura Local-First (Zero Rate Limit no Xano)**:
  - Todas as leituras periódicas do timer consultam 100% o SQLite local (`churrascontrol.db`), consumindo 0 requisições HTTP da cota do Xano.
- **Limpeza de Artefatos Legados**:
  - Descontinuação do antigo `churras_data.json` em prol do SQLite WAL.

## 3. Benefícios
- **Autonomia do Cliente**: Pedidos rápidos sem necessidade de aguardar garçom para ver o cardápio.
- **Zero Poluição de Dados**: A pré-comanda protege o salão de cliques acidentais; a cozinha só é acionada após confirmação explícita.
- **Controle Preciso de Estoque**: Evita vender pratos esgotados em horários de pico.
- **Experiência em Tempo Real Fluida**: Atualizações reativas de salão e mesas sem perda de foco ou scroll.
- **Proteção de Quota de API**: Consultas de auto-refresh sem impacto na cota do Xano.

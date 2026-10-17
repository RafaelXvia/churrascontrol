# precomanda-e-estoque Specification

## Purpose
Regras de autoatendimento gastronômico com geração de QR Codes por mesa, carrinho de pré-comanda isolado e baixa automática de estoque de produtos no ChurrasControl.

## Requirements

### Requirement: Baixa e Esgotamento Automático de Estoque
O sistema SHALL decrementar automaticamente o campo `qtd_disp` da tabela `produtos` na quantidade de unidades confirmadas em comanda. Quando `qtd_disp` atingir zero ou menos, o sistema SHALL atualizar automaticamente o campo `disponivel = 0` (marcando o produto como esgotado).

#### Scenario: Venda de última unidade do produto
- **WHEN** um produto possui `qtd_disp = 1` e tem 1 unidade lançada e confirmada em comanda
- **THEN** o sistema SHALL atualizar `qtd_disp = 0` e `disponivel = 0`, bloqueando novas seleções deste item no cardápio digital do cliente.

#### Scenario: Estorno por cancelamento ou remoção de item
- **WHEN** um operador remove um item previamente lançado da comanda
- **THEN** o sistema SHALL restituir a quantidade de volta ao `qtd_disp` do produto e, se o item estava esgotado (`disponivel = 0`), restabelecer `disponivel = 1`.

### Requirement: Pré-Comanda do Cliente via QR Code de Mesa
O sistema SHALL disponibilizar interface de autoatendimento onde itens selecionados pelo cliente permanecem exclusivamente em sessão temporária (`st.session_state`), sem gerar registros no banco nem afetar o salão até a ação explícita de "Confirmar Pedido".

#### Scenario: Cliente navegando e adicionando itens à pré-comanda
- **WHEN** o cliente na Mesa 6 adiciona produtos ao carrinho
- **THEN** o sistema SHALL manter os itens na pré-comanda local sem alterar o status da mesa física nem notificar o painel do salão.

#### Scenario: Confirmação e envio da pré-comanda
- **WHEN** o cliente clica no botão "Confirmar e Enviar Pedido"
- **THEN** o sistema SHALL criar ou reutilizar a comanda aberta daquela mesa, gravar os itens na tabela `itens_comanda`, decrementar o estoque, enfileirar as ações para o Xano e tornar o pedido imediatamente visível nas telas operacionais do restaurante.

### Requirement: Ajuste Granular de Itens na Comanda do Salão
O sistema SHALL disponibilizar controles de incremento (`➕`), decremento (`➖`) e exclusão (`🗑️`) na lista de itens registrados da comanda aberta em `pages/1_Salao_e_Mesas.py`.

#### Scenario: Operador aumentando quantidade de item
- **WHEN** o garçom clica no botão `➕` do item na comanda
- **THEN** o sistema SHALL incrementar a quantidade em 1 unidade, recalcular o subtotal da comanda, decrementar 1 unidade do estoque de `produtos` e enfileirar a alteração para o Xano.

#### Scenario: Operador diminuindo quantidade de item
- **WHEN** o garçom clica no botão `➖` do item na comanda com quantidade > 1
- **THEN** o sistema SHALL decrementar a quantidade em 1 unidade, estornar 1 unidade de volta ao estoque de `produtos` e atualizar o subtotal da comanda.

### Requirement: Atualização Reativa Periódica com Timer Regressivo
O sistema SHALL executar atualização silenciosa de dados a cada 60 segundos via `@st.fragment(run_every=60)` no Salão & Mesas e na Central de QR Codes sem disparar recarregamento de página completo (sem F5), mantendo o scroll do usuário e exibindo contador visual regressivo de 60s a 0s com reset automático contínuo.

#### Scenario: Expiração do ciclo de 60 segundos
- **WHEN** o cronômetro visual atinge 0s
- **THEN** o sistema SHALL reexecutar o fragmento via WebSocket com dados frescos do SQLite local e reiniciar a contagem regressiva em 60s sem alterar a posição de rolagem da tela.

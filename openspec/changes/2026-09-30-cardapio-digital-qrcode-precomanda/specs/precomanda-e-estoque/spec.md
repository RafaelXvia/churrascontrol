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

## Why

O coração do atendimento gastronômico é o lançamento contínuo de itens nas comandas dos clientes. O garçom precisa adicionar porções, bebidas e carnes com rapidez, registrar observações de preparo específicas para a cozinha (ex: "ao ponto", "sem gelo") e ter a garantia de que adições repetidas do mesmo produto sejam consolidadas sem poluir a comanda. Além disso, a contabilidade do restaurante exige que o preço cobrado seja fixado no momento do lançamento (`preco_momento`), sem flutuar caso o cardápio sofra alterações posteriores.

## What Changes

- **Motor de Consumo e Itens da Comanda (`data_manager.py`)**:
  - Implementação de `adicionar_item_comanda(comanda_id, produto_id, quantidade, observacao)`:
    - Gravação imutável de `preco_momento`, `nome_produto_historico` e `categoria_historico`.
    - Agrupamento inteligente: se o mesmo produto já constar na comanda, a quantidade é acumulada em vez de criar uma linha redundante, atualizando a observação caso informada.
  - Implementação de `obter_comanda_detalhes(comanda_id)`:
    - Retorno estruturado contendo dados da comanda, lista completa de itens com subtotal calculado (`quantidade * preco_momento`) e soma total geral.
  - Implementação de `editar_item_comanda(item_id, quantidade, preco_momento, observacao)`:
    - Ajuste de quantidade, preço pontual ou observação de preparo.
  - Implementação de `remover_item_comanda(item_id)`:
    - Exclusão atômica de um item de consumo lançado indevidamente.
- **Sincronização em Segundo Plano com Xano**:
  - Despacho assíncrono de eventos de inserção, edição e exclusão de itens para a fila do Xano (`_enqueue_xano`), preservando a responsividade imediata local.

## Capabilities

### New Capabilities
- `lancamento-itens-e-imutabilidade-consumo`: Lançamento de pedidos em comandas com snapshot histórico de preços, observações de cozinha e acumulação inteligente de quantidades.

### Modified Capabilities

## Impact

- `data_manager.py`: Novas rotinas de adição, edição, remoção e consulta detalhada de itens de consumo.
- `churras_data.json`: Criação da lista estruturada `itens_comanda` com referências a `comanda_id` e `produto_id`.

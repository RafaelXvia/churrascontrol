# lancamento-itens-e-imutabilidade-consumo Specification

## Purpose
Viabilizar o lançamento rápido e preciso de itens consumidos em comandas ativas, assegurando imutabilidade financeira de preços através de snapshots contábeis, agrupamento automático de produtos repetidos e anotação de instruções de preparo.

## Requirements

### Requirement: Lançamento com Snapshot Imutável de Preço
O sistema SHALL disponibilizar `adicionar_item_comanda(comanda_id, produto_id, quantidade, observacao)` capturando o valor unitário atual do produto e gravando-o no registro do item como `preco_momento`, juntamente com `nome_produto_historico` e `categoria_historico`.

#### Scenario: Lançamento de produto cadastrado
- **WHEN** o operador adiciona um item à comanda informando quantidade e observação
- **THEN** o sistema SHALL registrar a linha de consumo com o preço congelado no instante da operação e enfileirar a sincronização assíncrona com o Xano.

### Requirement: Acumulação Inteligente de Linhas de Consumo
O sistema SHALL verificar se o `produto_id` já consta lançado na mesma `comanda_id`. Caso já exista, o sistema SHALL somar a nova quantidade ao registro existente em vez de criar uma linha duplicada.

#### Scenario: Adição repetida de mesma bebida ou porção
- **WHEN** um cliente pede mais 2 unidades de um refrigerante já presente na comanda com 1 unidade
- **THEN** a linha existente do refrigerante SHALL ter sua quantidade atualizada para 3 unidades, recalculando o subtotal daquele item.

### Requirement: Detalhamento Estruturado da Comanda
O sistema SHALL fornecer `obter_comanda_detalhes(comanda_id)` retornando o cabeçalho da comanda, todos os itens com seus subtotais individuais (`quantidade * preco_momento`) e o somatório total de consumo.

#### Scenario: Consulta detalhada de comanda ativa
- **WHEN** o operador solicita os detalhes de uma mesa
- **THEN** a resposta SHALL conter a listagem discriminada de todos os produtos consumidos, suas quantidades, observações e o valor acumulado exato.

### Requirement: Edição e Remoção de Itens Lançados
O sistema SHALL permitir corrigir a quantidade ou observação de um item via `editar_item_comanda(item_id, ...)` e remover um lançamento cancelado via `remover_item_comanda(item_id)`.

#### Scenario: Remoção de item inserido por engano
- **WHEN** o operador cancela um item na comanda
- **THEN** o item SHALL ser removido imediatamente da lista de consumo e o total da comanda SHALL ser recalculado subtraindo o respectivo valor.

## MODIFIED Requirements

### Requirement: Lançamento com Snapshot Imutável de Preço
O sistema SHALL disponibilizar `adicionar_item_comanda(comanda_id, produto_id, quantidade, observacao)` capturando o valor unitário atual do produto e gravando-o no registro do item como `preco_momento`, juntamente com `nome_produto_historico` e `categoria_historico`. Os registros de itens lançados em comandas liquidadas SHALL ter imutabilidade perpétua e NÃO SHALL ser apagados por rotinas de limpeza periódica ou inicialização.

#### Scenario: Lançamento de produto cadastrado
- **WHEN** o operador adiciona um item à comanda informando quantidade e observação
- **THEN** o sistema SHALL registrar a linha de consumo com o preço congelado no instante da operação e enfileirar a sincronização assíncrona com o Xano.

#### Scenario: Preservação perpétua pós-pagamento
- **WHEN** uma comanda tem seu status alterado para `PAGA`
- **THEN** todos os seus itens associados em `itens_comanda` SHALL ser preservados permanentemente na base de dados, permitindo auditorias e relatórios históricos de produtos.

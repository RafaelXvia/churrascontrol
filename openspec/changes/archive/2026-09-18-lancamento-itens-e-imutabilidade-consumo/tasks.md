## 1. Funções de Gestão de Consumo na Comanda

- [x] 1.1 Implementar `adicionar_item_comanda` em `data_manager.py` com snapshot de `preco_momento` e `nome_produto_historico`.
- [x] 1.2 Implementar lógica de agregação de quantidade para produtos repetidos na mesma comanda.
- [x] 1.3 Implementar `obter_comanda_detalhes` com cálculo em tempo real de subtotais e valor total acumulado.
- [x] 1.4 Implementar funções de alteração e exclusão `editar_item_comanda` e `remover_item_comanda`.

## 2. Enfileiramento em Background para Xano

- [x] 2.1 Conectar as mutações de itens ao despachador assíncrono `_enqueue_xano`.
- [x] 2.2 Garantir que eventuais falhas de conexão externa não bloqueiem a persistência imediata local.

## 3. Testes e Validação

- [x] 3.1 Validar que adicionar o mesmo produto 2 vezes acumula quantidade sem duplicar itens.
- [x] 3.2 Verificar que alterar o preço no cardápio de produtos não modifica o `preco_momento` de itens já lançados.

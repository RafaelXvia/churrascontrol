## 1. Funções de Ciclo de Vida de Mesas e Comandas

- [x] 1.1 Implementar a função `abrir_mesa(numero_mesa, qtd_pessoas)` com bloqueio de duplicidade em `data_manager.py`.
- [x] 1.2 Implementar a função `listar_mesas()` agregando o cálculo dinâmico de `total_atual` a partir dos itens.
- [x] 1.3 Implementar a função `cancelar_comanda(comanda_id)` atualizando o status e liberando a mesa física.
- [x] 1.4 Implementar a função `excluir_mesa(mesa_id)` com tratamento seguro de desassociação de comanda.

## 2. Persistência e Integridade de Concorrência

- [x] 2.1 Garantir concorrência thread-safe através de `threading.Lock()` nas funções `load_data()` e `save_data()`.
- [x] 2.2 Estruturar a geração automática de chaves primárias através do dicionário `seq` em `churras_data.json`.

## 3. Testes e Validação

- [x] 3.1 Validar que abrir uma mesa já ocupada dispara exceção `ValueError`.
- [x] 3.2 Verificar que o cancelamento de uma mesa libera o número para nova abertura imediata.

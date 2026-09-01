## Why

O fluxo operacional de um restaurante ou churrascaria depende criticamente do controle em tempo real das mesas físicas e de seus atendimentos. Garçons e caixas precisam de funções ágeis para abrir uma mesa para determinado número de clientes, evitar duplicidade de abertura no mesmo número físico, acompanhar os subtotais consumidos e liberar ou cancelar comandas de forma segura.

## What Changes

- **Motor Operacional de Mesas e Atendimentos (`data_manager.py`)**:
  - Implementação da função `abrir_mesa(numero_mesa, qtd_pessoas)`: validação impeditiva de número de mesa já ocupado (`ValueError`), incremento atômico de sequenciais em `data["seq"]` e criação pareada da mesa física e da comanda com status `ABERTA`.
  - Implementação da função `listar_mesas()`: recuperação de todas as mesas ativas no salão com agregação em tempo real do total acumulado de consumo a partir dos itens de sua comanda vinculada.
  - Implementação de `cancelar_comanda(comanda_id)` e `excluir_mesa(mesa_id)`: marcação de status `CANCELADA`, anulação do vínculo `mesa_id = None` e desocupação imediata da mesa no salão.
- **Validações de Integridade de Salão**:
  - Garantia de que nenhuma mesa possa ter mais de uma comanda aberta simultaneamente.
  - Preservação do `numero_mesa_historico` na comanda mesmo após liberação ou exclusão da mesa física.

## Capabilities

### New Capabilities
- `gestao-operacional-mesas-e-comandas`: Regras de negócio, ciclo de vida e operações atômicas de abertura, acompanhamento e cancelamento de mesas e comandas no salão.

### Modified Capabilities

## Impact

- `data_manager.py`: Inclusão das funções centrais `abrir_mesa`, `listar_mesas`, `excluir_mesa` e `cancelar_comanda`.
- `churras_data.json`: Estruturação das chaves `mesas`, `comandas` e controle sequencial em `seq`.

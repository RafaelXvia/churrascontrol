# sincronizacao-comandas-xano Specification

## Purpose
Garantir a integridade referencial relacional entre as tabelas `comandas` e `itens_comanda` no Xano, sincronizando instantaneamente o ciclo de vida das comandas a partir do SQLite local e prevenindo registros órfãos ou erros 404 de fechamento.

## Requirements

### Requirement: Sincronização de Comanda na Abertura
O sistema SHALL transmitir uma requisição `POST /comandas` ao Xano sempre que uma nova comanda for criada no salão físico através de `abrir_mesa(numero_mesa, qtd_pessoas)` ou via autoatendimento em `confirmar_precomanda_cliente(numero_mesa, itens)`.

#### Scenario: Abertura de mesa no salão pelo operador
- **WHEN** uma mesa física for aberta com sucesso no SQLite local
- **THEN** a respectiva comanda com `id`, `numero_mesa` e `qtd_pessoas` SHALL ser enviada para persistência na tabela `comandas` do Xano via push imediato ou enfileiramento resiliente.

#### Scenario: Abertura de atendimento via QR Code do cliente
- **WHEN** um cliente sentado na mesa submete itens pelo cardápio digital criando uma nova comanda
- **THEN** a comanda pai criada no SQLite SHALL ser sincronizada com o Xano antes do envio dos itens de consumo.

### Requirement: Auto-Recuperação e Integridade em `itens_comanda`
O endpoint de lançamento de itens no Xano (`POST /comandas/{comanda_id}/itens`) SHALL verificar se a comanda informada existe na tabela `comandas`. Caso não exista, o endpoint SHALL criar o cabeçalho da comanda automaticamente antes de inserir o item em `itens_comanda`.

#### Scenario: Item lançado para comanda ainda não reconciliada
- **WHEN** uma requisição de adição de item chegar ao Xano com um `comanda_id` inexistente na tabela `comandas`
- **THEN** o Xano SHALL auto-criar o registro na tabela `comandas` e vincular o item normalmente sem quebrar a chave estrangeira relacional.

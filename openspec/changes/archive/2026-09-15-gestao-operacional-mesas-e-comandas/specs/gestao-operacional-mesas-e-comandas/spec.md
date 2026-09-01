# gestao-operacional-mesas-e-comandas Specification

## Purpose
Gerenciar o ciclo de vida operacional das mesas físicas no salão e suas respectivas comandas, garantindo unicidade de mesa ativa, acompanhamento instantâneo de consumo e controle seguro de cancelamentos.

## Requirements

### Requirement: Abertura Atômica de Mesa e Comanda
O sistema SHALL disponibilizar a operação `abrir_mesa(numero_mesa, qtd_pessoas)` que valida se o número da mesa já está em uso, cria o registro de mesa com status `OCUPADA`, inicializa uma nova comanda com status `ABERTA`, registra a data/hora de abertura em ISO-8601 e retorna os identificadores criados.

#### Scenario: Tentativa de abertura de mesa já ativa
- **WHEN** o operador tenta abrir uma mesa cujo número já existe na lista de mesas ativas
- **THEN** o sistema SHALL rejeitar a operação levantando um erro descritivo (`ValueError`) sem alterar a base de dados.

#### Scenario: Abertura bem-sucedida de nova mesa
- **WHEN** o operador informa um número de mesa não ocupado e a quantidade de pessoas
- **THEN** o sistema SHALL persistir a mesa e a comanda associada, retornando sucesso e os respectivos IDs.

### Requirement: Consulta Consolidada de Mesas Ativas
O sistema SHALL fornecer através de `listar_mesas()` a relação de todas as mesas ocupadas no salão, contendo `id`, `numero_mesa`, `capacidade`, `status`, `comanda_id` e o `total_atual` computado a partir da soma dos subtotais de seus itens ativos.

#### Scenario: Visualização do saldo atual da mesa
- **WHEN** a listagem de mesas ativas é solicitada
- **THEN** o total financeiro exibido para cada mesa SHALL refletir com exatidão o consumo em aberto de sua comanda vinculada.

### Requirement: Cancelamento e Liberação de Mesa
O sistema SHALL permitir cancelar uma comanda através de `cancelar_comanda(comanda_id)` ou `excluir_mesa(mesa_id)`, marcando o status da comanda como `CANCELADA`, desassociando o vínculo físico (`mesa_id = None`) e removendo a mesa do salão ativo.

#### Scenario: Cancelamento de atendimento
- **WHEN** uma comanda em andamento for cancelada
- **THEN** a mesa correspondente SHALL ser liberada imediatamente para nova ocupação e a comanda SHALL ser desconsiderada dos relatórios de receita.

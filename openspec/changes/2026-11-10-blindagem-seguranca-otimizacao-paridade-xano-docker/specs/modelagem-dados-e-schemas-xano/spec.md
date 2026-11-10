# Especificação Delta: Modelagem de Dados e Paridade Bidirecional Xano (`colaborador`, `mesas`, `produtos`)

## Requisitos Modificados e Adicionados

### Requisito 1: Paridade Completa de Colaboradores entre SQLite e Xano Cloud
Todo colaborador existente ou manipulado no SQLite (`colaboradores`) DEVE existir e refletir exatamente o mesmo estado na tabela `colaborador` do Xano Cloud.

#### Cenário: Reconciliação e Upsert Automático de Colaboradores no Xano
- **DADO** que existem colaboradores locais no SQLite (criados no seed inicial ou via tela de Colaboradores)
- **QUANDO** `reconciliar_colaboradores_xano()` ou uma operação `PATCH /colaborador/{id}` for processada pelo Sync Worker
- **ENTÃO** o sistema DEVE resolver o registro no Xano por `email` (ou criá-lo via `POST /colaborador` caso não exista no Xano), garantindo `0` erros `HTTP 404` na `fila_sincronizacao`.

#### Cenário: Atualização Completa de Campos em `PATCH /colaborador/{id}`
- **DADO** que um Gerente edita `nome`, `email`, `numero`, `cargo`, `senha_hash`, `primeiro_acesso` ou `ativo` de um colaborador
- **QUANDO** a sincronização enviar `PATCH /colaborador/{id}` para o Xano
- **ENTÃO** o endpoint XanoScript `colaborador_id_PATCH.xs` DEVE aceitar e persistir todos esses atributos na tabela `colaborador`.

### Requisito 2: Sincronização Não-Destrutiva de Produtos (`ON CONFLICT DO UPDATE`)
A função `sincronizar_produtos_xano()` NÃO DEVE executar `DELETE FROM produtos;` para não acionar `ON DELETE SET NULL` em `itens_comanda.produto_id`.

#### Cenário: Sincronização de produtos preserva vínculos históricos em `itens_comanda`
- **DADO** um item de comanda vinculado a `produto_id = 1`
- **QUANDO** `sincronizar_produtos_xano()` atualizar o catálogo local a partir do Xano
- **ENTÃO** os produtos DEVEM ser atualizados via `INSERT ... ON CONFLICT(id) DO UPDATE`, mantendo `itens_comanda.produto_id = 1` intacto.

### Requisito 3: Sincronização de Exclusão de Mesa no Xano
A função `excluir_mesa(mesa_id)` DEVE enfileirar `DELETE /mesas/{mesa_id}` na `fila_sincronizacao`.


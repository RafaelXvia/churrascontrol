# modelagem-dados-e-schemas-xano Specification

## Purpose
Estabelecer o modelo conceitual de domínio e os esquemas de dados relacionais no backend No-Code (Xano) para o sistema ChurrasControl, definindo entidades, integridade referencial e imutabilidade de registros financeiros.

## Requirements

### Requirement: Entidades de Domínio e Relacionamentos
O sistema SHALL estruturar o domínio de negócio em quatro entidades centrais documentadas em `docs/domain-model.md`: `Mesa` (espaço físico com status `LIVRE`, `OCUPADA`, `CONTA`), `Produto` (item de cardápio com `codigo_pdv` único e `preco_unitario`), `Comanda` (atendimento com status `ABERTA`, `PAGA`, `CANCELADA`) e `ItemComanda` (registro de consumo vinculado a uma comanda ativa).

#### Scenario: Definição de integridade referencial
- **WHEN** uma comanda for vinculada a uma mesa ativa
- **THEN** a mesa SHALL manter no máximo uma comanda com status `ABERTA` simultaneamente, garantindo a unicidade do atendimento no salão.

### Requirement: Schemas de Tabelas no Xano
O sistema SHALL disponibilizar no repositório os esquemas relacionais no formato Script Xano (`xano/table/`), contendo as definições das tabelas `mesas`, `comandas`, `itens_comanda`, `produto`, `cliente` e `user`.

#### Scenario: Estrutura da tabela de comandas
- **WHEN** a tabela `comandas` for consultada ou criada
- **THEN** ela SHALL possuir os campos `id`, `mesa_id`, `numero_mesa_historico`, `data_abertura`, `data_fechamento`, `status`, `taxa_servico`, `qtd_pessoas` e `valor_total`.

### Requirement: Princípio da Imutabilidade Histórica de Consumo
O sistema SHALL exigir que os itens adicionados às comandas guardem cópias imutáveis do preço (`preco_momento`), nome (`nome_produto_historico`) e categoria no instante da inserção.

#### Scenario: Alteração cadastral posterior de produto
- **WHEN** o preço de um produto for reajustado no cardápio após ter sido lançado em comandas existentes
- **THEN** os registros de `itens_comanda` já existentes SHALL permanecer inalterados, preservando a fidelidade contábil e o histórico financeiro.

## MODIFIED Requirements

### Requirement: Motor Analítico de Vendas
O sistema SHALL disponibilizar `obter_dashboard_dados(periodo)` suportando os intervalos `1d`, `7d`, `15d`, `30d` ou intervalos customizados por data início/fim, calculando faturamento bruto, total de comandas, ticket médio por comanda, total de clientes, ticket médio por pessoa, ranking de produtos e vendas por mesa e categoria a partir de comandas pagas e seus respectivos itens históricos preservados.

#### Scenario: Exclusão de comandas canceladas
- **WHEN** o dashboard analítico consolida as métricas do período
- **THEN** comandas com status `CANCELADA` ou `ABERTA` SHALL NÃO ser contabilizadas no faturamento e ticket médio.

#### Scenario: Preservação de itens em reinicializações
- **WHEN** o sistema é reiniciado ou a função `init_db()` é reexecutada
- **THEN** os registros de `itens_comanda` vinculados a comandas `PAGA` SHALL permanecer intactos na base de dados SQLite, mantendo os dados analíticos históricos acessíveis.

## ADDED Requirements

### Requirement: Agregação de Desempenho e Preferência por Mesa
O sistema SHALL disponibilizar a agregação analítica de vendas discriminada por mesa física a partir de `numero_mesa_historico` das comandas pagas, computando o faturamento total acumulado, a quantidade de atendimentos concluídos e o ticket médio de cada mesa.

#### Scenario: Identificação de mesas mais rentáveis
- **WHEN** a análise de desempenho por mesa é requisitada
- **THEN** o sistema SHALL retornar a lista de mesas físicas ordenadas por faturamento decrescente com a contagem de clientes atendidos e comandas fechadas.

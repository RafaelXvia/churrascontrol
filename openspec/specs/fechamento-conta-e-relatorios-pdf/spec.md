# fechamento-conta-e-relatorios-pdf Specification

## Purpose
Prover o fechamento contábil e liquidação de comandas com aplicação de serviço e rateio por pessoa, consolidação analítica de receitas do restaurante e emissão de relatórios gerenciais em PDF via ReportLab.

## Requirements

### Requirement: Encerramento Contábil de Comanda
O sistema SHALL disponibilizar `fechar_comanda(comanda_id, valor_final, taxa_servico)` que altera o status da comanda para `PAGA`, registra a data/hora de fechamento, grava o total liquidado, anula a associação física com a mesa (`mesa_id = None`), desocupa a mesa no salão ativo e agenda sincronização crítica com o Xano.

#### Scenario: Pagamento e liberação da mesa
- **WHEN** o operador confirma o pagamento da comanda
- **THEN** a mesa vinculada SHALL ser liberada instantaneamente no salão e a comanda SHALL ser arquivada como liquidada.

### Requirement: Motor Analítico de Vendas
O sistema SHALL disponibilizar `obter_dashboard_dados(periodo)` suportando os intervalos `1d`, `7d`, `15d` e `30d`, calculando faturamento bruto, total de comandas, ticket médio por comanda, total de clientes e ticket médio por pessoa exclusivamente a partir de comandas pagas.

#### Scenario: Exclusão de comandas canceladas
- **WHEN** o dashboard analítico consolida as métricas do período
- **THEN** comandas com status `CANCELADA` ou `ABERTA` SHALL NÃO ser contabilizadas no faturamento e ticket médio.

### Requirement: Exportação Executiva de Relatório em PDF
O sistema SHALL disponibilizar `gerar_pdf_bytes(periodo)` produzindo um fluxo binário de documento PDF contendo cabeçalho executivo, sumário das métricas financeiras, gráfico de tendências e tabela de auditoria estilizada.

#### Scenario: Download de relatório oficial
- **WHEN** o administrador solicita a emissão do relatório em PDF
- **THEN** o sistema SHALL sintetizar os dados do período e retornar os bytes do PDF para download imediato no navegador.

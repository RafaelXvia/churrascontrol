## Why

A conclusão do ciclo de atendimento exige regras financeiras claras no caixa: aplicação facultativa da taxa de serviço sugerida (10%), cálculo transparente da divisão de conta por quantidade de clientes (pax) e encerramento contábil com liberação da mesa. Complementarmente, o administrador do restaurante necessita de visibilidade executiva sobre receitas, evolução temporal das vendas, categorias mais lucrativas e a capacidade de exportar relatórios formais em PDF com layout profissional.

## What Changes

- **Fechamento Financeiro de Comandas (`data_manager.py`)**:
  - Implementação de `fechar_comanda(comanda_id, valor_final, taxa_servico)`:
    - Atualização do status para `PAGA`, registro de `data_fechamento` em ISO-8601, gravação do valor final liquidado e indicação da taxa de serviço.
    - Desassociação atômica da mesa física (`mesa_id = None`) e remoção da mesa do salão ativo, liberando-a para novos clientes.
    - Disparo de sincronização de evento crítico em background para o endpoint `/comandas/{id}/fechar` do Xano.
- **Motor de Inteligência e Métricas Analíticas**:
  - Implementação de `obter_dashboard_dados(periodo)` com suporte a filtros configuráveis (`1d`, `7d`, `15d`, `30d`).
  - Consolidação de KPIs executivos: Faturamento Total, Total de Comandas Finalizadas, Ticket Médio por Mesa, Total de Clientes Atendidos e Ticket Médio por Pessoa.
  - Agregação estatística de evolução diária de receita, distribuição de faturamento por categoria e ranking top produtos mais vendidos.
- **Gerador de Relatórios Oficiais em PDF (ReportLab)**:
  - Implementação de `gerar_pdf_bytes(periodo)` utilizando a biblioteca `reportlab`:
    - Estruturação via `SimpleDocTemplate` no padrão A4 com margens calibradas (14mm).
    - Paleta corporativa elegante: cabeçalho Obsidian `#0f172a`, acentos Amber `#d97706` e tabelas zebradas com dados de faturamento e auditoria.
    - Renderização direta em memória com `io.BytesIO` para download instantâneo sem poluição de arquivos residuais no disco.

## Capabilities

### New Capabilities
- `fechamento-conta-e-relatorios-pdf`: Fechamento financeiro de atendimentos, rateio por pessoa, métricas consolidadas de receita e geração de relatórios oficiais em PDF via ReportLab.

### Modified Capabilities

## Impact

- `data_manager.py`: Novas rotinas `fechar_comanda`, `obter_dashboard_dados` e `gerar_pdf_bytes`.
- Dependência: Uso do `reportlab` no backend para geração dinâmica de documentos PDF.

## 1. Fechamento de Comandas e Desocupação de Mesas

- [x] 1.1 Implementar `fechar_comanda` em `data_manager.py` com registro de valor final, data de fechamento e taxa de serviço.
- [x] 1.2 Implementar remoção da mesa ativa liberando o espaço no salão.
- [x] 1.3 Configurar o enfileiramento crítico do fechamento para sincronização com o endpoint `/comandas/{id}/fechar` do Xano.

## 2. Métricas Analíticas e Agregação

- [x] 2.1 Implementar `obter_dashboard_dados` consolidando faturamento, contagem de clientes e ticket médio.
- [x] 2.2 Estruturar agregação de vendas por categoria e ordenação de produtos mais vendidos.
- [x] 2.3 Suportar janelas temporais de análise (`1d`, `7d`, `15d`, `30d`).

## 3. Geração de PDF com ReportLab

- [x] 3.1 Implementar a rotina `gerar_pdf_bytes` usando `SimpleDocTemplate` e estilos do ReportLab.
- [x] 3.2 Formatar tabela de resumo executivo com cores institucionais (Obsidian `#0f172a` e Amber `#d97706`).
- [x] 3.3 Testar geração binária em memória retornando bytes válidos para download direto.

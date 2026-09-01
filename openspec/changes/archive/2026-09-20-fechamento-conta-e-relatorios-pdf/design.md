## Context

O processo de fechamento de conta em estabelecimentos alimentícios é um ponto sensível de auditoria. Divergências entre o valor cobrado e os itens consumidos geram reclamações de clientes e perdas fiscais. A emissão de um relatório impresso formal em PDF fornece a comprovação gerencial necessária para fechamento de caixa e prestação de contas dos turnos.

## Goals / Non-Goals

**Goals:**
- Liquidar comandas com cálculo opcional de taxa de serviço (10%) e divisão por pax.
- Liberar imediatamente a mesa física no salão após o pagamento.
- Consolidar métricas financeiras precisas considerando exclusivamente comandas pagas.
- Gerar relatórios em formato PDF com alta qualidade tipográfica em memória sem depender de dependências de sistema pesadas (como headless Chrome ou wkhtmltopdf).

**Non-Goals:**
- Integração direta com gateways de pagamento TEF/PIX bancário automático (operações registradas pelo operador).
- Impressão física direta em hardware de ponto de venda sem intervenção do usuário.

## Decisions

- **Decisão 1: Geração de PDF Nativamente com ReportLab**:
  - *Contexto*: Evitar ferramentas que necessitem de binários externos ou motores de renderização HTML instáveis.
  - *Decisão*: Utilizar `reportlab.platypus` (`SimpleDocTemplate`, `Table`, `Paragraph`) para criar o documento com layout determinístico e altíssimo desempenho.
- **Decisão 2: Filtro Estrito de Status Contábil**:
  - *Contexto*: Comandas canceladas não podem inflar as métricas de receita.
  - *Decisão*: O motor `obter_dashboard_dados` processa apenas comandas cujo `status == 'PAGA'`.

## Risks / Trade-offs

- [Consumo de Memória na Geração de PDF] Arquivos grandes em turnos com milhares de comandas poderiam onerar memória → Mitigação: O documento sintetiza KPIs executivos e limita o resumo analítico às comandas do período, mantendo o payload leve e rápido.

## Why

O projeto original possuía suas funcionalidades interativas (abertura de mesas, lançamento de comandas, cadastro de produtos e visualização de relatórios com download de PDF) restritas aos templates HTML Jinja2 (`templates/`). Para concluir a transição para Streamlit exigida na disciplina, todas essas funcionalidades operacionais devem ser implementadas nativamente no Streamlit em uma arquitetura multipage (`pages/`), consumindo a API FastAPI.

## What Changes

- **Página de Salão & Mesas (`pages/1_🥩_Salão_e_Mesas.py`)**:
  - Grid visual de mesas abertas com indicação de consumo atual.
  - Formulário para abertura de nova mesa (número e quantidade de pessoas).
  - Painel de gerenciamento de comanda da mesa selecionada: listagem de itens consumidos com subtotais, busca rápida de produtos do cardápio para lançamento com quantidade e observações, edição e remoção de itens, fechamento de conta com cálculo de taxa de serviço (10%) e divisão por pessoa, além de cancelamento de comanda.
- **Página de Cardápio & Produtos (`pages/2_📋_Cardapio.py`)**:
  - Tabela interativa com busca em tempo real por nome, código PDV ou categoria.
  - Formulário de cadastro de novo produto com validação de código PDV.
  - Edição de preço, categoria e nome de produtos existentes.
  - Exclusão de produtos do cardápio.
- **Página de Relatórios & Dashboard (`pages/3_📊_Relatorios.py`)**:
  - Filtro por períodos (`1d`, `7d`, `15d`, `30d`).
  - Cards de métricas (Faturamento Total, Total de Mesas, Ticket Médio por Mesa e Ticket por Pessoa).
  - Gráficos nativos interativos: evolução diária de vendas e faturamento por categoria.
  - Tabela dos top produtos mais vendidos e histórico de comandas finalizadas.
  - Botão de download direto do PDF executivo gerado pelo endpoint ReportLab do backend.
- **Testes & Validação**:
  - Script de teste funcional (`test_screens_streamlit.py`) validando a sintaxe e a integridade de todas as páginas criadas.

## Capabilities

### New Capabilities
- `telas-operacionais-streamlit`: Conjunto de páginas multipage do Streamlit fornecendo todas as funcionalidades operacionais do ChurrasControl integradas à API FastAPI.

### Modified Capabilities

## Impact

- `pages/1_🥩_Salão_e_Mesas.py`: Nova tela de operação de mesas e comandas.
- `pages/2_📋_Cardapio.py`: Nova tela de gestão de cardápio e produtos.
- `pages/3_📊_Relatorios.py`: Nova tela de dashboard analítico e download de PDF.
- `test_screens_streamlit.py`: Script de teste para validação das páginas.

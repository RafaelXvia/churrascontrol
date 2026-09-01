# telas-operacionais-streamlit Specification

## Purpose
Disponibilizar a suíte completa de interfaces operacionais em Streamlit para visualização executiva do salão, gestão interativa de mesas e comandas, catálogo de cardápio comercial e relatórios analíticos com emissão de PDF.

## Requirements

### Requirement: Painel Geral Operacional (`app.py`)
O sistema SHALL disponibilizar a página raiz `app.py` com visão consolidada das operações do salão, exibindo 4 métricas principais (Mesas Ocupadas, Consumo em Aberto, Faturamento 7 Dias, Itens no Cardápio) e uma grade com 3 cards de módulos interativos ("1. Salão e Mesas", "2. Cardápio Comercial", "3. Relatórios & PDF").
Os cards de módulo SHALL apresentar animação de elevação no hover (`translateY(-6px)`), bordas iluminadas nas cores temáticas (âmbar, azul e esmeralda), transição da seta de ação e navegação direta ao clicar no card.

#### Scenario: Visualização e navegação no Painel Geral
- **WHEN** o usuário acessa o Painel Geral e clica em qualquer card de módulo
- **THEN** a tela exibe os indicadores em tempo real e redireciona imediatamente para o módulo correspondente via `st.switch_page`.

### Requirement: Operação de Salão e Comandas (`pages/1_Salao_e_Mesas.py`)
O sistema SHALL disponibilizar a página `pages/1_Salao_e_Mesas.py` permitindo abrir novas mesas via modal dialog (`@st.dialog`), visualizar mesas em cards interativos padronizados e gerenciar comandas em painel lateral integrado.
Os cards de mesa SHALL ter altura fixa de 165px com padding interno equilibrado, contendo número da mesa, capacidade, badge de status ("OCUPADA"), subtotal e texto de ação ("Clique para abrir comanda ➔") sem quebra ou transbordamento de borda.

#### Scenario: Abertura de nova mesa via diálogo
- **WHEN** o operador clica no botão "+ Abrir Nova Mesa"
- **THEN** um diálogo modal em destaque é aberto solicitando número da mesa e capacidade de clientes, criando a comanda sem causar quebra visual na página.

#### Scenario: Seleção de mesa e gestão da comanda
- **WHEN** o operador clica sobre o card de uma mesa ativa
- **THEN** o card ganha destaque luminoso e o Painel da Comanda é exibido ao lado com a lista de itens consumidos, formulário de lançamento de produtos com quantidade e observação, cálculo de taxa de serviço (10%), valor por pessoa e botão de fechamento de conta com liberação automática da mesa.

### Requirement: Gerenciamento do Cardápio Comercial (`pages/2_Cardapio.py`)
O sistema SHALL disponibilizar a página `pages/2_Cardapio.py` para pesquisa dinâmica de produtos, visualização tabular com filtros por categoria, cadastro de novos itens com código único de PDV, edição de preços e exclusão de itens.

#### Scenario: Cadastro e busca de produto
- **WHEN** o operador pesquisa por nome/código ou cadastra um novo produto
- **THEN** a listagem atualiza instantaneamente com os dados salvos localmente.

### Requirement: Painel Analítico e Emissão de Relatório (`pages/3_Relatorios.py`)
O sistema SHALL disponibilizar a página `pages/3_Relatorios.py` exibindo KPIs de faturamento, ticket médio, total de pedidos por período configurável (`1d`, `7d`, `15d`, `30d`), gráficos de produtos mais vendidos e botão para download imediato do relatório em PDF.

#### Scenario: Exportação do relatório executivo
- **WHEN** o usuário seleciona o período e clica para baixar relatório
- **THEN** o arquivo PDF estruturado é gerado instantaneamente via ReportLab e disponibilizado para download.

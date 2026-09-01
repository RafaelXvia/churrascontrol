## Purpose

Disponibilizar a suíte de interfaces operacionais em Streamlit para gerenciamento de salão, cardápio comercial e relatórios executivos com exportação de PDF.

## ADDED Requirements

### Requirement: Operação de Salão e Comandas no Streamlit
O sistema SHALL disponibilizar a página `pages/1_🥩_Salão_e_Mesas.py` permitindo abrir novas mesas, visualizar comandas ativas, adicionar itens com observações e fechar contas com taxa de serviço e divisão por pessoa.

#### Scenario: Abertura e consumo de mesa
- **WHEN** o operador preenche o número da mesa, quantidade de pessoas e confirma a abertura
- **THEN** a mesa aparece como ativa no salão e passa a permitir inclusão de itens com quantidade e observações.

#### Scenario: Fechamento de conta
- **WHEN** o operador seleciona uma mesa ativa e clica para fechar comanda
- **THEN** o sistema exibe o resumo financeiro, permite selecionar taxa de 10%, exibe o valor por pessoa e conclui o encerramento liberando a mesa.

### Requirement: Gerenciamento do Cardápio no Streamlit
O sistema SHALL disponibilizar a página `pages/2_📋_Cardapio.py` permitindo busca de produtos, inclusão de novos itens com código PDV, edição e exclusão.

#### Scenario: Cadastro de produto no cardápio
- **WHEN** o usuário informa código PDV, nome, categoria e preço válido
- **THEN** o produto é registrado na API e listado imediatamente na tabela de cardápio.

### Requirement: Painel Analítico e Emissão de Relatório no Streamlit
O sistema SHALL disponibilizar a página `pages/3_📊_Relatorios.py` exibindo KPIs financeiros, gráficos de desempenho por período e download do documento PDF.

#### Scenario: Consulta e exportação de relatório
- **WHEN** o usuário seleciona um período e solicita o relatório
- **THEN** o sistema exibe os dados consolidados e disponibiliza o botão de download com o PDF emitido pelo backend.

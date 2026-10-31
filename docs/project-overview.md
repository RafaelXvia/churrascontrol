# Project Overview — ChurrasControl

## 1. Visão Geral
O **ChurrasControl** é uma aplicação completa de automação comercial (Ponto de Venda e Gestão de Mesas) voltada para o setor de alimentação (restaurantes, bares e churrascarias). O sistema permite controle operacional do salão em tempo real, lançamento de comandas, catálogo de produtos e emissão de relatórios analíticos de vendas e desempenho financeiro com exportação em PDF.

## 2. Problema
Restaurantes de pequeno e médio porte sofrem com perda de histórico de lançamentos, lentidão na emissão da conta, erros de divisão por pessoa e dificuldades para mensurar produtos de maior margem de faturamento. Sistemas complexos tradicionais impõem infraestruturas pesadas e curvas de aprendizado lentas.

## 3. Objetivos do Sistema
- Permitir abertura, ocupação, visualização e encerramento de comandas de mesas de maneira ágil.
- Manter o registro fidedigno do histórico financeiro de consumo sem perdas em caso de oscilações de rede (armazenamento local híbrido com sincronização em nuvem).
- Prover relatórios em tela e documentos gerenciais para impressão e prestação de contas.

## 4. Usuários e Atores
- **Operador de Salão / Garçom**: Realiza a abertura de mesas, lança itens e observações de preparo nas comandas.
- **Operador de Caixa**: Confere a comanda, aplica taxa de serviço opcional (10%), visualiza o valor por pessoa e conclui o pagamento.
- **Gerente / Administrador**: Cadastra e edita produtos no cardápio, monitora o faturamento total, ticket médio e exporta relatórios executivos em PDF.

## 5. Escopo e Módulos Principais
1. **Frente de Caixa & Mesas**: Grid responsivo de status de mesas, detalhamento de comandas em tempo real, inclusão e remoção de itens com observações.
2. **Cardápio de Produtos**: Gestão de produtos, prevenção em tempo real de duplicidade de código PDV e precificação.
3. **Métricas & Relatórios**: Dashboard com gráficos analíticos (Chart.js), divisão por períodos (`1d`, `7d`, `15d`, `30d`) e motor de geração de PDF com ReportLab.

## 6. Arquitetura Tecnológica
- **Linguagem / Framework**: Python 3.10+, FastAPI, Pydantic, ReportLab.
- **Frontend**: Streamlit.
  - *Restrição*: Streamlit será utilizado como tecnologia exclusiva para implementação do frontend da aplicação.
- **Infraestrutura**: Docker Compose (PostgreSQL 16) e suporte a deploy na plataforma Discloud.
- **Nuvem & Integração**: Xano Backend API com sincronização assíncrona por fila (`asyncio.Queue` / persistência SQLite).
- **Ferramentas de IA & MCP**: Xano Developer MCP (`@xano/developer-mcp`) integrado via `.vscode/mcp.json` e `.gemini/settings.json` para consulta e validação de XanoScript.

## 7. Diretrizes de Organização do Workspace
- **Código da Aplicação**: Fica restrito e concentrado dentro da pasta `crudfaculdade/`.
- **Material do Professor (`material do professor/`)**: Pasta externa dedicada estritamente à consulta pedagógica, manuais e documentações conceituais (somente leitura).
- **Pasta Discloud (`discloud/` na raiz)**: Reservada para backups de segurança gerenciados pelo usuário. Nunca deve ser apagada ou manipulada por agentes automatizados.

## 8. Suíte de Ferramentas e Qualidade (`crudfaculdade/tools/`)
Todas as rotinas de verificação, auditoria e testes automatizados estão centralizadas em `crudfaculdade/tools/`:
- `run_all.py`: Execução consolidada de toda a bateria de testes com relatório executivo.
- `db_diagnostics.py`: Diagnóstico em tempo real de integridade do SQLite (modo WAL), índices e monitoramento da fila de sincronização com o Xano.
- Suítes de testes automatizados (`test_app.py`, `test_sqlite_sync.py`, `test_security_performance.py`, `test_cardapio_delivery.py`, `test_cardapio_cliente_qrcode.py`).
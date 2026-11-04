# otimizacao-memoria-ram-discloud Specification

## Purpose
Garantir a execução eficiente, estável e com consumo reduzido de memória RAM da aplicação ChurrasControl no ambiente em nuvem da Discloud, eliminando bibliotecas desnecessárias de Data Science, prevenindo vazamentos de memória e sustentando a aplicação na faixa de 65MB a 75MB.

## Requirements

### Requirement: Erradicação de Pandas e Altair
O sistema SHALL operar sem dependência das bibliotecas `pandas` e `altair`, renderizando gráficos de séries temporais e barras em SVG e HTML/CSS nativos no navegador do cliente, sem alocação de extensões C compiladas de Data Science no servidor.

#### Scenario: Visualização do painel de gráficos analíticos
- **WHEN** o usuário acessa a página de relatórios e seleciona um período de análise
- **THEN** os gráficos de evolução temporal e de mix por categorias SHALL ser gerados como elementos vetoriais SVG e barras CSS nativas com custo zero de alocação de memória no processo Python.

### Requirement: Lazy Loading e Geração Sob Demanda de PDF
O sistema SHALL importar a biblioteca `reportlab` e compilar o arquivo PDF exclusivamente sob demanda quando o usuário acionar o botão de exportação, PROIBINDO importações globais na inicialização de módulos ou renderização antecipada de documentos PDF.

#### Scenario: Acesso à página de relatórios sem download
- **WHEN** o usuário navega pela tela de relatórios apenas para consultar indicadores e gráficos
- **THEN** nenhuma classe do ReportLab SHALL ser instanciada na memória RAM até que o botão de gerar PDF seja explicitamente clicado.

### Requirement: Estabilidade de Módulos sem Reload Redundante
O sistema SHALL importar `data_manager` e `ui_components` de forma estática e idempotente em todas as telas, PROIBINDO chamadas a `importlib.reload()` nos scripts das páginas.

#### Scenario: Interação contínua do usuário
- **WHEN** um usuário navega pelas telas ou executa comandos iterativos (abrir comanda, filtrar relatórios, adicionar itens)
- **THEN** o sistema SHALL reaproveitar as instâncias de módulos já carregadas sem reexecutar compilações nem criar definições duplicadas no heap do Python.

### Requirement: Parametrização Otimizada do Streamlit
O sistema SHALL configurar o Streamlit em modo headless sem monitoramento ativo de arquivos locais (`fileWatcherType = "none"`), limite de upload reduzido e com telemetria desativada.

#### Scenario: Execução em container na Discloud
- **WHEN** o servidor Streamlit é iniciado
- **THEN** nenhuma thread de inotify/watchdog SHALL ser alocada para inspecionar alterações de arquivos em tempo de execução.

### Requirement: Controle de Memória e WAL no SQLite
O sistema SHALL limitar o cache de páginas do SQLite a no máximo 2MB (`PRAGMA cache_size = -2000`), configurar autocheckpoint do WAL para 250 páginas e executar checkpoints periódicos para evitar crescimento indefinido do arquivo `.db-wal`.

#### Scenario: Escrita e leitura transacional no salão
- **WHEN** pedidos, fechamentos e sincronizações com o Xano ocorrem
- **THEN** as páginas do log WAL SHALL ser transferidas periodicamente ao banco principal e mantidas em tamanho reduzido.

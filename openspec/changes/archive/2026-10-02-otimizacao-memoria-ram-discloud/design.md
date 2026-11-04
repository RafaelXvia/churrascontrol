# Design Técnico: Otimização Radical de Memória RAM na Discloud

## 1. Visão Geral da Arquitetura Enxuta
A otimização atua na erradicação de bibliotecas pesadas desnecessárias e no enxugamento de recursos:
1. **Eliminação de Bibliotecas C/Data Science (`pandas`, `numpy`, `altair`)**: Gráficos analíticos e tabelas passam a ser desenhados diretamente em SVG vetorial e HTML/CSS nativos. Isso remove ~60MB de memória do processo Python.
2. **Lazy Loading de PDF (`reportlab`)**: As rotinas do ReportLab só são importadas se e quando o usuário clicar no botão de gerar PDF.
3. **Runtime Python & Ciclo de Vida Streamlit**: Eliminação do overhead de reruns com `importlib.reload` e inibição do file watcher inotify.
4. **Camada de Persistência SQLite**: Redução do buffer cache do SQLite para 2MB (`PRAGMA cache_size = -2000`) e autocompactação do log WAL (`PRAGMA wal_autocheckpoint = 250` e checkpoint passivo no worker).
5. **Alocação de Sistema Operacional no Container Linux**: Ajuste de variáveis de ambiente do alocador `glibc` (`MALLOC_TRIM_THRESHOLD_`) para garantir que páginas de memória liberadas pelo Python retornem imediatamente ao cgroup do Linux.

## 2. Decisões Técnicas Detalhadas

### 2.1 Eliminação do Pandas e Altair em Prol de Gráficos SVG/HTML
- **Problema**: O `pandas` era importado apenas para converter listas de dicionários em DataFrames para o `altair`, puxando `numpy`, `pyarrow` e bibliotecas C compiladas para a memória.
- **Solução**:
  - `render_svg_line_chart(evolucao)`: Gera um SVG puro com área gradiente, pontos de dados destacados e labels de moeda/data. Executado no cliente (browser) com 0 MB de custo de RAM no servidor.
  - `render_html_category_bars(cat_data)`: Renderiza barras horizontais com gradiente `#d97706` e porcentagens em CSS puro.
  - `render_ranking_table()` e `render_comandas_table()`: Tabelas estilizadas no padrão Dark Glassmorphic, consumindo listas de dicionários diretamente sem intermediários pesados.
  - Remoção definitiva de `pandas` do [requirements.txt](file:///c:/Users/K1ngs/Downloads/Faculdade/Innovation%20Lab%20Advanced%20NoLow%20Code/crudfaculdade/requirements.txt).

### 2.2 Lazy Loading do ReportLab e Geração de PDF Sob Demanda
- **Problema**: `reportlab` ficava carregado no topo de `data_manager.py` e gerava o PDF na montagem inicial de `pages/3_Relatorios.py`.
- **Solução**:
  - As importações de `SimpleDocTemplate`, `Paragraph`, etc., foram movidas exclusivamente para dentro de `data_manager.gerar_pdf_bytes()`.
  - Na tela de relatórios, o botão "Gerar Relatório PDF" só invoca o gerador quando acionado pelo usuário, salvando o buffer em `st.session_state["pdf_gerado"]`.

### 2.3 Remoção do `importlib.reload`
- **Problema**: O Streamlit reexecuta o script a cada clique. Executar `reload(data_manager)` e `reload(ui_components)` a cada rerun criava milhares de referências cíclicas e impedia que classes/funções fossem coletadas pelo GC.
- **Solução**: Uso exclusivo de importações estáticas (`import data_manager`, `import ui_components`).

### 2.4 Idempotência e PRAGMAs do SQLite
- Flag global `_db_initialized` para garantir execução única de `init_db()`.
- Configuração de `PRAGMA wal_autocheckpoint = 250;` (mantendo o teto do arquivo WAL abaixo de ~1MB).
- Configuração de `PRAGMA cache_size = -2000;` (limite estrito de 2MB de memória interna para páginas do SQLite).
- Execução periódica de `PRAGMA wal_checkpoint(PASSIVE);` no worker em background quando ocioso.

### 2.5 Tuning do Streamlit (`config.toml`) e Processo Mestre (`run.py`)
- `server.fileWatcherType = "none"`.
- `server.headless = true`.
- `client.toolbarMode = "minimal"`.
- Variáveis `MALLOC_TRIM_THRESHOLD_ = "100000"` e `PYTHONUNBUFFERED = "1"`.

# Tarefas de Implementação: Otimização Radical de Memória RAM na Discloud

- [x] 1. Configuração do Streamlit e Processo de Execução
  - [x] 1.1 Atualizar `.streamlit/config.toml` com `fileWatcherType = "none"`, `headless = true`, `port = 8080`, `maxUploadSize = 10` e `toolbarMode = "minimal"`.
  - [x] 1.2 Atualizar `run.py` definindo variáveis de ambiente `MALLOC_TRIM_THRESHOLD_` e `PYTHONUNBUFFERED`.

- [x] 2. Limpeza de Módulos e Reruns
  - [x] 2.1 Remover `importlib.reload` em `app.py`.
  - [x] 2.2 Remover `importlib.reload` em `pages/1_Salao_e_Mesas.py`.
  - [x] 2.3 Remover `importlib.reload` em `pages/2_Cardapio.py`.
  - [x] 2.4 Remover `importlib.reload` em `pages/3_Relatorios.py`.
  - [x] 2.5 Remover `importlib.reload` em `pages/4_Mesas_QRCodes.py`.
  - [x] 2.6 Remover `importlib.reload` em `pages/5_Cardapio_Cliente.py`.

- [x] 3. Camada de Dados e SQLite (`data_manager.py`)
  - [x] 3.1 Implementar flag `_db_initialized` para tornar `init_db()` estritamente idempotente.
  - [x] 3.2 Configurar PRAGMAs de memória em `get_connection()`: `cache_size = -2000` (2MB) e `wal_autocheckpoint = 250`.
  - [x] 3.3 Adicionar chamada de checkpoint passivo (`PRAGMA wal_checkpoint(PASSIVE)`) periódico no worker em background.
  - [x] 3.4 Implementar backoff adaptativo no loop ocioso do worker `_xano_sqlite_worker` (sleep de 2.5s quando sem tarefas pendentes).
  - [x] 3.5 Converter importações do `reportlab` para estritamente lazy-load dentro da função `gerar_pdf_bytes`.

- [x] 4. Erradicação de Pandas e Altair e Renderização Nativa em SVG/HTML (`pages/3_Relatorios.py`)
  - [x] 4.1 Remover importações de `pandas` e `altair`.
  - [x] 4.2 Remover `pandas` de `requirements.txt`.
  - [x] 4.3 Implementar renderizador nativo SVG vetorial `render_svg_line_chart` para evolução diária de vendas.
  - [x] 4.4 Implementar renderizador nativo CSS `render_html_category_bars` para mix por categorias.
  - [x] 4.5 Implementar tabelas HTML nativas para o ranking de produtos e auditoria de comandas.
  - [x] 4.6 Implementar fluxo de geração de PDF sob demanda do usuário no botão de exportação.

- [x] 5. Validação e Testes
  - [x] 5.1 Executar a suíte de testes completa via `python tools/run_all.py` garantindo 100% de sucesso.
  - [x] 5.2 Executar compactação e truncamento do banco WAL local de desenvolvimento.

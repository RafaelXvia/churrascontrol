# Proposta de Mudança: Otimização Radical de Memória RAM para Hospedagem na Discloud

## 1. Contexto & Problema
O ChurrasControl é hospedado na plataforma Discloud no container `churrascontrol` (`TYPE=site`, `RAM=512`).
Durante a execução, o container iniciava consumindo aproximadamente ~50MB de RAM (processo frio), porém subia para 148MB–160MB ao acessar a tela de Relatórios.
A investigação detalhada do processo identificou os fatores de sobrecarga:
1. **Recarregamento desnecessário de módulos (`importlib.reload`)**: Executado em todas as páginas a cada rerun do Streamlit, causando acúmulo de objetos obsoletos no heap e disparando `init_db()` repetidamente.
2. **Dependência excessiva de bibliotecas pesadas de Data Science (`pandas`, `numpy`, `altair`)**: O `pandas` era utilizado apenas na tela de relatórios para alimentar 2 gráficos do `altair`. Isso carregava na memória dezenas de megabytes de extensões C compiladas (`.so`), elevando a RAM de 70MB para quase 150MB.
3. **Carregamento antecipado e execução incondicional do `reportlab`**: O motor de geração de PDF era importado globalmente no `data_manager.py` e gerava os bytes do documento a cada render da página de relatórios, alocando canvas e métricas de fontes mesmo sem intenção de download do usuário.
4. **Monitoramento de arquivos desnecessário (`fileWatcherType`)**: O Streamlit em container mantinha threads de inotify/watchdog ativas para monitorar alterações de código estático.
5. **Mapeamento de arquivos WAL do SQLite**: O arquivo `churrascontrol.db-wal` crescia sem checkpoints compactadores frequentes, retendo páginas no Page Cache do container Linux.
6. **Retenção de memória glibc/Python**: Ausência de diretivas para o alocador C retornar blocos liberados de volta ao sistema operacional (`MALLOC_TRIM_THRESHOLD_`).

## 2. Objetivos
- Reduzir o footprint de RAM da aplicação para o patamar de **65 MB a 75 MB** em todas as telas, inclusive na aba de Relatórios.
- Eliminar integralmente as dependências de `pandas` e `altair` do projeto e do `requirements.txt`.
- Renderizar gráficos analíticos e tabelas executivas em SVG puro e HTML/CSS nativo com custo zero de memória de servidor.
- Adotar **Lazy Loading** estrito para o `reportlab` e geração de PDF sob demanda (apenas ao clicar no botão).
- Eliminar o overhead de recriação de módulos e classes Python a cada interação (`importlib.reload`).
- Estabelecer autocheckpoint e controle estrito de cache de páginas do SQLite.

## 3. Escopo da Mudança
- **Dentro do escopo**:
  - Remoção de `pandas` e `altair` do código e exclusão do `pandas` em `requirements.txt`.
  - Implementação de renderizadores nativos em SVG para a evolução temporal de faturamento e barras HTML/CSS para mix por categoria.
  - Implementação de tabelas nativas de ranking de produtos e auditoria de comandas sem necessidade de DataFrames.
  - Conversão do `reportlab` em módulo estritamente *lazy-loaded* dentro da função `gerar_pdf_bytes()` e fluxo de geração de PDF sob clique em `3_Relatorios.py`.
  - Remoção de `importlib.reload` em `app.py` e em todas as páginas de `pages/`.
  - Configuração de produção no `.streamlit/config.toml` (`fileWatcherType = "none"`, `headless = true`, `maxUploadSize = 10`, `toolbarMode = "minimal"`).
  - Idempotência na inicialização do banco (`init_db`) e ajuste de PRAGMAs do SQLite (`wal_autocheckpoint = 250`, `cache_size = -2000`, checkpoint periódico no worker).
  - Ajuste no orquestrador `run.py` para forçar desalocação de memória ao SO (`MALLOC_TRIM_THRESHOLD_`).
  - Execução e validação da bateria de testes automatizados com 100% de sucesso.
- **Fora do escopo**:
  - Migração de framework frontend (Streamlit permanece como tecnologia exclusiva de frontend).
  - Alterações nos contratos de rotas ou payloads do Xano.

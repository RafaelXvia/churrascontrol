# Lista de Tarefas — Saneamento de Arquivos Órfãos e Reestruturação Modular

## 1. Auditoria e Saneamento de Arquivos Órfãos e Caches

- [x] 1.1 Remover com segurança o banco transitório residual `churrascontrol_teste.db` localizado na raiz do projeto.
- [x] 1.2 Limpar recursivamente arquivos `.pyc` compilados de interpretadores antigos em `pages/__pycache__/` e `tools/__pycache__/`.
- [x] 1.3 Atualizar `.gitignore` para ignorar explicitamente:
  - `*_teste.db` e `*_test.db`
  - `*.db-shm` e `*.db-wal` (journals do SQLite WAL)
  - `temp/` e `tmp/`
  - `.env` e variações locais
- [x] 1.4 Atualizar `.discloudignore` para garantir que artefatos de teste, documentação OpenSpec interna e backups não aumentem o tempo de build e a retenção de memória do contêiner.

## 2. Isolamento Efêmero do Banco de Dados de Teste

- [x] 2.1 Refatorar `tools/run_all.py` para apontar `CHURRAS_DB_PATH` para um arquivo temporário em `tempfile.gettempdir()`.
- [x] 2.2 Adicionar rotina de limpeza no encerramento de `tools/test_suite.py` que garanta a deleção atômica do banco temporário após o término das asserções.
- [x] 2.3 Validar que a execução de `python tools/run_all.py` não cria novos arquivos `.db` na raiz do projeto.

## 3. Criação da Estrutura Modular (Backend & Frontend)

- [x] 3.1 Criar a pasta `backend/` com subpacotes:
  - `backend/database/` (para `data_manager.py`)
  - `backend/ai/` (para `ontologia.py` e `assistente_ia.py`)
  - `backend/xano/` (migrando a pasta `xano/` com tabelas e endpoints `.xs`)
  - `backend/backups/` (migrando a pasta `backups/`)
- [x] 3.2 Criar a pasta `frontend/` com subpacotes:
  - `frontend/components/` (para `ui_components.py`)
- [x] 3.3 Adicionar arquivos `__init__.py` nos novos pacotes com exportações limpas de classes e funções públicas.

## 4. Fachadas de Retrocompatibilidade e Atualização de Configurações

- [x] 4.1 Criar fachadas transparentes na raiz para `data_manager.py`, `ontologia.py`, `assistente_ia.py` e `ui_components.py` apontando para os novos módulos em `backend/` e `frontend/`.
- [x] 4.2 Atualizar `.vscode/mcp.json` e `.gemini/settings.json` para que o Xano Developer MCP reconheça o novo caminho `backend/xano/`.
- [x] 4.3 Testar inicialização local via `streamlit run app.py` e `python run.py` (porta 8080) assegurando que a navegação do Streamlit permaneça 100% funcional.

## 5. Validação Executiva de Qualidade

- [x] 5.1 Executar a suíte completa de testes unificada:
  ```bash
  python tools/run_all.py
  ```
- [x] 5.2 Executar o diagnóstico de integridade do banco:
  ```bash
  python tools/db_diagnostics.py
  ```
- [x] 5.3 Confirmar que todas as 8 páginas do Streamlit carregam sem erro de importação.

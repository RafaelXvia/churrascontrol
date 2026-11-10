# arquitetura-modular Specification

## Purpose
Estabelecer a segregação de responsabilidades entre Backend (persistência relacional SQLite, IA generativa RAG e esquemas Xano) e Frontend (componentes visuais e telas Streamlit), mantendo 100% de retrocompatibilidade através de fachadas na raiz do projeto.

## Requirements

### Requirement: Estrutura Modular de Pacotes
O sistema SHALL organizar o código em pacotes coesos:
- `backend/database/`: Persistência relacional transacional SQLite e fila de sincronização Xano.
- `backend/ai/`: Ontologia de domínio, representação semântica e motor analítico de RAG com Google Gemini.
- `backend/xano/`: Schemas de tabelas e endpoints em XanoScript (`.xs`).
- `backend/backups/`: Dumps SQL e JSON de contingência.
- `frontend/components/`: Navbar, controle de acesso RBAC, modais e componentes visuais.
- `pages/`: Telas operacionais multi-page nativas do Streamlit.

### Requirement: Fachadas de Retrocompatibilidade na Raiz
O sistema SHALL manter módulos de fachada transparentes na raiz do projeto para `data_manager.py`, `ontologia.py`, `assistente_ia.py` e `ui_components.py`, garantindo que scripts legados, orquestradores e testes continuem importando sem quebra de retrocompatibilidade.

### Requirement: Isolamento Efêmero do Banco de Testes
A execução de baterias de testes via `tools/run_all.py` ou `tools/test_suite.py` SHALL utilizar banco de dados temporário em `tempfile.gettempdir()`, excluído atômica e automaticamente após a conclusão das asserções, prevenindo a criação de arquivos residuais `.db` na raiz do repositório.

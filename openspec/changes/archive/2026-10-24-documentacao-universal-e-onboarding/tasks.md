# Lista de Tarefas — Documentação Universal e Onboarding

## 1. Elaboração do README.md Principal na Raiz

- [x] 1.1 Criar o arquivo `README.md` na raiz do projeto com cabeçalho profissional, badges de tecnologias e resumo executivo do sistema ChurrasControl.
- [x] 1.2 Incluir diagrama conceitual em ASCII da arquitetura (Frontend Streamlit -> SQLite WAL -> Xano Sync e RAG Gemini).
- [x] 1.3 Adicionar seção de **Guia Rápido de Instalação (Zero ao Deploy)** com instruções agnósticas multiplataforma (Windows PowerShell/CMD e Linux/macOS):
  - Clone do repositório
  - Criação e ativação de ambiente virtual (`venv`)
  - Instalação limpa de dependências (`pip install -r requirements.txt`)
  - Criação do `.env` a partir de `.env.example`
- [x] 1.4 Adicionar tabela de **Credenciais de Acesso e Perfis Operacionais**:
  - Gerente: `gerente@churrascontrol.com` / `1q2w`
  - Caixa: `joao@churrascontrol.com` / `1q2w`
  - Chave Mestra de Contingência: `CHURRAS-REC-2026` / `ADMIN123`
- [x] 1.5 Documentar os comandos de execução local:
  - `streamlit run app.py` (porta 8080 definida no `.streamlit/config.toml` ou 8501)
  - `python run.py` (execução containerizada Discloud)
- [x] 1.6 Incluir instruções para execução da suíte de testes (`python tools/run_all.py`) e diagnóstico do banco (`python tools/db_diagnostics.py`).
- [x] 1.7 Adicionar seção de deploy na nuvem Discloud explicando `discloud.config` e `.discloudignore`.

## 2. Universalização e Saneamento dos Arquivos em `docs/` e `AGENTS.md`

- [x] 2.1 Auditar `docs/project-overview.md` e substituir referências fixas a diretórios locais por referências agnósticas à raiz do projeto.
- [x] 2.2 Auditar `docs/mcp-xano.md` garantindo que o passo a passo de configuração do Xano Developer MCP seja 100% universal.
- [x] 2.3 Auditar `AGENTS.md` para garantir clareza universal nas instruções para novos desenvolvedores e agentes de IA.

## 3. Revisão de Links e Validação Markdown

- [x] 3.1 Verificar todos os links internos de markdown no `README.md` e em `docs/` assegurando que nenhum aponte para caminhos absolutos com letras de disco.
- [x] 3.2 Validar renderização e formatação da tabela de APIs e credenciais.

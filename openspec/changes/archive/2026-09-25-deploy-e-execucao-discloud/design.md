## Context

A Discloud é uma plataforma PaaS baseada em containers Linux que executa aplicações persistentes a partir de um arquivo `MAIN` especificado em `discloud.config`. Como o Streamlit é tradicionalmente executado via comando de terminal (`streamlit run app.py`), faz-se necessário um script Python intermediário (`run.py`) que sirva de orquestrador para o container, garantindo parâmetros de porta, host e reinicialização automática em caso de oscilações.

## Goals / Non-Goals

**Goals:**
- Configurar o manifesto `discloud.config` com limites adequados de RAM (512MB) e autorestart.
- Criar o wrapper `run.py` para disparar o Streamlit em modo headless nas portas exigidas pelo roteamento da Discloud.
- Minimizar o tamanho do pacote através do `.discloudignore`.
- Garantir que a aplicação suba sem intervenção manual.

**Non-Goals:**
- Implementar pipeline de CI/CD automatizado via GitHub Actions neste momento (deploy realizado via CLI/Upload zip).
- Configurar banco de dados externo adicional (o container consome o JSON local com worker em segundo plano para o Xano).

## Decisions

- **Decisão 1: Execução do Streamlit via Subprocesso em `run.py`**:
  - *Contexto*: A Discloud espera um processo Python de longa duração executado via `python run.py`.
  - *Decisão*: Invocar `sys.executable -m streamlit run app.py` com flags `--server.port 8080 --server.address 0.0.0.0 --server.headless true`.
- **Decisão 2: Uso de `.discloudignore` Robusto**:
  - *Contexto*: Pastas de documentação pesadas e arquivos zip locais consom quota de disco e atrasam o upload.
  - *Decisão*: Descartar pastas auxiliares mantendo apenas código-fonte, dados locais e dependências essenciais.

## Risks / Trade-offs

- [Limite de 512MB de RAM na Discloud Free] O Streamlit e as bibliotecas gráficas poderiam consumir memória excessiva → Mitigação: O `run.py` opera enxuto, sem carregar módulos desnecessários na thread pai, e as gerações de PDF são liberadas de memória imediatamente após o download.

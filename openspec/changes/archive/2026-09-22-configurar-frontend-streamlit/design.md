## Context

O projeto ChurrasControl possuía originalmente seu frontend estruturado em templates HTML Jinja2 com Tailwind CSS acoplados ao FastAPI (`templates/`). Conforme os requisitos da disciplina e o material pedagógico (Apêndice A), o frontend deve ser desacoplado e migrado para Streamlit.

## Goals / Non-Goals

**Goals:**
- Configurar o ambiente para suporte pleno ao Streamlit mantendo compatibilidade com as APIs FastAPI.
- Criar a aplicação base (`app.py`) e componentes visuais essenciais para verificação da arquitetura.
- Atualizar todos os artefatos de contexto e governança de agentes (`docs/project-overview.md`, `AGENTS.md` e `openspec/config.yaml`).
- Disponibilizar mecanismo automatizado de teste e verificação de ambiente (`test_streamlit_env.py`).

**Non-Goals:**
- Remover imediatamente os arquivos em `templates/` (eles serão descontinuados incrementalmente à medida que as páginas Streamlit forem implementadas em changes subsequentes).
- Alterar as rotas da API REST em `main.py` ou os modelos de dados no Xano.

## Decisions

- **Decisão 1: Manter FastAPI como Backend de Serviços e Streamlit como Frontend Desacoplado**:
  - *Alternativa considerada*: Reescrever todo o backend dentro de callbacks de Streamlit.
  - *Motivação*: Manter a API REST desacoplada permite reuso de validações, geração de PDF via ReportLab e background worker do Xano sem sobrecarregar o ciclo de re-execução (rerun) do Streamlit.
- **Decisão 2: Script de Validação Automatizado**:
  - *Motivação*: Atender ao requisito explícito de teste/verificação pré-archive utilizando um teste funcional que confere a importação e compatibilidade do Streamlit e bibliotecas chave.

## Risks / Trade-offs

- [Execução Simultânea] O operador precisará executar o backend FastAPI e o frontend Streamlit (em portas distintas, ex: 8080 e 8501) → Mitigação: Documentar comandos de inicialização e criar rotina de fallback no app Streamlit para alertar caso a API esteja offline.
- [Rate Limit Xano] Reruns frequentes do Streamlit poderiam esgotar a cota gratuita do Xano → Mitigação: O FastAPI continua centralizando a fila assíncrona com delay de 2.2s, isolando o Streamlit de bater diretamente no Xano sem controle.

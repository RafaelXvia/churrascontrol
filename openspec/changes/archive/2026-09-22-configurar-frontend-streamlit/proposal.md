## Why

Alinhamento com as diretrizes da disciplina Innovation Lab Advanced No/Low Code (Faculdade Impacta), que estabelece o Streamlit como tecnologia obrigatória e exclusiva para desenvolvimento do frontend do projeto integrador. Esta mudança define a infraestrutura inicial de frontend em Streamlit, registra a decisão arquitetural na governança do projeto e prepara a base para a migração visual das operações de mesas, cardápio e relatórios.

## What Changes

- **Governança e Contexto**: Atualização de `docs/project-overview.md`, `AGENTS.md` e `openspec/config.yaml` registrando o Streamlit como tecnologia obrigatória e exclusiva de frontend.
- **Dependências**: Adição de `streamlit` ao `requirements.txt`.
- **Estrutura Base**: Criação do ponto de entrada inicial do frontend (`app.py`) com layout responsivo e configuração base.
- **Validação e Testes**: Criação e execução de rotina de teste e verificação automatizada para garantir que as dependências, importações e o servidor Streamlit estejam operacionais.
- **Fora do Escopo**: Não inclui a recriação imediata de todas as telas em produção nem a remoção do backend FastAPI existente (que atuará como provedor de API para o frontend).

## Capabilities

### New Capabilities
- `frontend-streamlit`: Base da aplicação web em Streamlit para o ChurrasControl, definindo o ponto de entrada principal e preparação para as telas de salão, cardápio e relatórios.

### Modified Capabilities
<!-- Nenhuma especificação consolidada prévia existe ainda em openspec/specs/ -->

## Impact

- `requirements.txt`: Inclusão da biblioteca `streamlit`.
- `app.py`: Novo arquivo principal da interface web Streamlit.
- `docs/project-overview.md`, `AGENTS.md`, `openspec/config.yaml`: Atualização de regras operacionais e arquitetura de frontend.

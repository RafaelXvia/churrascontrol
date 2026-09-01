## Context

Após a configuração inicial do Streamlit e governança OpenSpec, as telas operacionais do ChurrasControl precisam ser materializadas no padrão multipage do Streamlit (`pages/`). O backend FastAPI (`main.py`) na porta 8080 expõe endpoints REST padronizados para mesas, comandas, produtos e relatórios.

## Goals / Non-Goals

**Goals:**
- Implementar as 3 páginas completas no diretório `pages/`:
  - `pages/1_🥩_Salão_e_Mesas.py`: Gestão de mesas e comandas.
  - `pages/2_📋_Cardapio.py`: Gestão de produtos.
  - `pages/3_📊_Relatorios.py`: Dashboards e download de PDF.
- Consumir a API FastAPI via chamadas HTTP (`httpx`), com tratamento de exceções amigável caso a API esteja offline.
- Validar a compilação e integridade de todas as páginas criadas através de script de teste.

**Non-Goals:**
- Não alterar as regras de negócio ou estrutura do banco no backend FastAPI.
- Não depender de componentes pesados de terceiros, priorizando componentes nativos do Streamlit.

## Decisions

- **Decisão 1: Utilizar Arquitetura Multipage Nativa do Streamlit**:
  - *Motivação*: O Streamlit reconhece automaticamente qualquer script Python colocado dentro da pasta `pages/` e renderiza a navegação na barra lateral sem a necessidade de roteadores manuais.
- **Decisão 2: Integração com Backend via `httpx`**:
  - *Motivação*: `httpx` já é dependência do projeto e permite realizar requisições síncronas simples dentro do fluxo de renderização do Streamlit, isolando o estado da interface da camada de persistência.

## Risks / Trade-offs

- [Estado de Sessão / Rerun] O Streamlit reexecuta o script a cada interação do usuário → Mitigação: Utilizar `st.session_state` para memorizar a mesa selecionada e os filtros aplicados entre os reruns.

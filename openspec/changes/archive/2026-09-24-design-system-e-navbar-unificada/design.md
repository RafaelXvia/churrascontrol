## Context

Aplicações de PDV gastronômico exigem foco estrito no conteúdo e navegação de um toque (one-tap). O menu lateral padrão do Streamlit exige abrir/fechar gavetas ou rouba 25% da largura horizontal da tela, prejudicando a visualização simultânea do salão de mesas e do painel lateral de comandas. A substituição por uma barra superior fixa resolve este problema ergonômico.

## Goals / Non-Goals

**Goals:**
- Ocultar 100% dos elementos nativos de sidebar do Streamlit sem falhas de layout.
- Construir uma Top Navbar moderna com efeito translúcido (glassmorphism: `backdrop-filter: blur(16px)`).
- Navegar instantaneamente entre telas utilizando `st.switch_page`.
- Padronizar fontes, paleta e espaçamentos através de uma única chamada `ui_components.render_navbar(active_tab)`.

**Non-Goals:**
- Utilizar bibliotecas externas pesadas de componentes React para Streamlit (como streamlit-elements ou streamlit-antd).
- Alterar as regras de negócio de manipulação de dados em `data_manager.py`.

## Decisions

- **Decisão 1: Navegação via `st.switch_page` na Navbar**:
  - *Contexto*: Garantir que o clique nos botões da navbar superior troque a página instantaneamente mantendo o estado de sessão.
  - *Decisão*: Utilizar os botões do Streamlit acoplados a `st.switch_page("app.py")` ou `st.switch_page("pages/...")`.
- **Decisão 2: Injeção CSS com !important em `ui_components.py`**:
  - *Contexto*: O Streamlit aplica estilos dinâmicos de tema que frequentemente sobrepõem regras simples de CSS.
  - *Decisão*: Usar seletores específicos com `!important` para supressão da sidebar e estilização do container principal.

## Risks / Trade-offs

- [Flicker de Carregamento da Sidebar] Em conexões mais lentas, a sidebar poderia piscar brevemente antes do CSS ser avaliado → Mitigação: Configurar `initial_sidebar_state="collapsed"` nas chamadas de `st.set_page_config` em todas as páginas.

## Why

A experiência de usuário padrão do Streamlit apresenta uma barra lateral expansível (sidebar) que desvia a atenção da operação do salão e consome largura útil em telas de PDV e tablets. Além disso, a navegação nativa de páginas fragmenta a identidade visual da aplicação. Para alcançar excelência visual e foco operacional, é necessário unificar o sistema de design em `ui_components.py`, implementar uma barra de navegação superior (Top Navbar) com efeito glassmorphism, suprimir completamente a sidebar nativa e fornecer feedback tátil/visual imediato nas seleções de mesa.

## What Changes

- **Centralização do Design System em `ui_components.py`**:
  - Injeção global de CSS (`inject_custom_theme`) com a tipografia 'Plus Jakarta Sans', paleta Obsidian escuro (`#080c14`), contenção responsiva de largura máxima (1440px) e estilização refinada de containers.
  - Supressão agressiva e total da barra lateral nativa do Streamlit (`[data-testid="stSidebar"]`, `[data-testid="collapsedControl"]`, botões de recolhimento e cabeçalhos padrão) em todas as páginas.
- **Top Navbar Unificada com Efeito Glassmorphism**:
  - Componente `render_navbar(active_tab)` renderizando no topo das páginas a identidade do restaurante ("🥩 CHURRASCONTROL POS") e botões de atalho: "📊 Painel Geral", "🍽️ Salão & Mesas", "📋 Cardápio" e "📈 Relatórios".
  - Transições suaves e roteamento transparente entre páginas através da API nativa `st.switch_page`.
  - Destaque luminoso e borda temática na aba atualmente ativa, sem exibição de badges redundantes.
- **Interatividade Visual em Mesas e Rodapé**:
  - Estilização de cards de mesas ativas com indicação tátil de seleção (`cc-mesa-card-active`), realce em borda âmbar (`#f59e0b`) e sombra difusa.
  - Implementação de `render_footer()` com créditos institucionais, status operacional e alinhamento visual de encerramento da página.

## Capabilities

### New Capabilities
- `design-system-e-navbar-unificada`: Sistema de design exclusivo do ChurrasControl com Top Navbar glassmorphism, supressão de sidebar nativa e componentes visuais corporativos de alta fidelidade.

### Modified Capabilities

## Impact

- `ui_components.py`: Módulo central de componentes e estilos visuais do projeto.
- `app.py`, `pages/1_Salao_e_Mesas.py`, `pages/2_Cardapio.py`, `pages/3_Relatorios.py`: Integração da Top Navbar e supressão visual de menus laterais.

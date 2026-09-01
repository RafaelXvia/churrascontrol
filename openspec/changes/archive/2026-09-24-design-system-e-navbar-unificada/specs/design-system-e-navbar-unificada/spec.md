# design-system-e-navbar-unificada Specification

## Purpose
Estabelecer um sistema de design de alta fidelidade visual para o ChurrasControl em `ui_components.py`, fornecendo Top Navbar unificada com efeito glassmorphism, supressão integral da barra lateral nativa do Streamlit e componentes visuais com feedback interativo.

## Requirements

### Requirement: Top Navbar com Efeito Glassmorphism e Roteamento
O sistema SHALL disponibilizar `render_navbar(active_tab)` que renderiza a barra superior fixa contendo o logotipo âmbar, o título institucional e 4 botões de navegação ("📊 Painel Geral", "🍽️ Salão & Mesas", "📋 Cardápio", "📈 Relatórios"), acionando a transição de telas via `st.switch_page`.

#### Scenario: Transição de página pelo menu superior
- **WHEN** o operador clica no botão correspondente a outra tela na barra de navegação
- **THEN** a aplicação SHALL executar `st.switch_page` carregando imediatamente a respectiva rota sem depender de links HTML externos.

### Requirement: Supressão Total da Barra Lateral Nativa
O sistema SHALL injetar regras de estilo em `inject_custom_theme()` que forçam `display: none !important` sobre os seletores de sidebar do Streamlit (`[data-testid="stSidebar"]`, `[data-testid="collapsedControl"]` e `header[data-testid="stHeader"]`), garantindo que o salão e as tabelas ocupem 100% da área útil da viewport.

#### Scenario: Carregamento de qualquer página do sistema
- **WHEN** uma página do ChurrasControl for aberta pelo navegador
- **THEN** a barra lateral nativa do Streamlit SHALL permanecer invisível e inacessível, impedindo distração visual.

### Requirement: Estilização Interativa de Cards e Rodapé
O sistema SHALL prover classes CSS para cards operacionais (`cc-mesa-card`, `cc-card`) com micro-animações no hover, além de `render_footer()` contendo rodapé corporativo padronizado com informações da plataforma.

#### Scenario: Seleção visual de mesa no salão
- **WHEN** o usuário seleciona uma mesa ativa
- **THEN** o card da mesa SHALL aplicar a classe `cc-mesa-card-active` exibindo borda âmbar luminosa e indicador de seleção ativo.

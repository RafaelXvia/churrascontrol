## 1. Módulo Central de Design System

- [x] 1.1 Criar o arquivo `ui_components.py` implementando a função `inject_custom_theme()`.
- [x] 1.2 Inserir regras CSS para importação da tipografia 'Plus Jakarta Sans' e paleta Obsidian/Slate.
- [x] 1.3 Implementar seletores de ocultação completa da sidebar nativa do Streamlit (`[data-testid="stSidebar"]`).

## 2. Top Navbar e Rodapé Institucional

- [x] 2.1 Desenvolver o componente `render_navbar(active_tab)` com efeito translúcido (glassmorphism).
- [x] 2.2 Integrar navegação nativa via `st.switch_page` para os quatro módulos da aplicação.
- [x] 2.3 Implementar o componente `render_footer()` padronizando o rodapé em todas as telas.

## 3. Integração e Validação

- [x] 3.1 Integrar `ui_components.render_navbar` e `render_footer` em `app.py` e em todas as páginas de `pages/`.
- [x] 3.2 Validar que a alternância entre abas preserva a estética visual e o estado de seleção da sessão.

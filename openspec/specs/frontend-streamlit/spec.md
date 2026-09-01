# frontend-streamlit Specification

## Purpose
Prover uma interface web moderna, interativa e de alta performance construída em Streamlit para o sistema ChurrasControl, utilizando sistema de design executivo, navegação integrada por barra superior e consumo direto de dados locais com resposta instantânea.

## Requirements

### Requirement: Ponto de entrada web Streamlit
O sistema SHALL disponibilizar uma aplicação Streamlit inicializável via `streamlit run app.py` configurada em layout `wide`, com sidebar colapsada, título "ChurrasControl - Painel Operacional" e ícone temático de corte gastronômico ("🥩").

#### Scenario: Execução da aplicação
- **WHEN** o operador executa `streamlit run app.py`
- **THEN** o servidor Streamlit inicializa renderizando o Painel Geral com KPIs consolidados (Mesas Ocupadas, Consumo em Aberto, Faturamento 7D, Itens no Cardápio) e grade de módulos navegáveis.

### Requirement: Barra de Navegação Superior Integrada (Top Navbar)
O sistema SHALL fornecer através de `ui_components.render_navbar(active_tab)` uma barra de navegação superior unificada exibindo a marca ("🥩 CHURRASCONTROL POS") e os 4 botões de navegação das áreas operacionais: "📊 Painel Geral", "🍽️ Salão & Mesas", "📋 Cardápio" e "📈 Relatórios". A barra SHALL NÃO conter pílulas ou badges redundantes de status (como "MODO LOCAL").

#### Scenario: Navegação entre páginas via barra superior
- **WHEN** o operador clica em qualquer uma das opções da barra de navegação
- **THEN** a aplicação realiza a troca de tela via `st.switch_page` destacando a aba ativa com estilo primário luminoso e mantendo a barra de navegação no topo de todas as páginas.

### Requirement: Design System e Componentes Centralizados
O sistema SHALL centralizar estilos CSS customizados e componentes em `ui_components.py`, injetando tokens de design escuro executivo (gradientes em tons Obsidian e Slate, bordas sutis e tipografia moderna), eliminando barras laterais nativas e fornecendo rodapé institucional elegante.

#### Scenario: Injeção de tema e layout
- **WHEN** qualquer página da aplicação é carregada
- **THEN** a função `inject_custom_theme()` é executada, aplicando classes utilitárias, tipografia aprimorada, transições suaves de hover e removendo padding excessivo do container padrão do Streamlit.

### Requirement: Registro de governança tecnológica
O projeto SHALL registrar em sua documentação e regras operacionais (`AGENTS.md`, `project-overview.md` e `config.yaml`) o Streamlit como frontend oficial e exclusivo.

#### Scenario: Consulta das diretrizes de desenvolvimento
- **WHEN** um desenvolvedor ou agente de IA consulta a documentação do projeto
- **THEN** as diretrizes indicam claramente o Streamlit como padrão obrigatório de frontend, proibindo a introdução de frameworks divergentes sem aprovação prévia.

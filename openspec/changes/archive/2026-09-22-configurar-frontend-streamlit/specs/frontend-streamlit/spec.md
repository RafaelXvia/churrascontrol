## Purpose

Prover uma interface web moderna, interativa e responsiva construída em Streamlit para visualização e operação do sistema ChurrasControl, consumindo os serviços da aplicação.

## ADDED Requirements

### Requirement: Ponto de entrada web Streamlit
O sistema SHALL disponibilizar uma aplicação Streamlit inicializável via `streamlit run app.py` configurada com título, ícone de página e layout responsivo.

#### Scenario: Execução com sucesso da aplicação
- **WHEN** o operador executa `streamlit run app.py`
- **THEN** o servidor Streamlit inicia sem erros e renderiza a tela principal com o título "ChurrasControl" e status de conexão operacional.

### Requirement: Registro de governança tecnológica
O projeto SHALL registrar em sua documentação e regras operacionais (`AGENTS.md`, `project-overview.md` e `config.yaml`) o Streamlit como frontend oficial e exclusivo.

#### Scenario: Consulta das diretrizes de desenvolvimento
- **WHEN** um desenvolvedor ou agente de IA consulta a documentação do projeto
- **THEN** as diretrizes indicam claramente o Streamlit como padrão obrigatório de frontend, proibindo a introdução de frameworks divergentes sem aprovação prévia.

### Requirement: Procedimento de verificação e testes do ambiente
O sistema SHALL fornecer um script ou comando de validação para verificar a presença de dependências, integridade de importação e integridade do ambiente antes do arquivamento da mudança.

#### Scenario: Execução do script de verificação
- **WHEN** o comando de teste de ambiente é acionado
- **THEN** o script valida as importações do Streamlit e dependências essenciais retornando código de sucesso 0.

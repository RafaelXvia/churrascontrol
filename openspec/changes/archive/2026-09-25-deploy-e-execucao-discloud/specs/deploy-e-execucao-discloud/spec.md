# deploy-e-execucao-discloud Specification

## Purpose
Estabelecer a infraestrutura de publicação e orquestração de deploy contínuo em nuvem para o ChurrasControl na plataforma Discloud, garantindo escalabilidade, binding de portas e monitoramento de saúde do processo.

## Requirements

### Requirement: Manifesto de Configuração Discloud
O sistema SHALL disponibilizar `discloud.config` contendo os parâmetros de infraestrutura: `ID=churrascontrol`, `TYPE=bot`, `MAIN=run.py`, `RAM=512`, `AUTORESTART=true` e `VERSION=latest`.

#### Scenario: Leitura do manifesto pela plataforma
- **WHEN** o pacote zip da aplicação for carregado na Discloud
- **THEN** a plataforma SHALL provisionar o container com 512MB de memória alocada e disparar `run.py` como processo mestre.

### Requirement: Orquestrador de Inicialização `run.py`
O sistema SHALL fornecer `run.py` responsável por invocar o Streamlit via `subprocess` com os argumentos `--server.port 8080`, `--server.address 0.0.0.0`, `--server.headless true` e `--browser.serverAddress 0.0.0.0`, redirecionando saídas padrão e monitorando o código de saída.

#### Scenario: Inicialização do serviço em produção
- **WHEN** o container Discloud executa `python run.py`
- **THEN** o servidor Streamlit SHALL escutar na porta 8080 permitindo tráfego web público através do roteamento da nuvem.

### Requirement: Otimização de Empacotamento com `.discloudignore`
O sistema SHALL fornecer `.discloudignore` contendo regras de exclusão para `.git`, `openspec`, `__pycache__`, `.gemini`, `test_*.py` e arquivos compactados `.zip`.

#### Scenario: Empacotamento para upload
- **WHEN** a ferramenta de deploy compacta a raiz da aplicação
- **THEN** arquivos de especificação, artefatos temporários e caches SHALL ser ignorados, gerando um pacote leve para deploy imediato.

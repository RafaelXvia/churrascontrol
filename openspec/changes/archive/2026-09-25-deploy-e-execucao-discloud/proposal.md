## Why

Para disponibilizar o ChurrasControl em ambiente de produção acessível pela equipe do restaurante e para avaliação acadêmica, a aplicação deve ser hospedada em nuvem na plataforma Discloud. É necessário configurar os descritores de infraestrutura, estabelecer o script de inicialização do processo em modo headless e configurar filtros de exclusão de artefatos desnecessários para otimizar o tempo de upload e o uso de memória.

## What Changes

- **Configuração da Aplicação na Discloud (`discloud.config`)**:
  - Definição do ID único do container (`churrascontrol`), tipo de processo (`bot`), script principal (`run.py`), alocação de memória RAM (512MB), autorestart automático e versão de runtime `latest`.
- **Script Orquestrador de Inicialização (`run.py`)**:
  - Inicialização do servidor Streamlit via subprocesso Python em modo headless (`--server.headless true`), expondo na interface de rede global (`--server.address 0.0.0.0`) e porta configurada para a porta padrão Discloud (`--server.port 8080`), com monitoramento contínuo de integridade do processo.
- **Filtragem de Artefatos de Deploy (`.discloudignore`)**:
  - Exclusão explícita de diretórios de controle de versão (`.git/`), histórico OpenSpec (`openspec/`), caches locais (`__pycache__/`, `.gemini/`), ambientes virtuais e arquivos compactados (`*.zip`), reduzindo expressivamente o payload de upload.
- **Tratamento de Compatibilidade no Windows (`app.py`)**:
  - Inclusão de rotina protetora em `app.py` que intercepta e suprime de forma segura a exceção inofensiva do `ProactorBasePipeTransport._call_connection_lost` específica de encerramento de conexões no Windows.

## Capabilities

### New Capabilities
- `deploy-e-execucao-discloud`: Infraestrutura de empacotamento, orquestração e execução contínua da aplicação em ambiente de nuvem na plataforma Discloud.

### Modified Capabilities

## Impact

- `discloud.config`: Arquivo de manifesto e dimensionamento de recursos na Discloud.
- `run.py`: Ponto de entrada operacional do container.
- `.discloudignore`: Regras de otimização de empacotamento.
- `app.py`: Resiliência de transporte de sockets de rede.

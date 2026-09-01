## Why

Atualmente, o sistema utiliza o arquivo `churras_data.json` como camada de persistência local para mitigar o Rate Limit do plano gratuito do Xano e manter a fluidez do Streamlit. Contudo, arquivos JSON planos possuem fragilidades estruturais: risco de corrupção em caso de crash durante gravação, bloqueio manual frágil por mutex e perda da fila de eventos em memória se a aplicação for reiniciada. 
Esta mudança substitui o armazenamento JSON por um banco de dados local transacional **SQLite (`churrascontrol.db`)**, mantendo a arquitetura **Local-First com Atualização Otimista (Optimistic UI)**: as operações do operador de caixa e garçom são gravadas instantaneamente no banco local (0-2ms) garantindo resposta visual em tempo real, enquanto uma tabela de fila persistente no próprio SQLite despacha os eventos críticos de forma assíncrona e ordenada para o Xano respeitando os limites da API.

## What Changes

- **Substituição de Persistência (`data_manager.py`)**:
  - Migração de `churras_data.json` para banco relacional embutido SQLite (`churrascontrol.db`) com ativação do modo WAL (*Write-Ahead Logging*) para suporte seguro a concorrência.
  - Criação das tabelas relacionais locais: `mesas`, `produtos`, `comandas`, `itens_comanda` e `fila_sincronizacao`.
  - Migração transparente dos dados existentes de `churras_data.json` para o SQLite na primeira inicialização.
- **Fila Persistente e Resiliente de Sincronização Xano**:
  - Criação da tabela `fila_sincronizacao` no SQLite para gerenciar itens pendentes de envio (`PENDENTE`, `ENVIADO`, `ERRO`).
  - Worker em thread desacoplada consumindo a fila persistente com intervalo de segurança (rate limit) de 2.5s por requisição.
  - Garantia de que reinicializações do servidor ou oscilações de rede não percam transações.
- **Preservação Integral dos Contratos de Interface**:
  - Todas as funções públicas de `data_manager.py` (`listar_mesas`, `abrir_mesa`, `obter_comanda_detalhes`, `adicionar_item_comanda`, `fechar_comanda`, `listar_produtos`, etc.) mantêm rigorosamente os mesmos parâmetros e retornos para não quebrar `app.py` nem as telas em `pages/`.
- **Rotina de Inicialização / Sincronização**:
  - Função de bootstrap que verifica a integridade do SQLite e inicializa o schema automaticamente.

## Capabilities

### New Capabilities
- `persistencia-sqlite-e-sync-persistente`: Persistência local relacional em SQLite com atualizações otimistas e fila de sincronização Xano em disco.

### Modified Capabilities
- `performance-e-design-streamlit`: Camada de dados agora opera sobre SQLite transacional em vez de arquivo JSON plano.

## Impact

- `data_manager.py`: Substituição do motor de manipulação de JSON por consultas SQL parametrizadas e gerenciador de conexões SQLite.
- `churras_data.json`: Depreciado como armazenamento ativo; mantido apenas para migração inicial única.
- `churrascontrol.db`: Novo arquivo de banco local criado automaticamente.
- Frontend (`app.py`, `pages/`): Não sofre quebras de contrato; mantém resposta visual instantânea.

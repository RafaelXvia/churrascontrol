## Why

O frontend Streamlit anterior apresentava lentidão perceptível devido a requisições HTTP repetitivas ao servidor local a cada interação, além de carregar recursos externos lentos e apresentar um design poluído por emojis. Esta mudança estabelece leitura e gravação imediatas em `churras_data.json`, sincronização seletiva com Xano apenas em eventos críticos com controle de rate limit, e um redesign executivo completo de alta fidelidade visual sem emojis.

## What Changes

- **Camada de Dados de Alta Performance (`data_manager.py`)**:
  - Leitura e gravação diretas em `churras_data.json` garantindo resposta instantânea (latência zero no frontend).
  - Fila desacoplada em thread de background com rate limit (delay de 2.5s) para despachar dados ao Xano exclusivamente em eventos essenciais (fechamento de comanda/pagamento e alterações estruturais de itens).
- **Redesign Executivo e Remoção de Emojis**:
  - Eliminação completa de todos os emojis em títulos, botões, métricas e nomes de arquivos.
  - Renomeação dos arquivos para: `pages/1_Salao_e_Mesas.py`, `pages/2_Cardapio.py`, `pages/3_Relatorios.py`.
  - Configuração de tema escuro premium em `.streamlit/config.toml` (paleta Obsidian `#0B0F17`, Slate `#1E293B`, Amber `#D97706`).
  - Remoção de dependências de imagens externas lentas no `app.py`.
- **Testes e Verificação**:
  - Atualização dos scripts de teste automatizado garantindo compilação e validação do fluxo local.

## Capabilities

### New Capabilities
- `performance-e-design-streamlit`: Camada de persistência local direta de alta velocidade com sincronização seletiva e interface executiva sóbria.

### Modified Capabilities

## Impact

- `data_manager.py`: Módulo central de dados e background worker Xano.
- `app.py`, `pages/1_Salao_e_Mesas.py`, `pages/2_Cardapio.py`, `pages/3_Relatorios.py`: Telas redesenhadas sem emojis.
- `.streamlit/config.toml`: Configuração do tema visual escuro executivo.

## Why

Após a migração para SQLite, o sistema alcançou excelente tempo de resposta local, mas ainda apresenta lacunas de segurança operacional, sanitização contra XSS, ausência de headers de autenticação para o Xano, e atrasos (lag) na sincronização devido a intervalos fixos do worker. Além disso, o usuário determinou que o **SQLite deve operar como verdade absoluta em paridade estrita com o Xano**, implementando as mesmas regras relacionais de integridade, constraints de domínio (preços positivos, quantidades válidas, unicidade estrita de comanda aberta por mesa) e integridade referencial.

## What Changes

- **Integridade Relacional e Restrições de Domínio no SQLite (`data_manager.py`)**:
  - Habilitar rigorosamente integridade referencial via `PRAGMA foreign_keys = ON;`.
  - Adicionar constraints `CHECK` no SQLite: `preco_unitario > 0`, `quantidade > 0`, `status IN ('LIVRE', 'OCUPADA')` para mesas e `status IN ('ABERTA', 'PAGA', 'CANCELADA')` para comandas.
  - Criar índice condicional único para garantir que uma mesa tenha no máximo UMA comanda com status `ABERTA` simultaneamente: `CREATE UNIQUE INDEX IF NOT EXISTS idx_comanda_unica_aberta ON comandas(mesa_id) WHERE status = 'ABERTA';`.
  - Criação de índices de performance para aceleração de buscas: `idx_produtos_codigo`, `idx_itens_comanda_comanda_id`, `idx_comandas_data_fechamento`.
- **Mitigação de Riscos de Segurança (XSS & Tratamento de Erros)**:
  - Sanitização de strings inseridas em templates HTML do Streamlit via `html.escape()`.
  - Remoção de capturas cegas (`except Exception: pass`) e introdução de logging estruturado com gravação do erro exato na coluna `ultimo_erro` da tabela `fila_sincronizacao`.
  - Suporte a autenticação no Xano via cabeçalho HTTP `Authorization: Bearer <token>` e chave de API via `XANO_API_KEY`.
- **Fila Inteligente e Redução de Lag de Sincronização**:
  - Transição do delay estático de 2.5s para controle adaptativo de taxa (*Token Bucket / Cooldown Adaptativo*): se a fila possui poucos itens ou está ociosa há mais de 2.5s, o despacho é imediato; se houve envio recente, aguarda apenas o intervalo estritamente necessário para respeitar o rate limit do Xano.
- **Controle de Acesso Operacional (PIN de Segurança)**:
  - Introdução de controle de acesso leve no frontend para operações críticas (exclusão de mesas, cancelamento de comandas e alteração cadastral de produtos), evitando operações acidentais ou desautorizadas no salão.

## Capabilities

### New Capabilities
- `integridade-relacional-e-seguranca`: SQLite como autoridade máxima de validação com constraints atômicas, sanitização de inputs contra injeção e segurança de API.
- `sincronizacao-adaptativa-xano`: Worker com cooldown adaptativo para esvaziamento acelerado da fila sem estourar rate limit.

### Modified Capabilities
- `performance-e-design-streamlit`: Reforço de segurança e índices de alta performance no banco de dados.

## Impact

- `data_manager.py`: Esquema DDL atualizado com constraints de domínio, índices, sanitização e fila adaptativa.
- `ui_components.py` e páginas: Sanitização de saída HTML e suporte a PIN nas operações críticas.

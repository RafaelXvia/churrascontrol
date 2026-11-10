# Proposta de Mudança: Blindagem de Segurança, Otimização de Performance, Paridade Total de Colaboradores no Xano e Benchmark Docker (512MB RAM / 0.50 CPU)

## 1. Contexto e Problema (Why)

A auditoria técnica profunda realizada sobre o repositório do **ChurrasControl** (`backend/`, `frontend/`, `pages/` e `backend/xano/`) e a ferramenta de diagnóstico (`tools/db_diagnostics.py`) revelaram três frentes críticas que precisam ser saneadas antes da validação sob estresse em container:

1. **Vulnerabilidades de Segurança Identificadas na Auditoria**:
   - **Segredos Criptográficos Hardcoded**: `CHURRAS_SALT` e `_FERNET_MASTER_KEY` estão fixos em texto claro no código de `backend/database/data_manager.py`.
   - **Exposição de Chave Mestra na Tela Pública de Login**: O modal público *"Recuperar Senha"* exibe no texto de ajuda a chave administrativa `'CHURRAS-REC-2026'`, permitindo tomada de conta (*Account Takeover*) de qualquer colaborador ou gerente sem autenticação.
   - **Falta de Validação do Token de QR Code no Cardápio Digital do Cliente**: A página `pages/5_Cardapio_Cliente.py` lê apenas `?mesa=N` da URL e ignora o parâmetro `&token=...`, permitindo que qualquer pessoa altere o número da mesa na URL e lance pedidos falsos em mesas alheias.
   - **Acesso Desprotegido à Central de QR Codes**: `pages/4_Mesas_QRCodes.py` não exige autenticação (`exigir_autenticacao()`), permitindo que usuários anônimos visualizem ou regerem tokens de todas as mesas.
   - **Hash de Senha Simples e Ausência de Rate Limit de Login**: Senhas utilizam `SHA-256` simples sem iterações (`PBKDF2`) e sem bloqueio temporário contra tentativas de força bruta.

2. **Gargalos de Otimização, Memória e Paridade SQLite ↔ Xano**:
   - **Problema Crítico de Queries $N+1$**: `obter_dashboard_dados()`, `listar_mesas()` e `listar_mesas_qrcodes()` executam consultas SQL dentro de loops `for` em Python (1 query por comanda ou por mesa), degradando severamente a CPU sob carga.
   - **Conflito de Journal Mode (`DELETE` vs `WAL`)**: Embora o sistema tenha sido projetado para `WAL`, `get_connection()` força `PRAGMA journal_mode = DELETE;` a cada abertura de conexão, anulando a concorrência de leitura/escrita e gerando contenção de I/O.
   - **Sincronização Destrutiva de Produtos (`DELETE FROM produtos`)**: `sincronizar_produtos_xano()` apaga toda a tabela `produtos` antes de reinserir, disparando `ON DELETE SET NULL` na chave estrangeira `produto_id` de `itens_comanda` e quebrando o vínculo de comandas abertas.
   - **Importação Desnecessária de `pandas` em `pages/7_Auditoria.py`**: Contrariando a especificação `otimizacao-memoria-ram-discloud`, a tela de auditoria carrega o `pandas` apenas para formatar uma tabela e exportar CSV, consumindo dezenas de megabytes extras de RAM.
   - **Acúmulo Infinito de Tabelas Operacionais**: Registros já processados (`ENVIADO`) em `fila_sincronizacao`, sessões expiradas em `sessoes_ativas` e logs antigos em `llm_fallback_logs` nunca sofrem expurgo (*pruning*).

3. **Ausência/Divergência da Entidade `colaborador` no Xano (Erro HTTP 404 na Fila)**:
   - O diagnóstico real do banco (`tools/db_diagnostics.py`) comprovou falhas `HTTP 404: ERROR_CODE_NOT_FOUND` na `fila_sincronizacao` para rotas `/colaborador/...` (`ID 59: PATCH /colaborador/15`, `ID 66: PATCH /colaborador/15`).
   - Além de a tabela `colaborador` e seus endpoints precisarem estar 100% publicados e espelhados no Xano (não existindo apenas no SQLite), o arquivo `backend/xano/api/churrascontrol/colaborador_id_PATCH.xs` aceitava apenas `senha_hash`, `primeiro_acesso` e `ativo` (ignorando `nome`, `email`, `numero` e `cargo`), e as operações `PATCH`/`DELETE` falhavam com `404` quando o ID auto-incrementado do SQLite divergia do ID no Xano ou quando o registro ainda não havia sido criado remotamente.

4. **Validação em Container Docker Restrito (`512 MB RAM` e `0.50 CPU`) com Teste de Carga E2E**:
   - É necessário homologar toda a aplicação rodando localmente em **Docker** (`http://localhost:8080`) com limites estritos de hardware (`mem_limit: 512m`, `cpus: 0.50`) através de uma bateria de carga automatizada que exercite **todas as funções do sistema** (login, logout, criação/edição/exclusão de colaborador e sync Xano, criação/edição/exclusão de produto, abertura de mesa, lançamento/incremento/decremento/remoção de item, pré-comanda via QR Code, cancelamento e fechamento de comanda, relatórios PDF e auditoria), **sem realizar qualquer deploy ou upload na Discloud**.

---

## 2. Escopo da Mudança (What Changes)

### 2.1. Blindagem de Segurança (Security Hardening)
- **Variáveis de Ambiente Criptográficas**: Leitura de `CHURRAS_FERNET_KEY` e `CHURRAS_SALT` a partir do `.env`, mantendo derivação determinística compatível apenas como fallback seguro para não invalidar dados já cifrados no banco atual.
- **Remoção de Backdoors de Recuperação de Senha**: Remoção das chaves mestras fixas (`CHURRAS-REC-2026`, `CHURRAS-MASTER`, `ADMIN123`) de `data_manager.py` e remoção da dica pública em `ui_components.py`. A recuperação exigirá validação estrita de e-mail + telefone cadastrado (com comparação constante `secrets.compare_digest`).
- **Upgrade de Hash de Senha com Compatibilidade Retroativa (`PBKDF2-HMAC-SHA256`)**: Novas senhas e redefinições passam a usar `hashlib.pbkdf2_hmac('sha256', ...)` com 100.000 iterações e salt por registro (`pbkdf2_sha256$...`), mantendo verificação transparente para hashes legados SHA-256 e atualizando-os automaticamente no próximo login bem-sucedido.
- **Rate Limiting Anti-Brute-Force no Login**: Bloqueio temporário em memória (60 segundos após 5 falhas consecutivas para o mesmo e-mail), registrado na trilha de auditoria.
- **Validação Estrita de Token QR Code no Autoatendimento (`pages/5_Cardapio_Cliente.py`)**: Verificação obrigatória do par `(mesa, token)` contra a tabela `qrcodes_mesas`. Tokens inválidos ou ausentes bloqueiam o lançamento de pedidos na pré-comanda. Geração de tokens criptograficamente aleatórios (`uuid4`) no `init_db()`.
- **Proteção RBAC na Central de QR Codes (`pages/4_Mesas_QRCodes.py`)**: Inclusão de `ui_components.verificar_permissao_acesso(["gerente", "caixa"])` no topo da página.

### 2.2. Otimização de Performance, Banco de Dados e Memória RAM
- **Ativação Real e Consistente do Modo `WAL`**: Configurado uma única vez na inicialização (`init_db()`) com `PRAGMA journal_mode = WAL; PRAGMA synchronous = NORMAL; PRAGMA temp_store = MEMORY;`, eliminando o `PRAGMA journal_mode = DELETE;` repetitivo em `get_connection()`.
- **Eliminação Total de Queries $N+1$**:
  - `obter_dashboard_dados()`: Substituição das $N$ queries de itens por uma única consulta agregada com `JOIN comandas c ON c.id = i.comanda_id`.
  - `listar_mesas()` e `listar_mesas_qrcodes()`: Cálculo de `total_atual` diretamente na query principal via `LEFT JOIN` e `SUM(i.quantidade * i.preco_momento) GROUP BY`.
- **Upsert Não-Destrutivo em `sincronizar_produtos_xano()`**: Substituição do `DELETE FROM produtos;` por `INSERT INTO produtos ... ON CONFLICT(id) DO UPDATE SET ...`, preservando a integridade referencial (`produto_id`) de todas as comandas abertas e históricas.
- **Remoção de `pandas` em `pages/7_Auditoria.py`**: Renderização nativa de lista de dicionários no `st.dataframe` e geração do arquivo CSV em memória usando os módulos nativos `csv` e `io.StringIO` do Python (0 MB de overhead de RAM).
- **Pruning Automático de Tabelas Temporárias**: Limpeza periódica no worker e no `init_db()` para remover `sessoes_ativas` expiradas, registros `ENVIADO` antigos da `fila_sincronizacao` (> 24h) e excesso de `llm_fallback_logs` (> 500 registros).

### 2.3. Paridade Completa de `colaborador` e Sincronização Resiliente no Xano
- **Atualização de `colaborador_id_PATCH.xs`**: Inclusão dos campos `nome`, `email`, `numero` e `cargo` (além de `senha_hash`, `primeiro_acesso`, `ativo`) e lógica de *Upsert por e-mail/ID* para que edições no SQLite reflitam integralmente no Xano.
- **Resolução Resiliente de Colaboradores e Comandas no `_despachar_requisicao_xano()`**:
  - Assim como já existe para `/itens_comanda/`, quando uma operação `PATCH /colaborador/{id}` ou `DELETE /colaborador/{id}` encontrar divergência de ID ou `404` no Xano, o despachante resolverá o registro remoto pelo `email` (ou criará via `POST /colaborador` no caso de `PATCH`), garantindo que **todos os colaboradores do SQLite existam e permaneçam 100% sincronizados no Xano**.
  - Adição do enfileiramento `DELETE /mesas/{mesa_id}` em `excluir_mesa()` e reconciliação automática de colaboradores locais com o Xano (`reconciliar_colaboradores_xano()`).

### 2.4. Containerização Docker (`512 MB RAM` / `0.50 CPU`) e Teste de Carga E2E
- **Infraestrutura Docker Local (`Dockerfile` e `docker-compose.yml`)**:
  - Imagem leve `python:3.11-slim` executando `python run.py` na porta `8080`.
  - Limites estritos aplicados no container: `mem_limit: 512m` (`512MB RAM`) e `cpus: 0.50` (`0.50 vCPU`).
  - **Restrição Estrita**: Nenhum envio ou alteração na Discloud; tudo hospedado e validado exclusivamente em `localhost` via Docker.
- **Script de Teste de Carga e Funcionalidade Completa (`tools/load_test_docker.py`)**:
  - Executa ciclos concorrentes e sequenciais contra a aplicação e valida:
    1. Login e Logout de Gerente e Caixa + bloqueio de credenciais inválidas.
    2. Adição, edição, troca de senha e exclusão de Colaborador (verificando persistência no SQLite e sincronização com Xano).
    3. Adição, edição de preço/estoque e exclusão de Produto no Cardápio.
    4. Abertura de Mesa, adição de múltiplos itens na Comanda, incremento/decremento de quantidade (validando baixa/estorno de estoque), remoção de item.
    5. Autoatendimento do Cliente via Token de QR Code válido e rejeição de Token inválido.
    6. Cancelamento de Comanda (com estorno de estoque) e Fechamento/Pagamento de Comanda (com taxa de 10% e liberação da mesa).
    7. Geração de Relatório Dashboard/PDF e verificação da Trilha de Auditoria.
    8. Monitoramento em tempo real de `docker stats` comprovando que o consumo de RAM permanece muito abaixo dos `512 MB` e sem erros de CPU/OOM.

---

## 3. Impacto Esperado

- **Segurança**: Eliminação de 100% das vulnerabilidades críticas e médias apontadas na auditoria.
- **Performance**: Redução de >90% no número de queries SQLite em telas de dashboard e salão (de $O(N)$ para $O(1)$ queries).
- **Memória RAM**: Redução de ~60–80 MB no pico de memória da tela de Auditoria pela remoção do `pandas`.
- **Xano Cloud Sync**: Zero erros `404` na `fila_sincronizacao`; tabela `colaborador` no Xano 100% populada e sincronizada com o SQLite.


# Plano de Tarefas (Tasks) — Blindagem de Segurança, Otimização, Paridade Xano (`colaborador`) e Teste de Carga Docker (512MB / 0.50 CPU)

## Fase 1: Blindagem de Segurança e Criptografia (Seção 2 da Auditoria)

- [x] **1.1 Externalização de Segredos e Criptografia Fernet (`backend/database/data_manager.py`, `.env.example`)**
  - **Critério de Aceite**: `FERNET_MASTER_KEY`, `CHURRAS_SALT` e `ADMIN_RECOVERY_CODE` lidos via variáveis de ambiente com fallback seguro de leitura legada (`_FERNET_LEGACY_CIPHER`) para não quebrar dados previamente criptografados. `.env.example` atualizado documentando as novas variáveis (incluindo variáveis opcionais `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_APP_PASSWORD`).
- [x] **1.2 Remoção de Backdoor Exposto na UI e Recuperação Segura (`frontend/components/ui_components.py`, `backend/database/data_manager.py`)**
  - **Critério de Aceite**: Remover a exibição da chave `'CHURRAS-REC-2026'` da tela de login (`ui_components.py`) e remover códigos estáticos hardcoded de `redefinir_senha_colaborador()`. Implementar suporte a envio de código temporário CSPRNG por e-mail (SMTP pessoal se configurado no `.env`) ou validação via `ADMIN_RECOVERY_CODE` definido exclusivamente no ambiente do servidor.
- [x] **1.3 Upgrade de Hash de Senha para `PBKDF2-HMAC-SHA256` + Rate Limiting (`backend/database/data_manager.py`)**
  - **Critério de Aceite**: `gerar_hash_senha()` passa a gerar hashes `pbkdf2_sha256$100000$<salt>$<hash>`. `autenticar_colaborador()` suporta verificação híbrida (migra transparentemente hashes SHA-256 legados para PBKDF2 no primeiro login válido) e aplica rate limiting bloqueando temporariamente após 5 tentativas inválidas em 5 minutos.
- [x] **1.4 Validação Obrigatória de Token QR Code e Guarda RBAC (`pages/5_Cardapio_Cliente.py`, `pages/4_Mesas_QRCodes.py`, `backend/database/data_manager.py`)**
  - **Critério de Aceite**:
    - `pages/5_Cardapio_Cliente.py` valida obrigatoriamente o parâmetro `token` da URL contra o `qr_code_token` da mesa no SQLite usando `hmac.compare_digest` (bloqueando acesso por enumeração de `mesa_id` sem token válido, exceto para colaborador autenticado em modo preview).
    - Tokens legados previsíveis (`mesa-1-token` a `mesa-6-token`) migrados automaticamente para UUID4 criptograficamente seguros.
    - `pages/4_Mesas_QRCodes.py` exige `verificar_permissao_acesso(["gerente", "caixa"])`.

---

## Fase 2: Otimização de Performance, SQLite WAL e Zero-Pandas (Seção 3 da Auditoria)

- [x] **2.1 Ativação Real do Modo `WAL` e Enxugamento de `get_connection()` (`backend/database/data_manager.py`)**
  - **Critério de Aceite**: Remover `PRAGMA journal_mode = DELETE;` de `get_connection()`, configurar `PRAGMA journal_mode = WAL;` e `PRAGMA synchronous = NORMAL;` uma única vez em `init_db()`, e manter `get_connection()` leve com `foreign_keys = ON` e `busy_timeout = 5000`.
- [x] **2.2 Eliminação de Queries $N+1$ (`backend/database/data_manager.py`)**
  - **Critério de Aceite**: Refatorar `obter_dashboard_dados()`, `listar_mesas()` e `listar_mesas_qrcodes()` para utilizar `LEFT JOIN` e `GROUP BY` em uma única consulta SQL, reduzindo de $O(N)$ queries para $O(1)$ query por chamada.
- [x] **2.3 Upsert Não-Destrutivo em `sincronizar_produtos_xano()` (`backend/database/data_manager.py`)**
  - **Critério de Aceite**: Substituir `DELETE FROM produtos;` por `INSERT INTO produtos ... ON CONFLICT(id) DO UPDATE SET ...`, garantindo que `itens_comanda.produto_id` nunca seja zerado (`NULL`) durante sincronizações com o Xano.
- [x] **2.4 Eliminação de `pandas` em `pages/7_Auditoria.py` e Pruning Automático de Tabelas (`pages/7_Auditoria.py`, `backend/database/data_manager.py`)**
  - **Critério de Aceite**:
    - Remover `import pandas as pd` de `pages/7_Auditoria.py`, usando `csv.DictWriter` + `io.StringIO` para exportação CSV e lista nativa de dicionários no `st.dataframe`.
    - Implementar `executar_limpeza_periodica_db()` para expurgar registros `ENVIADO` antigos da `fila_sincronizacao`, sessões expiradas de `sessoes_ativas` e limitar `llm_fallback_logs`.

---

## Fase 3: Paridade Total de `colaborador` e Sincronização Xano Resiliente

- [x] **3.1 Atualização do Endpoint XanoScript `colaborador_id_PATCH.xs` (`backend/xano/api/churrascontrol/colaborador_id_PATCH.xs`)**
  - **Critério de Aceite**: Atualizar `colaborador_id_PATCH.xs` para aceitar e persistir `nome`, `email`, `numero`, `cargo`, `senha_hash`, `primeiro_acesso` e `ativo`. Validar com `xano_validate_xanoscript` via MCP Xano e atualizar o endpoint no Xano Cloud.
- [x] **3.2 Resolução Inteligente por E-mail e Auto-Upsert em `_despachar_requisicao_xano()` (`backend/database/data_manager.py`)**
  - **Critério de Aceite**:
    - Ao processar `PATCH /colaborador/{id}` ou `DELETE /colaborador/{id}`, resolver o ID real no Xano via lookup por `email` caso o ID local difira ou retorne `404`.
    - Se o colaborador ainda existir no Xano durante um `PATCH`, realizar automaticamente o `POST /colaborador` (upsert completo) no Xano.
    - Tratar respostas `404` em `DELETE /colaborador/{id}`, `DELETE /mesas/{id}`, `PATCH /itens_comanda/{id}` e `POST /comandas/{id}/cancelar` de forma idempotente quando o recurso já não existir no Xano.
- [x] **3.3 Reconciliação Bidirecional de Colaboradores (`reconciliar_colaboradores_xano` e `sincronizar_colaboradores_xano`) (`backend/database/data_manager.py`)**
  - **Critério de Aceite**:
    - Implementar `reconciliar_colaboradores_xano()` garantindo que todos os colaboradores do SQLite (incluindo os de seed inicial e novos) sejam enviados ao Xano (`POST /colaborador`).
    - Implementar `sincronizar_colaboradores_xano()` para importar colaboradores do Xano via `ON CONFLICT(email) DO UPDATE`.
    - Adicionar `enfileirar_sincronizacao("DELETE", f"/mesas/{mesa_id}", {})` em `excluir_mesa()`.
    - Integrar a reconciliação de colaboradores em `forcar_sincronizacao_completa()` e zerar os 8 erros pendentes na `fila_sincronizacao`.

---

## Fase 4: Containerização Docker (512MB RAM / 0.50 CPU) e Teste de Carga E2E Completo

- [x] **4.1 Criação de `Dockerfile` e `docker-compose.yml` com Limite Estrito (512MB RAM / 0.50 CPU)**
  - **Critério de Aceite**:
    - `Dockerfile` otimizado (`python:3.11-slim`, `MALLOC_TRIM_THRESHOLD_=65536`, `PYTHONOPTIMIZE=1`, porta `8080`).
    - `docker-compose.yml` configurando `mem_limit: 512m` e `cpus: 0.50` expondo `http://localhost:8080`.
    - **Zero interação ou deploy na Discloud**.
- [x] **4.2 Construção do Script de Teste de Carga e Funcional E2E (`tools/load_test_docker.py`)**
  - **Critério de Aceite**: Script automatizado que executa contra o ambiente Docker (`http://localhost:8080` e banco/API do container) cobrindo:
    1. Login e Logout (`autenticar_colaborador`, criação/validação/encerramento de sessão persistente);
    2. Adição, edição, ativação/desativação, exclusão de colaborador e confirmação de sincronização no Xano;
    3. Adição, edição e remoção de produto no catálogo;
    4. Criação e remoção de mesa + validação de token QR Code;
    5. Abertura de comanda, adição de item (baixa de estoque), remoção de item (estorno de estoque), cancelamento/exclusão de comanda (estorno total) e fechamento financeiro de comanda;
    6. Carga concorrente HTTP em `http://localhost:8080` medindo latência, taxa de sucesso (100%), uso de CPU e pico de RAM via `docker stats` (`< 512 MB`, `OOMKilled = false`).
- [x] **4.3 Execução da Bateria de Testes Unitários + Teste de Carga no Docker**
  - **Critério de Aceite**: 100% dos testes passando sem regressões e relatório consolidado de performance/memória sob o limite de `512MB RAM` e `0.50 CPU`.


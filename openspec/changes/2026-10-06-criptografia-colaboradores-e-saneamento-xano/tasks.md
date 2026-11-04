# Lista de Tarefas — Criptografia de Colaboradores e Saneamento Xano

## Fase 1: Backup e Segurança de Dados
- [x] **1.1 Extrair dados de tabelas ativas do Xano em JSON** (`backups/xano_full_backup.json`)
- [x] **1.2 Gerar dump completo do SQLite** (`backups/churrascontrol_sqlite_backup.sql`)

## Fase 2: Implementação da Criptografia em `data_manager.py`
- [x] **2.1 Adicionar funções `criptografar_dado()` e `descriptografar_dado()` com Fernet AES-128-CBC + HMAC-SHA256**
- [x] **2.2 Atualizar `init_db()` para migrar registros existentes para formato criptografado**
- [x] **2.3 Atualizar `cadastrar_colaborador()` para criptografar nome, numero, cargo antes de salvar no SQLite e Xano**
- [x] **2.4 Atualizar `autenticar_usuario()` e `listar_colaboradores()` para descriptografar os campos dinamicamente**
- [x] **2.5 Atualizar `excluir_colaborador()` para verificar proteção do último gerente usando dados descriptografados**

## Fase 3: Saneamento e Limpeza da Pasta `crudfaculdade/xano/`
- [x] **3.1 Criar arquivo zip de backup da pasta xano legada em `backups/xano_legacy_files_backup.zip`**
- [x] **3.2 Deletar os mais de 30 arquivos .xs órfãos de templates não utilizados**
- [x] **3.3 Consolidar os 5 arquivos de tabela essenciais (`mesas.xs`, `comandas.xs`, `itens_comanda.xs`, `produto.xs`, `colaborador.xs`) com esquemas atualizados**
- [x] **3.4 Atualizar `xano/table/colaborador.xs` documentando os campos criptografados**

## Fase 4: Ferramenta de Restauração para a Nova Instância
- [x] **4.1 Criar `tools/restore_to_xano.py` para subir produtos, mesas e colaboradores para qualquer nova URL de instância do Xano**
- [x] **4.2 Atualizar e executar suíte de testes `tools/test_autenticacao_rbac.py` e `tools/run_all.py` para validar a criptografia**

## Fase 5: Governança de Janela Deslizante, Lockstep Sync Imediato e Normalização de Tabelas
- [x] **5.1 Estudo da documentação oficial do Xano e arquitetura de Rate Limits (10 req / 20s)**
- [x] **5.2 Endpoints idempotentes de UPSERT no Xano (`produto_POST.xs` e `colaborador_POST.xs`) para imunidade a duplicatas**
- [x] **5.3 Implementação do Governador de Janela Deslizante e `_sync_push_imediato_ou_enfileirar` em `data_manager.py`**
- [x] **5.4 Conexão de todas as mutações ao despacho imediato com fallback para fila persistente coordenada**
- [x] **5.5 Limpeza e reset estrito do SQLite e do Xano (apenas os 15 produtos do cardápio e 1 colaborador Gerente)**
- [x] **5.6 Adição de `sincronizar_colaboradores_xano` e botões de sincronização rápida em 1 única requisição GET**
- [x] **5.7 Validação completa de 100% das 6 suítes de testes automatizados (`tools/run_all.py`)**

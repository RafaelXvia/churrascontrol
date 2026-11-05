-- ==============================================================================
-- ChurrasControl — Schema Declarativo e Idempotente do Banco Relacional SQLite
-- Localização: backend/database/schema.sql
-- Modo de Execução: WAL (Write-Ahead Logging) + Foreign Keys ON
-- ==============================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- 1. Catálogo de Produtos
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_pdv TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL,
    preco_unitario REAL NOT NULL,
    descricao TEXT DEFAULT '',
    url_imagem TEXT DEFAULT '',
    qtd_disp INTEGER DEFAULT 15,
    precisa_produzir INTEGER DEFAULT 1,
    disponivel INTEGER DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_produtos_codigo ON produtos(codigo_pdv);
CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria);

-- 2. Gestão de Salão e Mesas
CREATE TABLE IF NOT EXISTS mesas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_mesa INTEGER UNIQUE NOT NULL,
    capacidade INTEGER DEFAULT 1,
    status TEXT DEFAULT 'OCUPADA'
);

-- 3. Comandas de Consumo (com cardinalidade única de comanda ABERTA por mesa)
CREATE TABLE IF NOT EXISTS comandas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mesa_id INTEGER,
    numero_mesa_historico INTEGER NOT NULL,
    data_abertura TEXT NOT NULL,
    data_fechamento TEXT,
    status TEXT DEFAULT 'ABERTA',
    taxa_servico INTEGER DEFAULT 1,
    qtd_pessoas INTEGER DEFAULT 1,
    valor_total REAL DEFAULT 0.0,
    FOREIGN KEY(mesa_id) REFERENCES mesas(id) ON DELETE SET NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_comanda_unica_aberta 
    ON comandas(mesa_id) WHERE status = 'ABERTA';
CREATE INDEX IF NOT EXISTS idx_comandas_status ON comandas(status);

-- 4. Itens Lançados em Comanda (com imutabilidade histórica de preço)
CREATE TABLE IF NOT EXISTS itens_comanda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comanda_id INTEGER NOT NULL,
    produto_id INTEGER,
    nome_produto_historico TEXT NOT NULL,
    categoria_historico TEXT,
    quantidade INTEGER NOT NULL DEFAULT 1,
    preco_momento REAL NOT NULL,
    observacao TEXT DEFAULT '',
    FOREIGN KEY(comanda_id) REFERENCES comandas(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_itens_comanda_cid ON itens_comanda(comanda_id);

-- 5. Fila Persistente de Sincronização Assíncrona com Xano
CREATE TABLE IF NOT EXISTS fila_sincronizacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metodo TEXT NOT NULL,
    rota TEXT NOT NULL,
    payload_json TEXT,
    status TEXT DEFAULT 'PENDENTE',
    tentativas INTEGER DEFAULT 0,
    criado_em TEXT NOT NULL,
    processado_em TEXT,
    ultimo_erro TEXT
);
CREATE INDEX IF NOT EXISTS idx_fila_status ON fila_sincronizacao(status);

-- 6. QR Codes Operacionais por Mesa
CREATE TABLE IF NOT EXISTS qrcodes_mesas (
    numero_mesa INTEGER PRIMARY KEY,
    token_qrcode TEXT NOT NULL,
    criado_em TEXT NOT NULL,
    atualizado_em TEXT NOT NULL
);

-- 7. Colaboradores, Acessos e Criptografia
CREATE TABLE IF NOT EXISTS colaboradores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    numero TEXT NOT NULL,
    cargo TEXT NOT NULL,
    primeiro_acesso INTEGER NOT NULL DEFAULT 1 CHECK(primeiro_acesso IN (0, 1)),
    ativo INTEGER NOT NULL DEFAULT 1 CHECK(ativo IN (0, 1)),
    criado_em TEXT NOT NULL,
    atualizado_em TEXT NOT NULL
);

-- 8. Sessões Ativas (Tokens de Autenticação)
CREATE TABLE IF NOT EXISTS sessoes_ativas (
    token TEXT PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    criado_em TEXT NOT NULL,
    expira_em TEXT NOT NULL,
    FOREIGN KEY(usuario_id) REFERENCES colaboradores(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_sessoes_token ON sessoes_ativas(token);

-- 9. Auditoria de Segurança e Operações Críticas
CREATE TABLE IF NOT EXISTS auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    usuario_nome TEXT,
    usuario_email TEXT,
    cargo TEXT,
    acao TEXT NOT NULL,
    modulo TEXT NOT NULL,
    detalhes TEXT,
    criado_em TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_auditoria_criado_em ON auditoria(criado_em);
CREATE INDEX IF NOT EXISTS idx_auditoria_modulo ON auditoria(modulo);
CREATE INDEX IF NOT EXISTS idx_auditoria_acao ON auditoria(acao);

-- 10. Ontologia Semântica de Domínio (Triple Store)
CREATE TABLE IF NOT EXISTS ontologia_conceitos (
    id TEXT PRIMARY KEY,
    tipo TEXT NOT NULL,
    nome_legivel TEXT NOT NULL,
    descricao TEXT
);

CREATE TABLE IF NOT EXISTS ontologia_sinonimos (
    termo TEXT PRIMARY KEY,
    conceito_id TEXT NOT NULL,
    FOREIGN KEY(conceito_id) REFERENCES ontologia_conceitos(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_ontologia_sinonimos_cid ON ontologia_sinonimos(conceito_id);

CREATE TABLE IF NOT EXISTS ontologia_relacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sujeito_id TEXT NOT NULL,
    predicado TEXT NOT NULL,
    objeto_id TEXT NOT NULL,
    peso REAL DEFAULT 1.0,
    FOREIGN KEY(sujeito_id) REFERENCES ontologia_conceitos(id)
);
CREATE INDEX IF NOT EXISTS idx_ontologia_busca ON ontologia_relacoes(sujeito_id, predicado);
CREATE INDEX IF NOT EXISTS idx_ontologia_inversa ON ontologia_relacoes(objeto_id, predicado);

-- 11. Conversas e Mensagens do Assistente IA (RAG)
CREATE TABLE IF NOT EXISTS chat_conversas (
    id TEXT PRIMARY KEY,
    titulo TEXT NOT NULL,
    usuario_id TEXT NOT NULL,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_chat_conversas_usr ON chat_conversas(usuario_id);

CREATE TABLE IF NOT EXISTS chat_mensagens (
    id TEXT PRIMARY KEY,
    conversa_id TEXT NOT NULL,
    papel TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    ferramentas_json TEXT,
    api_origem TEXT,
    modelo_utilizado TEXT,
    tentativas_falhas INTEGER DEFAULT 0,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(conversa_id) REFERENCES chat_conversas(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_chat_mensagens_cid ON chat_mensagens(conversa_id);

-- 12. Telemetria e Logs de Fallback LLM Multinível
CREATE TABLE IF NOT EXISTS llm_fallback_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversa_id TEXT,
    mensagem_id TEXT,
    api_origem TEXT NOT NULL,
    modelo TEXT NOT NULL,
    sucesso INTEGER NOT NULL,
    codigo_status INTEGER,
    erro_motivo TEXT,
    duracao_ms INTEGER,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_llm_fallback_criado ON llm_fallback_logs(criado_em);
CREATE INDEX IF NOT EXISTS idx_llm_fallback_busca ON llm_fallback_logs(api_origem, modelo, sucesso);

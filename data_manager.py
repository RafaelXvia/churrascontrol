"""
Módulo de Dados e Gerenciamento de Estado — ChurrasControl
Persistência relacional transacional de alta integridade via SQLite embutido (WAL mode),
com paridade estrita de regras de negócio em relação ao Xano (Dual Single Source of Truth).
Inclui sanitização contra XSS, constraints de domínio (preços, quantidades e cardinalidade única de comanda),
cooldown adaptativo de sincronização e autenticação segura com Xano.
"""
import os
import io
import html
import json
import time
import uuid
import logging
import sqlite3
import threading
import hashlib
import collections
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import httpx

import base64
from cryptography.fernet import Fernet, InvalidToken

CHURRAS_SALT = "CC_SALT_2026_INNOVATION_LAB"

# Chave mestra Fernet derivada deterministicamente por SHA-256 (32 bytes em Base64 URL-safe)
_raw_crypto_key = hashlib.sha256(b"CHURRASCONTROL_FERNET_MASTER_KEY_2026_INNOVATION_LAB").digest()
_FERNET_MASTER_KEY = base64.urlsafe_b64encode(_raw_crypto_key)
_cipher_suite = Fernet(_FERNET_MASTER_KEY)

def criptografar_dado(texto: str) -> str:
    """Criptografa uma string usando AES-128-CBC + HMAC-SHA256 (Fernet) com prefixo identificador 'ENC:'."""
    if texto is None:
        return ""
    texto_str = str(texto).strip()
    if not texto_str:
        return ""
    if texto_str.startswith("ENC:"):
        return texto_str
    token = _cipher_suite.encrypt(texto_str.encode("utf-8")).decode("utf-8")
    return f"ENC:{token}"

def descriptografar_dado(texto_cifrado: str) -> str:
    """Descriptografa um token cifrado Fernet com prefixo 'ENC:'. Retorna o texto original em caso de erro ou string plana."""
    if not texto_cifrado:
        return ""
    texto_str = str(texto_cifrado).strip()
    if not texto_str.startswith("ENC:"):
        return texto_str
    token = texto_str[4:]
    try:
        return _cipher_suite.decrypt(token.encode("utf-8")).decode("utf-8")
    except (InvalidToken, Exception) as e:
        logger.warning(f"Falha ao descriptografar token: {e}")
        return texto_str


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ChurrasControl")

DB_PATH = os.path.join(os.path.dirname(__file__), "churrascontrol.db")
LEGACY_JSON_PATH = os.path.join(os.path.dirname(__file__), "churras_data.json")
XANO_BASE_URL = os.getenv("XANO_BASE_URL", "https://x8ki-letl-twmt.n7.xano.io/api:churrascontrol")
XANO_API_KEY = os.getenv("XANO_API_KEY", os.getenv("XANO_AUTH_TOKEN", ""))

_db_lock = threading.Lock()
_rate_lock = threading.Lock()
_call_timestamps = collections.deque()
MAX_REQUESTS_PER_20S = 8  # Margem segura estrita abaixo do teto de 10 req / 20s do Xano Free
RATE_WINDOW_SECONDS = 20.0
RATE_LIMIT_COOLDOWN = 2.5
_last_xano_call_time = 0.0

def _pode_chamar_xano_agora() -> bool:
    """Verifica se a janela deslizante de 20s possui quota disponível (< 8 chamadas)."""
    with _rate_lock:
        agora = time.time()
        while _call_timestamps and (_call_timestamps[0] <= agora - RATE_WINDOW_SECONDS):
            _call_timestamps.popleft()
        return len(_call_timestamps) < MAX_REQUESTS_PER_20S

def _registrar_chamada_xano():
    """Registra o timestamp da requisição enviada ao Xano na janela deslizante."""
    global _last_xano_call_time
    with _rate_lock:
        agora = time.time()
        _call_timestamps.append(agora)
        _last_xano_call_time = agora

def _esperar_janela_rate_limit():
    """Garante que a próxima chamada ao Xano respeite estritamente a janela deslizante (elimina 429)."""
    while True:
        with _rate_lock:
            agora = time.time()
            while _call_timestamps and (_call_timestamps[0] <= agora - RATE_WINDOW_SECONDS):
                _call_timestamps.popleft()
            if len(_call_timestamps) < MAX_REQUESTS_PER_20S:
                return
            tempo_espera = max(0.2, (_call_timestamps[0] + RATE_WINDOW_SECONDS) - agora + 0.1)
        time.sleep(tempo_espera)

def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão SQLite configurada com WAL, timeout, limite de cache de 2MB e autocheckpoint."""
    conn = sqlite3.connect(DB_PATH, timeout=25.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA cache_size = -2000;")  # Limite de 2MB para cache de páginas SQLite
    conn.execute("PRAGMA wal_autocheckpoint = 250;")  # Mantém o arquivo .db-wal compacto (~1MB)
    return conn

_db_initialized = False

def init_db():
    """Inicializa as tabelas no SQLite com constraints rígidas, índices e migração de colunas (idempotente)."""
    global _db_initialized
    if _db_initialized:
        return
    with _db_lock:
        if _db_initialized:
            return
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Tabela de Produtos com verificação de preço estritamente positivo
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_pdv TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                preco_unitario REAL NOT NULL CHECK(preco_unitario > 0)
            );
            """)

            # 2. Tabela de Mesas com capacidade mínima e status restrito
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS mesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_mesa INTEGER UNIQUE NOT NULL,
                capacidade INTEGER NOT NULL DEFAULT 1 CHECK(capacidade >= 1),
                status TEXT NOT NULL DEFAULT 'OCUPADA' CHECK(status IN ('LIVRE', 'OCUPADA'))
            );
            """)

            # 3. Tabela de Comandas com cardinalidade e integridade financeira
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS comandas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mesa_id INTEGER,
                numero_mesa_historico INTEGER NOT NULL,
                data_abertura TEXT NOT NULL,
                data_fechamento TEXT,
                status TEXT NOT NULL DEFAULT 'ABERTA' CHECK(status IN ('ABERTA', 'PAGA', 'CANCELADA')),
                taxa_servico INTEGER NOT NULL DEFAULT 1 CHECK(taxa_servico IN (0, 1)),
                qtd_pessoas INTEGER NOT NULL DEFAULT 1 CHECK(qtd_pessoas >= 1),
                valor_total REAL NOT NULL DEFAULT 0.0 CHECK(valor_total >= 0.0),
                FOREIGN KEY(mesa_id) REFERENCES mesas(id) ON DELETE SET NULL
            );
            """)

            # REGRA DE OURO RELACIONAL: No máximo uma comanda ABERTA por mesa física
            cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_comanda_unica_aberta 
            ON comandas(mesa_id) WHERE status = 'ABERTA';
            """)

            # 4. Tabela de Itens de Comanda (Imutabilidade de preços e verificação de quantidade positiva)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_comanda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comanda_id INTEGER NOT NULL,
                produto_id INTEGER,
                nome_produto_historico TEXT NOT NULL,
                categoria_historico TEXT,
                quantidade INTEGER NOT NULL DEFAULT 1 CHECK(quantidade >= 1),
                preco_momento REAL NOT NULL CHECK(preco_momento >= 0.0),
                observacao TEXT DEFAULT '',
                FOREIGN KEY(comanda_id) REFERENCES comandas(id) ON DELETE CASCADE,
                FOREIGN KEY(produto_id) REFERENCES produtos(id) ON DELETE SET NULL
            );
            """)

            # 5. Tabela de Fila Persistente de Sincronização com Xano e rastreamento de erro
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS fila_sincronizacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metodo TEXT NOT NULL,
                rota TEXT NOT NULL,
                payload_json TEXT,
                status TEXT NOT NULL DEFAULT 'PENDENTE' CHECK(status IN ('PENDENTE', 'ENVIADO', 'ERRO')),
                tentativas INTEGER NOT NULL DEFAULT 0,
                ultimo_erro TEXT,
                criado_em TEXT NOT NULL,
                processado_em TEXT
            );
            """)

            # Atualização incremental de schema caso a coluna ultimo_erro não exista
            cursor.execute("PRAGMA table_info(fila_sincronizacao);")
            colunas_fila = [c["name"] for c in cursor.fetchall()]
            if "ultimo_erro" not in colunas_fila:
                cursor.execute("ALTER TABLE fila_sincronizacao ADD COLUMN ultimo_erro TEXT;")

            # 6. Atualização incremental de schema da tabela de PRODUTOS (paridade total com tabela Xano)
            cursor.execute("PRAGMA table_info(produtos);")
            colunas_produtos = [c["name"] for c in cursor.fetchall()]
            if "descricao" not in colunas_produtos:
                cursor.execute("ALTER TABLE produtos ADD COLUMN descricao TEXT DEFAULT '';")
            if "url_imagem" not in colunas_produtos:
                cursor.execute("ALTER TABLE produtos ADD COLUMN url_imagem TEXT DEFAULT '';")
            if "qtd_disp" not in colunas_produtos:
                cursor.execute("ALTER TABLE produtos ADD COLUMN qtd_disp INTEGER DEFAULT 15;")
            if "precisa_produzir" not in colunas_produtos:
                cursor.execute("ALTER TABLE produtos ADD COLUMN precisa_produzir INTEGER DEFAULT 1;")
            if "disponivel" not in colunas_produtos:
                cursor.execute("ALTER TABLE produtos ADD COLUMN disponivel INTEGER DEFAULT 1;")

            # 7. Índices de Alta Performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_produtos_codigo ON produtos(codigo_pdv);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_itens_comanda_cid ON itens_comanda(comanda_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_comandas_status ON comandas(status);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fila_status ON fila_sincronizacao(status);")

            # 8. Tabela de QR Codes e Tokens Estáveis por Mesa Física
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS qrcodes_mesas (
                numero_mesa INTEGER PRIMARY KEY,
                token_qrcode TEXT NOT NULL,
                criado_em TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            );
            """)
            for m_num in range(1, 11):
                cursor.execute("SELECT numero_mesa FROM qrcodes_mesas WHERE numero_mesa = ?", (m_num,))
                if not cursor.fetchone():
                    tok_inicial = f"mesa-{m_num}-token"
                    agora_iso = datetime.now().isoformat()
                    cursor.execute("""
                    INSERT INTO qrcodes_mesas (numero_mesa, token_qrcode, criado_em, atualizado_em)
                    VALUES (?, ?, ?, ?)
                    """, (m_num, tok_inicial, agora_iso, agora_iso))

            # 9. Tabela de Colaboradores e Autenticação (RBAC com Criptografia de Ponta a Ponta)
            # Migração transparente caso a tabela anterior possua a constraint restritiva CHECK(cargo IN ...)
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='colaboradores';")
            row_tab = cursor.fetchone()
            if row_tab and "CHECK(cargo IN" in row_tab["sql"]:
                cursor.execute("ALTER TABLE colaboradores RENAME TO colaboradores_old;")
                cursor.execute("""
                CREATE TABLE colaboradores (
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
                """)
                cursor.execute("SELECT * FROM colaboradores_old;")
                for r in cursor.fetchall():
                    nome_c = criptografar_dado(r["nome"])
                    num_c = criptografar_dado(r["numero"])
                    cargo_c = criptografar_dado(r["cargo"])
                    cursor.execute("""
                    INSERT INTO colaboradores (id, nome, email, senha_hash, numero, cargo, primeiro_acesso, ativo, criado_em, atualizado_em)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (r["id"], nome_c, r["email"], r["senha_hash"], num_c, cargo_c, r["primeiro_acesso"], r["ativo"], r["criado_em"], r["atualizado_em"]))
                cursor.execute("DROP TABLE colaboradores_old;")
            else:
                cursor.execute("""
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
                """)

            # Assegura que quaisquer registros já existentes sem o prefixo ENC: sejam devidamente criptografados
            cursor.execute("SELECT id, nome, numero, cargo FROM colaboradores;")
            for r in cursor.fetchall():
                modificado = False
                n_nome = r["nome"]
                n_num = r["numero"]
                n_cargo = r["cargo"]
                if not n_nome.startswith("ENC:"):
                    n_nome = criptografar_dado(n_nome)
                    modificado = True
                if not n_num.startswith("ENC:"):
                    n_num = criptografar_dado(n_num)
                    modificado = True
                if not n_cargo.startswith("ENC:"):
                    n_cargo = criptografar_dado(n_cargo)
                    modificado = True
                if modificado:
                    cursor.execute("UPDATE colaboradores SET nome = ?, numero = ?, cargo = ? WHERE id = ?", (n_nome, n_num, n_cargo, r["id"]))

            # Seed do Gerente Administrador inicial se não houver registros
            cursor.execute("SELECT COUNT(*) as total FROM colaboradores;")
            tot_colabs = cursor.fetchone()
            if tot_colabs and tot_colabs["total"] == 0:
                agora_iso = datetime.now().isoformat()
                raw_seed = f"{CHURRAS_SALT}:admin123"
                h_seed = hashlib.sha256(raw_seed.encode("utf-8")).hexdigest()
                cursor.execute("""
                INSERT INTO colaboradores (nome, email, senha_hash, numero, cargo, primeiro_acesso, ativo, criado_em, atualizado_em)
                VALUES (?, ?, ?, ?, ?, 1, 1, ?, ?)
                """, (criptografar_dado("Gerente Administrador"), "gerente@churrascontrol.com", h_seed, criptografar_dado("(31) 99999-9999"), criptografar_dado("gerente"), agora_iso, agora_iso))

            # Enriquecimento automático de fotos e descrições para produtos existentes sem foto
            _fotos_padrao = {
                "Tutu à Mineira": (
                    "Tradicional feijão batido mineiro com farinha de mandioca, servido com ovos fritos, couve fininha refogada no alho e torresmo pururuca estalando.",
                    "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80",
                    "Comida", 20, 1
                ),
                "Frango com Quiabo": (
                    "Galinha caipira ensopada em fogo lento com quiabo verde sem baba, molho dourado aromático com cheiro-verde e arroz branco soltinho.",
                    "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=600&auto=format&fit=crop&q=80",
                    "Comida", 15, 1
                ),
                "Feijoada Mineira": (
                    "Feijoada completa com carnes nobres curadas e defumadas (costelinha, lombo, paio e calabresa). Acompanha couve, farofa e laranja fresca.",
                    "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=600&auto=format&fit=crop&q=80",
                    "Comida", 25, 1
                ),
                "Vaca Atolada": (
                    "Costela bovina de primeira desmanchando na panela com mandioca cozida amanteigada, cheiro-verde fresco e pimenta biquinho.",
                    "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80",
                    "Comida", 18, 1
                ),
                "Tropeiro": (
                    "Feijão tropeiro clássico dos tropeiros mineiros, com farinha de milho crocante, bacon defumado, calabresa, ovos e couve rasgada.",
                    "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=600&auto=format&fit=crop&q=80",
                    "Comida", 30, 1
                ),
                "Carne de Panela": (
                    "Cortes nobres bovinos cozidos lentamente em caldo encorpado de legumes com batatas douradas e folhas de louro selecionadas.",
                    "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80",
                    "Comida", 16, 1
                ),
                "Picanha": (
                    "Corte nobre de picanha com capa de gordura perfeita, grelhada na parrilla ao ponto desejado, selada com flor de sal e servida fatiada.",
                    "https://images.unsplash.com/photo-1558030006-450675393462?w=600&auto=format&fit=crop&q=80",
                    "Carnes", 22, 1
                ),
                "Costela": (
                    "Costela bovina de ripa assada lentamente no bafo por 8 horas, soltando do osso com facilidade, acompanhada de molho chimichurri rústico.",
                    "https://images.unsplash.com/photo-1529193591184-b1d58069ecdd?w=600&auto=format&fit=crop&q=80",
                    "Carnes", 14, 1
                ),
                "Cerveja": (
                    "Cerveja puro malte gelada em temperatura estritamente ideal, garrafa servida trincando com colarinho cremoso.",
                    "https://images.unsplash.com/photo-1608270586620-248524c67de9?w=600&auto=format&fit=crop&q=80",
                    "Bebidas", 50, 0
                ),
                "Suco": (
                    "Suco natural da fruta preparado na hora, refrescante, servido com bastante gelo e opcional de hortelã fresca.",
                    "https://images.unsplash.com/photo-1613478223719-2ab802602423?w=600&auto=format&fit=crop&q=80",
                    "Bebidas", 40, 0
                ),
                "Pudim": (
                    "Pudim de leite condensado artesanal com textura aveludada sem furinhos, banhado em calda de caramelo dourada e brilhante.",
                    "https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=600&auto=format&fit=crop&q=80",
                    "Sobremesas", 15, 0
                )
            }
            for nome_key, (desc, url, cat, qtd, precisa_prod) in _fotos_padrao.items():
                cursor.execute("""
                UPDATE produtos 
                SET descricao = CASE WHEN (descricao IS NULL OR descricao = '') THEN ? ELSE descricao END,
                    url_imagem = CASE WHEN (url_imagem IS NULL OR url_imagem = '') THEN ? ELSE url_imagem END,
                    qtd_disp = CASE WHEN (qtd_disp IS NULL OR qtd_disp = 0) THEN ? ELSE qtd_disp END,
                    precisa_produzir = CASE WHEN precisa_produzir IS NULL THEN ? ELSE precisa_produzir END,
                    disponivel = 1
                WHERE nome LIKE ?;
                """, (desc, url, qtd, precisa_prod, f"%{nome_key}%"))

            # Imagem e descrição genérica de alta qualidade para produtos que restarem vazios
            cursor.execute("""
            UPDATE produtos
            SET url_imagem = 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80'
            WHERE url_imagem IS NULL OR url_imagem = '';
            """)
            cursor.execute("""
            UPDATE produtos
            SET descricao = 'Prato especial preparado com ingredientes selecionados, tempero autêntico da casa e finalização primorosa.'
            WHERE descricao IS NULL OR descricao = '';
            """)

            # Migração automática de dados legados do churras_data.json se o banco estiver vazio
            cursor.execute("SELECT COUNT(*) as total FROM produtos;")
            row = cursor.fetchone()
            if row and row["total"] == 0 and os.path.exists(LEGACY_JSON_PATH):
                try:
                    with open(LEGACY_JSON_PATH, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    for p in data.get("produtos", []):
                        cursor.execute("""
                        INSERT OR IGNORE INTO produtos (id, codigo_pdv, nome, categoria, preco_unitario)
                        VALUES (?, ?, ?, ?, ?)
                        """, (p["id"], str(p.get("codigo_pdv", "")).strip(), p["nome"], p["categoria"], float(p["preco_unitario"])))

                    for m in data.get("mesas", []):
                        cursor.execute("""
                        INSERT OR IGNORE INTO mesas (id, numero_mesa, capacidade, status)
                        VALUES (?, ?, ?, ?)
                        """, (m["id"], m["numero_mesa"], m.get("capacidade", 1), m.get("status", "OCUPADA")))

                    for c in data.get("comandas", []):
                        cursor.execute("""
                        INSERT OR IGNORE INTO comandas (id, mesa_id, numero_mesa_historico, data_abertura, data_fechamento, status, taxa_servico, qtd_pessoas, valor_total)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            c["id"],
                            c.get("mesa_id"),
                            c.get("numero_mesa_historico") or c.get("mesa_id") or 1,
                            c.get("data_abertura") or datetime.now().isoformat(),
                            c.get("data_fechamento"),
                            c.get("status", "ABERTA"),
                            1 if c.get("taxa_servico", True) else 0,
                            int(c.get("qtd_pessoas") or 1),
                            float(c.get("valor_total") or 0.0)
                        ))

                    for it in data.get("itens_comanda", []):
                        cursor.execute("""
                        INSERT OR IGNORE INTO itens_comanda (id, comanda_id, produto_id, nome_produto_historico, categoria_historico, quantidade, preco_momento, observacao)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            it["id"],
                            it["comanda_id"],
                            it.get("produto_id"),
                            it.get("nome_produto_historico", ""),
                            it.get("categoria_historico", ""),
                            int(it.get("quantidade") or 1),
                            float(it.get("preco_momento") or 0.0),
                            it.get("observacao", "")
                        ))

                    conn.commit()
                    logger.info("Migração legada concluída com sucesso no SQLite.")
                except Exception as e:
                    logger.error(f"Erro na migração legada: {e}")
            _db_initialized = True

init_db()

# ================= WORKER PERSISTENTE DE SINCRONIZAÇÃO XANO COM GOVERNANÇA DE JANELA =================

_DISABLE_XANO_ENQUEUE = False

def _enqueue_xano(metodo: str, rota: str, payload: dict = None):
    """Enfileira ação na tabela persistente de sincronização do SQLite sem travar a interface."""
    if _DISABLE_XANO_ENQUEUE or os.getenv("TESTING_ENV") == "1":
        return
    try:
        with _db_lock:
            with get_connection() as conn:
                conn.execute("""
                INSERT INTO fila_sincronizacao (metodo, rota, payload_json, status, tentativas, criado_em)
                VALUES (?, ?, ?, 'PENDENTE', 0, ?)
                """, (metodo, rota, json.dumps(payload or {}, ensure_ascii=False), datetime.now().isoformat()))
                conn.commit()
    except Exception as e:
        logger.error(f"Falha ao enfileirar tarefa no SQLite para o Xano: {e}")

def _sync_push_imediato_ou_enfileirar(metodo: str, rota: str, payload: dict = None) -> bool:
    """
    Sincronização imediata em lockstep (SQLite <-> Xano) com proteção total contra Rate Limit:
    1. Se houver cota disponível na janela deslizante de 20s (< 8 chamadas), realiza a chamada HTTP imediata (<300ms).
       Dessa forma, o dado aparece no SQLite e no Xano instantaneamente ('apareceu no sqlite já tá lá no xano').
    2. Se a cota estiver temporariamente preenchida, ou em caso de timeout / queda de rede / 429,
       enfileira automaticamente no SQLite persistente (fila_sincronizacao), garantindo entrega garantida offline-first
       sem bloquear a interface do usuário e sem disparar erros 429.
    """
    if _DISABLE_XANO_ENQUEUE or os.getenv("TESTING_ENV") == "1":
        return True

    payload = payload or {}
    agora_iso = datetime.now().isoformat()

    # Se a janela de 20s permitir, tenta push imediato síncrono
    if _pode_chamar_xano_agora():
        url = f"{XANO_BASE_URL.rstrip('/')}/{rota.lstrip('/')}"
        headers = {"Content-Type": "application/json"}
        if XANO_API_KEY:
            headers["Authorization"] = f"Bearer {XANO_API_KEY}"

        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.request(metodo, url, json=payload, headers=headers)
                _registrar_chamada_xano()
                
                if resp.status_code in (200, 201, 204):
                    logger.info(f"Sincronização imediata Xano concluída com sucesso: {metodo} {rota}")
                    # Grava na fila já como ENVIADO para histórico de auditoria
                    try:
                        with _db_lock:
                            with get_connection() as conn:
                                conn.execute("""
                                INSERT INTO fila_sincronizacao (metodo, rota, payload_json, status, tentativas, criado_em, processado_em)
                                VALUES (?, ?, ?, 'ENVIADO', 1, ?, ?)
                                """, (metodo, rota, json.dumps(payload, ensure_ascii=False), agora_iso, agora_iso))
                                conn.commit()
                    except Exception:
                        pass
                    return True
                elif resp.status_code == 429:
                    logger.warning(f"Xano retornou HTTP 429 no push imediato ({rota}). Enfileirando para entrega coordenada...")
                else:
                    logger.warning(f"Xano retornou HTTP {resp.status_code} no push imediato ({rota}). Enfileirando...")
        except Exception as ex:
            logger.info(f"Push imediato indisponível ({ex}). Enfileirando com segurança offline-first...")

    # Se não foi possível o envio imediato (ou quota cheia), enfileira no SQLite persistente
    _enqueue_xano(metodo, rota, payload)
    return False

def _xano_sqlite_worker():
    """Worker em background com governança de janela deslizante para drenar a fila sem qualquer 429."""
    _idle_counter = 0
    while True:
        try:
            tarefa = None
            with _db_lock:
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                    SELECT id, metodo, rota, payload_json, tentativas
                    FROM fila_sincronizacao
                    WHERE status = 'PENDENTE'
                    ORDER BY id ASC
                    LIMIT 1
                    """)
                    row = cursor.fetchone()
                    if row:
                        tarefa = {
                            "id": row["id"],
                            "metodo": row["metodo"],
                            "rota": row["rota"],
                            "payload": json.loads(row["payload_json"] or "{}"),
                            "tentativas": row["tentativas"]
                        }

            if not tarefa:
                _idle_counter += 1
                if _idle_counter >= 12:  # A cada ~30s de inatividade, consolida o WAL para diminuir memória
                    _idle_counter = 0
                    try:
                        with _db_lock:
                            with get_connection() as conn:
                                conn.execute("PRAGMA wal_checkpoint(PASSIVE);")
                    except Exception:
                        pass
                time.sleep(1.0)
                continue

            _idle_counter = 0

            # Aguarda vaga na janela deslizante (impossível violar rate limit de 10 req / 20s)
            _esperar_janela_rate_limit()

            tarefa_id = tarefa["id"]
            url = f"{XANO_BASE_URL.rstrip('/')}/{tarefa['rota'].lstrip('/')}"
            sucesso = False
            detalhe_erro = None

            headers = {"Content-Type": "application/json"}
            if XANO_API_KEY:
                headers["Authorization"] = f"Bearer {XANO_API_KEY}"

            is_rate_limited = False
            try:
                with httpx.Client(timeout=8.0) as client:
                    resp = client.request(tarefa["metodo"], url, json=tarefa["payload"], headers=headers)
                    _registrar_chamada_xano()
                    if resp.status_code in (200, 201, 204):
                        sucesso = True
                    elif resp.status_code == 429:
                        is_rate_limited = True
                        detalhe_erro = f"HTTP 429 (Rate Limit): {resp.text[:150]}"
                        logger.warning(f"Worker Xano: Rate Limit 429 detectado na tarefa {tarefa_id}.")
                    else:
                        detalhe_erro = f"HTTP {resp.status_code}: {resp.text[:200]}"
            except Exception as ex:
                sucesso = False
                detalhe_erro = str(ex)

            with _db_lock:
                with get_connection() as conn:
                    if sucesso:
                        conn.execute("""
                        UPDATE fila_sincronizacao
                        SET status = 'ENVIADO', processado_em = ?, ultimo_erro = NULL
                        WHERE id = ?
                        """, (datetime.now().isoformat(), tarefa_id))
                    elif is_rate_limited:
                        conn.execute("""
                        UPDATE fila_sincronizacao
                        SET status = 'PENDENTE', ultimo_erro = ?, processado_em = ?
                        WHERE id = ?
                        """, (detalhe_erro, datetime.now().isoformat(), tarefa_id))
                    else:
                        novas_tentativas = tarefa["tentativas"] + 1
                        novo_status = "ERRO" if novas_tentativas >= 5 else "PENDENTE"
                        conn.execute("""
                        UPDATE fila_sincronizacao
                        SET tentativas = ?, status = ?, ultimo_erro = ?, processado_em = ?
                        WHERE id = ?
                        """, (novas_tentativas, novo_status, detalhe_erro, datetime.now().isoformat(), tarefa_id))
                    conn.commit()

            if is_rate_limited:
                time.sleep(20.0)

        except Exception as e:
            logger.error(f"Erro no loop do worker Xano: {e}")
            time.sleep(1.0)

if "_worker_thread" not in globals() or not _worker_thread.is_alive():
    _worker_thread = threading.Thread(target=_xano_sqlite_worker, daemon=True)
    _worker_thread.start()

# ================= OPERAÇÕES DE MESAS E COMANDAS =================

def listar_mesas() -> List[dict]:
    """Lista todas as mesas ativas e calcula o consumo atual diretamente do SQLite."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT 
                m.id, 
                m.numero_mesa, 
                m.capacidade, 
                m.status,
                c.id as comanda_id
            FROM mesas m
            LEFT JOIN comandas c ON c.mesa_id = m.id AND c.status = 'ABERTA'
            ORDER BY m.numero_mesa ASC
            """)
            mesas_rows = cursor.fetchall()
            
            resultado = []
            for m in mesas_rows:
                comanda_id = m["comanda_id"] or m["id"]
                total_atual = 0.0
                if m["comanda_id"]:
                    cursor.execute("""
                    SELECT SUM(quantidade * preco_momento) as total
                    FROM itens_comanda
                    WHERE comanda_id = ?
                    """, (m["comanda_id"],))
                    tot_row = cursor.fetchone()
                    if tot_row and tot_row["total"] is not None:
                        total_atual = float(tot_row["total"])

                resultado.append({
                    "id": m["id"],
                    "numero_mesa": m["numero_mesa"],
                    "capacidade": m["capacidade"] or 1,
                    "status": m["status"] or "OCUPADA",
                    "comanda_id": comanda_id,
                    "total_atual": total_atual
                })
            return resultado

def abrir_mesa(numero_mesa: int, qtd_pessoas: int = 1) -> dict:
    """Abre uma nova mesa e comanda no salão com validação estrita de cardinalidade."""
    if qtd_pessoas <= 0:
        raise ValueError("A capacidade deve ser de no mínimo 1 pessoa.")
    if numero_mesa <= 0:
        raise ValueError("O número da mesa deve ser um valor positivo.")

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM mesas WHERE numero_mesa = ?", (numero_mesa,))
            if cursor.fetchone():
                raise ValueError(f"Mesa {numero_mesa} já está aberta no salão.")

            cursor.execute("""
            INSERT INTO mesas (numero_mesa, capacidade, status)
            VALUES (?, ?, 'OCUPADA')
            """, (numero_mesa, qtd_pessoas))
            nova_mesa_id = cursor.lastrowid

            cursor.execute("""
            INSERT INTO comandas (mesa_id, numero_mesa_historico, data_abertura, status, taxa_servico, qtd_pessoas, valor_total)
            VALUES (?, ?, ?, 'ABERTA', 1, ?, 0.0)
            """, (nova_mesa_id, numero_mesa, datetime.now().isoformat(), qtd_pessoas))
            nova_comanda_id = cursor.lastrowid

            conn.commit()
            return {"status": "ok", "mesa_id": nova_mesa_id, "comanda_id": nova_comanda_id}

def excluir_mesa(mesa_id: int):
    """Exclui a mesa e cancela comanda associada."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE comandas 
            SET status = 'CANCELADA', mesa_id = NULL 
            WHERE mesa_id = ?
            """, (mesa_id,))
            cursor.execute("DELETE FROM mesas WHERE id = ?", (mesa_id,))
            conn.commit()

def cancelar_comanda(comanda_id: int):
    """Cancela a comanda e libera a mesa física."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT mesa_id FROM comandas WHERE id = ?", (comanda_id,))
            row = cursor.fetchone()
            mesa_id = row["mesa_id"] if row else None

            cursor.execute("""
            UPDATE comandas 
            SET status = 'CANCELADA', mesa_id = NULL 
            WHERE id = ?
            """, (comanda_id,))

            if mesa_id:
                cursor.execute("DELETE FROM mesas WHERE id = ?", (mesa_id,))
            conn.commit()

    _sync_push_imediato_ou_enfileirar("POST", f"/comandas/{comanda_id}/cancelar", {
        "comanda_id": comanda_id
    })

def obter_comanda_detalhes(comanda_id: int) -> Optional[dict]:
    """Retorna detalhes da comanda e seus itens lançados."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM comandas WHERE id = ?", (comanda_id,))
            c = cursor.fetchone()
            if not c:
                return None

            cursor.execute("""
            SELECT id, comanda_id, produto_id, nome_produto_historico, categoria_historico, quantidade, preco_momento, observacao
            FROM itens_comanda
            WHERE comanda_id = ?
            ORDER BY id ASC
            """, (comanda_id,))
            itens_rows = cursor.fetchall()

            itens_formatados = []
            total = 0.0
            for it in itens_rows:
                sub = float(it["quantidade"]) * float(it["preco_momento"])
                total += sub
                itens_formatados.append({
                    "id": it["id"],
                    "comanda_id": it["comanda_id"],
                    "produto_id": it["produto_id"],
                    "produto_nome": it["nome_produto_historico"],
                    "categoria_historico": it["categoria_historico"],
                    "quantidade": it["quantidade"],
                    "preco_momento": it["preco_momento"],
                    "subtotal": sub,
                    "observacao": it["observacao"] or ""
                })

            comanda_resp = dict(c)
            comanda_resp["numero_mesa"] = c["numero_mesa_historico"]
            comanda_resp["valor_total"] = total
            comanda_resp["taxa_servico"] = bool(c["taxa_servico"])

            return {
                "comanda": comanda_resp,
                "itens": itens_formatados,
                "total": total
            }

# ================= GESTÃO ATÔMICA DE ESTOQUE (BAIXA E RESTAURAÇÃO) =================

def _decrementar_estoque_cursor(cursor, produto_id: int, quantidade: int):
    """Baixa de estoque atômica: subtrai quantidade e se <= 0 atualiza disponivel = 0."""
    cursor.execute("SELECT qtd_disp, disponivel FROM produtos WHERE id = ?", (produto_id,))
    p = cursor.fetchone()
    if p:
        saldo = p["qtd_disp"] if p["qtd_disp"] is not None else 15
        novo_saldo = max(0, saldo - quantidade)
        novo_disp = 1 if novo_saldo > 0 else 0
        cursor.execute("""
        UPDATE produtos 
        SET qtd_disp = ?, disponivel = ? 
        WHERE id = ?
        """, (novo_saldo, novo_disp, produto_id))
        return novo_saldo, novo_disp
    return 0, 0

def _incrementar_estoque_cursor(cursor, produto_id: int, quantidade: int):
    """Estorno de estoque atômico: adiciona quantidade e reativa disponivel = 1."""
    cursor.execute("SELECT qtd_disp, disponivel FROM produtos WHERE id = ?", (produto_id,))
    p = cursor.fetchone()
    if p:
        saldo = p["qtd_disp"] if p["qtd_disp"] is not None else 0
        novo_saldo = saldo + quantidade
        novo_disp = 1 if novo_saldo > 0 else 0
        cursor.execute("""
        UPDATE produtos 
        SET qtd_disp = ?, disponivel = ? 
        WHERE id = ?
        """, (novo_saldo, novo_disp, produto_id))
        return novo_saldo, novo_disp
    return 0, 0

def adicionar_item_comanda(comanda_id: int, produto_id: int, quantidade: int = 1, observacao: str = ""):
    """Lança item na comanda com validação, baixa automática de estoque e enfileiramento Xano."""
    if quantidade <= 0:
        raise ValueError("A quantidade deve ser de no mínimo 1 item.")

    obs_sanitizada = html.escape(observacao.strip()) if observacao else ""

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
            produto = cursor.fetchone()
            if not produto:
                raise ValueError("Produto não encontrado.")

            cursor.execute("""
            SELECT id, quantidade FROM itens_comanda 
            WHERE comanda_id = ? AND produto_id = ?
            """, (comanda_id, produto_id))
            item_existente = cursor.fetchone()

            if item_existente:
                nova_qtd = item_existente["quantidade"] + quantidade
                cursor.execute("""
                UPDATE itens_comanda 
                SET quantidade = ?, observacao = COALESCE(NULLIF(?, ''), observacao)
                WHERE id = ?
                """, (nova_qtd, obs_sanitizada or "", item_existente["id"]))
            else:
                cursor.execute("""
                INSERT INTO itens_comanda (comanda_id, produto_id, nome_produto_historico, categoria_historico, quantidade, preco_momento, observacao)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    comanda_id,
                    produto["id"],
                    produto["nome"],
                    produto["categoria"],
                    quantidade,
                    float(produto["preco_unitario"]),
                    obs_sanitizada or ""
                ))

            # Baixa automática de estoque e esgotamento automático se zerar
            _decrementar_estoque_cursor(cursor, produto["id"], quantidade)

            conn.commit()

    # Sincronização imediata em lockstep com o Xano (ou fila coordenada)
    _sync_push_imediato_ou_enfileirar("POST", f"/comandas/{comanda_id}/itens", {
        "produto_query": produto["nome"],
        "quantidade": quantidade,
        "observacao": obs_sanitizada or ""
    })

def editar_item_comanda(item_id: int, quantidade: int, preco_momento: float, observacao: str = ""):
    """Edita quantidade, preço e observação com validações de integridade e sanitização."""
    if quantidade <= 0:
        raise ValueError("A quantidade deve ser de no mínimo 1 item.")
    if preco_momento < 0:
        raise ValueError("O preço não pode ser negativo.")

    obs_sanitizada = html.escape(observacao.strip()) if observacao else ""

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT produto_id, quantidade FROM itens_comanda WHERE id = ?", (item_id,))
            it_antigo = cursor.fetchone()
            if not it_antigo:
                raise ValueError("Item não encontrado.")

            diff_qtd = quantidade - it_antigo["quantidade"]

            cursor.execute("""
            UPDATE itens_comanda
            SET quantidade = ?, preco_momento = ?, observacao = ?
            WHERE id = ?
            """, (quantidade, preco_momento, obs_sanitizada or "", item_id))
            
            # Ajuste de estoque proporcional
            if diff_qtd > 0:
                _decrementar_estoque_cursor(cursor, it_antigo["produto_id"], diff_qtd)
            elif diff_qtd < 0:
                _incrementar_estoque_cursor(cursor, it_antigo["produto_id"], abs(diff_qtd))

            conn.commit()

    _sync_push_imediato_ou_enfileirar("PATCH", f"/itens_comanda/{item_id}", {
        "quantidade": quantidade,
        "preco_momento": preco_momento,
        "observacao": obs_sanitizada or ""
    })

def remover_item_comanda(item_id: int):
    """Remove item da comanda, estorna o estoque atômico e sincroniza exclusão no Xano."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT produto_id, quantidade FROM itens_comanda WHERE id = ?", (item_id,))
            it = cursor.fetchone()
            if it and it["produto_id"]:
                _incrementar_estoque_cursor(cursor, it["produto_id"], it["quantidade"])

            cursor.execute("DELETE FROM itens_comanda WHERE id = ?", (item_id,))
            conn.commit()

    _sync_push_imediato_ou_enfileirar("DELETE", f"/itens_comanda/{item_id}")

# ================= GESTÃO DE QR CODES DE MESAS E PRÉ-COMANDA =================

def listar_mesas_qrcodes() -> List[dict]:
    """Retorna as mesas configuradas com seus tokens de QR Code, status do salão e consumo atual."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT q.numero_mesa, q.token_qrcode, q.atualizado_em,
                   m.id as mesa_id, m.status as mesa_status, m.capacidade,
                   c.id as comanda_id
            FROM qrcodes_mesas q
            LEFT JOIN mesas m ON m.numero_mesa = q.numero_mesa
            LEFT JOIN comandas c ON c.mesa_id = m.id AND c.status = 'ABERTA'
            ORDER BY q.numero_mesa ASC
            """)
            rows = cursor.fetchall()
            resultado = []
            for r in rows:
                comanda_id = r["comanda_id"]
                total_mesa = 0.0
                if comanda_id:
                    cursor.execute("SELECT SUM(quantidade * preco_momento) as total FROM itens_comanda WHERE comanda_id = ?", (comanda_id,))
                    tot_row = cursor.fetchone()
                    if tot_row and tot_row["total"] is not None:
                        total_mesa = float(tot_row["total"])
                
                status_real = r["mesa_status"] or "LIVRE"
                resultado.append({
                    "numero_mesa": r["numero_mesa"],
                    "token_qrcode": r["token_qrcode"],
                    "atualizado_em": r["atualizado_em"],
                    "mesa_id": r["mesa_id"],
                    "status": status_real,
                    "comanda_id": comanda_id,
                    "total_atual": total_mesa,
                    "capacidade": r["capacidade"] or 4
                })
            return resultado

def atualizar_qrcode_mesa(numero_mesa: int) -> str:
    """Gera e grava um novo token estável e único para o QR Code da mesa."""
    novo_token = f"m{numero_mesa}-{uuid.uuid4().hex[:8]}"
    now_str = datetime.now().isoformat()
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO qrcodes_mesas (numero_mesa, token_qrcode, criado_em, atualizado_em)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(numero_mesa) DO UPDATE SET
                token_qrcode = excluded.token_qrcode,
                atualizado_em = excluded.atualizado_em
            """, (numero_mesa, novo_token, now_str, now_str))
            conn.commit()
    return novo_token

def confirmar_precomanda_cliente(numero_mesa: int, itens: List[dict]) -> dict:
    """
    Confirma os itens da pré-comanda enviada pelo cliente sentado na mesa.
    - Se a mesa estiver livre ou sem comanda aberta, abre automaticamente e atualiza para OCUPADA.
    - Lança cada item no SQLite.
    - Decrementa o estoque (qtd_disp) e se <= 0 atualiza disponivel = 0.
    - Enfileira no Xano para reconciliação remota.
    - Faz a mesa aparecer imediatamente no Painel Geral e no Salão de Mesas.
    """
    if not itens:
        raise ValueError("A pré-comanda está vazia. Adicione ao menos um prato antes de enviar.")
    if numero_mesa <= 0:
        raise ValueError("Número de mesa inválido.")

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Localiza a mesa física ou cria com status OCUPADA
            cursor.execute("SELECT id, status FROM mesas WHERE numero_mesa = ?", (numero_mesa,))
            mesa_row = cursor.fetchone()
            
            if not mesa_row:
                cursor.execute("""
                INSERT INTO mesas (numero_mesa, capacidade, status)
                VALUES (?, 4, 'OCUPADA')
                """, (numero_mesa,))
                mesa_id = cursor.lastrowid
            else:
                mesa_id = mesa_row["id"]
                if mesa_row["status"] != "OCUPADA":
                    cursor.execute("UPDATE mesas SET status = 'OCUPADA' WHERE id = ?", (mesa_id,))

            # 2. Localiza comanda ABERTA ou cria nova comanda
            cursor.execute("SELECT id FROM comandas WHERE mesa_id = ? AND status = 'ABERTA'", (mesa_id,))
            comanda_row = cursor.fetchone()
            if comanda_row:
                comanda_id = comanda_row["id"]
            else:
                cursor.execute("""
                INSERT INTO comandas (mesa_id, numero_mesa_historico, data_abertura, status, taxa_servico, qtd_pessoas, valor_total)
                VALUES (?, ?, ?, 'ABERTA', 1, 2, 0.0)
                """, (mesa_id, numero_mesa, datetime.now().isoformat()))
                comanda_id = cursor.lastrowid

            # 3. Processa e lança cada item
            itens_confirmados = []
            for item in itens:
                prod_id = int(item["produto_id"])
                qtd = int(item.get("quantidade", 1))
                obs = html.escape(str(item.get("observacao", "")).strip())
                if qtd <= 0:
                    continue

                cursor.execute("SELECT id, nome, categoria, preco_unitario, qtd_disp, disponivel FROM produtos WHERE id = ?", (prod_id,))
                prod = cursor.fetchone()
                if not prod:
                    continue

                # Se já há o mesmo produto lançado na comanda, soma quantidade
                cursor.execute("SELECT id, quantidade FROM itens_comanda WHERE comanda_id = ? AND produto_id = ?", (comanda_id, prod_id))
                existente = cursor.fetchone()
                if existente:
                    nova_qtd = existente["quantidade"] + qtd
                    cursor.execute("""
                    UPDATE itens_comanda 
                    SET quantidade = ?, observacao = COALESCE(NULLIF(?, ''), observacao)
                    WHERE id = ?
                    """, (nova_qtd, obs or "", existente["id"]))
                else:
                    cursor.execute("""
                    INSERT INTO itens_comanda (comanda_id, produto_id, nome_produto_historico, categoria_historico, quantidade, preco_momento, observacao)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (comanda_id, prod["id"], prod["nome"], prod["categoria"], qtd, float(prod["preco_unitario"]), obs or ""))

                # Baixa atômica de estoque
                _decrementar_estoque_cursor(cursor, prod["id"], qtd)

                itens_confirmados.append({
                    "produto_id": prod["id"],
                    "nome": prod["nome"],
                    "quantidade": qtd,
                    "preco_unitario": float(prod["preco_unitario"]),
                    "observacao": obs
                })

            conn.commit()

    # Sincronização imediata (ou fila coordenada) com o Xano fora do lock de banco
    for it_conf in itens_confirmados:
        _sync_push_imediato_ou_enfileirar("POST", f"/comandas/{comanda_id}/itens", {
            "produto_query": it_conf["nome"],
            "quantidade": it_conf["quantidade"],
            "observacao": it_conf["observacao"]
        })

    return {
        "status": "sucesso",
        "mesa_id": mesa_id,
        "numero_mesa": numero_mesa,
        "comanda_id": comanda_id,
        "itens_confirmados": itens_confirmados,
        "total_itens": len(itens_confirmados)
    }

def fechar_comanda(comanda_id: int, valor_final: float, taxa_servico: bool = True):
    """Finaliza a comanda, libera a mesa física no SQLite e despacha evento crítico ao Xano."""
    if valor_final < 0:
        raise ValueError("O valor final da comanda não pode ser negativo.")

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT mesa_id FROM comandas WHERE id = ?", (comanda_id,))
            c = cursor.fetchone()
            if not c:
                raise ValueError("Comanda não encontrada.")

            mesa_id = c["mesa_id"]

            cursor.execute("""
            UPDATE comandas
            SET status = 'PAGA', data_fechamento = ?, valor_total = ?, taxa_servico = ?, mesa_id = NULL
            WHERE id = ?
            """, (datetime.now().isoformat(), round(valor_final, 2), 1 if taxa_servico else 0, comanda_id))

            if mesa_id:
                cursor.execute("DELETE FROM mesas WHERE id = ?", (mesa_id,))
            conn.commit()

    _sync_push_imediato_ou_enfileirar("POST", f"/comandas/{comanda_id}/fechar", {
        "valor_final": round(valor_final, 2),
        "taxa_servico": taxa_servico
    })

# ================= OPERAÇÕES DE PRODUTOS =================

def listar_produtos(busca: Optional[str] = None, categoria: Optional[str] = None, apenas_disponiveis: bool = False) -> List[dict]:
    """Lista os produtos do cardápio com suporte a busca textual, filtro de categoria, status e todos os metadados."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = """
            SELECT id, codigo_pdv, nome, categoria, preco_unitario,
                   COALESCE(descricao, '') as descricao,
                   COALESCE(url_imagem, '') as url_imagem,
                   COALESCE(qtd_disp, 0) as qtd_disp,
                   COALESCE(precisa_produzir, 1) as precisa_produzir,
                   COALESCE(disponivel, 1) as disponivel
            FROM produtos
            WHERE 1=1
            """
            params = []
            if busca:
                termo = f"%{busca.strip()}%"
                query += " AND (codigo_pdv LIKE ? OR nome LIKE ? OR categoria LIKE ? OR descricao LIKE ?)"
                params.extend([termo, termo, termo, termo])
            if categoria and categoria != "Todas":
                query += " AND categoria = ?"
                params.append(categoria)
            if apenas_disponiveis:
                query += " AND disponivel = 1"

            query += " ORDER BY categoria ASC, CAST(codigo_pdv AS INTEGER) ASC, nome ASC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

def criar_produto(
    codigo_pdv: str,
    nome: str,
    categoria: str,
    preco_unitario: float,
    descricao: str = "",
    url_imagem: str = "",
    qtd_disp: int = 15,
    precisa_produzir: bool = True,
    disponivel: bool = True
) -> dict:
    """Cadastra produto validando preço estritamente positivo, estoque não negativo e sanitizando entradas contra XSS."""
    cod = str(codigo_pdv).strip()
    if not cod:
        raise ValueError("Código PDV não pode ser vazio.")
    if preco_unitario <= 0:
        raise ValueError("O preço unitário deve ser estritamente positivo (maior que zero).")
    if qtd_disp < 0:
        raise ValueError("A quantidade disponível em estoque não pode ser negativa.")

    nome_sanitizado = html.escape(nome.strip())
    cat_sanitizada = html.escape(categoria.strip())
    desc_sanitizada = html.escape(descricao.strip()) if descricao else ""
    url_sanitizada = url_imagem.strip() if url_imagem else ""

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM produtos WHERE LOWER(codigo_pdv) = LOWER(?)", (cod,))
            if cursor.fetchone():
                raise ValueError(f"Código PDV '{cod}' já cadastrado no sistema.")

            cursor.execute("""
            INSERT INTO produtos (
                codigo_pdv, nome, categoria, preco_unitario,
                descricao, url_imagem, qtd_disp, precisa_produzir, disponivel
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cod,
                nome_sanitizado,
                cat_sanitizada,
                float(preco_unitario),
                desc_sanitizada,
                url_sanitizada,
                int(qtd_disp),
                1 if precisa_produzir else 0,
                1 if disponivel else 0
            ))
            novo_id = cursor.lastrowid
            conn.commit()

            prod_dict = {
                "id": novo_id,
                "codigo_pdv": cod,
                "nome": nome_sanitizado,
                "categoria": cat_sanitizada,
                "preco_unitario": float(preco_unitario),
                "descricao": desc_sanitizada,
                "url_imagem": url_sanitizada,
                "qtd_disp": int(qtd_disp),
                "precisa_produzir": 1 if precisa_produzir else 0,
                "disponivel": 1 if disponivel else 0
            }

    _sync_push_imediato_ou_enfileirar("POST", "/produto", {
        "codigo_pdv": cod,
        "nome": nome_sanitizado,
        "categoria": cat_sanitizada,
        "preco": float(preco_unitario),
        "descricao": desc_sanitizada,
        "url_imagem": url_sanitizada,
        "qtd_disp": int(qtd_disp),
        "precisa_produzir": bool(precisa_produzir),
        "disponivel": bool(disponivel)
    })

    return prod_dict

def atualizar_produto(
    produto_id: int,
    codigo_pdv: str,
    nome: str,
    categoria: str,
    preco_unitario: float,
    descricao: str = "",
    url_imagem: str = "",
    qtd_disp: int = 15,
    precisa_produzir: bool = True,
    disponivel: bool = True
):
    """Atualiza dados cadastrais e operacionais de um produto."""
    cod = str(codigo_pdv).strip()
    if not cod:
        raise ValueError("Código PDV não pode ser vazio.")
    if preco_unitario <= 0:
        raise ValueError("O preço unitário deve ser estritamente positivo (maior que zero).")
    if qtd_disp < 0:
        raise ValueError("A quantidade disponível não pode ser negativa.")

    nome_sanitizado = html.escape(nome.strip())
    cat_sanitizada = html.escape(categoria.strip())
    desc_sanitizada = html.escape(descricao.strip()) if descricao else ""
    url_sanitizada = url_imagem.strip() if url_imagem else ""

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM produtos WHERE LOWER(codigo_pdv) = LOWER(?) AND id != ?", (cod, produto_id))
            if cursor.fetchone():
                raise ValueError(f"Código PDV '{cod}' já em uso por outro produto.")

            cursor.execute("""
            UPDATE produtos
            SET codigo_pdv = ?, nome = ?, categoria = ?, preco_unitario = ?,
                descricao = ?, url_imagem = ?, qtd_disp = ?, precisa_produzir = ?, disponivel = ?
            WHERE id = ?
            """, (
                cod,
                nome_sanitizado,
                cat_sanitizada,
                float(preco_unitario),
                desc_sanitizada,
                url_sanitizada,
                int(qtd_disp),
                1 if precisa_produzir else 0,
                1 if disponivel else 0,
                produto_id
            ))
            if cursor.rowcount == 0:
                raise ValueError("Produto não encontrado.")
            conn.commit()

    _sync_push_imediato_ou_enfileirar("PATCH", f"/produto/{produto_id}", {
        "codigo_pdv": cod,
        "nome": nome_sanitizado,
        "categoria": cat_sanitizada,
        "preco": float(preco_unitario),
        "descricao": desc_sanitizada,
        "url_imagem": url_sanitizada,
        "qtd_disp": int(qtd_disp),
        "precisa_produzir": bool(precisa_produzir),
        "disponivel": bool(disponivel)
    })

def excluir_produto(produto_id: int):
    """Exclui produto do cardápio e sincroniza exclusão no Xano."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
            conn.commit()

    _sync_push_imediato_ou_enfileirar("DELETE", f"/produto/{produto_id}")

def sincronizar_produtos_xano() -> int:
    """
    Sincroniza o catálogo local do SQLite puxando os dados reais diretamente da tabela PRODUTO do Xano,
    incluindo URLs reais de fotos (Imgur), descrições completas, estoque e preços.
    Realiza espelhamento fiel (prunando do SQLite produtos que foram excluídos ou não existem no Xano).
    """
    url = f"{XANO_BASE_URL.rstrip('/')}/produto"
    try:
        headers = {"Content-Type": "application/json"}
        if XANO_API_KEY:
            headers["Authorization"] = f"Bearer {XANO_API_KEY}"
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=headers)
            _registrar_chamada_xano()
            if resp.status_code != 200:
                logger.warning(f"Falha ao consultar produtos no Xano (HTTP {resp.status_code})")
                return 0
            prods_xano = resp.json()

        sincronizados = 0
        with _db_lock:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM produtos;")
                for px in prods_xano:
                    nome = str(px.get("nome") or "").strip()
                    # Ignorar registros corrompidos de teste ou vazios
                    if not nome or nome.startswith("&lt;script") or nome.startswith("<script"):
                        continue

                    cod = str(px.get("codigo_pdv") or px.get("id") or "").strip()
                    if not cod:
                        continue

                    desc = str(px.get("descricao") or "").strip()
                    foto = str(px.get("url_imagem") or "").strip()
                    preco = float(px.get("preco") or px.get("preco_unitario") or 10.0)
                    if preco <= 0:
                        preco = 10.0
                    categoria = str(px.get("categoria") or "Comida").strip()
                    qtd = int(px.get("qtd_disp") or 10)
                    precisa = 1 if px.get("precisa_produzir") else 0
                    disp = 1 if px.get("disponivel", True) else 0

                    xano_id = int(px.get("id"))
                    cursor.execute("""
                    INSERT INTO produtos (
                        id, codigo_pdv, nome, categoria, preco_unitario,
                        descricao, url_imagem, qtd_disp, precisa_produzir, disponivel
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (xano_id, cod, nome, categoria, preco, desc, foto, qtd, precisa, disp))
                    sincronizados += 1

                # Reativa tarefas que possam ter sido bloqueadas por rate limit 429
                cursor.execute("""
                UPDATE fila_sincronizacao 
                SET status = 'PENDENTE', tentativas = 0 
                WHERE status = 'ERRO' AND ultimo_erro LIKE '%429%'
                """)

                conn.commit()
        logger.info(f"Sincronização com Xano concluída: {sincronizados} produtos atualizados com fotos reais.")
        return sincronizados
    except Exception as e:
        logger.warning(f"Erro ao sincronizar com Xano: {e}")
        return 0

# ================= RELATÓRIOS E PDF =================

def obter_dashboard_dados(periodo: str = "7d") -> dict:
    """Calcula indicadores executivos de faturamento diretamente via queries no SQLite filtradas por período."""
    mapa_dias = {"1d": 1, "7d": 7, "15d": 15, "30d": 30}
    dias = mapa_dias.get(periodo)

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            if dias is not None:
                data_limite = (datetime.now() - timedelta(days=dias)).isoformat()
                cursor.execute("""
                SELECT id, mesa_id, numero_mesa_historico, data_fechamento, qtd_pessoas, valor_total
                FROM comandas
                WHERE status = 'PAGA' AND data_fechamento >= ?
                ORDER BY data_fechamento DESC
                """, (data_limite,))
            else:
                cursor.execute("""
                SELECT id, mesa_id, numero_mesa_historico, data_fechamento, qtd_pessoas, valor_total
                FROM comandas
                WHERE status = 'PAGA'
                ORDER BY data_fechamento DESC
                """)
            pagas = cursor.fetchall()

            faturamento_total = 0.0
            total_pessoas = 0
            comandas_formatadas = []
            vendas_cat_map: Dict[str, float] = {}
            top_prod_map: Dict[str, dict] = {}
            evolucao_map: Dict[str, float] = {}

            for c in pagas:
                c_id = c["id"]
                v_total = float(c["valor_total"] or 0.0)
                q_pax = int(c["qtd_pessoas"] or 1)
                n_mesa = c["numero_mesa_historico"] or c["mesa_id"] or "-"
                dt_fechamento = c["data_fechamento"] or datetime.now().isoformat()

                faturamento_total += v_total
                total_pessoas += q_pax

                comandas_formatadas.append({
                    "id": c_id,
                    "numero_mesa": n_mesa,
                    "data_fechamento": dt_fechamento,
                    "qtd_pessoas": q_pax,
                    "valor_total": v_total
                })

                try:
                    dia_str = datetime.fromisoformat(str(dt_fechamento).replace("Z", "+00:00")).strftime("%d/%m")
                except Exception:
                    dia_str = datetime.now().strftime("%d/%m")
                evolucao_map[dia_str] = evolucao_map.get(dia_str, 0.0) + v_total

                cursor.execute("""
                SELECT nome_produto_historico, categoria_historico, quantidade, preco_momento
                FROM itens_comanda
                WHERE comanda_id = ?
                """, (c_id,))
                itens = cursor.fetchall()

                for it in itens:
                    p_nome = it["nome_produto_historico"] or "Item"
                    p_cat = it["categoria_historico"] or "Geral"
                    p_qtd = int(it["quantidade"] or 1)
                    p_sub = p_qtd * float(it["preco_momento"] or 0.0)

                    vendas_cat_map[p_cat] = vendas_cat_map.get(p_cat, 0.0) + p_sub

                    if p_nome not in top_prod_map:
                        top_prod_map[p_nome] = {"nome": p_nome, "categoria": p_cat, "quantidade_total": 0, "faturamento_total": 0.0}
                    top_prod_map[p_nome]["quantidade_total"] += p_qtd
                    top_prod_map[p_nome]["faturamento_total"] += p_sub

            total_comandas = len(comandas_formatadas)
            ticket_medio = (faturamento_total / total_comandas) if total_comandas > 0 else 0.0
            ticket_por_pessoa = (faturamento_total / total_pessoas) if total_pessoas > 0 else 0.0

            return {
                "periodo": periodo,
                "resumo": {
                    "faturamento_total": faturamento_total,
                    "total_comandas": total_comandas,
                    "ticket_medio": ticket_medio,
                    "total_pessoas": total_pessoas,
                    "ticket_por_pessoa": ticket_por_pessoa
                },
                "evolucao_diaria": [{"data": k, "total": v} for k, v in evolucao_map.items()],
                "vendas_por_categoria": [{"categoria": k, "total": v, "quantidade": 1} for k, v in vendas_cat_map.items()],
                "top_produtos": sorted(top_prod_map.values(), key=lambda x: x["quantidade_total"], reverse=True)[:8],
                "comandas_finalizadas": comandas_formatadas
            }

def gerar_pdf_bytes(periodo: str = "7d") -> bytes:
    """Gera o documento de relatório executivo em bytes PDF usando ReportLab (Lazy Loaded sob demanda)."""
    # Lazy Import do ReportLab: Só carrega na memória quando alguém explicitamente pedir o PDF
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    data = obter_dashboard_dados(periodo)
    mapa_dias = {
        "1d": "Últimas 24 Horas",
        "7d": "Últimos 7 Dias",
        "15d": "Últimos 15 Dias",
        "30d": "Últimos 30 Dias"
    }
    titulo_periodo = mapa_dias.get(periodo, "Últimos 7 Dias")
    gerado_em = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#d97706'),
        spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        'HeaderSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=10
    )
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=4
    )
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#1e293b')
    )
    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        textColor=colors.HexColor('#0f172a')
    )
    kpi_title_style = ParagraphStyle(
        'KPITitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        textColor=colors.HexColor('#64748b')
    )
    kpi_val_style = ParagraphStyle(
        'KPIVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#0f172a')
    )

    elements = []
    elements.append(Paragraph("ChurrasControl - Relatório Executivo de Vendas", title_style))
    elements.append(Paragraph(f"Período: <b>{titulo_periodo}</b> | Emitido em: {gerado_em}", subtitle_style))
    elements.append(Spacer(1, 4 * mm))

    resumo = data.get('resumo', {})
    fat_total = f"R$ {float(resumo.get('faturamento_total', 0)):.2f}"
    tot_com = str(resumo.get('total_comandas', 0))
    tkt_med = f"R$ {float(resumo.get('ticket_medio', 0)):.2f}"
    tot_pax = f"{resumo.get('total_pessoas', 0)} pessoas"

    kpi_data = [
        [
            Paragraph("FATURAMENTO TOTAL", kpi_title_style),
            Paragraph("MESAS FINALIZADAS", kpi_title_style),
            Paragraph("TICKET MÉDIO / MESA", kpi_title_style),
            Paragraph("TOTAL DE PESSOAS", kpi_title_style),
        ],
        [
            Paragraph(fat_total, kpi_val_style),
            Paragraph(tot_com, kpi_val_style),
            Paragraph(tkt_med, kpi_val_style),
            Paragraph(tot_pax, kpi_val_style),
        ]
    ]
    t_kpi = Table(kpi_data, colWidths=[45 * mm, 45 * mm, 45 * mm, 45 * mm])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t_kpi)
    elements.append(Spacer(1, 6 * mm))

    elements.append(Paragraph("1. Vendas por Categoria", section_style))
    cat_rows = [[Paragraph("Categoria", cell_bold), Paragraph("Quantidade", cell_bold), Paragraph("Total Faturado", cell_bold)]]
    for c in data.get('vendas_por_categoria', []):
        cat_rows.append([
            Paragraph(str(c.get('categoria', '')), cell_style),
            Paragraph(f"{c.get('quantidade', 0)} un", cell_style),
            Paragraph(f"R$ {float(c.get('total', 0)):.2f}", cell_bold)
        ])
    if len(cat_rows) == 1:
        cat_rows.append([Paragraph("Nenhum dado registrado no período.", cell_style), Paragraph("-", cell_style), Paragraph("-", cell_style)])

    t_cat = Table(cat_rows, colWidths=[80 * mm, 40 * mm, 60 * mm])
    t_cat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#cbd5e1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(t_cat)
    elements.append(Spacer(1, 5 * mm))

    elements.append(Paragraph("2. Top Produtos Mais Vendidos", section_style))
    prod_rows = [[Paragraph("Produto", cell_bold), Paragraph("Categoria", cell_bold), Paragraph("Qtd", cell_bold), Paragraph("Total Gerado", cell_bold)]]
    for p in data.get('top_produtos', []):
        prod_rows.append([
            Paragraph(str(p.get('nome', '')), cell_style),
            Paragraph(str(p.get('categoria', '')), cell_style),
            Paragraph(f"{p.get('quantidade_total', 0)}x", cell_bold),
            Paragraph(f"R$ {float(p.get('faturamento_total', 0)):.2f}", cell_bold)
        ])
    if len(prod_rows) == 1:
        prod_rows.append([Paragraph("Nenhum item vendido no período.", cell_style), Paragraph("-", cell_style), Paragraph("-", cell_style), Paragraph("-", cell_style)])

    t_prod = Table(prod_rows, colWidths=[75 * mm, 40 * mm, 25 * mm, 40 * mm])
    t_prod.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#cbd5e1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(t_prod)

    doc.build(elements)
    buffer.seek(0)
    pdf_output = buffer.getvalue()
    buffer.close()
    return pdf_output

# Versão memorizada em cache com descarte de instâncias pesadas de canvas
try:
    import streamlit as st
    @st.cache_data(ttl=180, max_entries=4, show_spinner=False)
    def gerar_pdf_bytes_cached(periodo: str = "7d") -> bytes:
        """Gera bytes do PDF com cache TTL para evitar reprocessamento do ReportLab em cada rerun."""
        return gerar_pdf_bytes(periodo)
except Exception:
    def gerar_pdf_bytes_cached(periodo: str = "7d") -> bytes:
        return gerar_pdf_bytes(periodo)


# ================= GESTÃO DE COLABORADORES E AUTENTICAÇÃO (RBAC) =================

def _gerar_hash_senha(senha: str) -> str:
    """Gera hash criptográfico SHA-256 com salt estático da aplicação."""
    raw = f"{CHURRAS_SALT}:{str(senha).strip()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def autenticar_usuario(email: str, senha: str) -> Optional[dict]:
    """Valida as credenciais de um colaborador e retorna seu perfil se ativo com dados sensíveis descriptografados."""
    init_db()
    email_limpo = str(email).strip().lower()
    senha_hash = _gerar_hash_senha(senha)
    
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, nome, email, numero, cargo, primeiro_acesso, ativo
            FROM colaboradores
            WHERE LOWER(email) = ? AND senha_hash = ? AND ativo = 1
            """, (email_limpo, senha_hash))
            row = cursor.fetchone()
            if row:
                nome_dec = descriptografar_dado(row["nome"])
                numero_dec = descriptografar_dado(row["numero"])
                cargo_dec = descriptografar_dado(row["cargo"])
                return {
                    "id": row["id"],
                    "nome": nome_dec,
                    "email": row["email"],
                    "numero": numero_dec,
                    "cargo": cargo_dec,
                    "primeiro_acesso": bool(row["primeiro_acesso"]),
                    "ativo": bool(row["ativo"])
                }
    return None

def cadastrar_colaborador(nome: str, email: str, senha: str, numero: str, cargo: str) -> dict:
    """Cadastra um novo colaborador criptografando nome, telefone, cargo e senha no SQLite e no Xano."""
    init_db()
    nome_limpo = html.escape(str(nome).strip())
    email_limpo = str(email).strip().lower()
    numero_limpo = html.escape(str(numero).strip())
    cargo_limpo = str(cargo).strip().lower()
    
    if not nome_limpo or not email_limpo or not senha.strip():
        raise ValueError("Nome, email e senha são obrigatórios.")
    if cargo_limpo not in ("caixa", "gerente"):
        raise ValueError("O cargo deve ser obrigatoriamente 'caixa' ou 'gerente'.")
    if "@" not in email_limpo:
        raise ValueError("Formato de e-mail inválido.")

    # Criptografia simétrica com chave Fernet dos dados sensíveis
    nome_cifrado = criptografar_dado(nome_limpo)
    numero_cifrado = criptografar_dado(numero_limpo)
    cargo_cifrado = criptografar_dado(cargo_limpo)
    senha_hash = _gerar_hash_senha(senha)
    agora_iso = datetime.now().isoformat()

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Validação de unicidade do e-mail
            cursor.execute("SELECT id FROM colaboradores WHERE LOWER(email) = ?", (email_limpo,))
            if cursor.fetchone():
                raise ValueError(f"Já existe um colaborador cadastrado com o e-mail '{email_limpo}'.")
            
            cursor.execute("""
            INSERT INTO colaboradores (nome, email, senha_hash, numero, cargo, primeiro_acesso, ativo, criado_em, atualizado_em)
            VALUES (?, ?, ?, ?, ?, 1, 1, ?, ?)
            """, (nome_cifrado, email_limpo, senha_hash, numero_cifrado, cargo_cifrado, agora_iso, agora_iso))
            novo_id = cursor.lastrowid
            conn.commit()

    # Sincronização imediata (ou fila coordenada) com o Xano contendo os dados estritamente criptografados
    _sync_push_imediato_ou_enfileirar("POST", "/colaborador", {
        "id": novo_id,
        "nome": nome_cifrado,
        "email": email_limpo,
        "numero": numero_cifrado,
        "cargo": cargo_cifrado,
        "senha_hash": senha_hash,
        "primeiro_acesso": 1
    })

    return {
        "id": novo_id,
        "nome": nome_limpo,
        "email": email_limpo,
        "numero": numero_limpo,
        "cargo": cargo_limpo,
        "primeiro_acesso": True,
        "ativo": True
    }

def atualizar_senha_colaborador(usuario_id: int, nova_senha: str) -> bool:
    """Atualiza a senha do colaborador e desativa a flag de primeiro acesso."""
    init_db()
    if not str(nova_senha).strip() or len(str(nova_senha).strip()) < 4:
        raise ValueError("A nova senha deve possuir pelo menos 4 caracteres.")
    
    senha_hash = _gerar_hash_senha(nova_senha)
    agora_iso = datetime.now().isoformat()

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE colaboradores
            SET senha_hash = ?, primeiro_acesso = 0, atualizado_em = ?
            WHERE id = ?
            """, (senha_hash, agora_iso, usuario_id))
            if cursor.rowcount == 0:
                return False
            conn.commit()

    _sync_push_imediato_ou_enfileirar("PATCH", f"/colaborador/{usuario_id}", {
        "primeiro_acesso": 0,
        "atualizado_em": agora_iso
    })
    return True

def listar_colaboradores() -> List[dict]:
    """Lista todos os colaboradores cadastrados descriptografando dinamicamente nome, telefone e cargo."""
    init_db()
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, nome, email, numero, cargo, primeiro_acesso, ativo, criado_em, atualizado_em
            FROM colaboradores
            ORDER BY id ASC
            """)
            rows = cursor.fetchall()
            lista = []
            for r in rows:
                lista.append({
                    "id": r["id"],
                    "nome": descriptografar_dado(r["nome"]),
                    "email": r["email"],
                    "numero": descriptografar_dado(r["numero"]),
                    "cargo": descriptografar_dado(r["cargo"]),
                    "primeiro_acesso": bool(r["primeiro_acesso"]),
                    "ativo": bool(r["ativo"]),
                    "criado_em": r["criado_em"],
                    "atualizado_em": r["atualizado_em"]
                })
            lista.sort(key=lambda x: (x["cargo"], x["nome"]))
            return lista

def excluir_colaborador(usuario_id: int) -> bool:
    """Remove um colaborador do banco de dados (não permite excluir se for o único gerente)."""
    init_db()
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT cargo, ativo FROM colaboradores WHERE id = ?", (usuario_id,))
            target = cursor.fetchone()
            if not target:
                return False
            
            cargo_target = descriptografar_dado(target["cargo"])
            if cargo_target == "gerente":
                # Contabiliza quantos gerentes ativos existem no total
                cursor.execute("SELECT cargo, ativo FROM colaboradores WHERE ativo = 1")
                todos_ativos = cursor.fetchall()
                gerentes_ativos = [c for c in todos_ativos if descriptografar_dado(c["cargo"]) == "gerente"]
                if len(gerentes_ativos) <= 1:
                    raise ValueError("Não é possível remover o único gerente administrador ativo do sistema.")

            cursor.execute("DELETE FROM colaboradores WHERE id = ?", (usuario_id,))
            conn.commit()

    _sync_push_imediato_ou_enfileirar("DELETE", f"/colaborador/{usuario_id}")
    return True

def sincronizar_colaboradores_xano() -> int:
    """
    Sincroniza os colaboradores locais do SQLite puxando os dados criptografados diretamente do Xano
    em uma única chamada GET (1 requisição HTTP), prevenindo rate limit.
    """
    url = f"{XANO_BASE_URL.rstrip('/')}/colaborador"
    try:
        headers = {"Content-Type": "application/json"}
        if XANO_API_KEY:
            headers["Authorization"] = f"Bearer {XANO_API_KEY}"
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=headers)
            _registrar_chamada_xano()
            if resp.status_code != 200:
                logger.warning(f"Falha ao consultar colaboradores no Xano (HTTP {resp.status_code})")
                return 0
            colabs_xano = resp.json()

        sincronizados = 0
        with _db_lock:
            with get_connection() as conn:
                cursor = conn.cursor()
                agora_iso = datetime.now().isoformat()
                for cx in colabs_xano:
                    email = str(cx.get("email") or "").strip().lower()
                    if not email or "@" not in email:
                        continue
                    
                    nome = str(cx.get("nome") or "").strip()
                    numero = str(cx.get("numero") or "").strip()
                    cargo = str(cx.get("cargo") or "caixa").strip()
                    senha_hash = str(cx.get("senha_hash") or "").strip()
                    p_acesso = 1 if cx.get("primeiro_acesso", True) else 0
                    ativo = 1 if cx.get("ativo", True) else 0
                    xano_id = int(cx.get("id"))

                    # Garantir que campos confidenciais tenham o envelope Fernet
                    if not nome.startswith("ENC:"):
                        nome = criptografar_dado(nome)
                    if not numero.startswith("ENC:"):
                        numero = criptografar_dado(numero)
                    if not cargo.startswith("ENC:"):
                        cargo = criptografar_dado(cargo)

                    cursor.execute("SELECT id FROM colaboradores WHERE LOWER(email) = ? OR id = ?", (email, xano_id))
                    row = cursor.fetchone()
                    if row:
                        cursor.execute("""
                        UPDATE colaboradores
                        SET id = ?, nome = ?, email = ?, senha_hash = ?, numero = ?, cargo = ?,
                            primeiro_acesso = ?, ativo = ?, atualizado_em = ?
                        WHERE id = ?
                        """, (xano_id, nome, email, senha_hash, numero, cargo, p_acesso, ativo, agora_iso, row["id"]))
                    else:
                        cursor.execute("""
                        INSERT INTO colaboradores (id, nome, email, senha_hash, numero, cargo, primeiro_acesso, ativo, criado_em, atualizado_em)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (xano_id, nome, email, senha_hash, numero, cargo, p_acesso, ativo, agora_iso, agora_iso))
                    sincronizados += 1
                conn.commit()
        logger.info(f"Sincronização de colaboradores com Xano concluída: {sincronizados} colaboradores sincronizados.")
        return sincronizados
    except Exception as e:
        logger.warning(f"Erro ao sincronizar colaboradores com Xano: {e}")
        return 0


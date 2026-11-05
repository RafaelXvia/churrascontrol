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
import secrets
import httpx
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import hmac
import base64
import smtplib
from email.message import EmailMessage
from cryptography.fernet import Fernet, InvalidToken

_DEFAULT_SALT = "CC_SALT_2026_INNOVATION_LAB"
CHURRAS_SALT = os.getenv("CHURRAS_SALT") or _DEFAULT_SALT

# Chave mestra Fernet lida do ambiente com fallback retrocompatível para leitura de dados existentes
_legacy_raw_key = hashlib.sha256(b"CHURRASCONTROL_FERNET_MASTER_KEY_2026_INNOVATION_LAB").digest()
_LEGACY_FERNET_KEY = base64.urlsafe_b64encode(_legacy_raw_key)
_legacy_cipher_suite = Fernet(_LEGACY_FERNET_KEY)

_env_fernet_secret = os.getenv("FERNET_MASTER_KEY", "").strip()
if _env_fernet_secret:
    try:
        # Aceita chave Fernet base64 válida ou deriva 32 bytes SHA-256 a partir da passphrase definida no .env
        if len(_env_fernet_secret) == 44 and _env_fernet_secret.endswith("="):
            _FERNET_MASTER_KEY = _env_fernet_secret.encode("utf-8")
        else:
            _FERNET_MASTER_KEY = base64.urlsafe_b64encode(hashlib.sha256(_env_fernet_secret.encode("utf-8")).digest())
        _cipher_suite = Fernet(_FERNET_MASTER_KEY)
    except Exception:
        _FERNET_MASTER_KEY = _LEGACY_FERNET_KEY
        _cipher_suite = _legacy_cipher_suite
else:
    _FERNET_MASTER_KEY = _LEGACY_FERNET_KEY
    _cipher_suite = _legacy_cipher_suite

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
    """Descriptografa um token cifrado Fernet com prefixo 'ENC:'. Suporta rotação de chave com fallback legado."""
    if not texto_cifrado:
        return ""
    texto_str = str(texto_cifrado).strip()
    if not texto_str.startswith("ENC:"):
        return texto_str
    token = texto_str[4:].encode("utf-8")
    try:
        return _cipher_suite.decrypt(token).decode("utf-8")
    except (InvalidToken, Exception):
        try:
            return _legacy_cipher_suite.decrypt(token).decode("utf-8")
        except (InvalidToken, Exception) as e:
            logger.warning(f"Falha ao descriptografar token: {e}")
            return texto_str


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ChurrasControl")

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# CHURRAS_DB_PATH permite isolar o banco (ex.: suíte de testes em cópia temporária), protegendo o histórico real.
DB_PATH = os.getenv("CHURRAS_DB_PATH") or os.path.join(_PROJECT_ROOT, "churrascontrol.db")
LEGACY_JSON_PATH = os.path.join(_PROJECT_ROOT, "churras_data.json")
XANO_BASE_URL = os.getenv("XANO_BASE_URL", "https://x8ki-letl-twmt.n7.xano.io/api:churrascontrol")
XANO_API_KEY = os.getenv("XANO_API_KEY", os.getenv("XANO_AUTH_TOKEN", ""))

_db_lock = threading.RLock()
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

def _auto_recuperar_banco_corrompido():
    """
    Se o arquivo .db foi corrompido no deploy/upload (ex: Discloud, Docker, cópia sem .db-wal),
    isola o arquivo corrompido em backup e cria um banco limpo e operacional automaticamente.
    """
    try:
        import shutil
        agora_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        if os.path.exists(DB_PATH):
            bak_path = f"{DB_PATH}.corrupt_{agora_str}.bak"
            try:
                shutil.copy2(DB_PATH, bak_path)
            except Exception:
                pass
            try:
                os.remove(DB_PATH)
            except Exception:
                try:
                    with open(DB_PATH, "wb") as f:
                        f.truncate(0)
                except Exception:
                    pass
        for ext in ["-wal", "-shm", "-journal"]:
            f_sidecar = f"{DB_PATH}{ext}"
            if os.path.exists(f_sidecar):
                try:
                    os.remove(f_sidecar)
                except Exception:
                    pass
        logger.warning("Banco corrompido isolado e limpo com sucesso para auto-recuperação.")
    except Exception as err:
        logger.error(f"Erro ao auto-recuperar banco corrompido: {err}")

def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão SQLite leve em modo WAL com timeout concorrente e recuperação automática."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=25.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        conn.execute("PRAGMA cache_size = -2000;")
        conn.execute("PRAGMA temp_store = MEMORY;")
        return conn
    except sqlite3.DatabaseError as e:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
        err_msg = str(e).lower()
        if "malformed" in err_msg or "corrupt" in err_msg or "not a database" in err_msg:
            logger.error(f"Detectado 'database disk image is malformed' ({e}). Executando auto-recuperação do banco...")
            _auto_recuperar_banco_corrompido()
            conn2 = sqlite3.connect(DB_PATH, timeout=25.0, check_same_thread=False)
            conn2.row_factory = sqlite3.Row
            conn2.execute("PRAGMA journal_mode = WAL;")
            conn2.execute("PRAGMA synchronous = NORMAL;")
            conn2.execute("PRAGMA foreign_keys = ON;")
            conn2.execute("PRAGMA busy_timeout = 5000;")
            conn2.execute("PRAGMA cache_size = -2000;")
            return conn2
        raise

_db_initialized = False

def init_db(tentativa_recuperacao: bool = False):
    """Inicializa as tabelas no SQLite com modo WAL ativo, constraints rígidas, índices e auto-recuperação."""
    global _db_initialized
    if _db_initialized:
        return
    with _db_lock:
        if _db_initialized:
            return
        conn = None
        try:
            conn = get_connection()
            try:
                conn.execute("PRAGMA journal_mode = WAL;")
                conn.execute("PRAGMA synchronous = NORMAL;")
            except Exception as w_err:
                logger.warning(f"Aviso ao ativar modo WAL no init_db: {w_err}")
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
                cursor.execute("SELECT numero_mesa, token_qrcode FROM qrcodes_mesas WHERE numero_mesa = ?", (m_num,))
                row_qr = cursor.fetchone()
                agora_iso = datetime.now().isoformat()
                if not row_qr:
                    tok_inicial = f"m{m_num}-{uuid.uuid4().hex[:10]}"
                    cursor.execute("""
                    INSERT INTO qrcodes_mesas (numero_mesa, token_qrcode, criado_em, atualizado_em)
                    VALUES (?, ?, ?, ?)
                    """, (m_num, tok_inicial, agora_iso, agora_iso))
                elif str(row_qr["token_qrcode"]).startswith("mesa-") and str(row_qr["token_qrcode"]).endswith("-token"):
                    # Migra tokens previsíveis legados ('mesa-1-token') para tokens aleatórios seguros
                    tok_seguro = f"m{m_num}-{uuid.uuid4().hex[:10]}"
                    cursor.execute("""
                    UPDATE qrcodes_mesas SET token_qrcode = ?, atualizado_em = ? WHERE numero_mesa = ?
                    """, (tok_seguro, agora_iso, m_num))

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
                h_seed = _gerar_hash_senha("admin123")
                cursor.execute("""
                INSERT INTO colaboradores (nome, email, senha_hash, numero, cargo, primeiro_acesso, ativo, criado_em, atualizado_em)
                VALUES (?, ?, ?, ?, ?, 0, 1, ?, ?)
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

            # 10. Tabela de Sessões Ativas (Persistência no F5 / Recarregamento de Página)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessoes_ativas (
                token TEXT PRIMARY KEY,
                usuario_id INTEGER NOT NULL,
                criado_em TEXT NOT NULL,
                expira_em TEXT NOT NULL,
                FOREIGN KEY(usuario_id) REFERENCES colaboradores(id) ON DELETE CASCADE
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessoes_token ON sessoes_ativas(token);")

            # 11. Tabela de Auditoria Operacional Completa
            cursor.execute("""
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
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_auditoria_criado_em ON auditoria(criado_em);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_auditoria_modulo ON auditoria(modulo);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_auditoria_acao ON auditoria(acao);")

            # 13. Tabelas da Ontologia Relacional (Graph-over-SQLite)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ontologia_conceitos (
                id TEXT PRIMARY KEY,
                tipo TEXT NOT NULL,
                nome_legivel TEXT NOT NULL,
                descricao TEXT
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ontologia_sinonimos (
                termo TEXT PRIMARY KEY,
                conceito_id TEXT NOT NULL,
                FOREIGN KEY(conceito_id) REFERENCES ontologia_conceitos(id) ON DELETE CASCADE
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ontologia_sinonimos_cid ON ontologia_sinonimos(conceito_id);")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ontologia_relacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sujeito_id TEXT NOT NULL,
                predicado TEXT NOT NULL,
                objeto_id TEXT NOT NULL,
                peso REAL DEFAULT 1.0,
                FOREIGN KEY(sujeito_id) REFERENCES ontologia_conceitos(id)
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ontologia_busca ON ontologia_relacoes(sujeito_id, predicado);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ontologia_inversa ON ontologia_relacoes(objeto_id, predicado);")

            # 14. Histórico Local de Sessões de Chat (Sem sincronização com Xano)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_conversas (
                id TEXT PRIMARY KEY,
                titulo TEXT NOT NULL,
                usuario_id TEXT NOT NULL,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_conversas_usr ON chat_conversas(usuario_id);")

            cursor.execute("""
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
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_mensagens_cid ON chat_mensagens(conversa_id);")

            # 15. Telemetria e Logs de Fallback do LLM (Local no SQLite / Sem Xano)
            cursor.execute("""
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
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_llm_fallback_criado ON llm_fallback_logs(criado_em);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_llm_fallback_busca ON llm_fallback_logs(api_origem, modelo, sucesso);")

            # 12. Limpeza preventiva de itens de comanda realmente órfãos.
            # IMPORTANTE (imutabilidade histórica): itens de comandas PAGAS são o histórico de vendas
            # (ranking de produtos, vendas por categoria, consumo por mesa) e NUNCA podem ser apagados.
            # Remove apenas itens sem comanda existente ou resíduos de comandas CANCELADAS
            # (o cancelamento já estorna o estoque e exclui os itens; isto cobre bancos legados).
            cursor.execute("""
            DELETE FROM itens_comanda
            WHERE comanda_id NOT IN (SELECT id FROM comandas)
               OR comanda_id IN (SELECT id FROM comandas WHERE status = 'CANCELADA');
            """)

            # 16. Pruning automático de registros antigos/expirados para estabilidade em 512MB RAM
            limite_fila_7d = (datetime.now() - timedelta(days=7)).isoformat()
            agora_limpeza = datetime.now().isoformat()
            cursor.execute("DELETE FROM fila_sincronizacao WHERE status = 'ENVIADO' AND processado_em < ?;", (limite_fila_7d,))
            cursor.execute("DELETE FROM fila_sincronizacao WHERE status = 'ERRO' AND ultimo_erro LIKE '%404%';")
            cursor.execute("DELETE FROM sessoes_ativas WHERE expira_em < ?;", (agora_limpeza,))
            cursor.execute("""
            DELETE FROM llm_fallback_logs
            WHERE id NOT IN (SELECT id FROM llm_fallback_logs ORDER BY id DESC LIMIT 500);
            """)
            conn.commit()

            _db_initialized = True
        except sqlite3.DatabaseError as err:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
                conn = None
            if ("malformed" in str(err).lower() or "corrupt" in str(err).lower()) and not tentativa_recuperacao:
                logger.error(f"Erro de integridade SQLite no init_db ({err}). Reconstruindo banco automaticamente...")
                _auto_recuperar_banco_corrompido()
                _db_initialized = False
                init_db(tentativa_recuperacao=True)
            else:
                raise
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

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
        headers = {"Content-Type": "application/json"}
        if XANO_API_KEY:
            headers["Authorization"] = f"Bearer {XANO_API_KEY}"

        try:
            with httpx.Client(timeout=4.0) as client:
                resp = _despachar_requisicao_xano(client, metodo, rota, payload, headers)
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

def _despachar_requisicao_xano(client: httpx.Client, metodo: str, rota: str, payload: dict, headers: dict) -> httpx.Response:
    """
    Executa a requisição ao Xano com resolução resiliente de IDs (itens_comanda, colaborador, comandas, mesas).
    Elimina erros 404 decorrentes da divergência de auto-increment entre SQLite e Xano.
    """
    payload = payload or {}
    url = f"{XANO_BASE_URL.rstrip('/')}/{rota.lstrip('/')}"

    if rota.startswith("/colaborador/"):
        partes = rota.strip("/").split("/")
        local_id = int(partes[1]) if len(partes) > 1 and partes[1].isdigit() else None
        email_alvo = str(payload.get("email") or "").strip().lower()

        if not email_alvo and local_id is not None:
            try:
                with _db_lock:
                    with get_connection() as conn:
                        r_loc = conn.execute("SELECT email FROM colaboradores WHERE id = ?", (local_id,)).fetchone()
                        if r_loc:
                            email_alvo = str(r_loc["email"] or "").strip().lower()
            except Exception:
                pass

        try:
            resp_list = client.get(f"{XANO_BASE_URL.rstrip('/')}/colaborador", headers=headers)
            _registrar_chamada_xano()
            remote_id = None
            if resp_list.status_code == 200:
                for cx in (resp_list.json() or []):
                    cx_email = str(cx.get("email") or "").strip().lower()
                    if email_alvo and cx_email == email_alvo:
                        remote_id = int(cx.get("id"))
                        break
                    elif not email_alvo and local_id is not None and int(cx.get("id", -1)) == local_id:
                        remote_id = int(cx.get("id"))
                        break

            if metodo == "DELETE":
                if remote_id is not None:
                    return client.delete(f"{XANO_BASE_URL.rstrip('/')}/colaborador/{remote_id}", headers=headers)
                return httpx.Response(200, json={"status": "ok", "mensagem": "Colaborador já ausente no Xano"})

            elif metodo == "PATCH":
                # POST /colaborador no Xano já realiza upsert completo por email (nome, numero, cargo, senha_hash, primeiro_acesso, ativo)
                if email_alvo and payload.get("nome") and payload.get("cargo"):
                    upsert_body = {
                        "nome": payload.get("nome"),
                        "email": email_alvo,
                        "numero": payload.get("numero", ""),
                        "cargo": payload.get("cargo"),
                        "senha_hash": payload.get("senha_hash", ""),
                        "primeiro_acesso": bool(payload.get("primeiro_acesso", False)),
                        "ativo": bool(payload.get("ativo", True))
                    }
                    resp_up = client.post(f"{XANO_BASE_URL.rstrip('/')}/colaborador", json=upsert_body, headers=headers)
                    if resp_up.status_code in (200, 201):
                        return resp_up
                if remote_id is not None:
                    return client.patch(f"{XANO_BASE_URL.rstrip('/')}/colaborador/{remote_id}", json=payload, headers=headers)
        except Exception as e:
            logger.warning(f"Resolução resiliente de colaborador no Xano falhou ({e}), tentando requisição direta...")

    if rota.startswith("/itens_comanda/"):
        cid = payload.get("comanda_id")
        pid = payload.get("produto_id")
        pnome = payload.get("produto_nome")

        if cid:
            try:
                resp_comanda = client.get(f"{XANO_BASE_URL.rstrip('/')}/comandas/{cid}", headers=headers)
                _registrar_chamada_xano()
                if resp_comanda.status_code == 200:
                    data_comanda = resp_comanda.json()
                    itens_xano = data_comanda.get("itens", []) or []
                    xano_id = None
                    for it in itens_xano:
                        if pid is not None and it.get("produto_id") == pid:
                            xano_id = it.get("id")
                            break
                        if pnome and str(it.get("produto_nome", "")).strip().lower() == str(pnome).strip().lower():
                            xano_id = it.get("id")
                            break

                    if xano_id:
                        if metodo == "DELETE":
                            return client.delete(f"{XANO_BASE_URL.rstrip('/')}/itens_comanda/{xano_id}", headers=headers)
                        elif metodo == "PATCH":
                            patch_body = {
                                "item_id": xano_id,
                                "quantidade": payload.get("quantidade", 1),
                                "preco_momento": float(payload.get("preco_momento", 0.0)),
                                "observacao": payload.get("observacao", "")
                            }
                            return client.patch(f"{XANO_BASE_URL.rstrip('/')}/itens_comanda/{xano_id}", json=patch_body, headers=headers)
                    else:
                        if metodo == "DELETE":
                            return httpx.Response(200, json={"status": "ok", "mensagem": "Item já ausente no Xano"})
                        elif metodo == "PATCH" and pnome:
                            add_body = {
                                "produto_query": pnome,
                                "quantidade": payload.get("quantidade", 1),
                                "observacao": payload.get("observacao", "")
                            }
                            return client.post(f"{XANO_BASE_URL.rstrip('/')}/comandas/{cid}/itens", json=add_body, headers=headers)
                elif resp_comanda.status_code == 404 and metodo in ("DELETE", "PATCH"):
                    return httpx.Response(200, json={"status": "ok", "mensagem": "Comanda já finalizada ou ausente no Xano"})
            except Exception as e:
                logger.warning(f"Tentativa de resolução de item no Xano falhou ({e}), tentando requisição direta...")

    resp = client.request(metodo, url, json=payload, headers=headers)
    if resp.status_code == 404 and (metodo == "DELETE" or rota.endswith("/cancelar")):
        return httpx.Response(200, json={"status": "ok", "mensagem": "Recurso já removido ou cancelado no Xano"})
    return resp

def reconciliar_comandas_abertas_xano() -> int:
    """
    Verifica no SQLite todas as comandas com status 'ABERTA' e garante que estejam
    sincronizadas com o Xano (junto com seus itens) para que nenhum lançamento fique órfão.
    Enfileira de forma coordenada para respeitar os limites de requisições do Xano.
    """
    if _DISABLE_XANO_ENQUEUE or os.getenv("TESTING_ENV") == "1":
        return 0

    total_sincronizadas = 0
    try:
        with _db_lock:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, numero_mesa_historico, qtd_pessoas, taxa_servico FROM comandas WHERE status = 'ABERTA'")
                comandas_abertas = cursor.fetchall()
                for c in comandas_abertas:
                    cid = c["id"]
                    
                    # Verifica se abertura da comanda já está registrada na fila
                    cursor.execute("""
                    SELECT id FROM fila_sincronizacao 
                    WHERE rota = '/comandas' AND payload_json LIKE ? AND status IN ('ENVIADO', 'PENDENTE')
                    """, (f'%"id": {cid}%',))
                    if not cursor.fetchone():
                        _enqueue_xano("POST", "/comandas", {
                            "id": cid,
                            "numero_mesa": c["numero_mesa_historico"],
                            "qtd_pessoas": c["qtd_pessoas"] or 1,
                            "taxa_servico": bool(c["taxa_servico"])
                        })
                        total_sincronizadas += 1

                    # Reconciliação dos itens já consumidos da comanda aberta
                    cursor.execute("""
                    SELECT produto_id, nome_produto_historico, quantidade, preco_momento, observacao
                    FROM itens_comanda
                    WHERE comanda_id = ?
                    """, (cid,))
                    itens_comanda = cursor.fetchall()
                    for it in itens_comanda:
                        cursor.execute("""
                        SELECT id FROM fila_sincronizacao 
                        WHERE rota = ? AND payload_json LIKE ? AND status IN ('ENVIADO', 'PENDENTE')
                        """, (f"/comandas/{cid}/itens", f'%"produto_query": "{it["nome_produto_historico"]}"%'))
                        if not cursor.fetchone():
                            _enqueue_xano("POST", f"/comandas/{cid}/itens", {
                                "produto_query": it["nome_produto_historico"],
                                "quantidade": it["quantidade"],
                                "observacao": it["observacao"] or ""
                            })
    except Exception as e:
        logger.warning(f"Erro na reconciliação de comandas abertas com Xano: {e}")
    return total_sincronizadas

def reconciliar_colaboradores_xano() -> int:
    """
    Garante paridade 1:1 dos colaboradores do SQLite (verdade absoluta) no Xano Cloud:
    1. Faz upsert (POST /colaborador) de todos os colaboradores locais do SQLite para o Xano;
    2. Remove do Xano colaboradores órfãos/residuais de teste que não existem no SQLite local;
    3. Alinha os IDs e limpa eventuais erros 404 antigos da fila_sincronizacao.
    """
    if _DISABLE_XANO_ENQUEUE or os.getenv("TESTING_ENV") == "1":
        return 0

    reconciliados = 0
    try:
        with _db_lock:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome, email, senha_hash, numero, cargo, primeiro_acesso, ativo FROM colaboradores")
                locais = [dict(r) for r in cursor.fetchall()]

        headers = {"Content-Type": "application/json"}
        if XANO_API_KEY:
            headers["Authorization"] = f"Bearer {XANO_API_KEY}"

        base = XANO_BASE_URL.rstrip("/")
        emails_locais = {str(c["email"]).strip().lower(): c for c in locais if c.get("email")}

        with httpx.Client(timeout=10.0) as client:
            _esperar_janela_rate_limit()
            resp_get = client.get(f"{base}/colaborador", headers=headers)
            _registrar_chamada_xano()
            remotos = resp_get.json() if resp_get.status_code == 200 else []
            remotos_por_email = {str(r.get("email") or "").strip().lower(): r for r in remotos if r.get("email")}

            # 1. Envia ou atualiza colaboradores locais que estão ausentes ou divergentes no Xano
            for email_loc, c_loc in emails_locais.items():
                r_rem = remotos_por_email.get(email_loc)
                precisa_upsert = False
                if not r_rem:
                    precisa_upsert = True
                else:
                    if (
                        str(r_rem.get("nome") or "") != str(c_loc["nome"])
                        or str(r_rem.get("numero") or "") != str(c_loc["numero"])
                        or str(r_rem.get("cargo") or "") != str(c_loc["cargo"])
                        or str(r_rem.get("senha_hash") or "") != str(c_loc["senha_hash"])
                        or bool(r_rem.get("primeiro_acesso", True)) != bool(c_loc["primeiro_acesso"])
                        or bool(r_rem.get("ativo", True)) != bool(c_loc["ativo"])
                    ):
                        precisa_upsert = True

                if precisa_upsert:
                    _esperar_janela_rate_limit()
                    resp_post = client.post(f"{base}/colaborador", json={
                        "nome": c_loc["nome"],
                        "email": email_loc,
                        "numero": c_loc["numero"],
                        "cargo": c_loc["cargo"],
                        "senha_hash": c_loc["senha_hash"],
                        "primeiro_acesso": bool(c_loc["primeiro_acesso"]),
                        "ativo": bool(c_loc["ativo"])
                    }, headers=headers)
                    _registrar_chamada_xano()
                    if resp_post.status_code in (200, 201):
                        reconciliados += 1

            # 2. Remove do Xano registros órfãos que já foram excluídos no SQLite
            for r_rem in remotos:
                em_rem = str(r_rem.get("email") or "").strip().lower()
                id_rem = r_rem.get("id")
                if id_rem is not None and em_rem not in emails_locais:
                    _esperar_janela_rate_limit()
                    resp_del = client.delete(f"{base}/colaborador/{id_rem}", headers=headers)
                    _registrar_chamada_xano()
                    if resp_del.status_code in (200, 204, 404):
                        reconciliados += 1

        with _db_lock:
            with get_connection() as conn:
                conn.execute("DELETE FROM fila_sincronizacao WHERE status = 'ERRO' AND rota LIKE '/colaborador%';")
                conn.commit()
    except Exception as e:
        logger.warning(f"Aviso na reconciliação de colaboradores com Xano: {e}")
    return reconciliados

def _xano_sqlite_worker():
    """Worker em background com governança de janela deslizante para puxar o estado primário do Xano e drenar a fila sem qualquer 429."""
    try:
        sincronizar_produtos_xano()
        sincronizar_colaboradores_xano()
        reconciliar_comandas_abertas_xano()
    except Exception:
        pass

    _idle_counter = 0
    _xano_pull_counter = 0
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
                _xano_pull_counter += 1
                if _xano_pull_counter >= 45:  # A cada ~45s puxa automaticamente do Xano (fonte primária)
                    _xano_pull_counter = 0
                    try:
                        sincronizar_produtos_xano()
                        sincronizar_colaboradores_xano()
                    except Exception:
                        pass
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
                    resp = _despachar_requisicao_xano(client, tarefa["metodo"], tarefa["rota"], tarefa["payload"], headers)
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
    """Lista todas as mesas ativas e calcula o consumo atual diretamente do SQLite em query única O(1) via LEFT JOIN."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT 
                m.id, 
                m.numero_mesa, 
                m.capacidade, 
                m.status,
                c.id as comanda_id,
                COALESCE(SUM(ic.quantidade * ic.preco_momento), 0.0) as total_atual
            FROM mesas m
            LEFT JOIN comandas c ON c.mesa_id = m.id AND c.status = 'ABERTA'
            LEFT JOIN itens_comanda ic ON ic.comanda_id = c.id
            GROUP BY m.id, m.numero_mesa, m.capacidade, m.status, c.id
            ORDER BY m.numero_mesa ASC
            """)
            mesas_rows = cursor.fetchall()
            
            resultado = []
            for m in mesas_rows:
                comanda_id = m["comanda_id"] or m["id"]
                total_atual = float(m["total_atual"] or 0.0)
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

    _sync_push_imediato_ou_enfileirar("POST", "/comandas", {
        "id": nova_comanda_id,
        "numero_mesa": numero_mesa,
        "qtd_pessoas": qtd_pessoas,
        "taxa_servico": True
    })

    registrar_auditoria(
        acao="ABERTURA_MESA",
        modulo="MESAS",
        detalhes=f"Mesa física {numero_mesa} aberta no salão (Capacidade: {qtd_pessoas} pessoas, Comanda #{nova_comanda_id})."
    )

    return {"status": "ok", "mesa_id": nova_mesa_id, "comanda_id": nova_comanda_id}

def excluir_mesa(mesa_id: int):
    """Exclui a mesa, estorna o estoque dos itens consumidos e cancela a comanda associada."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, numero_mesa_historico FROM comandas WHERE mesa_id = ?", (mesa_id,))
            comanda_rows = cursor.fetchall()
            for cr in comanda_rows:
                cid = cr["id"]
                cursor.execute("SELECT produto_id, quantidade FROM itens_comanda WHERE comanda_id = ?", (cid,))
                itens = cursor.fetchall()
                for it in itens:
                    if it["produto_id"]:
                        _incrementar_estoque_cursor(cursor, it["produto_id"], it["quantidade"])
                cursor.execute("DELETE FROM itens_comanda WHERE comanda_id = ?", (cid,))

            cursor.execute("""
            UPDATE comandas 
            SET status = 'CANCELADA', mesa_id = NULL, valor_total = 0.0
            WHERE mesa_id = ?
            """, (mesa_id,))
            cursor.execute("DELETE FROM mesas WHERE id = ?", (mesa_id,))
            conn.commit()

    _sync_push_imediato_ou_enfileirar("DELETE", f"/mesas/{mesa_id}", {"mesa_id": mesa_id})

    registrar_auditoria(
        acao="EXCLUSAO_MESA",
        modulo="MESAS_E_COMANDAS",
        detalhes=f"Mesa física ID {mesa_id} removida do salão com cancelamento e estorno de comandas."
    )

def cancelar_comanda(comanda_id: int):
    """Cancela a comanda, estorna o estoque de todos os itens, exclui itens e libera a mesa física."""
    num_mesa = None
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT mesa_id, numero_mesa_historico FROM comandas WHERE id = ?", (comanda_id,))
            row = cursor.fetchone()
            mesa_id = row["mesa_id"] if row else None
            num_mesa = row["numero_mesa_historico"] if row else None

            # 1. Estorna o estoque de todos os itens lançados nesta comanda
            cursor.execute("SELECT produto_id, quantidade FROM itens_comanda WHERE comanda_id = ?", (comanda_id,))
            itens = cursor.fetchall()
            for it in itens:
                if it["produto_id"]:
                    _incrementar_estoque_cursor(cursor, it["produto_id"], it["quantidade"])

            # 2. Exclui os itens da comanda cancelada para não ficarem órfãos
            cursor.execute("DELETE FROM itens_comanda WHERE comanda_id = ?", (comanda_id,))

            # 3. Atualiza status da comanda para CANCELADA e zera valor
            cursor.execute("""
            UPDATE comandas 
            SET status = 'CANCELADA', mesa_id = NULL, valor_total = 0.0
            WHERE id = ?
            """, (comanda_id,))

            if mesa_id:
                cursor.execute("DELETE FROM mesas WHERE id = ?", (mesa_id,))
            conn.commit()

    registrar_auditoria(
        acao="CANCELAMENTO_COMANDA",
        modulo="MESAS_E_COMANDAS",
        detalhes=f"Comanda #{comanda_id} (Mesa {num_mesa or '?'}) cancelada com estorno de estoque e remoção de itens."
    )

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

    registrar_auditoria(
        acao="ADICIONAR_ITEM",
        modulo="COMANDAS",
        detalhes=f"Item '{produto['nome']}' ({quantidade}x - R$ {float(produto['preco_unitario']):.2f}) adicionado à Comanda #{comanda_id}." + (f" Obs: {obs_sanitizada}" if obs_sanitizada else "")
    )

def editar_item_comanda(item_id: int, quantidade: int, preco_momento: float, observacao: str = ""):
    """Edita quantidade, preço e observação com validações de integridade e sanitização."""
    if quantidade <= 0:
        raise ValueError("A quantidade deve ser de no mínimo 1 item.")
    if preco_momento < 0:
        raise ValueError("O preço não pode ser negativo.")

    obs_sanitizada = html.escape(observacao.strip()) if observacao else ""
    cid = None
    pid = None
    pnome = ""

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT produto_id, quantidade, comanda_id, nome_produto_historico FROM itens_comanda WHERE id = ?", (item_id,))
            it_antigo = cursor.fetchone()
            if not it_antigo:
                raise ValueError("Item não encontrado.")

            diff_qtd = quantidade - it_antigo["quantidade"]
            cid = it_antigo["comanda_id"]
            pid = it_antigo["produto_id"]
            pnome = it_antigo["nome_produto_historico"]

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
        "comanda_id": cid,
        "produto_id": pid,
        "produto_nome": pnome,
        "quantidade": quantidade,
        "preco_momento": preco_momento,
        "observacao": obs_sanitizada or ""
    })

    registrar_auditoria(
        acao="EDITAR_ITEM",
        modulo="COMANDAS",
        detalhes=f"Item #{item_id} (Comanda #{cid}) alterado para {quantidade}x (R$ {preco_momento:.2f} un)."
    )

def remover_item_comanda(item_id: int):
    """Remove item da comanda, estorna o estoque atômico e sincroniza exclusão no Xano."""
    cid = None
    nome_removido = ""
    pid = None
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT produto_id, quantidade, comanda_id, nome_produto_historico FROM itens_comanda WHERE id = ?", (item_id,))
            it = cursor.fetchone()
            if it:
                cid = it["comanda_id"]
                nome_removido = it["nome_produto_historico"]
                pid = it["produto_id"]
                if it["produto_id"]:
                    _incrementar_estoque_cursor(cursor, it["produto_id"], it["quantidade"])

            cursor.execute("DELETE FROM itens_comanda WHERE id = ?", (item_id,))
            conn.commit()

    _sync_push_imediato_ou_enfileirar("DELETE", f"/itens_comanda/{item_id}", {
        "comanda_id": cid,
        "produto_id": pid,
        "produto_nome": nome_removido
    })

    registrar_auditoria(
        acao="REMOVER_ITEM",
        modulo="COMANDAS",
        detalhes=f"Item #{item_id} ('{nome_removido}') removido da Comanda #{cid or '?'} com estorno de estoque."
    )

# ================= GESTÃO DE QR CODES DE MESAS E PRÉ-COMANDA =================

def listar_mesas_qrcodes() -> List[dict]:
    """Retorna as mesas configuradas com seus tokens de QR Code, status do salão e consumo atual em consulta única O(1)."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT q.numero_mesa, q.token_qrcode, q.atualizado_em,
                   m.id as mesa_id, m.status as mesa_status, m.capacidade,
                   c.id as comanda_id,
                   COALESCE(SUM(ic.quantidade * ic.preco_momento), 0.0) as total_mesa
            FROM qrcodes_mesas q
            LEFT JOIN mesas m ON m.numero_mesa = q.numero_mesa
            LEFT JOIN comandas c ON c.mesa_id = m.id AND c.status = 'ABERTA'
            LEFT JOIN itens_comanda ic ON ic.comanda_id = c.id
            GROUP BY q.numero_mesa, q.token_qrcode, q.atualizado_em, m.id, m.status, m.capacidade, c.id
            ORDER BY q.numero_mesa ASC
            """)
            rows = cursor.fetchall()
            resultado = []
            for r in rows:
                status_real = r["mesa_status"] or "LIVRE"
                resultado.append({
                    "numero_mesa": r["numero_mesa"],
                    "token_qrcode": r["token_qrcode"],
                    "atualizado_em": r["atualizado_em"],
                    "mesa_id": r["mesa_id"],
                    "status": status_real,
                    "comanda_id": r["comanda_id"],
                    "total_atual": float(r["total_mesa"] or 0.0),
                    "capacidade": r["capacidade"] or 4
                })
            return resultado

def validar_acesso_cardapio_qr(numero_mesa: int, token: str) -> bool:
    """Valida em tempo constante (hmac.compare_digest) se o token de QR Code corresponde à mesa física."""
    if not token or numero_mesa <= 0:
        return False
    token_limpo = str(token).strip()
    if not token_limpo:
        return False
    with _db_lock:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT token_qrcode FROM qrcodes_mesas WHERE numero_mesa = ?",
                (int(numero_mesa),)
            ).fetchone()
            if not row or not row["token_qrcode"]:
                return False
            token_db = str(row["token_qrcode"]).strip()
            return hmac.compare_digest(token_db.encode("utf-8"), token_limpo.encode("utf-8"))

def atualizar_qrcode_mesa(numero_mesa: int) -> str:
    """Gera e grava um novo token estável e único para o QR Code da mesa."""
    novo_token = f"m{numero_mesa}-{uuid.uuid4().hex[:10]}"
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

    registrar_auditoria(
        acao="GERAR_QRCODE",
        modulo="QRCODES",
        detalhes=f"Novo QR Code gerado para a Mesa {numero_mesa} (Token: {novo_token})."
    )

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
            comanda_criada_agora = False
            if comanda_row:
                comanda_id = comanda_row["id"]
            else:
                cursor.execute("""
                INSERT INTO comandas (mesa_id, numero_mesa_historico, data_abertura, status, taxa_servico, qtd_pessoas, valor_total)
                VALUES (?, ?, ?, 'ABERTA', 1, 2, 0.0)
                """, (mesa_id, numero_mesa, datetime.now().isoformat()))
                comanda_id = cursor.lastrowid
                comanda_criada_agora = True

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

    # Enfileira comanda e itens no SQLite para sincronização transparente em background (elimina travamento de tela)
    if comanda_criada_agora:
        _enqueue_xano("POST", "/comandas", {
            "id": comanda_id,
            "numero_mesa": numero_mesa,
            "qtd_pessoas": 2,
            "taxa_servico": True
        })

    for it_conf in itens_confirmados:
        _enqueue_xano("POST", f"/comandas/{comanda_id}/itens", {
            "produto_query": it_conf["nome"],
            "quantidade": it_conf["quantidade"],
            "observacao": it_conf["observacao"]
        })

    registrar_auditoria(
        acao="PEDIDO_CLIENTE",
        modulo="CARDAPIO_DIGITAL",
        detalhes=f"Pedido digital do cliente confirmado para a Mesa {numero_mesa}: {len(itens_confirmados)} itens lançados na Comanda #{comanda_id}."
    )

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

    registrar_auditoria(
        acao="FECHAR_COMANDA",
        modulo="COMANDAS",
        detalhes=f"Comanda #{comanda_id} fechada e paga. Total: R$ {round(valor_final, 2):.2f} (Taxa de serviço: {'Sim' if taxa_servico else 'Não'})."
    )

def alternar_taxa_servico_comanda(comanda_id: int, taxa_servico: bool) -> bool:
    """Atualiza a opção de taxa de serviço na comanda no SQLite e sincroniza em tempo real com o Xano."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE comandas
            SET taxa_servico = ?
            WHERE id = ?
            """, (1 if taxa_servico else 0, comanda_id))
            conn.commit()

    _sync_push_imediato_ou_enfileirar("PATCH", f"/comandas/{comanda_id}", {
        "taxa_servico": bool(taxa_servico)
    })

    registrar_auditoria(
        acao="ALTERAR_TAXA_SERVICO",
        modulo="COMANDAS",
        detalhes=f"Taxa de serviço da Comanda #{comanda_id} alterada para {'Aplicada (10%)' if taxa_servico else 'Isenta (0%)'}."
    )
    return True


# ================= OPERAÇÕES DE PRODUTOS =================

def listar_produtos(busca: Optional[str] = None, categoria: Optional[str] = None, apenas_disponiveis: bool = False) -> List[dict]:
    """Lista os produtos do cardápio hidratando automaticamente do Xano (fonte primária) se o cache local SQLite estiver vazio."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM produtos")
            tot_row = cursor.fetchone()
            vazio = (not tot_row or tot_row["total"] == 0)

    if vazio:
        try:
            sincronizar_produtos_xano()
        except Exception:
            pass

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

    registrar_auditoria(
        acao="CRIAR_PRODUTO",
        modulo="CARDAPIO",
        detalhes=f"Novo produto '{nome_sanitizado}' (Cód PDV: {cod}, Categoria: {cat_sanitizada}) cadastrado por R$ {preco_unitario:.2f}. Estoque inicial: {qtd_disp}."
    )

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
    preco_antigo = preco_unitario

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, preco_unitario FROM produtos WHERE LOWER(codigo_pdv) = LOWER(?) AND id != ?", (cod, produto_id))
            if cursor.fetchone():
                raise ValueError(f"Código PDV '{cod}' já em uso por outro produto.")

            cursor.execute("SELECT preco_unitario FROM produtos WHERE id = ?", (produto_id,))
            p_ant = cursor.fetchone()
            if p_ant:
                preco_antigo = float(p_ant["preco_unitario"])

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

    registrar_auditoria(
        acao="EDITAR_PRODUTO",
        modulo="CARDAPIO",
        detalhes=f"Produto #{produto_id} ('{nome_sanitizado}') editado: Preço R$ {preco_antigo:.2f} -> R$ {preco_unitario:.2f}, Estoque {qtd_disp}, Status: {'Disponível' if disponivel else 'Indisponível'}."
    )

def excluir_produto(produto_id: int):
    """Exclui produto do cardápio e sincroniza exclusão no Xano."""
    nome_excluido = ""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nome FROM produtos WHERE id = ?", (produto_id,))
            p = cursor.fetchone()
            if p:
                nome_excluido = p["nome"]
            cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
            conn.commit()

    _sync_push_imediato_ou_enfileirar("DELETE", f"/produto/{produto_id}")

    registrar_auditoria(
        acao="EXCLUIR_PRODUTO",
        modulo="CARDAPIO",
        detalhes=f"Produto #{produto_id} ('{nome_excluido}') excluído do cardápio."
    )

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
        ids_remotos = []
        with _db_lock:
            with get_connection() as conn:
                cursor = conn.cursor()
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
                    ids_remotos.append(xano_id)
                    # Evita conflito de UNIQUE(codigo_pdv) em IDs diferentes antes do UPSERT
                    cursor.execute("DELETE FROM produtos WHERE codigo_pdv = ? AND id != ?", (cod, xano_id))
                    cursor.execute("""
                    INSERT INTO produtos (
                        id, codigo_pdv, nome, categoria, preco_unitario,
                        descricao, url_imagem, qtd_disp, precisa_produzir, disponivel
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        codigo_pdv = excluded.codigo_pdv,
                        nome = excluded.nome,
                        categoria = excluded.categoria,
                        preco_unitario = excluded.preco_unitario,
                        descricao = excluded.descricao,
                        url_imagem = excluded.url_imagem,
                        qtd_disp = excluded.qtd_disp,
                        precisa_produzir = excluded.precisa_produzir,
                        disponivel = excluded.disponivel
                    """, (xano_id, cod, nome, categoria, preco, desc, foto, qtd, precisa, disp))
                    sincronizados += 1

                if ids_remotos:
                    placeholders = ",".join("?" for _ in ids_remotos)
                    cursor.execute(f"DELETE FROM produtos WHERE id NOT IN ({placeholders})", ids_remotos)

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
            ids_pagas = []

            for c in pagas:
                c_id = c["id"]
                ids_pagas.append(c_id)
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

            if ids_pagas:
                placeholders = ",".join("?" for _ in ids_pagas)
                cursor.execute(f"""
                SELECT nome_produto_historico, categoria_historico, quantidade, preco_momento
                FROM itens_comanda
                WHERE comanda_id IN ({placeholders})
                """, ids_pagas)
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

_PBKDF2_ITERATIONS = 100_000
_login_attempts_lock = threading.Lock()
_login_attempts: Dict[str, List[float]] = {}
_recovery_tokens_lock = threading.Lock()
_recovery_tokens: Dict[str, tuple] = {}  # email -> (codigo_csprng, expira_timestamp)

def _gerar_hash_senha_legado(senha: str) -> str:
    """Hash SHA-256 legado para verificação e migração transparente."""
    raw = f"{CHURRAS_SALT}:{str(senha).strip()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def _gerar_hash_senha(senha: str) -> str:
    """Gera hash criptográfico forte com PBKDF2-HMAC-SHA256 (100.000 iterações)."""
    senha_limpa = str(senha).strip().encode("utf-8")
    salt_bytes = CHURRAS_SALT.encode("utf-8")
    dk = hashlib.pbkdf2_hmac("sha256", senha_limpa, salt_bytes, _PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${dk.hex()}"

def _verificar_hash_senha(senha_plana: str, hash_armazenado: str) -> tuple:
    """
    Verifica a senha contra o hash armazenado em tempo constante.
    Retorna (valido: bool, precisa_rehash: bool).
    """
    if not hash_armazenado or not senha_plana:
        return False, False
    hash_str = str(hash_armazenado).strip()
    if hash_str.startswith("pbkdf2_sha256$"):
        esperado = _gerar_hash_senha(senha_plana)
        return hmac.compare_digest(hash_str.encode("utf-8"), esperado.encode("utf-8")), False
    # Fallback de migração transparente a partir de SHA-256 legado
    legado = _gerar_hash_senha_legado(senha_plana)
    valido = hmac.compare_digest(hash_str.encode("utf-8"), legado.encode("utf-8"))
    return valido, valido

def _esta_bloqueado_rate_limit_login(email: str) -> bool:
    """Bloqueia temporariamente contas com >= 5 falhas nos últimos 5 minutos (300s)."""
    agora = time.time()
    with _login_attempts_lock:
        tentativas = [t for t in _login_attempts.get(email, []) if agora - t < 300.0]
        _login_attempts[email] = tentativas
        return len(tentativas) >= 5

def _registrar_falha_login(email: str):
    agora = time.time()
    with _login_attempts_lock:
        tentativas = [t for t in _login_attempts.get(email, []) if agora - t < 300.0]
        tentativas.append(agora)
        _login_attempts[email] = tentativas

def _limpar_falhas_login(email: str):
    with _login_attempts_lock:
        _login_attempts.pop(email, None)

def autenticar_usuario(email: str, senha: str) -> Optional[dict]:
    """Valida as credenciais de um colaborador com proteção anti-força bruta e migração transparente para PBKDF2."""
    init_db()
    email_limpo = str(email).strip().lower()
    if not email_limpo or not senha:
        return None

    if _esta_bloqueado_rate_limit_login(email_limpo):
        registrar_auditoria("FALHA_LOGIN", "AUTENTICACAO", f"Login bloqueado temporariamente por rate-limit (força bruta): {email_limpo}")
        return None

    user_res = None
    precisa_upgrade_hash = False
    novo_hash_pbkdf2 = ""
    payload_rehash_xano = None

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, nome, email, senha_hash, numero, cargo, primeiro_acesso, ativo
            FROM colaboradores
            WHERE LOWER(email) = ? AND ativo = 1
            """, (email_limpo,))
            row = cursor.fetchone()
            if row:
                valido, precisa_rehash = _verificar_hash_senha(senha, row["senha_hash"])
                if valido:
                    nome_dec = descriptografar_dado(row["nome"])
                    numero_dec = descriptografar_dado(row["numero"])
                    cargo_dec = descriptografar_dado(row["cargo"])
                    user_res = {
                        "id": row["id"],
                        "nome": nome_dec,
                        "email": row["email"],
                        "numero": numero_dec,
                        "cargo": cargo_dec,
                        "primeiro_acesso": bool(row["primeiro_acesso"]),
                        "ativo": bool(row["ativo"])
                    }
                    if precisa_rehash:
                        precisa_upgrade_hash = True
                        novo_hash_pbkdf2 = _gerar_hash_senha(senha)
                        agora_iso = datetime.now().isoformat()
                        cursor.execute("""
                        UPDATE colaboradores SET senha_hash = ?, atualizado_em = ? WHERE id = ?
                        """, (novo_hash_pbkdf2, agora_iso, row["id"]))
                        conn.commit()
                        payload_rehash_xano = {
                            "nome": row["nome"],
                            "email": row["email"],
                            "numero": row["numero"],
                            "cargo": row["cargo"],
                            "senha_hash": novo_hash_pbkdf2,
                            "primeiro_acesso": bool(row["primeiro_acesso"]),
                            "ativo": bool(row["ativo"]),
                            "atualizado_em": agora_iso
                        }

    if user_res:
        _limpar_falhas_login(email_limpo)
        if precisa_upgrade_hash and payload_rehash_xano:
            _sync_push_imediato_ou_enfileirar("PATCH", f"/colaborador/{user_res['id']}", payload_rehash_xano)
        registrar_auditoria("LOGIN", "AUTENTICACAO", f"Login efetuado com sucesso por {user_res['nome']} ({email_limpo})", usuario=user_res)
        return user_res

    # Se não encontrou ou falhou localmente, sincroniza imediatamente do Xano (fonte primária) e tenta novamente
    try:
        sincronizar_colaboradores_xano()
        with _db_lock:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT id, nome, email, senha_hash, numero, cargo, primeiro_acesso, ativo
                FROM colaboradores
                WHERE LOWER(email) = ? AND ativo = 1
                """, (email_limpo,))
                row_x = cursor.fetchone()
                if row_x:
                    valido_x, _ = _verificar_hash_senha(senha, row_x["senha_hash"])
                    if valido_x:
                        user_res = {
                            "id": row_x["id"],
                            "nome": descriptografar_dado(row_x["nome"]),
                            "email": row_x["email"],
                            "numero": descriptografar_dado(row_x["numero"]),
                            "cargo": descriptografar_dado(row_x["cargo"]),
                            "primeiro_acesso": bool(row_x["primeiro_acesso"]),
                            "ativo": bool(row_x["ativo"])
                        }
                        _limpar_falhas_login(email_limpo)
                        registrar_auditoria("LOGIN", "AUTENTICACAO", f"Login efetuado via Xano por {user_res['nome']} ({email_limpo})", usuario=user_res)
                        return user_res
    except Exception:
        pass

    _registrar_falha_login(email_limpo)
    registrar_auditoria("FALHA_LOGIN", "AUTENTICACAO", f"Tentativa de login rejeitada para o e-mail: {email_limpo}")
    return None

def formatar_telefone_br(numero: str) -> str:
    """Aplica máscara brasileira de telefone (XX) XXXXX-XXXX ou (XX) XXXX-XXXX."""
    digitos = "".join(ch for ch in str(numero or "") if ch.isdigit())
    if digitos.startswith("55") and len(digitos) in (12, 13):
        digitos = digitos[2:]
    digitos = digitos[:11]
    if len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    elif len(digitos) == 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    elif len(digitos) > 6:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    elif len(digitos) > 2:
        return f"({digitos[:2]}) {digitos[2:]}"
    return digitos

def cadastrar_colaborador(nome: str, email: str, senha: str, numero: str, cargo: str) -> dict:
    """Cadastra um novo colaborador criptografando nome, telefone, cargo e senha no SQLite e no Xano."""
    init_db()
    nome_limpo = html.escape(str(nome).strip())
    email_limpo = str(email).strip().lower()
    digitos_tel = "".join(ch for ch in str(numero or "") if ch.isdigit())
    if digitos_tel.startswith("55") and len(digitos_tel) in (12, 13):
        digitos_tel = digitos_tel[2:]
    if len(digitos_tel) not in (10, 11):
        raise ValueError("Informe um número de telefone válido com DDD (10 ou 11 dígitos, ex: (31) 98765-4321).")
    numero_limpo = formatar_telefone_br(digitos_tel)
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

    registrar_auditoria(
        acao="CRIAR_COLABORADOR",
        modulo="COLABORADORES",
        detalhes=f"Cadastrado colaborador '{nome_limpo}' ({email_limpo}) com cargo '{cargo_limpo}'."
    )

    return {
        "id": novo_id,
        "nome": nome_limpo,
        "email": email_limpo,
        "numero": numero_limpo,
        "cargo": cargo_limpo,
        "primeiro_acesso": True,
        "ativo": True
    }

def obter_colaborador_por_id(usuario_id: int) -> Optional[dict]:
    """Retorna os dados cadastrais do colaborador com os campos sensíveis descriptografados."""
    init_db()
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, nome, email, numero, cargo, primeiro_acesso, ativo, criado_em, atualizado_em
            FROM colaboradores
            WHERE id = ?
            """, (usuario_id,))
            r = cursor.fetchone()
            if not r:
                return None
            return {
                "id": r["id"],
                "nome": descriptografar_dado(r["nome"]),
                "email": r["email"],
                "numero": descriptografar_dado(r["numero"]),
                "cargo": descriptografar_dado(r["cargo"]),
                "primeiro_acesso": bool(r["primeiro_acesso"]),
                "ativo": bool(r["ativo"]),
                "criado_em": r["criado_em"],
                "atualizado_em": r["atualizado_em"]
            }

def editar_colaborador(
    usuario_id: Optional[int] = None,
    nome: str = "",
    email: str = "",
    numero: str = "",
    cargo: str = "",
    nova_senha: Optional[str] = None,
    primeiro_acesso: Optional[bool] = None,
    colaborador_id: Optional[int] = None,
    forcar_primeiro_acesso: Optional[bool] = None
) -> dict:
    """
    Atualiza os dados cadastrais de um colaborador (nome, email, numero, cargo, e opcionalmente senha e primeiro_acesso).
    Criptografa com Fernet todos os campos sensíveis no SQLite e enfileira/dispara sync para o Xano.
    """
    init_db()
    if usuario_id is None and colaborador_id is not None:
        usuario_id = colaborador_id
    if primeiro_acesso is None and forcar_primeiro_acesso is not None:
        primeiro_acesso = forcar_primeiro_acesso
    if usuario_id is None:
        raise ValueError("ID do colaborador é obrigatório.")

    nome_limpo = html.escape(str(nome).strip())
    email_limpo = str(email).strip().lower()
    digitos_tel = "".join(ch for ch in str(numero or "") if ch.isdigit())
    if digitos_tel.startswith("55") and len(digitos_tel) in (12, 13):
        digitos_tel = digitos_tel[2:]
    if len(digitos_tel) not in (10, 11):
        raise ValueError("Informe um número de telefone válido com DDD (10 ou 11 dígitos, ex: (31) 98765-4321).")
    numero_limpo = formatar_telefone_br(digitos_tel)
    cargo_limpo = str(cargo).strip().lower()

    if not nome_limpo or not email_limpo or not numero_limpo:
        raise ValueError("Nome, e-mail e número de telefone são obrigatórios.")
    if cargo_limpo not in ("caixa", "gerente"):
        raise ValueError("O cargo deve ser obrigatoriamente 'caixa' ou 'gerente'.")
    if "@" not in email_limpo:
        raise ValueError("Formato de e-mail inválido.")

    agora_iso = datetime.now().isoformat()
    nome_cifrado = criptografar_dado(nome_limpo)
    numero_cifrado = criptografar_dado(numero_limpo)
    cargo_cifrado = criptografar_dado(cargo_limpo)

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, cargo, email FROM colaboradores WHERE id = ?", (usuario_id,))
            target = cursor.fetchone()
            if not target:
                raise ValueError("Colaborador não encontrado.")

            cursor.execute("SELECT id FROM colaboradores WHERE LOWER(email) = ? AND id != ?", (email_limpo, usuario_id))
            if cursor.fetchone():
                raise ValueError(f"Já existe outro colaborador com o e-mail '{email_limpo}'.")

            cargo_antigo = descriptografar_dado(target["cargo"])
            if cargo_antigo == "gerente" and cargo_limpo != "gerente":
                cursor.execute("SELECT id, cargo FROM colaboradores WHERE ativo = 1")
                todos = cursor.fetchall()
                gerentes = [c for c in todos if descriptografar_dado(c["cargo"]) == "gerente"]
                if len(gerentes) <= 1:
                    raise ValueError("Não é possível alterar o cargo do único gerente administrador do sistema.")

            campos_sql = [
                "nome = ?",
                "email = ?",
                "numero = ?",
                "cargo = ?",
                "atualizado_em = ?"
            ]
            params = [nome_cifrado, email_limpo, numero_cifrado, cargo_cifrado, agora_iso]
            cursor.execute("SELECT senha_hash, ativo, primeiro_acesso FROM colaboradores WHERE id = ?", (usuario_id,))
            colab_info = cursor.fetchone()
            senha_hash_val = colab_info["senha_hash"] if colab_info else ""
            ativo_val = bool(colab_info["ativo"]) if colab_info else True
            pa_default = bool(colab_info["primeiro_acesso"]) if colab_info else False

            payload_xano = {
                "nome": nome_cifrado,
                "email": email_limpo,
                "numero": numero_cifrado,
                "cargo": cargo_cifrado,
                "senha_hash": senha_hash_val,
                "primeiro_acesso": pa_default,
                "ativo": ativo_val,
                "atualizado_em": agora_iso
            }

            if nova_senha and len(str(nova_senha).strip()) >= 4:
                senha_hash = _gerar_hash_senha(nova_senha.strip())
                campos_sql.append("senha_hash = ?")
                params.append(senha_hash)
                payload_xano["senha_hash"] = senha_hash

            if primeiro_acesso is not None:
                pa_val = 1 if primeiro_acesso else 0
                campos_sql.append("primeiro_acesso = ?")
                params.append(pa_val)
                payload_xano["primeiro_acesso"] = bool(primeiro_acesso)

            params.append(usuario_id)
            cursor.execute(f"UPDATE colaboradores SET {', '.join(campos_sql)} WHERE id = ?", params)
            conn.commit()

    _sync_push_imediato_ou_enfileirar("PATCH", f"/colaborador/{usuario_id}", payload_xano)

    detalhes_edit = f"Colaborador #{usuario_id} atualizado: Nome='{nome_limpo}', Email='{email_limpo}', Cargo='{cargo_limpo}'"
    if nova_senha:
        detalhes_edit += ", Senha alterada"
    if primeiro_acesso is not None:
        detalhes_edit += f", Primeiro Acesso={'Sim' if primeiro_acesso else 'Não'}"
    registrar_auditoria("EDITAR_COLABORADOR", "COLABORADORES", detalhes_edit)

    return {
        "id": usuario_id,
        "nome": nome_limpo,
        "email": email_limpo,
        "numero": numero_limpo,
        "cargo": cargo_limpo,
        "atualizado_em": agora_iso
    }

def atualizar_senha_colaborador(usuario_id: int, nova_senha: str) -> bool:
    """Atualiza a senha do colaborador e desativa a flag de primeiro acesso."""
    init_db()
    if not str(nova_senha).strip() or len(str(nova_senha).strip()) < 4:
        raise ValueError("A nova senha deve possuir pelo menos 4 caracteres.")
    
    senha_hash = _gerar_hash_senha(nova_senha)
    agora_iso = datetime.now().isoformat()
    colab_atual = None

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
            cursor.execute("SELECT id, nome, email, numero, cargo, ativo FROM colaboradores WHERE id = ?", (usuario_id,))
            colab_atual = cursor.fetchone()
            conn.commit()

    if colab_atual:
        _sync_push_imediato_ou_enfileirar("PATCH", f"/colaborador/{usuario_id}", {
            "nome": colab_atual["nome"],
            "email": colab_atual["email"],
            "numero": colab_atual["numero"],
            "cargo": colab_atual["cargo"],
            "senha_hash": senha_hash,
            "primeiro_acesso": False,
            "ativo": bool(colab_atual["ativo"]),
            "atualizado_em": agora_iso
        })

    registrar_auditoria(
        acao="ALTERAR_SENHA",
        modulo="AUTENTICACAO",
        detalhes=f"Senha pessoal alterada com sucesso para o colaborador ID #{usuario_id}."
    )

    return True

def processar_recuperacao_por_email(email: str, base_url: Optional[str] = None) -> str:
    """
    Processa a recuperação de senha solicitando exclusivamente o e-mail:
    1. Localiza o colaborador cadastrado e ativo (sincronizando do Xano se necessário).
    2. Dispara e-mail HTML executivo via SMTP Gmail (paivaweirich@gmail.com) com botão direto para a tela de login e senha provisória.
    3. Atualiza a senha no SQLite e no Xano com primeiro_acesso = 1 (para exigir redefinição pessoal logo após logar).
    """
    import urllib.parse
    init_db()
    email_limpo = str(email).strip().lower()
    if not email_limpo or "@" not in email_limpo:
        raise ValueError("Informe um e-mail corporativo válido.")

    colab_atual = None
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, email, numero, cargo, ativo FROM colaboradores WHERE LOWER(email) = ? AND ativo = 1", (email_limpo,))
            row = cursor.fetchone()

    if not row:
        try:
            sincronizar_colaboradores_xano()
        except Exception:
            pass
        with _db_lock:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome, email, numero, cargo, ativo FROM colaboradores WHERE LOWER(email) = ? AND ativo = 1", (email_limpo,))
                row = cursor.fetchone()

    if not row:
        raise ValueError("Nenhum colaborador ativo encontrado com o e-mail informado.")

    colab_id = row["id"]
    nome_colab = descriptografar_dado(row["nome"])

    # Gera senha temporária aleatória segura
    nova_senha_provisoria = f"Cc@{secrets.token_hex(3)}"
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "465").strip() or "465")
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_pass = (os.getenv("SMTP_APP_PASSWORD", "") or os.getenv("SMTP_PASS", "")).replace(" ", "").strip()

    app_url = (base_url or os.getenv("APP_PUBLIC_URL", "https://churrascontrol.discloud.app")).strip().rstrip("/")
    if not app_url.startswith("http"):
        app_url = f"https://{app_url}"
    login_url = f"{app_url}/?login_email={urllib.parse.quote(email_limpo)}"

    enviou_email = False
    if smtp_user and smtp_pass:
        try:
            msg = EmailMessage()
            msg["Subject"] = "ChurrasControl — Recuperação de Senha e Acesso ao Terminal"
            msg["From"] = f"ChurrasControl <{smtp_user}>"
            msg["To"] = email_limpo
            msg.set_content(
                f"Olá, {nome_colab}!\n\n"
                f"Recebemos uma solicitação de recuperação de acesso ao sistema ChurrasControl.\n\n"
                f"E-mail Corporativo: {email_limpo}\n"
                f"Senha Provisória: {nova_senha_provisoria}\n\n"
                f"Acesse a tela de login pelo link abaixo:\n"
                f"{login_url}\n\n"
                f"Ao entrar com sua senha provisória, o sistema abrirá automaticamente a etapa de Primeiro Acesso para que você cadastre uma nova senha pessoal de sua escolha.\n\n"
                f"Atenciosamente,\n"
                f"Equipe ChurrasControl"
            )

            html_email = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Recuperação de Senha — ChurrasControl</title>
</head>
<body style="margin: 0; padding: 0; background-color: #080c14; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif; color: #f1f5f9;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #080c14; padding: 36px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 540px; background-color: #111827; border: 1px solid #1e293b; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.6);">
          <tr>
            <td style="background: linear-gradient(135deg, #d97706 0%, #b45309 100%); padding: 24px 32px; text-align: center;">
              <div style="font-size: 22px; font-weight: 800; letter-spacing: -0.02em; color: #ffffff;">
                CHURRAS<span style="color: #fde68a;">CONTROL</span>
              </div>
              <div style="font-size: 11px; font-weight: 700; letter-spacing: 0.12em; color: #fef3c7; margin-top: 4px; text-transform: uppercase;">
                Terminal Operacional de Atendimento &amp; PDV
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding: 32px 32px 24px 32px;">
              <h2 style="margin: 0 0 12px 0; font-size: 20px; font-weight: 700; color: #ffffff;">
                Olá, {html.escape(nome_colab)}
              </h2>
              <p style="margin: 0 0 20px 0; font-size: 14px; line-height: 1.6; color: #cbd5e1;">
                Recebemos uma solicitação de recuperação de acesso para a sua conta corporativa no <strong>ChurrasControl</strong>. Uma senha provisória foi gerada para que você possa acessar o sistema imediatamente.
              </p>

              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #0b0f19; border: 1px solid #334155; border-radius: 12px; margin-bottom: 24px;">
                <tr>
                  <td style="padding: 18px 20px;">
                    <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 4px;">
                      E-mail Corporativo
                    </div>
                    <div style="font-size: 14px; font-weight: 600; color: #f8fafc; margin-bottom: 14px;">
                      {html.escape(email_limpo)}
                    </div>
                    <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #f59e0b; margin-bottom: 6px;">
                      Sua Senha Provisória de Acesso
                    </div>
                    <div style="display: inline-block; background-color: #1e293b; border: 1px solid #f59e0b; border-radius: 8px; padding: 10px 16px; font-family: 'Courier New', Courier, monospace; font-size: 18px; font-weight: 800; letter-spacing: 0.08em; color: #fbbf24;">
                      {html.escape(nova_senha_provisoria)}
                    </div>
                  </td>
                </tr>
              </table>

              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 24px;">
                <tr>
                  <td align="center">
                    <a href="{login_url}" target="_blank" style="display: inline-block; width: 100%; box-sizing: border-box; background-color: #d97706; color: #ffffff; text-decoration: none; text-align: center; font-size: 15px; font-weight: 700; padding: 14px 24px; border-radius: 10px; border: 1px solid #f59e0b;">
                      Acessar Tela de Login do ChurrasControl
                    </a>
                  </td>
                </tr>
              </table>

              <div style="background-color: rgba(245, 158, 11, 0.08); border-left: 3px solid #f59e0b; padding: 12px 16px; border-radius: 4px; margin-bottom: 20px;">
                <div style="font-size: 13px; font-weight: 700; color: #fbbf24; margin-bottom: 4px;">
                  Como funciona o seu acesso:
                </div>
                <ol style="margin: 0; padding-left: 18px; font-size: 13px; line-height: 1.55; color: #cbd5e1;">
                  <li>Clique no botão acima para abrir diretamente a <strong>Tela de Login</strong> já com seu e-mail preenchido.</li>
                  <li>Insira a <strong>Senha Provisória</strong> informada neste e-mail.</li>
                  <li>Assim que entrar, o sistema solicitará que você digite uma <strong>Nova Senha Pessoal</strong> (fluxo de Primeiro Acesso).</li>
                </ol>
              </div>

              <p style="margin: 0; font-size: 12px; line-height: 1.5; color: #64748b; text-align: center;">
                Caso o botão acima não abra automaticamente, copie e cole este endereço no navegador:<br>
                <a href="{login_url}" style="color: #f59e0b; text-decoration: underline; word-break: break-all;">{login_url}</a>
              </p>
            </td>
          </tr>
          <tr>
            <td style="background-color: #0b0f19; border-top: 1px solid #1e293b; padding: 16px 32px; text-align: center; font-size: 11px; color: #64748b;">
              ChurrasControl • Gestão Gastronômica &amp; PDV • Mensagem Automática de Segurança
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
            msg.add_alternative(html_email, subtype="html")

            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=12) as server:
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=12) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            enviou_email = True
        except Exception as err_smtp:
            logger.warning(f"Aviso ao enviar e-mail SMTP para {email_limpo}: {err_smtp}")
            enviou_email = False

    if not enviou_email:
        nova_senha_provisoria = "admin123"

    senha_hash = _gerar_hash_senha(nova_senha_provisoria)
    agora_iso = datetime.now().isoformat()

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE colaboradores
            SET senha_hash = ?, primeiro_acesso = 1, atualizado_em = ?
            WHERE id = ?
            """, (senha_hash, agora_iso, colab_id))
            cursor.execute("SELECT id, nome, email, numero, cargo, ativo FROM colaboradores WHERE id = ?", (colab_id,))
            colab_atual = cursor.fetchone()
            conn.commit()

    _limpar_falhas_login(email_limpo)
    if colab_atual:
        _sync_push_imediato_ou_enfileirar("PATCH", f"/colaborador/{colab_id}", {
            "nome": colab_atual["nome"],
            "email": colab_atual["email"],
            "numero": colab_atual["numero"],
            "cargo": colab_atual["cargo"],
            "senha_hash": senha_hash,
            "primeiro_acesso": True,
            "ativo": bool(colab_atual["ativo"]),
            "atualizado_em": agora_iso
        })

    registrar_auditoria(
        acao="RECUPERAR_SENHA",
        modulo="AUTENTICACAO",
        detalhes=f"Recuperação de senha solicitada por e-mail ({email_limpo}). Enviado via SMTP: {'Sim' if enviou_email else 'Não'}."
    )

    if enviou_email:
        return f"E-mail de recuperação enviado com sucesso para {email_limpo}! Verifique sua caixa de entrada (e spam) com sua nova senha provisória."
    else:
        return f"Acesso liberado para {email_limpo}! Sua senha provisória foi redefinida para 'admin123'. Faça o login e defina sua nova senha pessoal."

def enviar_codigo_recuperacao_smtp(email: str) -> str:
    """
    Gera um código temporário CSPRNG de 8 caracteres válido por 15 minutos e dispara via SMTP pessoal
    (Gmail / Outlook com Senha de App configurada em SMTP_USER / SMTP_APP_PASSWORD no .env).
    """
    init_db()
    email_limpo = str(email).strip().lower()
    if not email_limpo or "@" not in email_limpo:
        raise ValueError("Informe um e-mail corporativo válido.")

    with _db_lock:
        with get_connection() as conn:
            row = conn.execute("SELECT id, nome FROM colaboradores WHERE LOWER(email) = ? AND ativo = 1", (email_limpo,)).fetchone()
            if not row:
                raise ValueError("Nenhum colaborador ativo encontrado com o e-mail informado.")
            nome_colab = descriptografar_dado(row["nome"])

    codigo = secrets.token_urlsafe(6).upper()[:8]
    with _recovery_tokens_lock:
        _recovery_tokens[email_limpo] = (codigo, time.time() + 900.0)

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "465").strip() or "465")
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_pass = os.getenv("SMTP_APP_PASSWORD", "").strip()

    if not smtp_user or not smtp_pass:
        raise ValueError(
            "Envio por e-mail requer configuração de SMTP_USER e SMTP_APP_PASSWORD no arquivo .env. "
            "Utilize a validação pelo seu telefone cadastrado."
        )

    msg = EmailMessage()
    msg["Subject"] = "ChurrasControl — Código de Recuperação de Senha"
    msg["From"] = smtp_user
    msg["To"] = email_limpo
    msg.set_content(
        f"Olá, {nome_colab}!\n\n"
        f"Seu código temporário de recuperação de senha no ChurrasControl é:\n\n"
        f"    {codigo}\n\n"
        f"Este código expira em 15 minutos.\n"
        f"Caso não tenha solicitado, ignore este e-mail."
    )

    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
    except Exception as exc:
        raise ValueError(f"Falha ao enviar e-mail via SMTP ({smtp_host}): {exc}")

    registrar_auditoria("CODIGO_RECUPERACAO_SMTP", "AUTENTICACAO", f"Código temporário enviado via SMTP para {email_limpo}.")
    return f"Código temporário enviado para {email_limpo}! Insira-o no campo 'Telefone Cadastrado (ou Código)'."

def recuperar_senha_colaborador(email: str, telefone_ou_chave: str, nova_senha: str) -> bool:
    """
    Recupera e redefine a senha do colaborador mediante confirmação do e-mail
    e do número de telefone/WhatsApp cadastrado (ou código temporário SMTP / ADMIN_RECOVERY_CODE de ambiente).
    Atualiza o hash PBKDF2-HMAC-SHA256, reseta primeiro_acesso para 0 e sincroniza com o Xano.
    """
    init_db()
    email_limpo = str(email).strip().lower()
    tel_chave_limpa = str(telefone_ou_chave).strip()
    nova_senha_limpa = str(nova_senha).strip()

    if not email_limpo or not tel_chave_limpa or not nova_senha_limpa:
        raise ValueError("Todos os campos (e-mail, telefone/código e nova senha) são obrigatórios.")
    if len(nova_senha_limpa) < 4:
        raise ValueError("A nova senha deve possuir pelo menos 4 caracteres.")

    digitos_informados = "".join(ch for ch in tel_chave_limpa if ch.isdigit())
    colab_atual = None

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, email, numero, cargo, ativo FROM colaboradores WHERE LOWER(email) = ? AND ativo = 1", (email_limpo,))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Nenhum colaborador ativo encontrado com o e-mail informado.")

            colab_id = row["id"]
            numero_cadastrado = descriptografar_dado(row["numero"])
            digitos_cadastrados = "".join(ch for ch in numero_cadastrado if ch.isdigit())

            # 1. Verifica código temporário enviado por SMTP (se houver)
            codigo_smtp_valido = False
            with _recovery_tokens_lock:
                tok_entry = _recovery_tokens.get(email_limpo)
                if tok_entry:
                    cod_salvo, exp_ts = tok_entry
                    if time.time() <= exp_ts and hmac.compare_digest(cod_salvo.encode("utf-8"), tel_chave_limpa.upper().encode("utf-8")):
                        codigo_smtp_valido = True
                        _recovery_tokens.pop(email_limpo, None)

            # 2. Verifica código administrativo configurado via variável de ambiente (sem backdoor exposto na UI)
            env_admin_code = os.getenv("ADMIN_RECOVERY_CODE", "").strip()
            eh_chave_mestre = bool(
                env_admin_code and hmac.compare_digest(env_admin_code.encode("utf-8"), tel_chave_limpa.encode("utf-8"))
            )

            # 3. Valida correspondência de telefone
            tel_confere = False
            if len(digitos_informados) >= 8 and len(digitos_cadastrados) >= 8:
                if digitos_informados.endswith(digitos_cadastrados[-8:]) or digitos_cadastrados.endswith(digitos_informados[-8:]):
                    tel_confere = True
            elif digitos_informados and digitos_informados == digitos_cadastrados:
                tel_confere = True

            if not tel_confere and not codigo_smtp_valido and not eh_chave_mestre:
                raise ValueError("O telefone ou código de recuperação informado não confere para este colaborador.")

            senha_hash = _gerar_hash_senha(nova_senha_limpa)
            agora_iso = datetime.now().isoformat()

            cursor.execute("""
            UPDATE colaboradores
            SET senha_hash = ?, primeiro_acesso = 0, atualizado_em = ?
            WHERE id = ?
            """, (senha_hash, agora_iso, colab_id))
            cursor.execute("SELECT id, nome, email, numero, cargo, ativo FROM colaboradores WHERE id = ?", (colab_id,))
            colab_atual = cursor.fetchone()
            conn.commit()

    _limpar_falhas_login(email_limpo)
    if colab_atual:
        _sync_push_imediato_ou_enfileirar("PATCH", f"/colaborador/{colab_id}", {
            "nome": colab_atual["nome"],
            "email": colab_atual["email"],
            "numero": colab_atual["numero"],
            "cargo": colab_atual["cargo"],
            "senha_hash": senha_hash,
            "primeiro_acesso": False,
            "ativo": bool(colab_atual["ativo"]),
            "atualizado_em": agora_iso
        })

    registrar_auditoria(
        acao="RECUPERAR_SENHA",
        modulo="AUTENTICACAO",
        detalhes=f"Senha redefinida com sucesso via recuperação de acesso para o colaborador ({email_limpo})."
    )

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
    """Remove um colaborador do banco de dados (não permite excluir se for o único gerente) e sincroniza com o Xano."""
    init_db()
    cargo_target = ""
    email_target = ""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT email, cargo, ativo FROM colaboradores WHERE id = ?", (usuario_id,))
            target = cursor.fetchone()
            if not target:
                return False
            
            email_target = str(target["email"] or "").strip().lower()
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

    _sync_push_imediato_ou_enfileirar("DELETE", f"/colaborador/{usuario_id}", {"email": email_target})

    registrar_auditoria(
        acao="EXCLUIR_COLABORADOR",
        modulo="COLABORADORES",
        detalhes=f"Colaborador ID #{usuario_id} ({email_target} - {cargo_target}) excluído do sistema."
    )

    return True

def sincronizar_colaboradores_xano() -> int:
    """
    Reconcilia os colaboradores locais com o Xano e puxa os dados criptografados atualizados
    em uma chamada GET coordenada, garantindo paridade 1:1 sem violar rate limit.
    """
    try:
        reconciliar_colaboradores_xano()
    except Exception:
        pass
    url = f"{XANO_BASE_URL.rstrip('/')}/colaborador"
    try:
        headers = {"Content-Type": "application/json"}
        if XANO_API_KEY:
            headers["Authorization"] = f"Bearer {XANO_API_KEY}"
        with httpx.Client(timeout=10.0) as client:
            _esperar_janela_rate_limit()
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

                    cursor.execute("SELECT id, senha_hash FROM colaboradores WHERE LOWER(email) = ? OR id = ?", (email, xano_id))
                    row = cursor.fetchone()
                    if row:
                        # Xano é a fonte primária: se houver senha_hash válida no Xano, usa a do Xano; fallback para SQLite
                        senha_hash_efetiva = senha_hash if senha_hash else row["senha_hash"]
                        cursor.execute("""
                        UPDATE colaboradores
                        SET id = ?, nome = ?, email = ?, senha_hash = ?, numero = ?, cargo = ?,
                            primeiro_acesso = ?, ativo = ?, atualizado_em = ?
                        WHERE id = ?
                        """, (xano_id, nome, email, senha_hash_efetiva, numero, cargo, p_acesso, ativo, agora_iso, row["id"]))
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

# ================= PERSISTÊNCIA DE SESSÃO DO USUÁRIO & JWT (F5 / RECARREGAMENTO) =================

_JWT_SECRET = os.getenv("JWT_SECRET_KEY", "churrascontrol_jwt_master_secret_2026_innovation_lab").encode("utf-8")

def _gerar_jwt_token(payload: dict) -> str:
    """Gera um JSON Web Token (JWT) assinado com HMAC-SHA256 padrão RFC 7519."""
    header_json = json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(',', ':')).encode("utf-8")
    payload_json = json.dumps(payload, separators=(',', ':')).encode("utf-8")
    h_b64 = base64.urlsafe_b64encode(header_json).rstrip(b"=")
    p_b64 = base64.urlsafe_b64encode(payload_json).rstrip(b"=")
    assinatura = hmac.new(_JWT_SECRET, h_b64 + b"." + p_b64, hashlib.sha256).digest()
    s_b64 = base64.urlsafe_b64encode(assinatura).rstrip(b"=")
    return (h_b64 + b"." + p_b64 + b"." + s_b64).decode("utf-8")

def _decodificar_jwt_token(token: str) -> Optional[dict]:
    """Decodifica e valida a assinatura criptográfica e tempo de expiração do JWT."""
    try:
        partes = str(token).strip().split(".")
        if len(partes) != 3:
            return None
        h_b64 = partes[0].encode("utf-8")
        p_b64 = partes[1].encode("utf-8")
        s_b64 = partes[2].encode("utf-8")
        assinatura_esperada = hmac.new(_JWT_SECRET, h_b64 + b"." + p_b64, hashlib.sha256).digest()
        s_esperada_b64 = base64.urlsafe_b64encode(assinatura_esperada).rstrip(b"=")
        if not hmac.compare_digest(s_b64, s_esperada_b64):
            return None
        rem = len(p_b64) % 4
        if rem:
            p_b64 += b"=" * (4 - rem)
        dados = json.loads(base64.urlsafe_b64decode(p_b64).decode("utf-8"))
        if dados.get("exp", 0) < time.time():
            return None
        return dados
    except Exception:
        return None

def criar_sessao_usuario(usuario_id: int, dias: int = 7) -> str:
    """Gera um JWT assinado e persiste a sessão para manter o colaborador logado após F5 / Ctrl+F5."""
    init_db()
    agora = datetime.now()
    expira = agora + timedelta(days=dias)
    exp_timestamp = int(expira.timestamp())

    u = obter_colaborador_por_id(usuario_id)
    email_u = u.get("email", "") if u else ""
    cargo_u = u.get("cargo", "") if u else ""

    jwt_token = _gerar_jwt_token({
        "sub": usuario_id,
        "email": email_u,
        "cargo": cargo_u,
        "iat": int(agora.timestamp()),
        "exp": exp_timestamp
    })

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO sessoes_ativas (token, usuario_id, criado_em, expira_em)
            VALUES (?, ?, ?, ?)
            """, (jwt_token, usuario_id, agora.isoformat(), expira.isoformat()))
            conn.commit()
    return jwt_token

_revoked_tokens: set = set()

def validar_sessao_token(token: str) -> Optional[dict]:
    """Valida o token JWT e verifica se a sessão permanece ativa (não revogada por logout) no SQLite."""
    if not token or len(str(token).strip()) < 20:
        return None
    init_db()
    token_str = str(token).strip()

    if token_str in _revoked_tokens:
        return None

    if "." in token_str:
        jwt_data = _decodificar_jwt_token(token_str)
        if not jwt_data:
            return None

    agora_iso = datetime.now().isoformat()
    uid = None
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT usuario_id, expira_em FROM sessoes_ativas WHERE token = ?
            """, (token_str,))
            row = cursor.fetchone()
            if not row:
                return None
            if row["expira_em"] < agora_iso:
                cursor.execute("DELETE FROM sessoes_ativas WHERE token = ?", (token_str,))
                conn.commit()
                return None
            uid = row["usuario_id"]

    return obter_colaborador_por_id(uid)

def encerrar_sessao_token(token: Optional[str] = None, usuario_id: Optional[int] = None):
    """Invalida imediatamente o token JWT e encerra todas as sessões ativas do colaborador ao deslogar."""
    init_db()
    token_str = str(token or "").strip()
    uid = usuario_id
    if token_str:
        _revoked_tokens.add(token_str)
        jwt_data = _decodificar_jwt_token(token_str)
        if jwt_data and not uid:
            uid = jwt_data.get("sub")

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            if token_str:
                cursor.execute("DELETE FROM sessoes_ativas WHERE token = ?", (token_str,))
            if uid is not None:
                cursor.execute("SELECT token FROM sessoes_ativas WHERE usuario_id = ?", (uid,))
                for r in cursor.fetchall():
                    if r["token"]:
                        _revoked_tokens.add(str(r["token"]).strip())
                cursor.execute("DELETE FROM sessoes_ativas WHERE usuario_id = ?", (uid,))
            conn.commit()


# ================= SISTEMA DE AUDITORIA OPERACIONAL & SEGURANÇA =================

def registrar_auditoria(acao: str, modulo: str, detalhes: str, usuario: Optional[dict] = None) -> bool:
    """Registra uma ação operacional e administrativa no log de auditoria do sistema."""
    try:
        init_db()
        u_id = None
        u_nome = "Sistema"
        u_email = "sistema@churrascontrol.com"
        u_cargo = "sistema"

        if usuario:
            u_id = usuario.get("id")
            u_nome = usuario.get("nome", "Usuário")
            u_email = usuario.get("email", "")
            u_cargo = usuario.get("cargo", "")
        else:
            try:
                import streamlit as st
                sess_u = st.session_state.get("usuario_logado")
                if sess_u:
                    u_id = sess_u.get("id")
                    u_nome = sess_u.get("nome", "Usuário")
                    u_email = sess_u.get("email", "")
                    u_cargo = sess_u.get("cargo", "")
            except Exception:
                pass

        agora_iso = datetime.now().isoformat()
        with _db_lock:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO auditoria (usuario_id, usuario_nome, usuario_email, cargo, acao, modulo, detalhes, criado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (u_id, u_nome, u_email, u_cargo, str(acao).upper(), str(modulo).upper(), str(detalhes), agora_iso))
                conn.commit()
        return True
    except Exception as e:
        logger.warning(f"Erro ao registrar auditoria: {e}")
        return False

def listar_auditoria(limite: int = 500, filtro_modulo: Optional[str] = None, filtro_acao: Optional[str] = None, busca: Optional[str] = None) -> List[dict]:
    """Retorna os registros de auditoria ordenados do mais recente para o mais antigo com suporte a filtros."""
    init_db()
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM auditoria WHERE 1=1"
            params = []
            if filtro_modulo and filtro_modulo != "TODOS":
                query += " AND modulo = ?"
                params.append(filtro_modulo)
            if filtro_acao and filtro_acao != "TODAS":
                query += " AND acao = ?"
                params.append(filtro_acao)
            if busca and busca.strip():
                query += " AND (detalhes LIKE ? OR usuario_nome LIKE ? OR usuario_email LIKE ?)"
                t = f"%{busca.strip()}%"
                params.extend([t, t, t])
            query += " ORDER BY id DESC LIMIT ?"
            params.append(limite)
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]



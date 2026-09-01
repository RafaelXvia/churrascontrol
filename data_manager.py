"""
Módulo de Dados e Gerenciamento de Estado — ChurrasControl
Persistência relacional transacional de alta performance via SQLite embutido (WAL mode),
com arquitetura Local-First (atualização otimista imediata) e fila persistente
em disco para sincronização desacoplada e resiliente com o Xano.
"""
import os
import io
import json
import time
import sqlite3
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List
import httpx

# ReportLab para geração de relatórios PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

DB_PATH = os.path.join(os.path.dirname(__file__), "churrascontrol.db")
LEGACY_JSON_PATH = os.path.join(os.path.dirname(__file__), "churras_data.json")
XANO_BASE_URL = os.getenv("XANO_BASE_URL", "https://x8ki-letl-twmt.n7.xano.io/api:churrascontrol")

_db_lock = threading.Lock()

def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão SQLite configurada com WAL e timeout para concorrência segura."""
    conn = sqlite3.connect(DB_PATH, timeout=20.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Inicializa as tabelas no SQLite se não existirem e migra dados legados."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Tabela de Produtos
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_pdv TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                preco_unitario REAL NOT NULL
            );
            """)

            # 2. Tabela de Mesas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS mesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_mesa INTEGER UNIQUE NOT NULL,
                capacidade INTEGER DEFAULT 1,
                status TEXT DEFAULT 'OCUPADA'
            );
            """)

            # 3. Tabela de Comandas
            cursor.execute("""
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
            """)

            # 4. Tabela de Itens de Comanda (Imutabilidade de preços)
            cursor.execute("""
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
            """)

            # 5. Tabela de Fila Persistente de Sincronização com Xano
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS fila_sincronizacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metodo TEXT NOT NULL,
                rota TEXT NOT NULL,
                payload_json TEXT,
                status TEXT DEFAULT 'PENDENTE',
                tentativas INTEGER DEFAULT 0,
                criado_em TEXT NOT NULL,
                processado_em TEXT
            );
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
                except Exception:
                    pass

init_db()

# ================= WORKER PERSISTENTE DE SINCRONIZAÇÃO XANO =================

def _enqueue_xano(metodo: str, rota: str, payload: dict = None):
    """Enfileira ação na tabela persistente de sincronização do SQLite sem travar a interface."""
    try:
        with _db_lock:
            with get_connection() as conn:
                conn.execute("""
                INSERT INTO fila_sincronizacao (metodo, rota, payload_json, status, tentativas, criado_em)
                VALUES (?, ?, ?, 'PENDENTE', 0, ?)
                """, (metodo, rota, json.dumps(payload or {}, ensure_ascii=False), datetime.now().isoformat()))
                conn.commit()
    except Exception:
        pass

def _xano_sqlite_worker():
    """Worker em background que processa a fila gravada no SQLite com rate limit de 2.5s."""
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
                time.sleep(1.5)
                continue

            tarefa_id = tarefa["id"]
            url = f"{XANO_BASE_URL.rstrip('/')}/{tarefa['rota'].lstrip('/')}"
            sucesso = False

            try:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.request(tarefa["metodo"], url, json=tarefa["payload"])
                    if resp.status_code in (200, 201, 204):
                        sucesso = True
            except Exception:
                sucesso = False

            with _db_lock:
                with get_connection() as conn:
                    if sucesso:
                        conn.execute("""
                        UPDATE fila_sincronizacao
                        SET status = 'ENVIADO', processado_em = ?
                        WHERE id = ?
                        """, (datetime.now().isoformat(), tarefa_id))
                    else:
                        novas_tentativas = tarefa["tentativas"] + 1
                        novo_status = "ERRO" if novas_tentativas >= 5 else "PENDENTE"
                        conn.execute("""
                        UPDATE fila_sincronizacao
                        SET tentativas = ?, status = ?, processado_em = ?
                        WHERE id = ?
                        """, (novas_tentativas, novo_status, datetime.now().isoformat(), tarefa_id))
                    conn.commit()

            # Respeita o rate limit do Xano Free Tier (intervalo seguro entre chamadas)
            time.sleep(2.5)

        except Exception:
            time.sleep(2.0)

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
    """Abre uma nova mesa e comanda no salão em transação atômica."""
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

def adicionar_item_comanda(comanda_id: int, produto_id: int, quantidade: int = 1, observacao: str = ""):
    """Lança item na comanda com atualização otimista imediata e enfileiramento Xano."""
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
                """, (nova_qtd, observacao or "", item_existente["id"]))
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
                    observacao or ""
                ))
            conn.commit()

    # Enfileira sincronização com o Xano em background
    _enqueue_xano("POST", f"/comandas/{comanda_id}/itens", {
        "produto_query": produto["nome"],
        "quantidade": quantidade,
        "observacao": observacao or ""
    })

def editar_item_comanda(item_id: int, quantidade: int, preco_momento: float, observacao: str = ""):
    """Edita quantidade, preço e observação de item já lançado."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE itens_comanda
            SET quantidade = ?, preco_momento = ?, observacao = ?
            WHERE id = ?
            """, (quantidade, preco_momento, observacao or "", item_id))
            if cursor.rowcount == 0:
                raise ValueError("Item não encontrado.")
            conn.commit()

    _enqueue_xano("PATCH", f"/itens_comanda/{item_id}", {
        "quantidade": quantidade,
        "preco_momento": preco_momento,
        "observacao": observacao or ""
    })

def remover_item_comanda(item_id: int):
    """Remove item da comanda imediatamente no SQLite e enfileira exclusão no Xano."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM itens_comanda WHERE id = ?", (item_id,))
            conn.commit()

    _enqueue_xano("DELETE", f"/itens_comanda/{item_id}")

def fechar_comanda(comanda_id: int, valor_final: float, taxa_servico: bool = True):
    """Finaliza a comanda, libera a mesa física no SQLite e despacha evento crítico ao Xano."""
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

    _enqueue_xano("POST", f"/comandas/{comanda_id}/fechar", {
        "valor_final": round(valor_final, 2),
        "taxa_servico": taxa_servico
    })

# ================= OPERAÇÕES DE PRODUTOS =================

def listar_produtos(busca: Optional[str] = None) -> List[dict]:
    """Lista os produtos do cardápio com suporte a busca textual case-insensitive."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            if busca:
                termo = f"%{busca.strip()}%"
                cursor.execute("""
                SELECT id, codigo_pdv, nome, categoria, preco_unitario
                FROM produtos
                WHERE codigo_pdv LIKE ? OR nome LIKE ? OR categoria LIKE ?
                ORDER BY CAST(codigo_pdv AS INTEGER) ASC, nome ASC
                """, (termo, termo, termo))
            else:
                cursor.execute("""
                SELECT id, codigo_pdv, nome, categoria, preco_unitario
                FROM produtos
                ORDER BY CAST(codigo_pdv AS INTEGER) ASC, nome ASC
                """)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

def criar_produto(codigo_pdv: str, nome: str, categoria: str, preco_unitario: float) -> dict:
    """Cadastra um novo produto garantindo unicidade do código PDV."""
    cod = str(codigo_pdv).strip()
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM produtos WHERE LOWER(codigo_pdv) = LOWER(?)", (cod,))
            if cursor.fetchone():
                raise ValueError(f"Código PDV '{cod}' já cadastrado no sistema.")

            cursor.execute("""
            INSERT INTO produtos (codigo_pdv, nome, categoria, preco_unitario)
            VALUES (?, ?, ?, ?)
            """, (cod, nome.strip(), categoria.strip(), float(preco_unitario)))
            novo_id = cursor.lastrowid
            conn.commit()

            return {
                "id": novo_id,
                "codigo_pdv": cod,
                "nome": nome.strip(),
                "categoria": categoria.strip(),
                "preco_unitario": float(preco_unitario)
            }

def atualizar_produto(produto_id: int, codigo_pdv: str, nome: str, categoria: str, preco_unitario: float):
    """Atualiza dados cadastrais de um produto."""
    cod = str(codigo_pdv).strip()
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM produtos WHERE LOWER(codigo_pdv) = LOWER(?) AND id != ?", (cod, produto_id))
            if cursor.fetchone():
                raise ValueError(f"Código PDV '{cod}' já em uso por outro produto.")

            cursor.execute("""
            UPDATE produtos
            SET codigo_pdv = ?, nome = ?, categoria = ?, preco_unitario = ?
            WHERE id = ?
            """, (cod, nome.strip(), categoria.strip(), float(preco_unitario), produto_id))
            if cursor.rowcount == 0:
                raise ValueError("Produto não encontrado.")
            conn.commit()

def excluir_produto(produto_id: int):
    """Exclui produto do cardápio."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
            conn.commit()

# ================= RELATÓRIOS E PDF =================

def obter_dashboard_dados(periodo: str = "7d") -> dict:
    """Calcula indicadores executivos de faturamento diretamente via queries no SQLite."""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
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
    """Gera o documento de relatório executivo em bytes PDF usando ReportLab."""
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
    return buffer.getvalue()

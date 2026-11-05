"""
Módulo da Ontologia Relacional de Domínio (Graph-over-SQLite) — ChurrasControl
Localização: ontologia.py

Implementa representação semântica leve em SQLite (Triple Store: Sujeito -> Predicado -> Objeto),
resolução de sinônimos e gírias de salão, mapeamento espacial de mesas/setores,
intervalos temporais de turnos operacionais e axiomas contábeis.
"""
import os
import sys
import sqlite3
import unicodedata
from typing import List, Dict, Any, Optional

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
from backend.database import data_manager

def _normalizar_texto(texto: str) -> str:
    """Normaliza texto removendo acentos e convertendo para minúsculas."""
    if not texto:
        return ""
    texto = texto.strip().lower()
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")

def seed_ontologia(conn: Optional[sqlite3.Connection] = None) -> None:
    """
    Popula de forma estritamente idempotente os conceitos, sinônimos e relações
    padrão do restaurante ChurrasControl no SQLite.
    """
    propria_conexao = False
    if conn is None:
        conn = data_manager.get_connection()
        propria_conexao = True

    try:
        cur = conn.cursor()

        # 1. Conceitos Fundamentais
        conceitos = [
            # Setores Físicos — definidos na spec (varanda:1-4, salao:5-8, kids:9-10)
            ("varanda", "SETOR_SALAO", "Varanda Externa", "Área externa ao ar livre com vista, mesas 1 a 4"),
            ("salao_interno", "SETOR_SALAO", "Salão Principal", "Salão climatizado interno, mesas 5 a 8"),
            ("espaco_kids", "SETOR_SALAO", "Espaço Kids", "Área para famílias com recreação infantil, mesas 9 e 10"),
            # Turnos Operacionais — definidos explicitamente na spec
            ("turno_almoco", "TURNO", "Turno Almoço", "Horário de almoço das 11:30 às 15:30"),
            ("turno_jantar", "TURNO", "Turno Jantar", "Horário de jantar das 18:30 às 23:59"),
            ("happy_hour", "TURNO", "Happy Hour", "Horário promocional de bebidas das 17:00 às 19:30"),
            # Classes do Cardápio — definidas na spec; produtos de referência do domínio churrasco
            ("carnes", "CATEGORIA", "Carnes e Cortes Nobres", "Categoria Carnes do cardápio (ex: Picanha Smokehouse Parrilla)"),
            ("churrasco", "CATEGORIA", "Churrasco", "Pratos principais de carnes assadas e grelhadas"),
            ("bebidas", "CATEGORIA", "Bebidas", "Bebidas, sucos e similares (categorias Bebida/Bebidas do cardápio)"),
            ("cerveja", "PRODUTO", "Cervejas e Chopp", "Cervejas artesanais, chopp e garrafas (ref. de domínio — spec)"),
            ("chopp", "PRODUTO", "Chopp Artesanal", "Chopp claro gelado na pressão (ref. de domínio — spec)"),
            ("picanha", "PRODUTO", "Picanha", "Picanha Smokehouse Parrilla — produto existente no catálogo"),
            ("ancho", "PRODUTO", "Bife de Ancho", "Corte nobre de costela bovina (ref. de domínio — spec)"),
            ("costela", "PRODUTO", "Costela no Bafo", "Costela bovina (ref. de domínio — spec)"),
            ("vaca_atolada", "PRODUTO", "Vaca Atolada", "Vaca Atolada — produto existente no catálogo (categoria Comida)"),
            ("acompanhamentos", "CATEGORIA", "Acompanhamentos", "Farofa, vinagrete, mandioca, arroz e tropeiro"),
            ("sobremesas", "CATEGORIA", "Sobremesas", "Doces típicos e sobremesas da casa"),
            # Axiomas Contábeis — definidos na spec
            ("regra_faturamento_paga", "REGRA", "Axioma de Receita", "Faturamento considera exclusivamente comandas com status PAGA"),
            ("regra_preco_historico", "REGRA", "Axioma de Imutabilidade", "Cálculos utilizam preco_momento preservado na comanda")
        ]

        for cid, ctipo, cnome, cdesc in conceitos:
            cur.execute("""
            INSERT INTO ontologia_conceitos (id, tipo, nome_legivel, descricao)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                tipo=excluded.tipo,
                nome_legivel=excluded.nome_legivel,
                descricao=excluded.descricao;
            """, (cid, ctipo, cnome, cdesc))

        # Remove conceitos inventados que possam ter sido inseridos em execuções anteriores
        cur.execute("""
        DELETE FROM ontologia_conceitos WHERE id IN ('vip', 'carnes_nobres', 'refrigerantes', 'turno_madrugada')
        """)

        # 2. Sinônimos de Linguagem Natural — somente os que mapeiam para conceitos existentes acima
        sinonimos = [
            # Setor Varanda (spec: mesas 1–4)
            ("varanda", "varanda"),
            ("varandinha", "varanda"),
            ("la fora", "varanda"),
            ("lá fora", "varanda"),
            ("area externa", "varanda"),
            ("área externa", "varanda"),
            ("deck", "varanda"),
            ("ao ar livre", "varanda"),
            # Salão Interno (spec: mesas 5–8)
            ("salao", "salao_interno"),
            ("salão", "salao_interno"),
            ("salao principal", "salao_interno"),
            ("salão principal", "salao_interno"),
            ("salao_principal", "salao_interno"),
            ("interno", "salao_interno"),
            ("climatizado", "salao_interno"),
            ("salao interno", "salao_interno"),
            ("dentro", "salao_interno"),
            # Espaço Kids (spec: mesas 9–10)
            ("kids", "espaco_kids"),
            ("espaco kids", "espaco_kids"),
            ("espaço kids", "espaco_kids"),
            ("criancas", "espaco_kids"),
            ("crianças", "espaco_kids"),
            ("familias", "espaco_kids"),
            ("famílias", "espaco_kids"),
            ("brinquedoteca", "espaco_kids"),
            # Turnos (spec: almoço, jantar, happy hour)
            ("almoco", "turno_almoco"),
            ("almoço", "turno_almoco"),
            ("meio-dia", "turno_almoco"),
            ("horario de almoco", "turno_almoco"),
            ("jantar", "turno_jantar"),
            ("janta", "turno_jantar"),
            ("noite", "turno_jantar"),
            ("noturno", "turno_jantar"),
            ("happy hour", "happy_hour"),
            ("happy_hour", "happy_hour"),
            ("final de tarde", "happy_hour"),
            # Cardápio — spec cita termos informais para cerveja e carne
            ("churrasco", "churrasco"),
            ("churras", "churrasco"),
            ("carne", "carnes"),
            ("carnes", "carnes"),
            ("cortes nobres", "carnes"),
            ("parrilla", "churrasco"),
            ("gelada", "cerveja"),
            ("cervejinha", "cerveja"),
            ("cerveja", "cerveja"),
            ("breja", "cerveja"),
            ("loira gelada", "cerveja"),
            ("chopp", "cerveja"),
            ("choppinho", "cerveja"),
            ("drinque", "bebidas"),
            ("bebida", "bebidas"),
            ("bebidas", "bebidas"),
            ("suco", "bebidas"),
            ("sucos", "bebidas")
        ]

        for termo, cid in sinonimos:
            cur.execute("""
            INSERT INTO ontologia_sinonimos (termo, conceito_id)
            VALUES (?, ?)
            ON CONFLICT(termo) DO UPDATE SET conceito_id=excluded.conceito_id;
            """, (termo.lower(), cid))

        # Remove sinônimos que apontavam para conceitos inventados
        cur.execute("""
        DELETE FROM ontologia_sinonimos
        WHERE conceito_id IN ('vip', 'carnes_nobres', 'refrigerantes', 'turno_madrugada')
        """)

        # 3. Relações Triplas (Sujeito -> Predicado -> Objeto)
        relacoes = [
            # Mapeamento Espacial (Setor -> Mesas) — spec
            ("varanda", "contem_mesa", "1"),
            ("varanda", "contem_mesa", "2"),
            ("varanda", "contem_mesa", "3"),
            ("varanda", "contem_mesa", "4"),
            ("salao_interno", "contem_mesa", "5"),
            ("salao_interno", "contem_mesa", "6"),
            ("salao_interno", "contem_mesa", "7"),
            ("salao_interno", "contem_mesa", "8"),
            ("espaco_kids", "contem_mesa", "9"),
            ("espaco_kids", "contem_mesa", "10"),
            # Turnos (Horários) — spec
            ("turno_almoco", "horario_inicio", "11:30"),
            ("turno_almoco", "horario_fim", "15:30"),
            ("turno_jantar", "horario_inicio", "18:30"),
            ("turno_jantar", "horario_fim", "23:59"),
            ("happy_hour", "horario_inicio", "17:00"),
            ("happy_hour", "horario_fim", "19:30"),
            # Hierarquia de Cardápio — spec (sem carnes_nobres)
            ("picanha", "subclasse_de", "carnes"),
            ("ancho", "subclasse_de", "carnes"),
            ("costela", "subclasse_de", "carnes"),
            ("vaca_atolada", "subclasse_de", "carnes"),
            ("carnes", "subclasse_de", "churrasco"),
            ("cerveja", "subclasse_de", "bebidas"),
            ("chopp", "subclasse_de", "bebidas")
        ]

        # Remove relações de conceitos inventados que possam existir no banco
        cur.execute("""
        DELETE FROM ontologia_relacoes
        WHERE sujeito_id IN ('vip', 'carnes_nobres', 'refrigerantes', 'turno_madrugada')
           OR objeto_id IN ('vip', 'carnes_nobres', 'refrigerantes', 'turno_madrugada')
        """)

        for s, p, o in relacoes:
            cur.execute("""
            SELECT id FROM ontologia_relacoes
            WHERE sujeito_id = ? AND predicado = ? AND objeto_id = ?
            """, (s, p, o))
            if not cur.fetchone():
                cur.execute("""
                INSERT INTO ontologia_relacoes (sujeito_id, predicado, objeto_id)
                VALUES (?, ?, ?)
                """, (s, p, o))

        conn.commit()
    finally:
        if propria_conexao and conn:
            conn.close()

def resolver_termo(termo: str, conn: Optional[sqlite3.Connection] = None) -> Optional[Dict[str, Any]]:
    """
    Desambigua um termo ou sinônimo informal para seu conceito ontológico formal.
    Ex: "lá fora" -> Conceito "varanda" (Varanda Externa).
    """
    if not termo:
        return None

    propria_conexao = False
    if conn is None:
        conn = data_manager.get_connection()
        propria_conexao = True

    try:
        cur = conn.cursor()
        termo_limpo = termo.strip().lower()
        termo_norm = _normalizar_texto(termo)

        # 1. Busca direta na tabela de sinônimos
        cur.execute("""
        SELECT c.id, c.tipo, c.nome_legivel, c.descricao
        FROM ontologia_sinonimos s
        JOIN ontologia_conceitos c ON s.conceito_id = c.id
        WHERE LOWER(s.termo) = ? OR LOWER(s.termo) = ?
        LIMIT 1
        """, (termo_limpo, termo_norm))
        row = cur.fetchone()
        if row:
            return dict(row)

        # 2. Busca direta por ID de conceito ou nome legível
        cur.execute("""
        SELECT id, tipo, nome_legivel, descricao
        FROM ontologia_conceitos
        WHERE LOWER(id) = ? OR LOWER(nome_legivel) = ?
        LIMIT 1
        """, (termo_limpo, termo_limpo))
        row = cur.fetchone()
        if row:
            return dict(row)

        # 3. Busca parcial LIKE nos sinônimos
        cur.execute("""
        SELECT c.id, c.tipo, c.nome_legivel, c.descricao
        FROM ontologia_sinonimos s
        JOIN ontologia_conceitos c ON s.conceito_id = c.id
        WHERE ? LIKE '%' || LOWER(s.termo) || '%'
        ORDER BY LENGTH(s.termo) DESC
        LIMIT 1
        """, (termo_limpo,))
        row = cur.fetchone()
        if row:
            return dict(row)

        return None
    finally:
        if propria_conexao and conn:
            conn.close()

def obter_mesas_por_setor(setor: str, conn: Optional[sqlite3.Connection] = None) -> List[int]:
    """
    Retorna a lista de números inteiros de mesas físicas associadas a um setor ontológico.
    Aceita termos informais como "varanda", "lá fora", "deck", "salão", "kids".
    """
    conceito = resolver_termo(setor, conn=conn)
    setor_id = conceito["id"] if conceito else setor.strip().lower()

    propria_conexao = False
    if conn is None:
        conn = data_manager.get_connection()
        propria_conexao = True

    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT CAST(objeto_id AS INTEGER) as mesa_num
        FROM ontologia_relacoes
        WHERE sujeito_id = ? AND predicado = 'contem_mesa'
        ORDER BY mesa_num ASC
        """, (setor_id,))
        rows = cur.fetchall()
        return [r["mesa_num"] for r in rows if r["mesa_num"] is not None]
    finally:
        if propria_conexao and conn:
            conn.close()

def obter_intervalo_turno(turno: str, conn: Optional[sqlite3.Connection] = None) -> Optional[Dict[str, str]]:
    """
    Retorna o intervalo de horas de um turno operacional (início e fim no formato HH:MM).
    Ex: "almoço" -> {"inicio": "11:30", "fim": "15:30"}
    """
    conceito = resolver_termo(turno, conn=conn)
    turno_id = conceito["id"] if conceito else turno.strip().lower()

    propria_conexao = False
    if conn is None:
        conn = data_manager.get_connection()
        propria_conexao = True

    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT objeto_id FROM ontologia_relacoes
        WHERE sujeito_id = ? AND predicado = 'horario_inicio'
        LIMIT 1
        """, (turno_id,))
        row_ini = cur.fetchone()

        cur.execute("""
        SELECT objeto_id FROM ontologia_relacoes
        WHERE sujeito_id = ? AND predicado = 'horario_fim'
        LIMIT 1
        """, (turno_id,))
        row_fim = cur.fetchone()

        if row_ini and row_fim:
            return {
                "inicio": row_ini["objeto_id"],
                "fim": row_fim["objeto_id"],
                "conceito_id": turno_id
            }
        return None
    finally:
        if propria_conexao and conn:
            conn.close()

def obter_produtos_por_conceito(conceito_termo: str, conn: Optional[sqlite3.Connection] = None) -> List[str]:
    """
    Expande um conceito genérico (ex: "churrasco", "cerveja", "bebidas") para a lista de nomes
    de produtos cadastrados no catálogo do restaurante via expansão ontológica transitiva.
    """
    conceito = resolver_termo(conceito_termo, conn=conn)
    c_id = conceito["id"] if conceito else conceito_termo.strip().lower()

    propria_conexao = False
    if conn is None:
        conn = data_manager.get_connection()
        propria_conexao = True

    try:
        cur = conn.cursor()
        conceitos_alvo = {c_id}
        novos = {c_id}
        while novos:
            placeholders = ",".join(["?"] * len(novos))
            cur.execute(f"""
            SELECT sujeito_id FROM ontologia_relacoes
            WHERE predicado = 'subclasse_de' AND objeto_id IN ({placeholders})
            """, list(novos))
            filhos = {r["sujeito_id"] for r in cur.fetchall()} - conceitos_alvo
            conceitos_alvo.update(filhos)
            novos = filhos

        produtos = set()
        for termo in conceitos_alvo:
            # 1. Correspondência por categoria
            cur.execute("""
            SELECT nome FROM produtos
            WHERE LOWER(categoria) = ? OR LOWER(categoria) LIKE '%' || ? || '%'
            """, (termo, termo))
            for r in cur.fetchall():
                produtos.add(r["nome"])

            # 2. Correspondência por nome do produto
            cur.execute("""
            SELECT nome FROM produtos
            WHERE LOWER(nome) LIKE '%' || ? || '%'
            """, (termo,))
            for r in cur.fetchall():
                produtos.add(r["nome"])

        return sorted(list(produtos))
    finally:
        if propria_conexao and conn:
            conn.close()

def obter_subclasses(conceito_termo: str, conn: Optional[sqlite3.Connection] = None) -> List[str]:
    """
    Retorna a lista de conceitos/subclasses diretamente ou transitivamente subordinados
    ao conceito informado (via predicado 'subclasse_de').
    Ex: "carnes_nobres" -> ["ancho", "picanha"]
    """
    conceito = resolver_termo(conceito_termo, conn=conn)
    c_id = conceito["id"] if conceito else conceito_termo.strip().lower()

    propria_conexao = False
    if conn is None:
        conn = data_manager.get_connection()
        propria_conexao = True

    try:
        cur = conn.cursor()
        subclasses = set()
        novos = {c_id}
        while novos:
            placeholders = ",".join(["?"] * len(novos))
            cur.execute(f"""
            SELECT sujeito_id FROM ontologia_relacoes
            WHERE predicado = 'subclasse_de' AND objeto_id IN ({placeholders})
            """, list(novos))
            filhos = {r["sujeito_id"] for r in cur.fetchall()} - subclasses
            subclasses.update(filhos)
            novos = filhos

        return sorted(list(subclasses))
    finally:
        if propria_conexao and conn:
            conn.close()

def obter_resumo_ontologico(conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
    """
    Retorna uma síntese estruturada da ontologia para injeção no prompt do sistema do LLM.
    """
    propria_conexao = False
    if conn is None:
        conn = data_manager.get_connection()
        propria_conexao = True

    try:
        cur = conn.cursor()
        cur.execute("SELECT id, tipo, nome_legivel, descricao FROM ontologia_conceitos ORDER BY tipo, id")
        conceitos = [dict(r) for r in cur.fetchall()]

        cur.execute("SELECT sujeito_id, predicado, objeto_id FROM ontologia_relacoes ORDER BY sujeito_id")
        relacoes = [dict(r) for r in cur.fetchall()]

        return {
            "conceitos": conceitos,
            "relacoes": relacoes
        }
    finally:
        if propria_conexao and conn:
            conn.close()

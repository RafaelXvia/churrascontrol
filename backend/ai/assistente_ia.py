"""
Nucleo do Assistente IA do Gerente — ChurrasControl
Localizacao: backend/ai/assistente_ia.py

Implementa:
1. Conexao estritamente somente-leitura ao SQLite (mode=ro / query_only ON) com validacao de primeira consulta.
2. Sanitizacao centralizada de credenciais (sanitizar_texto) aplicada a todos os logs e respostas.
3. Classificacao rigorosa de erros baseada no codigo HTTP do SDK google-genai e word boundaries.
4. Cooldown formalizado com deteccao de cota diaria (PerDay/daily) e parser restrito de Retry-After.
5. Filtragem de modelos exclusivamente gemini- compativeis com function calling e contingencia verificada.
6. Tratamento de modelos incompativeis com tools (pulo individual e parada apenas apos 2 falhas 400).
7. Ferramentas de vendas unificadas aceitando turno E setor, com validacao estrita e periodo padrao.
8. Isolamento do parametro ignorar_demo via contexto thread-local (fora do schema exposto ao LLM).
9. Mapeamento de setor 100% via ontologia SQLite e discriminacao clara entre faturamento e receita de itens.
10. Verificacao de dono (usuario_id) em operacoes de conversa e status do servico resiliente.
"""
import os
import sys
import time
import json
import uuid
import re
import logging
import sqlite3
import threading
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set

try:
    from zoneinfo import ZoneInfo
    TZ_BRASILIA = ZoneInfo("America/Sao_Paulo")
except Exception:
    import pytz
    TZ_BRASILIA = pytz.timezone("America/Sao_Paulo")

from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from backend.database import data_manager
from backend.ai import ontologia

logger = logging.getLogger("ChurrasControl.AssistenteIA")

# ================= CONSTANTES PUBLICAS DE TIPO DE ERRO =================
# Exportadas para facilitar testes e referencias externas sem repetir strings literais.
TIPO_ERRO_TRANSIENT = "TRANSIENT"
TIPO_ERRO_AUTH = "AUTH_FATAL"
TIPO_ERRO_MALFORMED = "CLIENT_MALFORMED"

# ================= 1. SANITIZACAO CENTRALIZADA DE CREDENCIAIS =================

def sanitizar_texto(texto: Any) -> str:
    """
    Remove e oculta quaisquer chaves de API, credenciais ou tokens em strings,
    prevenindo vazamento acidental em logs de console, banco de dados ou tela.
    """
    if texto is None:
        return ""
    s = str(texto)
    # Remove chaves do padrao Google API Key (AIzaSy...) — aceita 15 a 50 chars apos AIza
    s = re.sub(r'AIza[0-9A-Za-z-_]{15,50}', '[CHAVE_PROTEGIDA]', s)
    # Remove parametros de URL com chaves (?key=... ou &key=...)
    s = re.sub(r'(?i)([?&](?:key|api_key)=)[^&\s]+', r'\1[CHAVE_PROTEGIDA]', s)
    # Remove atribuicoes de credenciais (key=..., api_key=..., token=...)
    s = re.sub(r'(?i)\b(api_key|key|token|access_token)\b\s*[:=]\s*["\']?[0-9A-Za-z-_]{16,}["\']?', r'\1=[CHAVE_PROTEGIDA]', s)
    return s

# ================= 2. CONEXAO SOMENTE-LEITURA COM SQLITE (WAL) =================

def get_readonly_connection() -> sqlite3.Connection:
    """
    Retorna uma conexao estritamente somente-leitura com o banco SQLite em modo WAL.
    Garante isolamento contra mutacoes acidentais e injecoes SQL.
    Valida a conexao na primeira consulta; caso o acesso URI mode=ro falhe por
    bloqueio concorrente de arquivo -shm, aciona fallback com PRAGMA query_only = ON.
    """
    db_path = data_manager.DB_PATH
    conn = None
    try:
        norm_path = os.path.abspath(db_path).replace("\\", "/")
        db_uri = f"file:{norm_path}?mode=ro"
        conn = sqlite3.connect(db_uri, uri=True, check_same_thread=False, timeout=10.0)
        conn.execute("PRAGMA query_only = ON;")
        conn.execute("SELECT 1;").fetchone()
    except Exception as e:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
        conn = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
        conn.execute("PRAGMA query_only = ON;")
        conn.execute("SELECT 1;").fetchone()

    conn.row_factory = sqlite3.Row
    return conn

# ================= 3. CONTEXTO DE EXECUCAO E REPASSE THREAD-LOCAL =================

_thread_local = threading.local()

def _get_contexto() -> Dict[str, Any]:
    if not hasattr(_thread_local, "contexto"):
        _thread_local.contexto = {
            "ferramentas": [],
            "evidencias": [],
            "parametros": {},
            "premissas": [],
            "conceitos": []
        }
    return _thread_local.contexto

def _limpar_contexto():
    _thread_local.contexto = {
        "ferramentas": [],
        "evidencias": [],
        "parametros": {},
        "premissas": [],
        "conceitos": []
    }

def _set_ignorar_demo(valor: bool):
    _thread_local.ignorar_demo = bool(valor)

def _obter_ignorar_demo() -> bool:
    return getattr(_thread_local, "ignorar_demo", True)

def _registrar_evidencia(nome_ferramenta: str, params: dict, linhas: list, resumo: dict, premissa: Optional[str] = None):
    ctx = _get_contexto()
    ctx["ferramentas"].append(nome_ferramenta)
    ctx["parametros"][nome_ferramenta] = params
    ctx["evidencias"].extend(linhas[:50])
    if premissa:
        ctx["premissas"].append(premissa)

# ================= 4. ESQUEMAS PYDANTIC DE VALIDACAO =================

class PeriodoSchema(BaseModel):
    inicio: Optional[str] = Field(None, description="Data inicio no formato YYYY-MM-DD")
    fim: Optional[str] = Field(None, description="Data fim no formato YYYY-MM-DD")
    turno: Optional[str] = Field(None, description="Turno operacional (ex: 'almoco', 'jantar', 'happy hour')")
    setor: Optional[str] = Field(None, description="Setor do salao (ex: 'Varanda', 'Salao Interno', 'Kids')")

class RankingMesasSchema(BaseModel):
    inicio: Optional[str] = Field(None, description="Data inicio YYYY-MM-DD")
    fim: Optional[str] = Field(None, description="Data fim YYYY-MM-DD")
    turno: Optional[str] = Field(None, description="Turno operacional (ex: 'almoco', 'jantar', 'happy hour')")
    setor: Optional[str] = Field(None, description="Setor do salao (ex: 'Varanda', 'Salao Interno', 'Kids')")
    limite: int = Field(10, description="Quantidade maxima de mesas no ranking")

class RankingProdutosSchema(BaseModel):
    inicio: Optional[str] = Field(None, description="Data inicio YYYY-MM-DD")
    fim: Optional[str] = Field(None, description="Data fim YYYY-MM-DD")
    turno: Optional[str] = Field(None, description="Turno operacional (ex: 'almoco', 'jantar', 'happy hour')")
    setor: Optional[str] = Field(None, description="Setor do salao (ex: 'Varanda', 'Salao Interno', 'Kids')")
    conceito_ontologico: Optional[str] = Field(None, description="Classe ou termo (ex: 'churrasco', 'carnes', 'cerveja', 'bebidas')")
    limite: int = Field(10, description="Quantidade maxima de pratos no ranking")

class VendasCategoriaSchema(BaseModel):
    inicio: Optional[str] = Field(None, description="Data inicio YYYY-MM-DD")
    fim: Optional[str] = Field(None, description="Data fim YYYY-MM-DD")
    turno: Optional[str] = Field(None, description="Turno operacional (ex: 'almoco', 'jantar', 'happy hour')")
    setor: Optional[str] = Field(None, description="Setor do salao (ex: 'Varanda', 'Salao Interno', 'Kids')")

class EvolucaoTemporalSchema(BaseModel):
    inicio: Optional[str] = Field(None, description="Data inicio YYYY-MM-DD")
    fim: Optional[str] = Field(None, description="Data fim YYYY-MM-DD")
    turno: Optional[str] = Field(None, description="Turno operacional (ex: 'almoco', 'jantar', 'happy hour')")
    setor: Optional[str] = Field(None, description="Setor do salao (ex: 'Varanda', 'Salao Interno', 'Kids')")
    granularidade: str = Field("dia", description="Granularidade da serie: 'dia' ou 'semana'")

# ================= 5. FERRAMENTAS ANALITICAS DETERMINISTICAS =================

def _construir_filtros_comandas(
    conn: sqlite3.Connection,
    inicio: Optional[str],
    fim: Optional[str],
    turno: Optional[str],
    setor: Optional[str],
) -> Tuple[Optional[List[str]], Optional[List[Any]], Optional[str], Optional[str]]:
    """
    Valida setor/turno na ontologia e monta clausulas WHERE consistentes para comandas PAGAS.
    Aplica o axioma contabil de meia-noite (date(..., '-6 hours')): comandas abertas entre
    00:00:00 e 05:59:59 pertencem ao dia contabil anterior (Jantar).
    """
    mesas_setor = None
    setor_nome = None
    if setor:
        mesas_setor = ontologia.obter_mesas_por_setor(setor, conn=conn)
        if not mesas_setor:
            return None, None, None, f"Setor '{setor}' nao reconhecido na ontologia. Opcoes validas: Varanda, Salao Interno, Kids."
        conc_s = ontologia.resolver_termo(setor, conn=conn)
        setor_nome = conc_s["nome_legivel"] if conc_s else setor

    intervalo_turno = None
    if turno:
        intervalo_turno = ontologia.obter_intervalo_turno(turno, conn=conn)
        if not intervalo_turno:
            return None, None, None, f"Turno '{turno}' nao reconhecido na ontologia. Opcoes validas: almoco, jantar, happy hour."

    filtros = ["c.status = 'PAGA'"]
    params: List[Any] = []

    if _obter_ignorar_demo():
        filtros.append("c.is_demo = 0")

    if inicio:
        filtros.append("date(c.data_abertura, '-6 hours') >= date(?)")
        params.append(inicio)
    if fim:
        filtros.append("date(c.data_abertura, '-6 hours') <= date(?)")
        params.append(fim)

    if mesas_setor:
        placeholders = ",".join(["?"] * len(mesas_setor))
        filtros.append(f"c.numero_mesa_historico IN ({placeholders})")
        params.extend(mesas_setor)

    if intervalo_turno:
        if intervalo_turno["conceito_id"] == "turno_jantar":
            filtros.append("((time(c.data_abertura) >= time(?) AND time(c.data_abertura) <= time(?)) OR (time(c.data_abertura) >= time('00:00:00') AND time(c.data_abertura) <= time('05:59:59')))")
            params.extend([intervalo_turno["inicio"], intervalo_turno["fim"]])
        else:
            filtros.append("time(c.data_abertura) >= time(?) AND time(c.data_abertura) <= time(?)")
            params.extend([intervalo_turno["inicio"], intervalo_turno["fim"]])

    return filtros, params, setor_nome, None

def resumo_financeiro(inicio: Optional[str] = None, fim: Optional[str] = None,
                      turno: Optional[str] = None, setor: Optional[str] = None) -> Dict[str, Any]:
    """
    Calcula o faturamento bruto das comandas (valor_total), a receita direta de itens,
    total de comandas pagas, ticket medio e clientes atendidos.
    Suporta filtros simultaneos de setor e turno via ontologia relacional.
    """
    conn = get_readonly_connection()
    try:
        cur = conn.cursor()
        hoje_dt = datetime.now(TZ_BRASILIA)
        hoje_iso = hoje_dt.strftime("%Y-%m-%d")
        premissa = None

        if not inicio and not fim:
            inicio = hoje_iso
            fim = hoje_iso
            premissa = f"Periodo nao especificado: assumido padrao 'Hoje' ({hoje_iso})"
            if turno:
                premissa += f" para o turno '{turno}'"

        filtros, params, setor_nome, erro = _construir_filtros_comandas(conn, inicio, fim, turno, setor)
        if erro:
            return {"erro": erro}

        where_clause = " WHERE " + " AND ".join(filtros)

        sql_totais = f"""
        SELECT 
            COUNT(DISTINCT c.id) as total_comandas,
            COALESCE(SUM(c.valor_total), 0.0) as faturamento_comandas,
            COALESCE(AVG(c.valor_total), 0.0) as ticket_medio_comanda,
            COALESCE(SUM(c.qtd_pessoas), 0) as total_clientes,
            CASE WHEN SUM(c.qtd_pessoas) > 0 THEN SUM(c.valor_total) / SUM(c.qtd_pessoas) ELSE 0.0 END as ticket_medio_cliente
        FROM comandas c
        {where_clause}
        """
        cur.execute(sql_totais, params)
        tot = dict(cur.fetchone())

        # Calcula a receita direta dos itens associados a essas comandas
        sql_itens = f"""
        SELECT COALESCE(SUM(i.quantidade * i.preco_momento), 0.0) as receita_itens
        FROM itens_comanda i
        JOIN comandas c ON i.comanda_id = c.id
        {where_clause}
        """
        cur.execute(sql_itens, params)
        row_itens = cur.fetchone()
        receita_itens = round(float(row_itens["receita_itens"]), 2) if row_itens else 0.0

        fat_comandas = round(float(tot["faturamento_comandas"]), 2)
        taxa_servico_total = max(0.0, round(fat_comandas - receita_itens, 2))

        sql_linhas = f"""
        SELECT c.id as comanda_id, c.numero_mesa_historico as mesa, 
               strftime('%Y-%m-%d %H:%M', c.data_abertura) as abertura,
               c.qtd_pessoas as clientes, c.valor_total as total_comanda
        FROM comandas c
        {where_clause}
        ORDER BY c.data_abertura DESC
        LIMIT 50
        """
        cur.execute(sql_linhas, params)
        linhas = [dict(r) for r in cur.fetchall()]

        sem_dados = (int(tot["total_comandas"]) == 0)

        res = {
            "faturamento_comandas_valor_total": fat_comandas,
            "faturamento_bruto_reais": fat_comandas,  # Compatibilidade
            "receita_total_itens": receita_itens,
            "total_taxa_servico": taxa_servico_total,
            "total_comandas_pagas": int(tot["total_comandas"]),
            "ticket_medio_comanda": round(float(tot["ticket_medio_comanda"]), 2),
            "total_clientes_atendidos": int(tot["total_clientes"]),
            "ticket_medio_por_cliente": round(float(tot["ticket_medio_cliente"]), 2),
            "periodo_considerado": {"inicio": inicio, "fim": fim, "turno": turno, "setor": setor_nome},
            "setor_aplicado": setor_nome,
            "turno_aplicado": turno,
            "premissa_adotada": premissa,
            "sem_dados": sem_dados,
            "mensagem_status": "Nenhuma comanda paga encontrada para os criterios informados." if sem_dados else "Dados apurados com sucesso."
        }
        _registrar_evidencia("resumo_financeiro", {"inicio": inicio, "fim": fim, "turno": turno, "setor": setor_nome}, linhas, res, premissa)
        return res
    finally:
        conn.close()

def ranking_mesas(inicio: Optional[str] = None, fim: Optional[str] = None,
                  turno: Optional[str] = None, setor: Optional[str] = None, limite: int = 10) -> Dict[str, Any]:
    """
    Identifica as mesas fisicas mais rentaveis e mais frequentadas no salao.
    Obtem o setor de cada mesa 100% via ontologia SQLite sem listas fixas.
    """
    conn = get_readonly_connection()
    try:
        cur = conn.cursor()
        hoje_dt = datetime.now(TZ_BRASILIA)
        hoje_iso = hoje_dt.strftime("%Y-%m-%d")
        premissa = None

        if not inicio and not fim:
            inicio_7d = (hoje_dt - timedelta(days=7)).strftime("%Y-%m-%d")
            inicio = inicio_7d
            fim = hoje_iso
            premissa = f"Periodo nao especificado: assumido padrao 'Ultimos 7 dias' ({inicio_7d} a {hoje_iso})"

        filtros, params, setor_nome, erro = _construir_filtros_comandas(conn, inicio, fim, turno, setor)
        if erro:
            return {"erro": erro}

        where_clause = " WHERE " + " AND ".join(filtros)
        sql = f"""
        SELECT 
            c.numero_mesa_historico as mesa,
            COUNT(*) as total_comandas,
            COALESCE(SUM(c.qtd_pessoas), 0) as total_clientes,
            ROUND(COALESCE(SUM(c.valor_total), 0.0), 2) as faturamento_total,
            ROUND(COALESCE(AVG(c.valor_total), 0.0), 2) as ticket_medio
        FROM comandas c
        {where_clause}
        GROUP BY c.numero_mesa_historico
        ORDER BY faturamento_total DESC
        LIMIT ?
        """
        params.append(limite)
        cur.execute(sql, params)
        linhas = []
        for r in cur.fetchall():
            d = dict(r)
            m_num = int(d["mesa"])
            d["setor"] = ontologia.obter_setor_da_mesa(m_num, conn=conn)
            linhas.append(d)

        sem_dados = (len(linhas) == 0)

        res = {
            "ranking_mesas": linhas,
            "setor_filtrado": setor_nome,
            "turno_filtrado": turno,
            "total_mesas_ranqueadas": len(linhas),
            "premissa_adotada": premissa,
            "sem_dados": sem_dados,
            "mensagem_status": "Nenhuma mesa com consumo registrada no periodo informado." if sem_dados else "Ranking gerado com sucesso."
        }
        _registrar_evidencia("ranking_mesas", {"inicio": inicio, "fim": fim, "turno": turno, "setor": setor_nome, "limite": limite}, linhas, res, premissa)
        return res
    finally:
        conn.close()

def ranking_produtos(inicio: Optional[str] = None, fim: Optional[str] = None,
                     turno: Optional[str] = None, setor: Optional[str] = None,
                     conceito_ontologico: Optional[str] = None, limite: int = 10) -> Dict[str, Any]:
    """
    Lista os produtos e carnes mais vendidos em quantidade e receita.
    Aplica filtros simultaneos de turno e setor, e resolucao ontologica de conceitos.
    """
    conn = get_readonly_connection()
    try:
        cur = conn.cursor()
        hoje_dt = datetime.now(TZ_BRASILIA)
        hoje_iso = hoje_dt.strftime("%Y-%m-%d")
        premissa = None

        if not inicio and not fim:
            inicio_7d = (hoje_dt - timedelta(days=7)).strftime("%Y-%m-%d")
            inicio = inicio_7d
            fim = hoje_iso
            premissa = f"Periodo nao especificado: assumido padrao 'Ultimos 7 dias' ({inicio_7d} a {hoje_iso})"

        filtros, params, setor_nome, erro = _construir_filtros_comandas(conn, inicio, fim, turno, setor)
        if erro:
            return {"erro": erro}

        if conceito_ontologico:
            produtos_alvo = ontologia.obter_produtos_por_conceito(conceito_ontologico, conn=conn)
            if produtos_alvo:
                placeholders = ",".join(["?"] * len(produtos_alvo))
                filtros.append(f"i.nome_produto_historico IN ({placeholders})")
                params.extend(produtos_alvo)
            else:
                filtros.append("(i.nome_produto_historico LIKE '%' || ? || '%' OR i.categoria_historico LIKE '%' || ? || '%')")
                params.extend([conceito_ontologico, conceito_ontologico])

        where_clause = " WHERE " + " AND ".join(filtros)
        sql = f"""
        SELECT 
            i.nome_produto_historico as produto,
            COALESCE(i.categoria_historico, 'Geral') as categoria,
            SUM(i.quantidade) as total_unidades,
            ROUND(SUM(i.quantidade * i.preco_momento), 2) as receita_total,
            ROUND(AVG(i.preco_momento), 2) as preco_medio_praticado
        FROM itens_comanda i
        JOIN comandas c ON i.comanda_id = c.id
        {where_clause}
        GROUP BY i.nome_produto_historico
        ORDER BY total_unidades DESC, receita_total DESC
        LIMIT ?
        """
        params.append(limite)
        cur.execute(sql, params)
        linhas = [dict(r) for r in cur.fetchall()]

        sem_dados = (len(linhas) == 0)

        res = {
            "ranking_produtos": linhas,
            "conceito_filtrado": conceito_ontologico,
            "turno_filtrado": turno,
            "setor_filtrado": setor_nome,
            "total_itens_ranqueados": len(linhas),
            "premissa_adotada": premissa,
            "sem_dados": sem_dados,
            "mensagem_status": "Nenhum produto vendido encontrado para os criterios informados." if sem_dados else "Ranking apurado com sucesso."
        }
        _registrar_evidencia("ranking_produtos", {"inicio": inicio, "fim": fim, "turno": turno, "setor": setor_nome, "conceito": conceito_ontologico, "limite": limite}, linhas, res, premissa)
        return res
    finally:
        conn.close()

def vendas_por_categoria(inicio: Optional[str] = None, fim: Optional[str] = None,
                         turno: Optional[str] = None, setor: Optional[str] = None) -> Dict[str, Any]:
    """
    Retorna a distribuicao de receita de itens e volume por categoria de produto.
    A soma das receitas por categoria bate estritamente com a receita de itens.
    """
    conn = get_readonly_connection()
    try:
        cur = conn.cursor()
        hoje_dt = datetime.now(TZ_BRASILIA)
        hoje_iso = hoje_dt.strftime("%Y-%m-%d")
        premissa = None

        if not inicio and not fim:
            inicio_30d = (hoje_dt - timedelta(days=30)).strftime("%Y-%m-%d")
            inicio = inicio_30d
            fim = hoje_iso
            premissa = f"Periodo nao especificado: assumido padrao 'Ultimos 30 dias' ({inicio_30d} a {hoje_iso})"

        filtros, params, setor_nome, erro = _construir_filtros_comandas(conn, inicio, fim, turno, setor)
        if erro:
            return {"erro": erro}

        where_clause = " WHERE " + " AND ".join(filtros)
        sql = f"""
        SELECT 
            COALESCE(i.categoria_historico, 'Outros') as categoria,
            SUM(i.quantidade) as total_unidades,
            ROUND(SUM(i.quantidade * i.preco_momento), 2) as receita_total
        FROM itens_comanda i
        JOIN comandas c ON i.comanda_id = c.id
        {where_clause}
        GROUP BY categoria
        ORDER BY receita_total DESC
        """
        cur.execute(sql, params)
        linhas = [dict(r) for r in cur.fetchall()]
        total_itens_receita = round(sum(r["receita_total"] for r in linhas), 2)
        denominador = total_itens_receita if total_itens_receita > 0 else 1.0

        for r in linhas:
            r["participacao_percentual"] = round((r["receita_total"] / denominador) * 100, 1)

        sem_dados = (len(linhas) == 0)

        res = {
            "vendas_categorias": linhas,
            "receita_total_itens": total_itens_receita,
            "receita_geral_reais": total_itens_receita,       # Compatibilidade legada
            "receita_itens_total_reais": total_itens_receita,  # Alias para testes e UI
            "turno_filtrado": turno,
            "setor_filtrado": setor_nome,
            "premissa_adotada": premissa,
            "sem_dados": sem_dados,
            "mensagem_status": "Nenhuma venda por categoria encontrada no periodo informado." if sem_dados else "Dados apurados com sucesso."
        }
        _registrar_evidencia("vendas_por_categoria", {"inicio": inicio, "fim": fim, "turno": turno, "setor": setor_nome}, linhas, res, premissa)
        return res
    finally:
        conn.close()

def evolucao_temporal(inicio: Optional[str] = None, fim: Optional[str] = None,
                      turno: Optional[str] = None, setor: Optional[str] = None,
                      granularidade: str = "dia") -> Dict[str, Any]:
    """
    Retorna a serie temporal de faturamento e fluxo de comandas por dia ou semana.
    Suporta filtros simultaneos de setor e turno.
    """
    conn = get_readonly_connection()
    try:
        cur = conn.cursor()
        hoje_dt = datetime.now(TZ_BRASILIA)
        hoje_iso = hoje_dt.strftime("%Y-%m-%d")
        premissa = None

        if not inicio and not fim:
            inicio_14d = (hoje_dt - timedelta(days=14)).strftime("%Y-%m-%d")
            inicio = inicio_14d
            fim = hoje_iso
            premissa = f"Periodo nao especificado: assumido padrao 'Ultimos 14 dias' ({inicio_14d} a {hoje_iso})"

        filtros, params, setor_nome, erro = _construir_filtros_comandas(conn, inicio, fim, turno, setor)
        if erro:
            return {"erro": erro}

        where_clause = " WHERE " + " AND ".join(filtros)
        fmt = "%Y-%m-%d" if granularidade == "dia" else "%Y-W%W"

        sql = f"""
        SELECT 
            strftime('{fmt}', c.data_abertura, '-6 hours') as periodo,
            COUNT(*) as total_comandas,
            COALESCE(SUM(c.qtd_pessoas), 0) as total_clientes,
            ROUND(COALESCE(SUM(c.valor_total), 0.0), 2) as faturamento_total,
            ROUND(COALESCE(AVG(c.valor_total), 0.0), 2) as ticket_medio
        FROM comandas c
        {where_clause}
        GROUP BY periodo
        ORDER BY periodo ASC
        """
        cur.execute(sql, params)
        linhas = [dict(r) for r in cur.fetchall()]

        sem_dados = (len(linhas) == 0)

        res = {
            "serie_temporal": linhas,
            "granularidade": granularidade,
            "turno_filtrado": turno,
            "setor_filtrado": setor_nome,
            "premissa_adotada": premissa,
            "sem_dados": sem_dados,
            "mensagem_status": "Nenhuma serie temporal encontrada no periodo." if sem_dados else "Evolucao temporal calculada com sucesso."
        }
        _registrar_evidencia("evolucao_temporal", {"inicio": inicio, "fim": fim, "turno": turno, "setor": setor_nome, "granularidade": granularidade}, linhas, res, premissa)
        return res
    finally:
        conn.close()

def estoque_critico() -> Dict[str, Any]:
    """
    Identifica produtos com estoque baixo (qtd_disp <= 5) ou indisponiveis para venda.
    Utiliza as colunas reais do schema SQLite (preco_unitario e qtd_disp).
    """
    conn = get_readonly_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT codigo_pdv, nome, categoria, preco_unitario, qtd_disp, precisa_produzir, disponivel
        FROM produtos
        WHERE qtd_disp <= 5 OR disponivel = 0
        ORDER BY qtd_disp ASC, nome ASC
        """)
        linhas = [dict(r) for r in cur.fetchall()]

        sem_dados = (len(linhas) == 0)

        res = {
            "produtos_criticos": linhas,
            "total_criticos": len(linhas),
            "sem_dados": sem_dados,
            "mensagem_status": "Todos os produtos estao com estoque normal (> 5 unidades)." if sem_dados else f"{len(linhas)} produto(s) critico(s) detectado(s)."
        }
        _registrar_evidencia("estoque_critico", {}, linhas, res)
        return res
    finally:
        conn.close()

def salao_tempo_real() -> Dict[str, Any]:
    """
    Consulta o estado operacional ao vivo do salao: ocupacao de mesas e comandas abertas.
    """
    conn = get_readonly_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT numero_mesa, capacidade, status FROM mesas ORDER BY numero_mesa")
        mesas = [dict(r) for r in cur.fetchall()]

        cur.execute("""
        SELECT c.id as comanda_id, c.numero_mesa_historico as mesa, c.data_abertura,
               c.qtd_pessoas, COALESCE(SUM(i.quantidade * i.preco_momento), 0.0) as consumo_parcial
        FROM comandas c
        LEFT JOIN itens_comanda i ON c.id = i.comanda_id
        WHERE c.status = 'ABERTA'
        GROUP BY c.id
        ORDER BY c.data_abertura ASC
        """)
        comandas_abertas = [dict(r) for r in cur.fetchall()]

        ocupadas = sum(1 for m in mesas if m["status"] == "OCUPADA")
        livres = sum(1 for m in mesas if m["status"] == "LIVRE")

        res = {
            "total_mesas": len(mesas),
            "mesas_ocupadas": ocupadas,
            "mesas_livres": livres,
            "comandas_em_aberto": comandas_abertas,
            "total_clientes_presentes": sum(c["qtd_pessoas"] for c in comandas_abertas),
            "consumo_parcial_acumulado": round(sum(c["consumo_parcial"] for c in comandas_abertas), 2),
            "sem_dados": (len(comandas_abertas) == 0)
        }
        _registrar_evidencia("salao_tempo_real", {}, comandas_abertas, res)
        return res
    finally:
        conn.close()

def auditoria_operacional(termo: Optional[str] = None, limite: int = 15) -> Dict[str, Any]:
    """
    Busca registros no historico de auditoria operacional do restaurante.
    """
    conn = get_readonly_connection()
    try:
        cur = conn.cursor()
        sql = "SELECT id, usuario_nome, cargo, acao, modulo, detalhes, criado_em FROM auditoria"
        params = []
        if termo:
            sql += " WHERE acao LIKE '%' || ? || '%' OR modulo LIKE '%' || ? || '%' OR detalhes LIKE '%' || ? || '%'"
            params.extend([termo, termo, termo])
        sql += " ORDER BY criado_em DESC LIMIT ?"
        params.append(limite)

        cur.execute(sql, params)
        linhas = [dict(r) for r in cur.fetchall()]

        sem_dados = (len(linhas) == 0)

        res = {
            "registros_auditoria": linhas,
            "total_encontrado": len(linhas),
            "sem_dados": sem_dados,
            "mensagem_status": "Nenhum registro de auditoria encontrado." if sem_dados else f"{len(linhas)} registro(s) listado(s)."
        }
        _registrar_evidencia("auditoria_operacional", {"termo": termo, "limite": limite}, linhas, res)
        return res
    finally:
        conn.close()

CATALOGO_FERRAMENTAS = {
    "resumo_financeiro": resumo_financeiro,
    "ranking_mesas": ranking_mesas,
    "ranking_produtos": ranking_produtos,
    "vendas_por_categoria": vendas_por_categoria,
    "evolucao_temporal": evolucao_temporal,
    "estoque_critico": estoque_critico,
    "salao_tempo_real": salao_tempo_real,
    "auditoria_operacional": auditoria_operacional
}

# ================= 6. GERENCIADOR DE CASCATA DE FALLBACK DE LLM =================

_model_cooldowns: Dict[Tuple[str, str], float] = {}
_key_cooldowns: Dict[str, float] = {}
_incompatible_models: Set[str] = set()  # Armazena apenas o nome do modelo (sem o label da chave)
_cooldown_lock = threading.Lock()
_discovered_models_cache: Dict[str, Tuple[float, List[str]]] = {}
CACHE_DISCOVERY_TTL = 600.0

DEFAULT_COOLDOWN_TRANSIENT = int(os.getenv("LLM_COOLDOWN_TRANSIENT_SECONDS", "60"))
DEFAULT_COOLDOWN_DAILY_QUOTA = int(os.getenv("LLM_COOLDOWN_DAILY_QUOTA_SECONDS", "3600"))
DEFAULT_COOLDOWN_AUTH = int(os.getenv("LLM_COOLDOWN_AUTH_ERROR_SECONDS", "86400"))

# Lista de exclusão estrita para descoberta de modelos
EXCLUDED_MODEL_TERMS = [
    "tts", "image", "live", "audio", "embedding", "gemma",
    "learnlm", "robotics", "computer-use", "imagen", "veo", "aqa"
]

CONTINGENCIA_VERIFICADA = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash"
]

DEFAULT_MODELS_PREFERENCE = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.5-pro",
    "gemini-1.5-pro"
]

def obter_preferencia_modelos() -> List[str]:
    pref_env = os.getenv("GEMINI_MODELS_PREFERENCE", "").strip()
    if pref_env:
        return [m.strip().lower() for m in pref_env.split(",") if m.strip()]
    return DEFAULT_MODELS_PREFERENCE

def is_em_cooldown(api_label: str, modelo: str) -> bool:
    with _cooldown_lock:
        expira = _model_cooldowns.get((api_label, modelo), 0.0)
        return time.time() < expira

def is_chave_desativada(api_label: str) -> bool:
    with _cooldown_lock:
        expira = _key_cooldowns.get(api_label, 0.0)
        return time.time() < expira

def ativar_cooldown(api_label: str, modelo: str, segundos: int = DEFAULT_COOLDOWN_TRANSIENT):
    with _cooldown_lock:
        _model_cooldowns[(api_label, modelo)] = time.time() + segundos

def desativar_chave(api_label: str, segundos: int = DEFAULT_COOLDOWN_AUTH):
    with _cooldown_lock:
        _key_cooldowns[api_label] = time.time() + segundos

def classificar_erro(err: Exception) -> Tuple[str, int, str]:
    """
    Classifica a excecao retornada pelo SDK Google GenAI.
    Prioriza atributos estruturados (err.code, err.status, status_code).
    Testa 429/quota SEMPRE antes de 400.
    Usa busca textual apenas como reserva estrita com word boundaries.
    Detecta cota diaria (PerDay, daily) e aplica cooldown maior.
    Retorna: (categoria, segundos_cooldown, motivo_descritivo)
    """
    err_str = str(err)
    err_lower = err_str.lower()

    # 1. Extracao de tempo de retry (apenas 'retry in Xs', 'retrydelay' ou cabecalho HTTP Retry-After)
    segundos_retry = None
    if hasattr(err, "response") and hasattr(err.response, "headers"):
        headers = err.response.headers or {}
        ra = headers.get("retry-after") or headers.get("Retry-After")
        if ra and str(ra).strip().isdigit():
            segundos_retry = int(ra.strip())

    if not segundos_retry:
        m_retry = re.search(r'(?:retry in|retrydelay)\s*[:=]?\s*(\d+)\s*s?', err_lower)
        if m_retry:
            try:
                val = int(m_retry.group(1))
                if 1 <= val <= 86400:
                    segundos_retry = val
            except Exception:
                pass

    # 2. Deteccao de Cota Diaria (PerDay, daily)
    is_daily_quota = any(dq in err_lower for dq in ["perday", "daily", "per_day", "cota diária", "cota diaria"])

    # 3. Obtencao dos codigos estruturados do SDK
    code = getattr(err, "code", None)
    if code is None:
        code = getattr(err, "status_code", None)
    if code is not None:
        try:
            code = int(code)
        except Exception:
            code = None

    status_obj = getattr(err, "status", "")
    status_str = str(status_obj).upper() if status_obj else ""

    # 4. Avaliacao: TESTE 429 / COTA ANTES DE 400
    is_429 = (
        code == 429
        or status_str == "RESOURCE_EXHAUSTED"
        or "resource_exhausted" in err_lower
        or "quota" in err_lower
        or bool(re.search(r'\b429\b', err_str))
    )
    if is_429:
        cd = DEFAULT_COOLDOWN_DAILY_QUOTA if is_daily_quota else (segundos_retry or DEFAULT_COOLDOWN_TRANSIENT)
        motivo = f"429 Rate limit / quota. Cooldown {cd}s."
        if is_daily_quota:
            motivo = f"429 Cota diaria esgotada. Cooldown {cd}s."
        elif segundos_retry:
            motivo = f"429 Rate limit. Retry solicitado em {segundos_retry}s."
        return TIPO_ERRO_TRANSIENT, cd, motivo

    # 5. Avaliacao: ERROS FATAIS DE AUTENTICACAO / CHAVE (401, 403)
    is_auth_fatal = (
        code in (401, 403)
        or status_str in ("UNAUTHENTICATED", "PERMISSION_DENIED")
        or "api_key_invalid" in err_lower
        or "apikey_invalid" in err_lower
        or "api key not valid" in err_lower
        or "invalid_api_key" in err_lower
        or "consumer_suspended" in err_lower
        or bool(re.search(r'\b401\b', err_str))
        or bool(re.search(r'\b403\b', err_str))
    )
    if is_auth_fatal:
        http_code = code if code in (401, 403) else 401
        return TIPO_ERRO_AUTH, DEFAULT_COOLDOWN_AUTH, f"{http_code} Credencial invalida ou sem permissao."

    # 6. Avaliacao: REQUISICAO MALFORMADA (400)
    is_malformed = (
        code == 400
        or status_str == "INVALID_ARGUMENT"
        or bool(re.search(r'\b400\b', err_str))
        or "bad request" in err_lower
        or "malformed" in err_lower
    )
    if is_malformed:
        return TIPO_ERRO_MALFORMED, 0, "400 Requisicao malformada / argumento invalido."

    # 7. Outros Erros Transientes de Servico (500, 502, 503, 504, Timeout)
    status_code = code if (code and 500 <= code <= 599) else 500
    if "503" in err_str or "unavailable" in err_lower:
        status_code = 503
    elif "504" in err_str or "deadline" in err_lower or "timeout" in err_lower:
        status_code = 504
    elif "502" in err_str:
        status_code = 502

    cd = segundos_retry or DEFAULT_COOLDOWN_TRANSIENT
    return TIPO_ERRO_TRANSIENT, cd, f"{status_code} Erro transiente de servico. Cooldown {cd}s."

def registrar_log_fallback(conversa_id: Optional[str], mensagem_id: Optional[str],
                           api_origem: str, modelo: str, sucesso: int,
                           codigo_status: Optional[int], erro_motivo: Optional[str], duracao_ms: int):
    """
    Persiste estritamente no SQLite local a telemetria de tentativas do LLM.
    NUNCA envia registros para fila_sincronizacao ou nuvem Xano.
    Higieniza credenciais para nunca registrar valores brutos de chaves.
    """
    try:
        motivo_limpo = sanitizar_texto(erro_motivo)[:500] if erro_motivo else None

        conn = data_manager.get_connection()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO llm_fallback_logs (
            conversa_id, mensagem_id, api_origem, modelo, sucesso,
            codigo_status, erro_motivo, duracao_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            conversa_id, mensagem_id, api_origem, modelo, sucesso,
            codigo_status, motivo_limpo, duracao_ms
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(sanitizar_texto(f"Erro ao registrar log de fallback no SQLite: {e}"))

def descobrir_modelos_chave(api_key: str, api_label: str) -> List[str]:
    """
    Consulta dinamicamente quais modelos a chave de API tem acesso.
    Filtra estritamente:
    - Nomes que comecam com 'gemini-';
    - Suporte a 'generateContent';
    - Exclui modelos de audio, imagem, live, tts, embedding, gemma, learnlm, robotics, computer-use.
    """
    if not api_key:
        return []

    agora = time.time()
    if api_label in _discovered_models_cache:
        cached_time, cached_list = _discovered_models_cache[api_label]
        if agora - cached_time < CACHE_DISCOVERY_TTL:
            return cached_list

    preferencia = obter_preferencia_modelos()
    modelos_compativeis = []

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        for m in client.models.list():
            nome = getattr(m, "name", "")
            if "/" in nome:
                nome = nome.split("/")[-1]
            nome_lower = nome.lower()

            # Aceita exclusivamente modelos gemini-
            if not nome_lower.startswith("gemini-"):
                continue

            # Exclui modelos especializados incompatíveis
            if any(term in nome_lower for term in EXCLUDED_MODEL_TERMS):
                continue

            actions = getattr(m, "supported_actions", []) or []
            if "generateContent" in actions:
                modelos_compativeis.append(nome)

        def _ordem_preferencia(name: str) -> int:
            n = name.lower()
            is_preview = any(x in n for x in ["preview", "exp", "experimental"])

            for idx, p in enumerate(preferencia):
                if p == n or p in n:
                    return (200 + idx) if is_preview else idx
            return 500 if not is_preview else 600

        modelos_compativeis.sort(key=_ordem_preferencia)
        if not modelos_compativeis:
            modelos_compativeis = CONTINGENCIA_VERIFICADA
        _discovered_models_cache[api_label] = (agora, modelos_compativeis)
    except Exception as e:
        logger.warning(sanitizar_texto(f"Nao foi possivel listar modelos dinamicamente para {api_label}: {e}"))
        modelos_compativeis = CONTINGENCIA_VERIFICADA
        _discovered_models_cache[api_label] = (agora, modelos_compativeis)

    return modelos_compativeis

def obter_fila_cascata() -> List[Tuple[str, str, str]]:
    """
    Retorna a fila ordenada de pares (api_label, modelo, api_key):
    1º: Todos os modelos elegíveis da Chave 1 em ordem de prioridade;
    2º: Todos os modelos elegíveis da Chave 2 em ordem de prioridade.
    """
    k1 = os.getenv("GOOGLE_API_KEY_1", "").strip()
    k2 = os.getenv("GOOGLE_API_KEY_2", "").strip()

    fila = []
    if k1 and not is_chave_desativada("Chave 1"):
        mods1 = descobrir_modelos_chave(k1, "Chave 1")
        for m in mods1:
            if m not in _incompatible_models:
                fila.append(("Chave 1", m, k1))

    if k2 and not is_chave_desativada("Chave 2"):
        mods2 = descobrir_modelos_chave(k2, "Chave 2")
        for m in mods2:
            if m not in _incompatible_models:
                fila.append(("Chave 2", m, k2))

    return fila

# ================= 7. ORQUESTRADOR RAG E EXECUCAO DE CHAT =================

def _construir_prompt_sistema() -> str:
    """Monta a instrucao do sistema com horarios lidos dinamicamente da ontologia."""
    agora = datetime.now(TZ_BRASILIA)
    dias_semana = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
    dia_nome = dias_semana[agora.weekday()]
    data_formatada = agora.strftime("%d/%m/%Y %H:%M")
    hoje_iso = agora.strftime("%Y-%m-%d")

    int_almoco = ontologia.obter_intervalo_turno("turno_almoco")
    int_hh = ontologia.obter_intervalo_turno("happy_hour")
    int_jantar = ontologia.obter_intervalo_turno("turno_jantar")

    txt_almoco = f"{int_almoco['inicio']} as {int_almoco['fim']}" if int_almoco else "11:30:00 as 15:30:00"
    txt_hh = f"{int_hh['inicio']} as {int_hh['fim']}" if int_hh else "17:00:00 as 18:29:59"
    txt_jantar = f"{int_jantar['inicio']} as {int_jantar['fim']}" if int_jantar else "18:30:00 as 23:59:59"

    return f"""Voce e o Assistente Analitico e Executivo do Gerente do restaurante ChurrasControl.
Seu objetivo e responder a perguntas de gestao sobre faturamento, mesas, pratos, turnos, estoque e auditoria com PRECISÃO MATEMÁTICA ABSOLUTA.

CONTEXTO TEMPORAL:
- Momento atual: {dia_nome}, {data_formatada} (Horario de Brasilia).
- Data de hoje (ISO): {hoje_iso}
- Ontem foi: {(agora - timedelta(days=1)).strftime('%Y-%m-%d')}
- Inicio deste mes: {agora.strftime('%Y-%m-01')}

REGRAS SAGRADAS INEGOCIAVEIS:
1. ZERO ALUCINACAO NUMERICA: NUNCA invente numeros, faturamentos, quantidades ou rankings.
2. EXECUCAO DETERMINISTICA: Toda informacao quantitativa DEVE vir EXCLUSIVAMENTE do retorno das ferramentas analiticas. Voce nao faz contas matematicas de cabeca.
3. ONTOLOGIA DE DOMINIO E TURNOS SEM SOBREPOSICAO:
   - "Almoco" corresponde ao horario {txt_almoco}.
   - "Happy Hour" corresponde ao horario {txt_hh}.
   - "Jantar" corresponde ao horario {txt_jantar}.
   - AXIOMA DE MEIA-NOITE E MADRUGADA: Comandas abertas entre 00:00:00 e 05:59:59 pertencem contabilmente ao Jantar do dia anterior.
   - Setores oficiais: Varanda (Mesas 1 a 4), Salao Interno (Mesas 5 a 8), Kids (Mesas 9 e 10).
   - "Churrasco" / "Carnes" engloba Picanha, Ancho, Costela e Vaca Atolada.
   - Faturamento considera exclusivamente comandas com status PAGA.
4. FILTROS E PREMISSAS:
   - Todas as ferramentas analiticas de vendas aceitam setor e turno. Use-os sempre que o Gerente especificar.
   - Se a ferramenta retornar premissa adotada, informe-a explicitamente no inicio da resposta.
   - Se a ferramenta retornar erro de setor ou turno invalido, explique claramente as opcoes validas ao Gerente.
5. RESPOSTAS SEM DADOS:
   - Se a ferramenta indicar sem_dados=True ou zero linhas, declare isso com franqueza. NUNCA invente numeros.
6. VALORES DISCRIMINADOS:
   - Quando disponiveis, discrimine expressamente o faturamento total das comandas (incluindo taxa de servico) e a receita direta de itens.
"""

def carregar_contexto_recente(conversa_id: str, pergunta_atual: str = "", limite: int = 6) -> List[Dict[str, str]]:
    """Carrega as ultimas mensagens anteriores para compor o historico de dialogo contextual."""
    conn = data_manager.get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT papel, conteudo
        FROM chat_mensagens
        WHERE conversa_id = ?
        ORDER BY criado_em DESC
        LIMIT ?
        """, (conversa_id, limite + 1))
        rows = [dict(r) for r in cur.fetchall()]
        rows.reverse()
        if rows and rows[-1]["papel"] == "user" and rows[-1]["conteudo"].strip() == pergunta_atual.strip():
            rows.pop()
        return rows[-limite:]
    finally:
        conn.close()

def executar_pergunta_gerente(pergunta: str, conversa_id: Optional[str] = None, ignorar_demo: bool = True) -> Dict[str, Any]:
    """
    Executa a pergunta do Gerente atraves da cascata de fallback de modelos LLM.
    Aplica classificacao estrita de erros, tratamento de modelos incompativeis com tools,
    sanitizacao centralizada de chaves e repasse do filtro de demo via thread-local.
    """
    _limpar_contexto()
    _set_ignorar_demo(ignorar_demo)

    k1 = os.getenv("GOOGLE_API_KEY_1", "").strip()
    k2 = os.getenv("GOOGLE_API_KEY_2", "").strip()

    if not k1 and not k2:
        return {
            "sucesso": False,
            "resposta": "Nenhuma chave de API configurada. Por favor, adicione GOOGLE_API_KEY_1 ou GOOGLE_API_KEY_2 no arquivo .env para habilitar o Assistente IA.",
            "api_origem": "Nenhuma",
            "modelo": "Nenhum",
            "tentativas_falhas": 0,
            "evidencias": []
        }

    tentativas_falhas = 0
    mensagem_id = str(uuid.uuid4())
    system_instruction = _construir_prompt_sistema()
    tools_list = list(CATALOGO_FERRAMENTAS.values())
    avisos_cascata = []
    erros_400_consecutivos = 0

    from google import genai
    from google.genai import types

    historico_anterior = carregar_contexto_recente(conversa_id, pergunta_atual=pergunta, limite=6) if conversa_id else []
    contents_payload = []
    for h in historico_anterior:
        role = "user" if h["papel"] == "user" else "model"
        txt = sanitizar_texto(h["conteudo"])[:1000] if h["conteudo"] else ""
        if txt:
            contents_payload.append(types.Content(role=role, parts=[types.Part.from_text(text=txt)]))
    contents_payload.append(types.Content(role="user", parts=[types.Part.from_text(text=pergunta)]))

    chaves_candidatas = [("Chave 1", k1), ("Chave 2", k2)]

    for api_label, api_key in chaves_candidatas:
        if not api_key:
            continue
        if is_chave_desativada(api_label):
            avisos_cascata.append(f"{api_label} desativada previamente por credencial invalida.")
            continue

        modelos = descobrir_modelos_chave(api_key, api_label)
        pular_chave_atual = False

        for modelo in modelos:
            if pular_chave_atual:
                break
            if modelo in _incompatible_models:
                continue
            if is_em_cooldown(api_label, modelo):
                continue

            inicio_tentativa = time.time()
            try:
                client = genai.Client(api_key=api_key)
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                    tools=tools_list
                )

                response = client.models.generate_content(
                    model=modelo,
                    contents=contents_payload if historico_anterior else pergunta,
                    config=config
                )

                duracao_ms = int((time.time() - inicio_tentativa) * 1000)
                resposta_texto = response.text

                # Trata resposta vazia do modelo como falha para tentar proximo modelo
                if not resposta_texto or not resposta_texto.strip():
                    raise Exception("Resposta vazia retornada pelo modelo LLM.")

                resposta_texto = sanitizar_texto(resposta_texto)

                registrar_log_fallback(
                    conversa_id=conversa_id,
                    mensagem_id=mensagem_id,
                    api_origem=api_label,
                    modelo=modelo,
                    sucesso=1,
                    codigo_status=200,
                    erro_motivo=None,
                    duracao_ms=duracao_ms
                )

                ctx = _get_contexto()
                return {
                    "sucesso": True,
                    "resposta": resposta_texto,
                    "api_origem": api_label,
                    "modelo": modelo,
                    "tentativas_falhas": tentativas_falhas,
                    "duracao_ms": duracao_ms,
                    "avisos": avisos_cascata,
                    "premissas": ctx["premissas"],
                    "ferramentas_invocadas": ctx["ferramentas"],
                    "parametros": ctx["parametros"],
                    "evidencias": ctx["evidencias"]
                }

            except Exception as err:
                duracao_ms = int((time.time() - inicio_tentativa) * 1000)
                tentativas_falhas += 1
                erro_str = sanitizar_texto(str(err))
                tipo_erro, cd_segundos, _motivo_err = classificar_erro(err)
                err_lower = str(err).lower()

                # Verifica se o erro 400 e devido a falta de suporte a ferramentas ou system instruction
                is_tool_incompatibility = (
                    tipo_erro == TIPO_ERRO_MALFORMED
                    and any(p in err_lower for p in ["tool", "function", "system_instruction", "system instruction", "unsupported", "not supported"])
                )

                if is_tool_incompatibility:
                    _incompatible_models.add(modelo)
                    logger.warning(sanitizar_texto(f"Modelo {modelo} incompativel com tools/system_instruction. Pulando..."))
                    registrar_log_fallback(
                        conversa_id=conversa_id,
                        mensagem_id=mensagem_id,
                        api_origem=api_label,
                        modelo=modelo,
                        sucesso=0,
                        codigo_status=400,
                        erro_motivo=erro_str[:400],
                        duracao_ms=duracao_ms
                    )
                    continue

                if tipo_erro == TIPO_ERRO_AUTH:
                    desativar_chave(api_label, segundos=cd_segundos)
                    pular_chave_atual = True
                    avisos_cascata.append(f"{api_label} retornou credencial invalida/sem permissao. Alternando para proxima chave...")
                    registrar_log_fallback(
                        conversa_id=conversa_id,
                        mensagem_id=mensagem_id,
                        api_origem=api_label,
                        modelo=modelo,
                        sucesso=0,
                        codigo_status=401,
                        erro_motivo=erro_str[:400],
                        duracao_ms=duracao_ms
                    )
                    logger.warning(sanitizar_texto(f"Credencial invalida na {api_label}: {err}. Desativando chave..."))
                    break

                elif tipo_erro == TIPO_ERRO_MALFORMED:
                    erros_400_consecutivos += 1
                    registrar_log_fallback(
                        conversa_id=conversa_id,
                        mensagem_id=mensagem_id,
                        api_origem=api_label,
                        modelo=modelo,
                        sucesso=0,
                        codigo_status=400,
                        erro_motivo=erro_str[:400],
                        duracao_ms=duracao_ms
                    )
                    # Para a cascata somente se 2 modelos distintos confirmarem erro 400
                    if erros_400_consecutivos >= 2:
                        logger.error(sanitizar_texto(f"Erro 400 confirmado em 2 modelos consecutivos. Interrompendo cascata."))
                        return {
                            "sucesso": False,
                            "resposta": "Requisicao invalida ou nao suportada pelos modelos de IA. A execucao foi interrompida com seguranca.",
                            "api_origem": api_label,
                            "modelo": modelo,
                            "tentativas_falhas": tentativas_falhas,
                            "duracao_ms": duracao_ms,
                            "avisos": avisos_cascata,
                            "evidencias": []
                        }
                    else:
                        logger.warning(sanitizar_texto(f"Erro 400 no modelo {modelo}. Tentando proximo modelo para confirmacao..."))
                        continue

                else:  # TIPO_ERRO_TRANSIENT
                    ativar_cooldown(api_label, modelo, segundos=cd_segundos)
                    registrar_log_fallback(
                        conversa_id=conversa_id,
                        mensagem_id=mensagem_id,
                        api_origem=api_label,
                        modelo=modelo,
                        sucesso=0,
                        codigo_status=503,
                        erro_motivo=erro_str[:400],
                        duracao_ms=duracao_ms
                    )
                    logger.warning(sanitizar_texto(f"Falha transiente na {api_label} ({modelo}): {err}. Cooldown {cd_segundos}s. Tentando proximo..."))
                    continue

    return {
        "sucesso": False,
        "resposta": (
            "No momento, o servico do Assistente de Inteligencia Artificial esta temporariamente indisponivel "
            "devido a limitacoes momentaneas de cota dos provedores. Por favor, tente novamente em instantes "
            "ou consulte os relatorios analiticos em PDF na aba de Fechamento."
        ),
        "api_origem": "Cascata Esgotada",
        "modelo": "Nenhum",
        "tentativas_falhas": tentativas_falhas,
        "duracao_ms": 0,
        "avisos": avisos_cascata,
        "evidencias": []
    }

# ================= 8. PERSISTENCIA LOCAL E VERIFICACAO DE DONO =================

def criar_conversa(usuario_id: str, titulo: str = "Nova Conversa") -> str:
    conversa_id = str(uuid.uuid4())
    conn = data_manager.get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO chat_conversas (id, titulo, usuario_id)
        VALUES (?, ?, ?)
        """, (conversa_id, titulo, str(usuario_id)))
        conn.commit()
        return conversa_id
    finally:
        conn.close()

def renomear_conversa(conversa_id: str, novo_titulo: str, usuario_id: Optional[str] = None) -> bool:
    """Atualiza o titulo verificando se o usuario informado e dono da conversa."""
    if not novo_titulo or not novo_titulo.strip():
        return False
    conn = data_manager.get_connection()
    try:
        cur = conn.cursor()
        sql = "UPDATE chat_conversas SET titulo = ? WHERE id = ?"
        params = [novo_titulo.strip()[:60], conversa_id]
        if usuario_id:
            sql += " AND usuario_id = ?"
            params.append(str(usuario_id))
        cur.execute(sql, params)
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()

def excluir_conversa(conversa_id: str, usuario_id: Optional[str] = None) -> bool:
    """Exclui a conversa e suas mensagens verificando propriedade do usuario."""
    conn = data_manager.get_connection()
    try:
        cur = conn.cursor()
        if usuario_id:
            cur.execute("SELECT id FROM chat_conversas WHERE id = ? AND usuario_id = ?", (conversa_id, str(usuario_id)))
            if not cur.fetchone():
                return False
        cur.execute("DELETE FROM chat_mensagens WHERE conversa_id = ?", (conversa_id,))
        cur.execute("DELETE FROM chat_conversas WHERE id = ?", (conversa_id,))
        conn.commit()
        return True
    finally:
        conn.close()

def gerar_titulo_automatico(pergunta: str) -> str:
    p = pergunta.strip().replace("\n", " ")
    prefixos = [
        "quanto faturamos", "qual o faturamento", "quais os pratos", "quais os cortes",
        "como foi o", "qual foi o", "quais as mesas", "como esta o", "como está o",
        "por favor,", "gostaria de saber", "quais produtos"
    ]
    for pref in prefixos:
        if p.lower().startswith(pref):
            p = p[len(pref):].strip()
            break
    if len(p) > 35:
        p = p[:32].rstrip() + "..."
    if not p or len(p) < 3:
        p = "Consulta de Gestao"
    return p.capitalize()

def listar_conversas(usuario_id: str) -> List[Dict[str, Any]]:
    conn = data_manager.get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT id, titulo, criado_em
        FROM chat_conversas
        WHERE usuario_id = ?
        ORDER BY criado_em DESC
        """, (str(usuario_id),))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def salvar_mensagem_chat(conversa_id: str, papel: str, conteudo: str,
                         ferramentas_json: Optional[str] = None,
                         api_origem: Optional[str] = None,
                         modelo_utilizado: Optional[str] = None,
                         tentativas_falhas: int = 0) -> str:
    msg_id = str(uuid.uuid4())
    conn = data_manager.get_connection()
    try:
        cur = conn.cursor()
        conteudo_limpo = sanitizar_texto(conteudo)
        cur.execute("""
        INSERT INTO chat_mensagens (
            id, conversa_id, papel, conteudo, ferramentas_json,
            api_origem, modelo_utilizado, tentativas_falhas
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            msg_id, conversa_id, papel, conteudo_limpo, ferramentas_json,
            api_origem, modelo_utilizado, tentativas_falhas
        ))
        conn.commit()
        return msg_id
    finally:
        conn.close()

def carregar_historico_chat(conversa_id: str) -> List[Dict[str, Any]]:
    conn = data_manager.get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT id, papel, conteudo, ferramentas_json, api_origem, modelo_utilizado, tentativas_falhas, criado_em
        FROM chat_mensagens
        WHERE conversa_id = ?
        ORDER BY criado_em ASC
        """, (conversa_id,))
        rows = []
        for r in cur.fetchall():
            d = dict(r)
            if d.get("ferramentas_json"):
                try:
                    d["ferramentas_data"] = json.loads(d["ferramentas_json"])
                except Exception:
                    d["ferramentas_data"] = None
            rows.append(d)
        return rows
    finally:
        conn.close()

# ================= 9. STATUS E DIAGNOSTICO DO SERVICO =================

def obter_status_servico() -> Dict[str, Any]:
    """
    Retorna o status operacional detalhado sem expor credenciais.
    Reflete cascata ativa, em cooldown ou esgotada.
    """
    k1 = bool(os.getenv("GOOGLE_API_KEY_1", "").strip())
    k2 = bool(os.getenv("GOOGLE_API_KEY_2", "").strip())

    if not k1 and not k2:
        return {
            "status": "indisponivel",
            "rotulo": "Chaves Nao Configuradas (.env)",
            "cor": "#ef4444"
        }

    k1_ativa = k1 and not is_chave_desativada("Chave 1")
    k2_ativa = k2 and not is_chave_desativada("Chave 2")

    if not k1_ativa and not k2_ativa:
        return {
            "status": "indisponivel",
            "rotulo": "Indisponivel: Cascata Esgotada / Chaves Desativadas",
            "cor": "#ef4444"
        }

    mods1 = descobrir_modelos_chave(os.getenv("GOOGLE_API_KEY_1", ""), "Chave 1") if k1_ativa else []
    mods2 = descobrir_modelos_chave(os.getenv("GOOGLE_API_KEY_2", ""), "Chave 2") if k2_ativa else []

    m1_livres = [m for m in mods1 if not is_em_cooldown("Chave 1", m) and m not in _incompatible_models]
    m2_livres = [m for m in mods2 if not is_em_cooldown("Chave 2", m) and m not in _incompatible_models]

    if m1_livres:
        return {
            "status": "ativo_chave_1",
            "rotulo": "Servico Ativo (Chave 1 em operacao)",
            "cor": "#10b981"
        }
    elif m2_livres:
        return {
            "status": "ativo_chave_2",
            "rotulo": "Servico Ativo (Chave 2 em operacao)",
            "cor": "#38bdf8"
        }
    else:
        return {
            "status": "cooldown",
            "rotulo": "Modelos em Cooldown Temporario",
            "cor": "#f59e0b"
        }

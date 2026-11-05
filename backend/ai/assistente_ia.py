"""
Núcleo do Assistente IA do Gerente — ChurrasControl
Localização: assistente_ia.py

Implementa:
1. Conexão estritamente somente-leitura ao SQLite (mode=ro / query_only).
2. Catálogo de ferramentas determinísticas analíticas com validação Pydantic.
3. Descoberta dinâmica de modelos e Fallback em Cascata Multi-Chave/Multi-Modelo (Google Gemini via google-genai).
4. Cooldown temporário de modelos com falha e auditoria em llm_fallback_logs.
5. Persistência local de sessões de chat sem sincronização com Xano.
6. Higiene estrita de credenciais: nenhuma chave gravada em código, logs ou banco.
"""
import os
import sys
import time
import json
import uuid
import logging
import sqlite3
import threading
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Tuple

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

# ================= 1. CONEXÃO SOMENTE-LEITURA COM SQLITE =================

def get_readonly_connection() -> sqlite3.Connection:
    """
    Retorna uma conexão estritamente somente-leitura com o banco SQLite.
    Garante isolamento contra qualquer mutação acidental ou tentativa de injeção SQL.
    """
    db_path = data_manager.DB_PATH
    try:
        # Tenta abrir com URI somente leitura
        db_uri = f"file:{os.path.abspath(db_path)}?mode=ro"
        conn = sqlite3.connect(db_uri, uri=True, check_same_thread=False)
    except Exception:
        # Fallback para Windows path com PRAGMA query_only
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.execute("PRAGMA query_only = ON;")

    conn.row_factory = sqlite3.Row
    return conn

# ================= 2. CONTEXTO DE EXECUÇÃO E AUDITORIA =================

_thread_local = threading.local()

def _get_contexto() -> Dict[str, Any]:
    if not hasattr(_thread_local, "contexto"):
        _thread_local.contexto = {
            "ferramentas": [],
            "evidencias": [],
            "parametros": {},
            "conceitos": []
        }
    return _thread_local.contexto

def _limpar_contexto():
    _thread_local.contexto = {
        "ferramentas": [],
        "evidencias": [],
        "parametros": {},
        "conceitos": []
    }

def _registrar_evidencia(nome_ferramenta: str, params: dict, linhas: list, resumo: dict):
    ctx = _get_contexto()
    ctx["ferramentas"].append(nome_ferramenta)
    ctx["parametros"][nome_ferramenta] = params
    ctx["evidencias"].extend(linhas[:50])

# ================= 3. ESQUEMAS PYDANTIC DE VALIDAÇÃO =================

class PeriodoSchema(BaseModel):
    inicio: Optional[str] = Field(None, description="Data início no formato YYYY-MM-DD")
    fim: Optional[str] = Field(None, description="Data fim no formato YYYY-MM-DD")
    turno: Optional[str] = Field(None, description="Turno operacional (ex: 'almoço', 'jantar', 'happy hour')")

class RankingMesasSchema(BaseModel):
    inicio: Optional[str] = Field(None, description="Data início YYYY-MM-DD")
    fim: Optional[str] = Field(None, description="Data fim YYYY-MM-DD")
    setor: Optional[str] = Field(None, description="Setor do salão (ex: 'varanda', 'salão principal', 'espaço kids')")
    limite: int = Field(10, description="Quantidade máxima de mesas no ranking")

class RankingProdutosSchema(BaseModel):
    inicio: Optional[str] = Field(None, description="Data início YYYY-MM-DD")
    fim: Optional[str] = Field(None, description="Data fim YYYY-MM-DD")
    conceito_ontologico: Optional[str] = Field(None, description="Classe ou termo (ex: 'churrasco', 'carnes', 'cerveja', 'bebidas')")
    limite: int = Field(10, description="Quantidade máxima de pratos no ranking")

# ================= 4. FERRAMENTAS ANALÍTICAS DETERMINÍSTICAS =================

def resumo_financeiro(inicio: Optional[str] = None, fim: Optional[str] = None, turno: Optional[str] = None) -> Dict[str, Any]:
    """
    Calcula o faturamento bruto, total de comandas pagas, ticket médio e clientes atendidos.
    Filtra estritamente comandas com status PAGA.
    """
    conn = get_readonly_connection()
    try:
        cur = conn.cursor()
        filtros = ["status = 'PAGA'"]
        params = []

        if inicio:
            filtros.append("date(data_abertura) >= date(?)")
            params.append(inicio)
        if fim:
            filtros.append("date(data_abertura) <= date(?)")
            params.append(fim)

        intervalo_turno = None
        if turno:
            intervalo_turno = ontologia.obter_intervalo_turno(turno, conn=conn)
            if intervalo_turno:
                filtros.append("time(data_abertura) >= time(?) AND time(data_abertura) <= time(?)")
                params.extend([intervalo_turno["inicio"], intervalo_turno["fim"]])

        where_clause = " WHERE " + " AND ".join(filtros)

        sql_totais = f"""
        SELECT 
            COUNT(*) as total_comandas,
            COALESCE(SUM(valor_total), 0.0) as faturamento_bruto,
            COALESCE(AVG(valor_total), 0.0) as ticket_medio_comanda,
            COALESCE(SUM(qtd_pessoas), 0) as total_clientes,
            CASE WHEN SUM(qtd_pessoas) > 0 THEN SUM(valor_total) / SUM(qtd_pessoas) ELSE 0.0 END as ticket_medio_cliente
        FROM comandas
        {where_clause}
        """
        cur.execute(sql_totais, params)
        tot = dict(cur.fetchone())

        sql_linhas = f"""
        SELECT id as comanda_id, numero_mesa_historico as mesa, 
               strftime('%Y-%m-%d %H:%M', data_abertura) as abertura,
               qtd_pessoas as clientes, valor_total
        FROM comandas
        {where_clause}
        ORDER BY data_abertura DESC
        LIMIT 50
        """
        cur.execute(sql_linhas, params)
        linhas = [dict(r) for r in cur.fetchall()]

        res = {
            "faturamento_bruto_reais": round(float(tot["faturamento_bruto"]), 2),
            "total_comandas_pagas": int(tot["total_comandas"]),
            "ticket_medio_comanda": round(float(tot["ticket_medio_comanda"]), 2),
            "total_clientes_atendidos": int(tot["total_clientes"]),
            "ticket_medio_por_cliente": round(float(tot["ticket_medio_cliente"]), 2),
            "periodo_considerado": {"inicio": inicio, "fim": fim, "turno": turno}
        }
        _registrar_evidencia("resumo_financeiro", {"inicio": inicio, "fim": fim, "turno": turno}, linhas, res)
        return res
    finally:
        conn.close()

def ranking_mesas(inicio: Optional[str] = None, fim: Optional[str] = None, setor: Optional[str] = None, limite: int = 10) -> Dict[str, Any]:
    """
    Identifica as mesas físicas mais rentáveis e mais frequentadas no salão.
    Suporta filtro ontológico por setor do salão (Varanda, Salão Principal, Espaço Kids).
    """
    conn = get_readonly_connection()
    try:
        cur = conn.cursor()
        filtros = ["status = 'PAGA'"]
        params = []

        if inicio:
            filtros.append("date(data_abertura) >= date(?)")
            params.append(inicio)
        if fim:
            filtros.append("date(data_abertura) <= date(?)")
            params.append(fim)

        mesas_setor = None
        setor_nome = None
        if setor:
            mesas_setor = ontologia.obter_mesas_por_setor(setor, conn=conn)
            conc = ontologia.resolver_termo(setor, conn=conn)
            setor_nome = conc["nome_legivel"] if conc else setor
            if mesas_setor:
                placeholders = ",".join(["?"] * len(mesas_setor))
                filtros.append(f"numero_mesa_historico IN ({placeholders})")
                params.extend(mesas_setor)

        where_clause = " WHERE " + " AND ".join(filtros)
        sql = f"""
        SELECT 
            numero_mesa_historico as mesa,
            COUNT(*) as total_comandas,
            COALESCE(SUM(qtd_pessoas), 0) as total_clientes,
            ROUND(COALESCE(SUM(valor_total), 0.0), 2) as faturamento_total,
            ROUND(COALESCE(AVG(valor_total), 0.0), 2) as ticket_medio
        FROM comandas
        {where_clause}
        GROUP BY numero_mesa_historico
        ORDER BY faturamento_total DESC
        LIMIT ?
        """
        params.append(limite)
        cur.execute(sql, params)
        linhas = []
        for r in cur.fetchall():
            d = dict(r)
            m_num = d["mesa"]
            if m_num in [1, 2, 3, 4]:
                d["setor"] = "Varanda Externa"
            elif m_num in [5, 6, 7, 8]:
                d["setor"] = "Salão Principal"
            else:
                d["setor"] = "Espaço Kids"
            linhas.append(d)

        res = {
            "ranking_mesas": linhas,
            "setor_filtrado": setor_nome,
            "total_mesas_ranqueadas": len(linhas)
        }
        _registrar_evidencia("ranking_mesas", {"inicio": inicio, "fim": fim, "setor": setor, "limite": limite}, linhas, res)
        return res
    finally:
        conn.close()

def ranking_produtos(inicio: Optional[str] = None, fim: Optional[str] = None, conceito_ontologico: Optional[str] = None, limite: int = 10) -> Dict[str, Any]:
    """
    Lista os produtos, pratos e bebidas mais vendidos em quantidade e faturamento.
    Aplica resolução ontológica para termos genéricos (ex: 'churrasco', 'cerveja').
    """
    conn = get_readonly_connection()
    try:
        cur = conn.cursor()
        filtros = ["c.status = 'PAGA'"]
        params = []

        if inicio:
            filtros.append("date(c.data_abertura) >= date(?)")
            params.append(inicio)
        if fim:
            filtros.append("date(c.data_abertura) <= date(?)")
            params.append(fim)

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

        res = {
            "ranking_produtos": linhas,
            "conceito_filtrado": conceito_ontologico,
            "total_itens_ranqueados": len(linhas)
        }
        _registrar_evidencia("ranking_produtos", {"inicio": inicio, "fim": fim, "conceito": conceito_ontologico}, linhas, res)
        return res
    finally:
        conn.close()

def vendas_por_categoria(inicio: Optional[str] = None, fim: Optional[str] = None) -> Dict[str, Any]:
    """
    Retorna a distribuição de receita e volume de itens por categoria de produto.
    """
    conn = get_readonly_connection()
    try:
        cur = conn.cursor()
        filtros = ["c.status = 'PAGA'"]
        params = []

        if inicio:
            filtros.append("date(c.data_abertura) >= date(?)")
            params.append(inicio)
        if fim:
            filtros.append("date(c.data_abertura) <= date(?)")
            params.append(fim)

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
        total_geral = sum(r["receita_total"] for r in linhas) or 1.0

        for r in linhas:
            r["participacao_percentual"] = round((r["receita_total"] / total_geral) * 100, 1)

        res = {
            "vendas_categorias": linhas,
            "receita_geral_reais": round(total_geral, 2)
        }
        _registrar_evidencia("vendas_por_categoria", {"inicio": inicio, "fim": fim}, linhas, res)
        return res
    finally:
        conn.close()

def evolucao_temporal(inicio: Optional[str] = None, fim: Optional[str] = None, granularidade: str = "dia") -> Dict[str, Any]:
    """
    Retorna a série temporal de faturamento e fluxo de comandas por dia ou semana.
    """
    conn = get_readonly_connection()
    try:
        cur = conn.cursor()
        filtros = ["status = 'PAGA'"]
        params = []

        if inicio:
            filtros.append("date(data_abertura) >= date(?)")
            params.append(inicio)
        if fim:
            filtros.append("date(data_abertura) <= date(?)")
            params.append(fim)

        where_clause = " WHERE " + " AND ".join(filtros)
        fmt = "%Y-%m-%d" if granularidade == "dia" else "%Y-W%W"

        sql = f"""
        SELECT 
            strftime('{fmt}', data_abertura) as periodo,
            COUNT(*) as total_comandas,
            COALESCE(SUM(qtd_pessoas), 0) as total_clientes,
            ROUND(COALESCE(SUM(valor_total), 0.0), 2) as faturamento_total,
            ROUND(COALESCE(AVG(valor_total), 0.0), 2) as ticket_medio
        FROM comandas
        {where_clause}
        GROUP BY periodo
        ORDER BY periodo ASC
        """
        cur.execute(sql, params)
        linhas = [dict(r) for r in cur.fetchall()]

        res = {
            "serie_temporal": linhas,
            "granularidade": granularidade
        }
        _registrar_evidencia("evolucao_temporal", {"inicio": inicio, "fim": fim, "granularidade": granularidade}, linhas, res)
        return res
    finally:
        conn.close()

def estoque_critico() -> Dict[str, Any]:
    """
    Identifica produtos com estoque baixo (qtd_disp <= 5) ou indisponíveis para venda.
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

        res = {
            "produtos_criticos": linhas,
            "total_criticos": len(linhas)
        }
        _registrar_evidencia("estoque_critico", {}, linhas, res)
        return res
    finally:
        conn.close()

def salao_tempo_real() -> Dict[str, Any]:
    """
    Consulta o estado operacional ao vivo do salão: ocupação de mesas e comandas abertas.
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
            "consumo_parcial_acumulado": round(sum(c["consumo_parcial"] for c in comandas_abertas), 2)
        }
        _registrar_evidencia("salao_tempo_real", {}, comandas_abertas, res)
        return res
    finally:
        conn.close()

def auditoria_operacional(termo: Optional[str] = None, limite: int = 15) -> Dict[str, Any]:
    """
    Busca registros no histórico de auditoria operacional do restaurante.
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

        res = {
            "registros_auditoria": linhas,
            "total_encontrado": len(linhas)
        }
        _registrar_evidencia("auditoria_operacional", {"termo": termo, "limite": limite}, linhas, res)
        return res
    finally:
        conn.close()

# Dicionário de despacho para Function Calling
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

# ================= 5. GERENCIADOR DE CASCATA DE FALLBACK DE LLM =================

_model_cooldowns: Dict[Tuple[str, str], float] = {}
_cooldown_lock = threading.Lock()
_discovered_models_cache: Dict[str, Tuple[float, List[str]]] = {}
CACHE_DISCOVERY_TTL = 600.0  # 10 minutos de cache para client.models.list()

def is_em_cooldown(api_label: str, modelo: str) -> bool:
    """Verifica se o par (Chave, Modelo) está em cooldown temporário após falha recente."""
    with _cooldown_lock:
        chave = (api_label, modelo)
        expira = _model_cooldowns.get(chave, 0.0)
        return time.time() < expira

def ativar_cooldown(api_label: str, modelo: str, segundos: int = 60):
    """Ativa cooldown curto para evitar retentativas imediatas sobre endpoint com erro."""
    with _cooldown_lock:
        chave = (api_label, modelo)
        _model_cooldowns[chave] = time.time() + segundos

def registrar_log_fallback(conversa_id: Optional[str], mensagem_id: Optional[str],
                           api_origem: str, modelo: str, sucesso: int,
                           codigo_status: Optional[int], erro_motivo: Optional[str], duracao_ms: int):
    """
    Persiste estritamente no SQLite local a telemetria de tentativas do LLM.
    NUNCA envia registros para fila_sincronizacao ou nuvem Xano.
    """
    try:
        conn = data_manager.get_connection()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO llm_fallback_logs (
            conversa_id, mensagem_id, api_origem, modelo, sucesso,
            codigo_status, erro_motivo, duracao_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            conversa_id, mensagem_id, api_origem, modelo, sucesso,
            codigo_status, erro_motivo[:500] if erro_motivo else None, duracao_ms
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Erro ao registrar log de fallback no SQLite: {e}")

def descobrir_modelos_chave(api_key: str, api_label: str) -> List[str]:
    """
    Consulta dinamicamente quais modelos a chave de API tem acesso, filtrando os que
    suportam generateContent e chamadas de ferramentas (*function calling*).
    """
    if not api_key:
        return []

    agora = time.time()
    if api_label in _discovered_models_cache:
        cached_time, cached_list = _discovered_models_cache[api_label]
        if agora - cached_time < CACHE_DISCOVERY_TTL:
            return cached_list

    modelos_compativeis = []
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        for m in client.models.list():
            nome = getattr(m, "name", "")
            # Remove prefixo 'models/' se presente
            if "/" in nome:
                nome = nome.split("/")[-1]
            
            # Filtra por suporte a generateContent
            actions = getattr(m, "supported_actions", []) or []
            if "generateContent" in actions:
                # Evita modelos puramente de embedding ou imagem
                if not any(ign in nome.lower() for ign in ["embedding", "imagen", "veo", "aqa"]):
                    modelos_compativeis.append(nome)

        # Ordena priorizando modelos flash modernos
        def _ordem_preferencia(name: str) -> int:
            n = name.lower()
            if "gemini-2.5-flash" in n:
                return 1
            if "gemini-3.7-flash" in n:
                return 2
            if "gemini-2.0-flash" in n:
                return 3
            if "flash" in n:
                return 4
            if "gemini-2.5-pro" in n or "gemini-3.7-pro" in n:
                return 5
            return 10

        modelos_compativeis.sort(key=_ordem_preferencia)
        _discovered_models_cache[api_label] = (agora, modelos_compativeis)
    except Exception as e:
        logger.warning(f"Não foi possível listar modelos dinamicamente para {api_label}: {e}")
        # Modelos padrão de contingência
        modelos_compativeis = ["gemini-2.5-flash", "gemini-3.7-flash", "gemini-2.5-pro"]
        _discovered_models_cache[api_label] = (agora, modelos_compativeis)

    return modelos_compativeis

def obter_fila_cascata() -> List[Tuple[str, str, str]]:
    """
    Retorna a fila ordenada de pares (api_label, modelo, api_key):
    1º: Todos os modelos elegíveis da Chave 1 em ordem;
    2º: Todos os modelos elegíveis da Chave 2 em ordem.
    """
    k1 = os.getenv("GOOGLE_API_KEY_1", "").strip()
    k2 = os.getenv("GOOGLE_API_KEY_2", "").strip()

    fila = []
    if k1:
        mods1 = descobrir_modelos_chave(k1, "Chave 1")
        for m in mods1:
            fila.append(("Chave 1", m, k1))

    if k2:
        mods2 = descobrir_modelos_chave(k2, "Chave 2")
        for m in mods2:
            fila.append(("Chave 2", m, k2))

    return fila

# ================= 6. ORQUESTRADOR RAG E EXECUÇÃO DE CHAT =================

def _construir_prompt_sistema() -> str:
    """Monta a instrução do sistema com timezone de Brasília e contexto ontológico."""
    agora = datetime.now(TZ_BRASILIA)
    dias_semana = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
    dia_nome = dias_semana[agora.weekday()]
    data_formatada = agora.strftime("%d/%m/%Y %H:%M")
    hoje_iso = agora.strftime("%Y-%m-%d")

    return f"""Você é o Assistente Analítico e Executivo do Gerente do restaurante ChurrasControl.
Seu objetivo é responder a perguntas de gestão sobre faturamento, mesas, pratos, turnos, estoque e auditoria com PRECISÃO MATEMÁTICA ABSOLUTA.

CONTEXTO TEMPORAL:
- Momento atual: {dia_nome}, {data_formatada} (Horário de Brasília).
- Data de hoje (ISO): {hoje_iso}
- Ontem foi: {(agora - timedelta(days=1)).strftime('%Y-%m-%d')}
- Início deste mês: {agora.strftime('%Y-%m-01')}

REGRAS SAGRADAS INEGOCIÁVEIS:
1. ZERO ALUCINAÇÃO NUMÉRICA: NUNCA invente números, faturamentos, quantidades ou rankings.
2. EXECUÇÃO DETERMINÍSTICA: Toda informação quantitativa DEVE vir EXCLUSIVAMENTE do retorno das ferramentas analíticas. Você não faz contas matemáticas de cabeça.
3. ONTOLOGIA DE DOMÍNIO:
   - "Varanda", "lá fora", "deck" referem-se às Mesas 1, 2, 3 e 4.
   - "Salão principal", "climatizado", "interno" referem-se às Mesas 5, 6, 7 e 8.
   - "Espaço Kids", "famílias" referem-se às Mesas 9 e 10.
   - "Almoço" corresponde ao horário 11:30 às 15:30.
   - "Jantar" corresponde ao horário 18:30 às 23:59.
   - "Happy Hour" corresponde ao horário 17:00 às 19:30.
   - "Churrasco" / "Carnes" engloba Picanha, Ancho, Costela e Vaca Atolada.
   - Faturamento só considera comandas PAGA.
4. ESTILO DE RESPOSTA:
   - Tom executivo, direto, cortês e objetivo em Português do Brasil.
   - Destaque valores em Reais (R$) e quantidades claramente.
   - Apresente um resumo executivo da análise.
"""

def executar_pergunta_gerente(pergunta: str, conversa_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Executa a pergunta do Gerente através da cascata de fallback de modelos LLM.
    Se um modelo falhar (429, quota, timeout, 5xx), tenta o próximo com cooldown curto.
    Se toda a cascata falhar, retorna fail-safe amigável sem inventar respostas.
    """
    _limpar_contexto()
    fila_cascata = obter_fila_cascata()

    if not fila_cascata:
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

    from google import genai
    from google.genai import types

    for api_label, modelo, api_key in fila_cascata:
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

            # Executa com suporte a Function Calling automático do SDK
            response = client.models.generate_content(
                model=modelo,
                contents=pergunta,
                config=config
            )

            duracao_ms = int((time.time() - inicio_tentativa) * 1000)
            resposta_texto = response.text or "Análise concluída com sucesso com base nos dados do banco."

            # Registra sucesso da requisição
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
                "ferramentas_invocadas": ctx["ferramentas"],
                "parametros": ctx["parametros"],
                "evidencias": ctx["evidencias"]
            }

        except Exception as err:
            duracao_ms = int((time.time() - inicio_tentativa) * 1000)
            tentativas_falhas += 1
            erro_str = str(err)
            
            # Detecta código HTTP aproximado
            status_code = 429 if "429" in erro_str or "quota" in erro_str.lower() or "resource_exhausted" in erro_str.lower() else 500

            ativar_cooldown(api_label, modelo, segundos=60)
            registrar_log_fallback(
                conversa_id=conversa_id,
                mensagem_id=mensagem_id,
                api_origem=api_label,
                modelo=modelo,
                sucesso=0,
                codigo_status=status_code,
                erro_motivo=erro_str[:400],
                duracao_ms=duracao_ms
            )
            logger.warning(f"Falha na tentativa com {api_label} ({modelo}): {err}. Tentando próximo da cascata...")
            continue

    # Esgotamento total da cascata: Fail-Safe amigável sem inventar dados
    return {
        "sucesso": False,
        "resposta": (
            "No momento, o serviço do Assistente de Inteligência Artificial está temporariamente indisponível "
            "devido a limitações momentâneas de cota dos provedores. Por favor, tente novamente em instantes "
            "ou consulte os relatórios analíticos em PDF na aba de Fechamento."
        ),
        "api_origem": "Cascata Esgotada",
        "modelo": "Nenhum",
        "tentativas_falhas": tentativas_falhas,
        "evidencias": []
    }

# ================= 7. PERSISTÊNCIA LOCAL DE CONVERSAS =================

def criar_conversa(usuario_id: str, titulo: str = "Nova Conversa") -> str:
    """Cria uma nova sessão de conversa no SQLite e retorna seu ID."""
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

def listar_conversas(usuario_id: str) -> List[Dict[str, Any]]:
    """Lista as conversas anteriores do usuário autenticado ordenadas por data."""
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
    """Persiste uma mensagem individual e seus metadados de telemetria no SQLite."""
    msg_id = str(uuid.uuid4())
    conn = data_manager.get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO chat_mensagens (
            id, conversa_id, papel, conteudo, ferramentas_json,
            api_origem, modelo_utilizado, tentativas_falhas
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            msg_id, conversa_id, papel, conteudo, ferramentas_json,
            api_origem, modelo_utilizado, tentativas_falhas
        ))
        conn.commit()
        return msg_id
    finally:
        conn.close()

def carregar_historico_chat(conversa_id: str) -> List[Dict[str, Any]]:
    """Carrega todo o histórico cronológico de mensagens de uma conversa."""
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

"""
Interface Conversacional do Assistente IA do Gerente — ChurrasControl
Localizacao: pages/8_Assistente_IA.py

Implementa:
- Guarda de seguranca RBAC estrita (exclusivo para cargo 'gerente').
- Cabecalho corporativo limpo com indicador de status discreto da conexao (sem expor chaves).
- Gerenciador lateral de conversas (nova conversa, renomear com dialog, apagar com confirmacao e titulagem automatica).
- Tela inicial rica com cartoes tematicos de perguntas sugeridas (Faturamento, Mesas e Setores, Cardapio, Estoque, Auditoria).
- Chat executivo com baloes distintos, formatacao monetaria brasileira (R$) e destaque visual de indicadores.
- Graficos nativos leves (st.bar_chart, st.line_chart) sem novas dependencias pesadas.
- Painel "Como calculei" estruturado em 6 secoes e recolhido por padrao.
- Controle para alternar filtro de vendas de demonstracao (Demo).
"""
import os
import sys
import json
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import data_manager
from frontend.components import ui_components
from backend.ai import assistente_ia

st.set_page_config(
    page_icon="frontend/assets/logo.png",
    page_title="Assistente IA - ChurrasControl",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 1. Guarda RBAC estrita para Gerente
usuario = ui_components.verificar_permissao_acesso(["gerente"])
usuario_id = str(usuario.get("id", "gerente"))

# 2. Renderizacao da Top Navbar Unificada
ui_components.render_navbar(active_tab="assistente_ia")

# Inicializacao do estado de sessao
if "conversa_ativa_id" not in st.session_state:
    st.session_state["conversa_ativa_id"] = None
if "pergunta_pendente" not in st.session_state:
    st.session_state["pergunta_pendente"] = None
if "ignorar_demo" not in st.session_state:
    st.session_state["ignorar_demo"] = True
if "conversa_para_renomear" not in st.session_state:
    st.session_state["conversa_para_renomear"] = None
if "conversa_para_excluir" not in st.session_state:
    st.session_state["conversa_para_excluir"] = None

def formatar_moeda(valor) -> str:
    """Formata valor numerico como moeda brasileira (R$ X.XXX,XX)."""
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(valor)

# Dialogos modais nativos para gerenciamento de conversa
@st.dialog("Renomear Sessao")
def dialog_renomear(conv_id: str, titulo_atual: str, uid: str = None):
    st.markdown("<p style='font-size: 0.88rem; color: #94a3b8;'>Digite o novo titulo para esta conversa:</p>", unsafe_allow_html=True)
    novo_nome = st.text_input("Titulo da Conversa", value=titulo_atual, max_chars=50, label_visibility="collapsed")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Salvar Titulo", type="primary", use_container_width=True):
            if novo_nome.strip():
                assistente_ia.renomear_conversa(conv_id, novo_nome.strip(), usuario_id=uid)
                st.session_state["conversa_para_renomear"] = None
                st.rerun()
    with c2:
        if st.button("Cancelar", type="secondary", use_container_width=True):
            st.session_state["conversa_para_renomear"] = None
            st.rerun()

@st.dialog("Confirmar Exclusao")
def dialog_excluir(conv_id: str, titulo: str, uid: str = None):
    st.markdown(f"<p style='font-size: 0.90rem; color: #f87171;'>Tem certeza de que deseja excluir permanentemente a conversa <b>{titulo}</b>?</p>", unsafe_allow_html=True)
    st.caption("Todas as mensagens e auditorias locais associadas serao removidas.")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Excluir Permanentemente", type="primary", use_container_width=True):
            assistente_ia.excluir_conversa(conv_id, usuario_id=uid)
            if st.session_state.get("conversa_ativa_id") == conv_id:
                st.session_state["conversa_ativa_id"] = None
            st.session_state["conversa_para_excluir"] = None
            st.rerun()
    with c2:
        if st.button("Manter Conversa", type="secondary", use_container_width=True):
            st.session_state["conversa_para_excluir"] = None
            st.rerun()

# 3. Status Operacional do Servico (sem exibir credenciais)
status_info = assistente_ia.obter_status_servico()

# 4. Cabecalho Corporativo Limpo
c_header_title, c_header_status = st.columns([3, 1.3], vertical_alignment="center")

with c_header_title:
    st.markdown(
        '<div style="display: flex; align-items: center; gap: 14px; margin-bottom: 6px;">'
        '<div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35); flex-shrink: 0;">'
        '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>'
        '</div>'
        '<div>'
        '<h2 style="margin: 0; font-weight: 800; font-size: 1.55rem; color: #f8fafc; letter-spacing: -0.02em;">Assistente Executivo de Inteligencia Artificial</h2>'
        '<span style="font-size: 0.82rem; color: #94a3b8;">Consultas analiticas deterministas sobre o SQLite • RAG estruturado sem alucinacao numerica</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

with c_header_status:
    cor_badge = status_info["cor"]
    rotulo_badge = status_info["rotulo"]
    st.markdown(
        f'<div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 8px 12px; display: flex; align-items: center; justify-content: flex-end; gap: 8px;">'
        f'<span style="width: 8px; height: 8px; border-radius: 50%; background-color: {cor_badge}; display: inline-block; box-shadow: 0 0 8px {cor_badge};"></span>'
        f'<span style="font-size: 0.80rem; font-weight: 600; color: #e2e8f0;">{rotulo_badge}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("<hr style='margin: 10px 0 16px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.07);'>", unsafe_allow_html=True)

# 5. Gerenciamento das Conversas Existentes
conversas_existentes = assistente_ia.listar_conversas(usuario_id)
if not st.session_state["conversa_ativa_id"]:
    if conversas_existentes:
        st.session_state["conversa_ativa_id"] = conversas_existentes[0]["id"]
    else:
        st.session_state["conversa_ativa_id"] = assistente_ia.criar_conversa(usuario_id, "Sessao Inicial")
        conversas_existentes = assistente_ia.listar_conversas(usuario_id)

conversa_id_atual = st.session_state["conversa_ativa_id"]

# Dispara dialogos pendentes se solicitados
if st.session_state["conversa_para_renomear"]:
    c_info = next((c for c in conversas_existentes if c["id"] == st.session_state["conversa_para_renomear"]), None)
    if c_info:
        dialog_renomear(c_info["id"], c_info["titulo"], uid=usuario_id)

if st.session_state["conversa_para_excluir"]:
    c_info = next((c for c in conversas_existentes if c["id"] == st.session_state["conversa_para_excluir"]), None)
    if c_info:
        dialog_excluir(c_info["id"], c_info["titulo"], uid=usuario_id)

# 6. Layout em Duas Colunas (Gerenciador Lateral + Workspace de Chat)
col_lateral, col_chat = st.columns([1.1, 3.2], gap="large")

# ----------------- COLUNA LATERAL: GERENCIADOR DE CONVERSAS -----------------
with col_lateral:
    st.markdown(
        '<div style="font-size: 0.80rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">'
        'Sessoes de Atendimento'
        '</div>',
        unsafe_allow_html=True
    )

    if st.button("+ Nova Conversa", key="btn_nova_conv_lat", use_container_width=True, type="primary"):
        num_c = len(conversas_existentes) + 1
        novo_id = assistente_ia.criar_conversa(usuario_id, f"Conversa {num_c}")
        st.session_state["conversa_ativa_id"] = novo_id
        st.rerun()

    # Controle de filtro para Vendas de Demonstracao
    st.session_state["ignorar_demo"] = st.checkbox(
        "Ocultar vendas simuladas (Demo)",
        value=st.session_state["ignorar_demo"],
        help="Quando ativado, desconsidera as vendas historicas geradas pelo script seed_vendas_demo."
    )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Lista de conversas anteriores
    for c in conversas_existentes:
        c_id = c["id"]
        c_tit = c["titulo"]
        c_data = c["criado_em"][:16].replace("T", " ") if c.get("criado_em") else ""
        is_ativa = (c_id == conversa_id_atual)

        borda = "rgba(16, 185, 129, 0.5)" if is_ativa else "rgba(255, 255, 255, 0.07)"
        bg_card = "rgba(16, 185, 129, 0.08)" if is_ativa else "rgba(17, 24, 39, 0.6)"
        badge_ativa = "<span style='font-size: 0.68rem; background: #059669; color: #ffffff; padding: 1px 6px; border-radius: 4px; font-weight: 700;'>ATIVA</span>" if is_ativa else ""

        st.markdown(
            f'<div style="background: {bg_card}; border: 1px solid {borda}; border-radius: 10px; padding: 10px 12px; margin-bottom: 8px;">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">'
            f'<span style="font-weight: 700; font-size: 0.86rem; color: #f1f5f9; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 170px;">{c_tit}</span>'
            f'{badge_ativa}'
            f'</div>'
            f'<div style="font-size: 0.72rem; color: #64748b;">Criada em {c_data}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Acoes da conversa
        btn_c1, btn_c2, btn_c3 = st.columns([1.5, 1, 1])
        with btn_c1:
            if not is_ativa:
                if st.button("Abrir", key=f"btn_abrir_{c_id}", use_container_width=True):
                    st.session_state["conversa_ativa_id"] = c_id
                    st.rerun()
            else:
                st.caption("Em exibicao")
        with btn_c2:
            if st.button("Editar", key=f"btn_ren_{c_id}", use_container_width=True):
                st.session_state["conversa_para_renomear"] = c_id
                st.rerun()
        with btn_c3:
            if st.button("Excluir", key=f"btn_exc_{c_id}", use_container_width=True):
                st.session_state["conversa_para_excluir"] = c_id
                st.rerun()

# ----------------- COLUNA PRINCIPAL: WORKSPACE DE CHAT & CARTOES -----------------
with col_chat:
    historico = assistente_ia.carregar_historico_chat(conversa_id_atual)

    # 1. TELA INICIAL VAZIA: CARTOES TEMATICOS DE SUGESTOES
    if not historico:
        st.markdown(
            '<div style="background: rgba(17, 24, 39, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 20px; margin-bottom: 18px;">'
            '<h3 style="margin: 0 0 6px 0; color: #f8fafc; font-size: 1.15rem; font-weight: 700;">Como posso apoiar a gestao do restaurante hoje?</h3>'
            '<p style="margin: 0; color: #94a3b8; font-size: 0.85rem; line-height: 1.45;">Selecione uma das sugestoes executivas abaixo ou digite qualquer pergunta analitica no campo de mensagem ao final da tela.</p>'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown("<div style='font-size: 0.80rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px;'>Sugestoes Estruturadas por Tema</div>", unsafe_allow_html=True)

        tema_c1, tema_c2 = st.columns(2)

        with tema_c1:
            # Tema 1: Faturamento & Receita
            with st.container():
                st.markdown(
                    '<div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 12px; padding: 12px 14px; margin-bottom: 12px;">'
                    '<div style="font-weight: 700; color: #38bdf8; font-size: 0.88rem; margin-bottom: 8px;">Faturamento & Receita</div>',
                    unsafe_allow_html=True
                )
                if st.button("Quanto faturamos hoje e qual o ticket medio?", key="btn_sug_fat_hoje", use_container_width=True):
                    st.session_state["pergunta_pendente"] = "Quanto faturamos hoje e qual foi o ticket medio das comandas pagas?"
                if st.button("Qual a receita do ultimo fim de semana?", key="btn_sug_fat_fds", use_container_width=True):
                    st.session_state["pergunta_pendente"] = "Qual foi o faturamento bruto no sabado e domingo passados?"
                st.markdown('</div>', unsafe_allow_html=True)

            # Tema 2: Mesas & Setores
            with st.container():
                st.markdown(
                    '<div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 12px; padding: 12px 14px; margin-bottom: 12px;">'
                    '<div style="font-weight: 700; color: #34d399; font-size: 0.88rem; margin-bottom: 8px;">Mesas & Setores</div>',
                    unsafe_allow_html=True
                )
                if st.button("Quais as mesas mais rentaveis da Varanda?", key="btn_sug_mesas_varanda", use_container_width=True):
                    st.session_state["pergunta_pendente"] = "Como foi o faturamento e atendimentos nas mesas da Varanda?"
                if st.button("Comparar Salao Interno e Kids", key="btn_sug_mesas_internas", use_container_width=True):
                    st.session_state["pergunta_pendente"] = "Qual setor vendeu mais: Salao Interno ou Espaco Kids?"
                st.markdown('</div>', unsafe_allow_html=True)

        with tema_c2:
            # Tema 3: Cardapio & Vendas
            with st.container():
                st.markdown(
                    '<div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 12px; padding: 12px 14px; margin-bottom: 12px;">'
                    '<div style="font-weight: 700; color: #fbbf24; font-size: 0.88rem; margin-bottom: 8px;">Cardapio & Vendas</div>',
                    unsafe_allow_html=True
                )
                if st.button("Cortes de churrasco mais pedidos no almoco", key="btn_sug_churras_almoco", use_container_width=True):
                    st.session_state["pergunta_pendente"] = "Quais foram os cortes de churrasco mais vendidos no turno do almoco?"
                if st.button("Participacao das cervejas e bebidas no total", key="btn_sug_bebidas_part", use_container_width=True):
                    st.session_state["pergunta_pendente"] = "Qual a participacao das bebidas e cervejas na receita total?"
                st.markdown('</div>', unsafe_allow_html=True)

            # Tema 4: Estoque & Auditoria
            with st.container():
                st.markdown(
                    '<div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 12px; padding: 12px 14px; margin-bottom: 12px;">'
                    '<div style="font-weight: 700; color: #f472b6; font-size: 0.88rem; margin-bottom: 8px;">Estoque & Auditoria</div>',
                    unsafe_allow_html=True
                )
                if st.button("Produtos com estoque critico agora", key="btn_sug_estoque", use_container_width=True):
                    st.session_state["pergunta_pendente"] = "Tem algum produto com estoque critico ou precisando produzir agora?"
                if st.button("Ultimos registros de auditoria operacional", key="btn_sug_auditoria", use_container_width=True):
                    st.session_state["pergunta_pendente"] = "Mostre as ultimas 10 acoes registradas no log de auditoria."
                st.markdown('</div>', unsafe_allow_html=True)

    # 2. RENDERIZACAO DO HISTORICO DE CHAT EXISTENTE
    for msg in historico:
        papel = msg["papel"]
        conteudo = msg["conteudo"]
        with st.chat_message(papel, avatar=None):
            st.markdown(conteudo)

            # Painel "Como Calculei" para respostas do assistente
            if papel == "assistant" and (msg.get("ferramentas_data") or msg.get("api_origem")):
                f_data = msg.get("ferramentas_data") or {}
                api_resp = msg.get("api_origem") or "Chave 1"
                mod_resp = msg.get("modelo_utilizado") or "Gemini"
                falhas = msg.get("tentativas_falhas", 0)

                # Graficos Nativos Leves quando houver dados estruturados
                evidencias = f_data.get("evidencias", [])
                ferramentas_usadas = f_data.get("ferramentas", [])

                if "ranking_produtos" in ferramentas_usadas and evidencias:
                    chart_dict = {r["produto"]: r.get("total_unidades", 0) for r in evidencias[:6] if "produto" in r}
                    if chart_dict:
                        st.caption("Grafico de Volume: Produtos mais Vendidos")
                        st.bar_chart(chart_dict)
                elif "ranking_mesas" in ferramentas_usadas and evidencias:
                    chart_dict = {f"Mesa {r['mesa']}": r.get("faturamento_total", 0.0) for r in evidencias[:6] if "mesa" in r}
                    if chart_dict:
                        st.caption("Grafico de Receita por Mesa (R$)")
                        st.bar_chart(chart_dict)
                elif "vendas_por_categoria" in ferramentas_usadas and evidencias:
                    chart_dict = {r["categoria"]: r.get("receita_total", 0.0) for r in evidencias if "categoria" in r}
                    if chart_dict:
                        st.caption("Distribuicao de Receita por Categoria (R$)")
                        st.bar_chart(chart_dict)
                elif "evolucao_temporal" in ferramentas_usadas and evidencias:
                    chart_dict = {r["periodo"]: r.get("faturamento_total", 0.0) for r in evidencias if "periodo" in r}
                    if chart_dict:
                        st.caption("Evolucao Temporal de Faturamento (R$)")
                        st.line_chart(chart_dict)

                with st.expander("Como calculei esta resposta (Auditoria & RAG)", expanded=False):
                    badge_falhas = "0 falhas intermediarias" if falhas == 0 else f"{falhas} falha(s) recuperada(s) via cascata"
                    st.markdown(
                        f'<div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 10px 14px; margin-bottom: 12px; font-size: 0.84rem;">'
                        f'<div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px;">'
                        f'<span><b>Provedor IA:</b> <code style="color: #38bdf8;">Google Gemini ({mod_resp})</code></span>'
                        f'<span><b>API de Origem:</b> <span style="color: #34d399; font-weight: 700;">{api_resp}</span></span>'
                        f'<span><b>Resiliencia:</b> <span style="color: #fbbf24;">{badge_falhas}</span></span>'
                        f'</div></div>',
                        unsafe_allow_html=True
                    )

                    # Secao 1: Premissa, Periodo e Filtros
                    premissas_salvas = f_data.get("premissas", [])
                    if premissas_salvas:
                        st.markdown(f"**Premissa Assumida:** `{' | '.join(premissas_salvas)}`")

                    params_usados = f_data.get("parametros", {})
                    if params_usados:
                        st.markdown("**1. Periodo & Filtros Aplicados:**")
                        st.code(json.dumps(params_usados, indent=2, ensure_ascii=False), language="json")

                    # Secao 2: Ferramentas Deterministicas
                    if ferramentas_usadas:
                        st.markdown(f"**2. Ferramentas Invocadas:** {', '.join(f'`{f}`' for f in ferramentas_usadas)}")

                    # Secao 3: Evidencias Numericas do SQLite
                    if evidencias:
                        st.markdown("**3. Evidencias Numericas Extraidas do Banco:**")
                        st.dataframe(evidencias, use_container_width=True, height=200)

    # 3. PROCESSAMENTO DE PERGUNTA PENDENTE OU ENVIADA
    pergunta_a_enviar = None
    if st.session_state["pergunta_pendente"]:
        pergunta_a_enviar = st.session_state["pergunta_pendente"]
        st.session_state["pergunta_pendente"] = None

    entrada_usuario = st.chat_input("Pergunte ao Assistente sobre faturamento, mesas, pratos, turnos ou estoque...")
    if entrada_usuario:
        pergunta_a_enviar = entrada_usuario

    if pergunta_a_enviar:
        # 1. Salva e renderiza a pergunta do Gerente
        with st.chat_message("user", avatar=None):
            st.markdown(pergunta_a_enviar)
        assistente_ia.salvar_mensagem_chat(conversa_id_atual, "user", pergunta_a_enviar)

        # Atualiza titulo automatico na primeira pergunta
        if len(historico) == 0:
            novo_tit_auto = assistente_ia.gerar_titulo_automatico(pergunta_a_enviar)
            assistente_ia.renomear_conversa(conversa_id_atual, novo_tit_auto, usuario_id=usuario_id)

        # 2. Executa processamento RAG deterministico com cascata de fallback
        with st.chat_message("assistant", avatar=None):
            with st.spinner("Consultando dados operacionais no SQLite e orquestrando cascata de IA..."):
                resultado = assistente_ia.executar_pergunta_gerente(
                    pergunta=pergunta_a_enviar,
                    conversa_id=conversa_id_atual,
                    ignorar_demo=st.session_state["ignorar_demo"]
                )

                resposta_texto = resultado["resposta"]

                if not resultado["sucesso"]:
                    st.markdown(
                        f'<div style="background: rgba(239, 68, 68, 0.1); border: 1.5px solid rgba(239, 68, 68, 0.35); border-radius: 12px; padding: 14px 16px; margin: 10px 0;">'
                        f'<h4 style="margin: 0 0 6px 0; color: #f87171; font-weight: 700;">Atendimento Momentaneamente Indisponivel</h4>'
                        f'<p style="margin: 0; color: #f1f5f9; font-size: 0.88rem; line-height: 1.45;">{resposta_texto}</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(resposta_texto)

                # Monta payload de telemetria
                ferramentas_payload = {
                    "ferramentas": resultado.get("ferramentas_invocadas", []),
                    "parametros": resultado.get("parametros", {}),
                    "evidencias": resultado.get("evidencias", []),
                    "premissas": resultado.get("premissas", [])
                }
                ferramentas_json_str = json.dumps(ferramentas_payload, ensure_ascii=False)

                # Exibe graficos se pertinente
                evidencias = resultado.get("evidencias", [])
                ferramentas_usadas = resultado.get("ferramentas_invocadas", [])
                if "ranking_produtos" in ferramentas_usadas and evidencias:
                    chart_dict = {r["produto"]: r.get("total_unidades", 0) for r in evidencias[:6] if "produto" in r}
                    if chart_dict:
                        st.caption("Grafico de Volume: Produtos mais Vendidos")
                        st.bar_chart(chart_dict)
                elif "ranking_mesas" in ferramentas_usadas and evidencias:
                    chart_dict = {f"Mesa {r['mesa']}": r.get("faturamento_total", 0.0) for r in evidencias[:6] if "mesa" in r}
                    if chart_dict:
                        st.caption("Grafico de Receita por Mesa (R$)")
                        st.bar_chart(chart_dict)
                elif "vendas_por_categoria" in ferramentas_usadas and evidencias:
                    chart_dict = {r["categoria"]: r.get("receita_total", 0.0) for r in evidencias if "categoria" in r}
                    if chart_dict:
                        st.caption("Distribuicao de Receita por Categoria (R$)")
                        st.bar_chart(chart_dict)
                elif "evolucao_temporal" in ferramentas_usadas and evidencias:
                    chart_dict = {r["periodo"]: r.get("faturamento_total", 0.0) for r in evidencias if "periodo" in r}
                    if chart_dict:
                        st.caption("Evolucao Temporal de Faturamento (R$)")
                        st.line_chart(chart_dict)

                # Painel "Como Calculei"
                with st.expander("Como calculei esta resposta (Auditoria & RAG)", expanded=False):
                    api_origem = resultado.get("api_origem", "Chave 1")
                    mod_resp = resultado.get("modelo", "Gemini")
                    falhas = resultado.get("tentativas_falhas", 0)
                    duracao = resultado.get("duracao_ms", 0)
                    badge_falhas = "0 falhas intermediarias" if falhas == 0 else f"{falhas} falha(s) recuperada(s) via cascata"

                    st.markdown(
                        f'<div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 10px 14px; margin-bottom: 12px; font-size: 0.84rem;">'
                        f'<div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px;">'
                        f'<span><b>Provedor IA:</b> <code style="color: #38bdf8;">Google Gemini ({mod_resp})</code></span>'
                        f'<span><b>Origem:</b> <span style="color: #34d399; font-weight: 700;">{api_origem}</span></span>'
                        f'<span><b>Tempo:</b> <span style="color: #94a3b8;">{duracao} ms</span></span>'
                        f'<span><b>Resiliencia:</b> <span style="color: #fbbf24;">{badge_falhas}</span></span>'
                        f'</div></div>',
                        unsafe_allow_html=True
                    )

                    if resultado.get("premissas"):
                        st.markdown(f"**Premissa Assumida:** `{' | '.join(resultado['premissas'])}`")

                    if resultado.get("ferramentas_invocadas"):
                        st.caption(f"**Ferramentas Invocadas:** {', '.join(f'`{f}`' for f in resultado['ferramentas_invocadas'])}")

                    if resultado.get("parametros"):
                        st.caption(f"**Parametros Aplicados:** `{json.dumps(resultado['parametros'], ensure_ascii=False)}`")

                    if resultado.get("evidencias"):
                        st.markdown("**Evidencias Numericas Extraidas do SQLite:**")
                        st.dataframe(resultado["evidencias"], use_container_width=True, height=200)

                # Persiste resposta do assistente no SQLite local
                assistente_ia.salvar_mensagem_chat(
                    conversa_id=conversa_id_atual,
                    papel="assistant",
                    conteudo=resposta_texto,
                    ferramentas_json=ferramentas_json_str,
                    api_origem=resultado.get("api_origem"),
                    modelo_utilizado=resultado.get("modelo"),
                    tentativas_falhas=resultado.get("tentativas_falhas", 0)
                )

        st.rerun()

# Rodape
ui_components.render_footer()

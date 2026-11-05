"""
Interface Conversacional do Assistente IA do Gerente — ChurrasControl
Localização: pages/8_Assistente_IA.py

Implementa:
- Guarda de segurança RBAC estrita (exclusivo para cargo 'gerente').
- Interface moderna com st.chat_message e st.chat_input.
- Botões de atalho para perguntas executivas rápidas.
- Painel auditável "Como calculei" exibindo telemetria da cascata (Chave 1/2, modelo, falhas) e dataframe SQLite.
- Gerenciamento de histórico de sessões de chat.
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
    page_title="Assistente IA - ChurrasControl",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 1. Guarda RBAC estrita para Gerente
usuario = ui_components.verificar_permissao_acesso(["gerente"])

# 2. Renderização da Top Navbar
ui_components.render_navbar(active_tab="assistente_ia")

# Inicialização do estado de conversas
usuario_id = str(usuario.get("id", "gerente"))
if "conversa_ativa_id" not in st.session_state:
    st.session_state["conversa_ativa_id"] = None
if "pergunta_pendente" not in st.session_state:
    st.session_state["pergunta_pendente"] = None

# Cabeçalho da Página
c_title, c_actions = st.columns([3, 1.2], vertical_alignment="center")

with c_title:
    st.markdown(
        '<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">'
        '<div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>'
        '</div>'
        '<div>'
        '<h2 style="margin: 0; font-weight: 800; font-size: 1.6rem; color: #f8fafc; letter-spacing: -0.02em;">Assistente Executivo de Inteligência Artificial</h2>'
        '<span style="font-size: 0.82rem; color: #94a3b8;">RAG Estruturado & Ontologia Relacional • Cálculos Determinísticos Sem Alucinação</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

with c_actions:
    if st.button("Nova Conversa", key="btn_nova_conversa", use_container_width=True, type="secondary"):
        novo_id = assistente_ia.criar_conversa(usuario_id, f"Conversa {st.session_state.get('cont_conv', 1)}")
        st.session_state["conversa_ativa_id"] = novo_id
        st.session_state["cont_conv"] = st.session_state.get("cont_conv", 1) + 1
        st.rerun()

# 3. Validação de Credenciais Google Gemini (Chave 1 e Chave 2)
k1 = os.getenv("GOOGLE_API_KEY_1", "").strip()
k2 = os.getenv("GOOGLE_API_KEY_2", "").strip()

if not k1 and not k2:
    st.markdown(
        '<div style="background: rgba(245, 158, 11, 0.1); border: 1.5px solid rgba(245, 158, 11, 0.35); border-radius: 16px; padding: 20px; margin: 15px 0;">'
        '<h4 style="margin: 0 0 6px 0; color: #fbbf24; font-weight: 700;">Configuração de Chaves do Google Gemini Necessária</h4>'
        '<p style="margin: 0 0 10px 0; color: #e2e8f0; font-size: 0.88rem; line-height: 1.45;">Para habilitar o Assistente IA, configure pelo menos uma chave de API no arquivo <code>.env</code> na raiz do projeto:</p>'
        '<pre style="background: rgba(0,0,0,0.5); padding: 10px; border-radius: 8px; color: #38bdf8; font-size: 0.82rem; margin: 0 0 10px 0;">GOOGLE_API_KEY_1=AIzaSy...&#10;GOOGLE_API_KEY_2=AIzaSy... (opcional para cascata automática)</pre>'
        '<p style="margin: 0; color: #94a3b8; font-size: 0.80rem;"><i>Por diretriz rigorosa de segurança, chaves de API nunca são salvas no banco de dados ou exibidas em logs.</i></p>'
        '</div>',
        unsafe_allow_html=True
    )

# 4. Gerenciamento de Conversa Ativa
conversas_existentes = assistente_ia.listar_conversas(usuario_id)
if not st.session_state["conversa_ativa_id"]:
    if conversas_existentes:
        st.session_state["conversa_ativa_id"] = conversas_existentes[0]["id"]
    else:
        st.session_state["conversa_ativa_id"] = assistente_ia.criar_conversa(usuario_id, "Sessão Inicial")

conversa_id_atual = st.session_state["conversa_ativa_id"]

# Seletor de Sessões e Perguntas Rápidas
col_sel, col_quick = st.columns([1.2, 3], vertical_alignment="center")

with col_sel:
    opcoes_conv = {c["id"]: f"{c['titulo']} ({c['criado_em'][:10]})" for c in conversas_existentes}
    if conversa_id_atual in opcoes_conv:
        sel_idx = list(opcoes_conv.keys()).index(conversa_id_atual)
        escolha = st.selectbox("Sessão Atual", options=list(opcoes_conv.keys()), index=sel_idx, format_func=lambda x: opcoes_conv.get(x, x), label_visibility="collapsed")
        if escolha != conversa_id_atual:
            st.session_state["conversa_ativa_id"] = escolha
            st.rerun()

with col_quick:
    st.markdown("<div style='font-size: 0.78rem; color: #94a3b8; margin-bottom: 4px; font-weight: 600;'>PERGUNTAS FREQUENTES:</div>", unsafe_allow_html=True)
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("Faturamento Hoje", key="btn_q_fat", use_container_width=True):
            st.session_state["pergunta_pendente"] = "Quanto faturamos hoje e qual foi o ticket médio das comandas pagas?"
    with q2:
        if st.button("Top Pratos Almoço", key="btn_q_top", use_container_width=True):
            st.session_state["pergunta_pendente"] = "Quais foram os pratos e carnes mais vendidos no turno do almoço?"
    with q3:
        if st.button("Mesas na Varanda", key="btn_q_varanda", use_container_width=True):
            st.session_state["pergunta_pendente"] = "Como foi o faturamento e atendimentos nas mesas da varanda?"
    with q4:
        if st.button("Estoque Crítico", key="btn_q_est", use_container_width=True):
            st.session_state["pergunta_pendente"] = "Tem algum produto com estoque crítico ou precisando produzir agora?"

st.markdown("<hr style='margin: 12px 0 18px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.07);'>", unsafe_allow_html=True)

# 5. Renderização do Histórico da Conversa
historico = assistente_ia.carregar_historico_chat(conversa_id_atual)

# Renderiza mensagens existentes
for msg in historico:
    papel = msg["papel"]
    conteudo = msg["conteudo"]
    with st.chat_message(papel, avatar=None):
        st.markdown(conteudo)
        
        # Painel "Como Calculei" para mensagens do assistente
        if papel == "assistant" and (msg.get("ferramentas_data") or msg.get("api_origem")):
            f_data = msg.get("ferramentas_data") or {}
            api_resp = msg.get("api_origem") or "Chave 1"
            mod_resp = msg.get("modelo_utilizado") or "Gemini"
            falhas = msg.get("tentativas_falhas", 0)
            
            with st.expander("Como calculei esta resposta (Auditoria & RAG)", expanded=False):
                badge_falhas = "0 falhas intermediárias" if falhas == 0 else f"{falhas} falha(s) recuperada(s) via cascata"
                st.markdown(
                    f'<div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 10px 14px; margin-bottom: 12px; font-size: 0.84rem;">'
                    f'<div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px;">'
                    f'<span><b>Provedor IA:</b> <code style="color: #38bdf8;">Google Gemini ({mod_resp})</code></span>'
                    f'<span><b>API de Origem:</b> <span style="color: #34d399; font-weight: 700;">{api_resp}</span></span>'
                    f'<span><b>Resiliência:</b> <span style="color: #fbbf24;">{badge_falhas}</span></span>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
                
                ferramentas_usadas = f_data.get("ferramentas", [])
                if ferramentas_usadas:
                    st.caption(f"**Ferramentas Determinísticas Invocadas:** {', '.join(f'`{f}`' for f in ferramentas_usadas)}")
                
                params_usados = f_data.get("parametros", {})
                if params_usados:
                    st.caption(f"**Parâmetros Aplicados:** `{json.dumps(params_usados, ensure_ascii=False)}`")

                evidencias = f_data.get("evidencias", [])
                if evidencias:
                    st.markdown("**Evidências Numéricas Extraídas:**")
                    st.dataframe(evidencias, use_container_width=True, height=220)

# Processa pergunta pendente dos botões de atalho
pergunta_a_enviar = None
if st.session_state["pergunta_pendente"]:
    pergunta_a_enviar = st.session_state["pergunta_pendente"]
    st.session_state["pergunta_pendente"] = None

# Entrada de Chat
entrada_usuario = st.chat_input("Pergunte sobre faturamento, mesas, pratos, turnos ou estoque...")
if entrada_usuario:
    pergunta_a_enviar = entrada_usuario

if pergunta_a_enviar:
    # 1. Renderiza e salva mensagem do usuário
    with st.chat_message("user", avatar=None):
        st.markdown(pergunta_a_enviar)
    assistente_ia.salvar_mensagem_chat(conversa_id_atual, "user", pergunta_a_enviar)

    # 2. Executa processamento RAG com cascata de fallback
    with st.chat_message("assistant", avatar=None):
        with st.spinner("Consultando dados operacionais e orquestrando cascata de IA..."):
            resultado = assistente_ia.executar_pergunta_gerente(pergunta_a_enviar, conversa_id=conversa_id_atual)
            
            resposta_texto = resultado["resposta"]
            st.markdown(resposta_texto)

            # Monta payload de ferramentas e auditoria
            ferramentas_payload = {
                "ferramentas": resultado.get("ferramentas_invocadas", []),
                "parametros": resultado.get("parametros", {}),
                "evidencias": resultado.get("evidencias", [])
            }
            ferramentas_json_str = json.dumps(ferramentas_payload, ensure_ascii=False)

            # Painel "Como Calculei"
            with st.expander("Como calculei esta resposta (Auditoria & RAG)", expanded=False):
                api_origem = resultado.get("api_origem", "Chave 1")
                mod_resp = resultado.get("modelo", "Gemini")
                falhas = resultado.get("tentativas_falhas", 0)
                badge_falhas = "0 falhas intermediárias" if falhas == 0 else f"{falhas} falha(s) recuperada(s) via cascata"

                st.markdown(
                    f'<div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 10px 14px; margin-bottom: 12px; font-size: 0.84rem;">'
                    f'<div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px;">'
                    f'<span><b>Provedor IA:</b> <code style="color: #38bdf8;">Google Gemini ({mod_resp})</code></span>'
                    f'<span><b>API de Origem:</b> <span style="color: #34d399; font-weight: 700;">{api_origem}</span></span>'
                    f'<span><b>Resiliência:</b> <span style="color: #fbbf24;">{badge_falhas}</span></span>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )

                if resultado.get("ferramentas_invocadas"):
                    st.caption(f"**Ferramentas Determinísticas Invocadas:** {', '.join(f'`{f}`' for f in resultado['ferramentas_invocadas'])}")
                
                if resultado.get("parametros"):
                    st.caption(f"**Parâmetros Aplicados:** `{json.dumps(resultado['parametros'], ensure_ascii=False)}`")

                if resultado.get("evidencias"):
                    st.markdown("**Evidências Numéricas Extraídas do SQLite:**")
                    st.dataframe(resultado["evidencias"], use_container_width=True, height=220)

            # Persiste mensagem do assistente no SQLite
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

# Rodapé
ui_components.render_footer()

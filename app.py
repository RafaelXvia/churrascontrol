import sys

# Suprime o aviso inofensivo do Windows ProactorEventLoop ao encerrar conexões
if sys.platform == "win32":
    try:
        from asyncio.proactor_events import _ProactorBasePipeTransport
        _orig_call_connection_lost = _ProactorBasePipeTransport._call_connection_lost
        def _silent_call_connection_lost(self, exc):
            try:
                _orig_call_connection_lost(self, exc)
            except (ConnectionResetError, OSError):
                pass
        _ProactorBasePipeTransport._call_connection_lost = _silent_call_connection_lost
    except Exception:
        pass

import streamlit as st
from datetime import datetime
from backend.database import data_manager
from frontend.components import ui_components

st.set_page_config(
    page_title="ChurrasControl - Painel Operacional",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 1. Guarda de segurança e autenticação (exige login e primeiro acesso redefinido)
usuario = ui_components.exigir_autenticacao()

# Caixa acessa estritamente Salão & Mesas e Cardápio; redireciona imediatamente se tentar acessar o Painel Geral
if str(usuario.get("cargo", "")).lower() == "caixa":
    st.switch_page("pages/1_Salao_e_Mesas.py")

is_gerente = (usuario and str(usuario.get("cargo", "")).lower() == "gerente")

# Renderiza a barra de navegação no topo e remove a sidebar
ui_components.render_navbar(active_tab="home")

# Leitura direta e instantânea dos dados locais
mesas = data_manager.listar_mesas()
produtos = data_manager.listar_produtos()
dash_dados = data_manager.obter_dashboard_dados("7d")
resumo = dash_dados.get("resumo", {})

total_mesas_ocupadas = len(mesas)
consumo_em_aberto = sum(float(m.get("total_atual", 0.0)) for m in mesas)
faturamento_7d = float(resumo.get("faturamento_total", 0.0))
ticket_medio = float(resumo.get("ticket_medio", 0.0))

# Seção de Boas-vindas e Visão Rápida
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 10px; margin-bottom: 1.25rem;">
    <div>
        <h2 style="margin: 0; font-size: 1.6rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
            Painel Geral Operacional
        </h2>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.9rem;">
            Visão consolidada do salão em tempo real, fluxo de pedidos e métricas do turno.
        </p>
    </div>
    <div style="font-size: 0.8rem; color: #64748b; background: rgba(255, 255, 255, 0.04); padding: 6px 14px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.07);">
        Última leitura: <span style="color: #f8fafc; font-weight: 600;">""" + datetime.now().strftime("%H:%M:%S") + """</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Grid de Métricas Principais (4 KPIs com Cards Estilizados)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        label="Mesas Ocupadas",
        value=f"{total_mesas_ocupadas} mesa(s)",
        help="Total de mesas com atendimento em andamento"
    )

with kpi2:
    st.metric(
        label="Consumo em Aberto",
        value=f"R$ {consumo_em_aberto:,.2f}",
        help="Soma total dos pedidos não finalizados"
    )

with kpi3:
    st.metric(
        label="Faturamento (7 Dias)",
        value=f"R$ {faturamento_7d:,.2f}",
        help="Receita bruta finalizada nos últimos 7 dias"
    )

with kpi4:
    st.metric(
        label="Itens no Cardápio",
        value=f"{len(produtos)} produtos",
        help="Total de produtos ativos no catálogo do PDV"
    )

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# ================= MÓDULOS OPERACIONAIS (CARDS CLICÁVEIS COM SVGS) =================
st.markdown("""
<div style="margin: 1.5rem 0 0.85rem 0;">
    <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #f8fafc;">
        Módulos do Sistema
    </h3>
    <p style="margin: 2px 0 0 0; color: #94a3b8; font-size: 0.85rem;">
        Selecione o setor operacional que deseja gerenciar:
    </p>
</div>
""", unsafe_allow_html=True)

if is_gerente:
    mod1, mod2, mod3 = st.columns(3)

    with mod1:
        st.markdown("""
        <div class="cc-module-card cc-clickable-card theme-amber">
            <div>
                <div class="cc-module-header">
                    <div class="cc-module-left">
                        <div class="cc-module-icon icon-amber">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/>
                            </svg>
                        </div>
                        <div class="cc-module-titles">
                            <h4>1. Salão e Mesas</h4>
                            <span class="badge-amber">Frente de Caixa & Garçom</span>
                        </div>
                    </div>
                    <div class="cc-module-chevron">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </div>
                </div>
                <p class="cc-module-desc">
                    Abertura de mesas, visualização de comandas, lançamento de itens com observações e fechamento de conta.
                </p>
            </div>
            <div class="cc-module-action" style="color: #f59e0b !important;">
                <span>Acessar Salão & Mesas</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Salão e Mesas", key="btn_card_salao", use_container_width=True):
            st.switch_page("pages/1_Salao_e_Mesas.py")

    with mod2:
        st.markdown("""
        <div class="cc-module-card cc-clickable-card theme-blue">
            <div>
                <div class="cc-module-header">
                    <div class="cc-module-left">
                        <div class="cc-module-icon icon-blue">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><path d="M9 14h6"/><path d="M9 18h6"/><path d="M9 10h6"/>
                            </svg>
                        </div>
                        <div class="cc-module-titles">
                            <h4>2. Cardápio Comercial</h4>
                            <span class="badge-blue">Produtos & Precificação</span>
                        </div>
                    </div>
                    <div class="cc-module-chevron">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </div>
                </div>
                <p class="cc-module-desc">
                    Gestão do catálogo de produtos, código único de PDV, categorias e atualização rápida de preços.
                </p>
            </div>
            <div class="cc-module-action" style="color: #60a5fa !important;">
                <span>Acessar Cardápio</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Cardápio Comercial", key="btn_card_cardapio", use_container_width=True):
            st.switch_page("pages/2_Cardapio.py")

    with mod3:
        st.markdown("""
        <div class="cc-module-card cc-clickable-card theme-emerald">
            <div>
                <div class="cc-module-header">
                    <div class="cc-module-left">
                        <div class="cc-module-icon icon-emerald">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
                            </svg>
                        </div>
                        <div class="cc-module-titles">
                            <h4>3. Relatórios & PDF</h4>
                            <span class="badge-emerald">Auditoria & Performance</span>
                        </div>
                    </div>
                    <div class="cc-module-chevron">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </div>
                </div>
                <p class="cc-module-desc">
                    Indicadores de faturamento, ticket médio por comanda, histórico de vendas e emissão de relatório PDF.
                </p>
            </div>
            <div class="cc-module-action" style="color: #34d399 !important;">
                <span>Acessar Relatórios</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Relatórios & PDF", key="btn_card_relatorios", use_container_width=True):
            st.switch_page("pages/3_Relatorios.py")

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    mod4, mod5, mod6 = st.columns(3)

    with mod4:
        st.markdown("""
        <div class="cc-module-card cc-clickable-card theme-amber">
            <div>
                <div class="cc-module-header">
                    <div class="cc-module-left">
                        <div class="cc-module-icon icon-amber">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                            </svg>
                        </div>
                        <div class="cc-module-titles">
                            <h4>4. Colaboradores</h4>
                            <span class="badge-amber">Controle de Acessos</span>
                        </div>
                    </div>
                </div>
                <p class="cc-module-desc">
                    Gestão da equipe, controle de cargos RBAC (Caixa e Gerente) e redefinição segura de credenciais.
                </p>
            </div>
            <div class="cc-module-action" style="color: #f59e0b !important;">
                <span>Acessar Equipe</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Colaboradores", key="btn_card_colabs", use_container_width=True):
            st.switch_page("pages/6_Colaboradores.py")

    with mod5:
        st.markdown("""
        <div class="cc-module-card cc-clickable-card theme-blue">
            <div>
                <div class="cc-module-header">
                    <div class="cc-module-left">
                        <div class="cc-module-icon icon-blue">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                            </svg>
                        </div>
                        <div class="cc-module-titles">
                            <h4>5. Auditoria Operacional</h4>
                            <span class="badge-blue">Trilha de Segurança</span>
                        </div>
                    </div>
                </div>
                <p class="cc-module-desc">
                    Rastreabilidade completa de ações, cancelamentos, abertura de mesas e eventos do sistema.
                </p>
            </div>
            <div class="cc-module-action" style="color: #60a5fa !important;">
                <span>Acessar Auditoria</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Auditoria", key="btn_card_auditoria", use_container_width=True):
            st.switch_page("pages/7_Auditoria.py")

    with mod6:
        st.markdown("""
        <div class="cc-module-card cc-clickable-card theme-emerald" style="border-color: rgba(16, 185, 129, 0.4);">
            <div>
                <div class="cc-module-header">
                    <div class="cc-module-left">
                        <div class="cc-module-icon icon-emerald">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/>
                            </svg>
                        </div>
                        <div class="cc-module-titles">
                            <h4>6. Assistente IA</h4>
                            <span class="badge-emerald" style="background: rgba(16, 185, 129, 0.2); color: #34d399;">RAG & Ontologia</span>
                        </div>
                    </div>
                </div>
                <p class="cc-module-desc">
                    Análise conversacional de faturamento, setores de mesas, pratos mais vendidos e estoque com IA executiva.
                </p>
            </div>
            <div class="cc-module-action" style="color: #10b981 !important;">
                <span>Conversar com o Assistente</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Conversar com o Assistente IA", key="btn_card_ia", use_container_width=True):
            st.switch_page("pages/8_Assistente_IA.py")

else:
    # Perfil Caixa: foco total no Salão e Mesas
    mod1, mod2 = st.columns([2, 1])

    with mod1:
        st.markdown("""
        <div class="cc-module-card cc-clickable-card theme-amber" style="min-height: 180px;">
            <div>
                <div class="cc-module-header">
                    <div class="cc-module-left">
                        <div class="cc-module-icon icon-amber">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/>
                            </svg>
                        </div>
                        <div class="cc-module-titles">
                            <h4>Salão e Gestão de Mesas</h4>
                            <span class="badge-amber">Módulo Operacional do Caixa</span>
                        </div>
                    </div>
                    <div class="cc-module-chevron">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </div>
                </div>
                <p class="cc-module-desc">
                    Abertura de mesas, visualização de comandas, lançamento de itens com observações e fechamento de conta com cálculo de taxa e divisão por pessoa.
                </p>
            </div>
            <div class="cc-module-action" style="color: #f59e0b !important;">
                <span>Acessar Salão & Mesas</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Salão e Mesas", key="btn_card_salao_caixa", use_container_width=True):
            st.switch_page("pages/1_Salao_e_Mesas.py")

    with mod2:
        st.markdown("""
        <div class="cc-module-card" style="border-color: rgba(56, 189, 248, 0.35); min-height: 180px;">
            <div>
                <div class="cc-module-header">
                    <div class="cc-module-left">
                        <div class="cc-module-icon icon-blue">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>
                            </svg>
                        </div>
                        <div class="cc-module-titles">
                            <h4>Perfil: Operador de Caixa</h4>
                            <span class="badge-blue">Frente de Salão</span>
                        </div>
                    </div>
                </div>
                <p class="cc-module-desc">
                    Seu acesso está configurado para a operação de salão e caixa. Módulos de cadastro de produtos, faturamento e relatórios executivos são restritos ao perfil de Gerente.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Rodapé Executivo
ui_components.render_footer()


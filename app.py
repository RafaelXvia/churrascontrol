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
import importlib
import data_manager
importlib.reload(data_manager)
import ui_components
importlib.reload(ui_components)

st.set_page_config(
    page_title="ChurrasControl - Painel Operacional",
    page_icon="🥩",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

# ================= MÓDULOS OPERACIONAIS (CARDS CLICÁVEIS) =================
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

mod1, mod2, mod3 = st.columns(3)

with mod1:
    st.markdown("""
    <div class="cc-module-card cc-clickable-card theme-amber">
        <div>
            <div class="cc-module-header">
                <div class="cc-module-left">
                    <div class="cc-module-icon icon-amber">🍽️</div>
                    <div class="cc-module-titles">
                        <h4>1. Salão e Mesas</h4>
                        <span class="badge-amber">Frente de Caixa & Garçom</span>
                    </div>
                </div>
                <div class="cc-module-chevron">➔</div>
            </div>
            <p class="cc-module-desc">
                Abertura de mesas, visualização de comandas, lançamento de itens com observações e fechamento de conta.
            </p>
        </div>
        <div class="cc-module-action" style="color: #f59e0b !important;">
            <span>Acessar Salão & Mesas</span>
            <span style="font-size: 0.95rem; transition: transform 0.25s ease;">➔</span>
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
                    <div class="cc-module-icon icon-blue">📋</div>
                    <div class="cc-module-titles">
                        <h4>2. Cardápio Comercial</h4>
                        <span class="badge-blue">Produtos & Precificação</span>
                    </div>
                </div>
                <div class="cc-module-chevron">➔</div>
            </div>
            <p class="cc-module-desc">
                Gestão do catálogo de produtos, código único de PDV, categorias e atualização rápida de preços.
            </p>
        </div>
        <div class="cc-module-action" style="color: #60a5fa !important;">
            <span>Acessar Cardápio</span>
            <span style="font-size: 0.95rem; transition: transform 0.25s ease;">➔</span>
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
                    <div class="cc-module-icon icon-emerald">📊</div>
                    <div class="cc-module-titles">
                        <h4>3. Relatórios & PDF</h4>
                        <span class="badge-emerald">Auditoria & Performance</span>
                    </div>
                </div>
                <div class="cc-module-chevron">➔</div>
            </div>
            <p class="cc-module-desc">
                Indicadores de faturamento, ticket médio por comanda, histórico de vendas e emissão de relatório PDF.
            </p>
        </div>
        <div class="cc-module-action" style="color: #34d399 !important;">
            <span>Acessar Relatórios</span>
            <span style="font-size: 0.95rem; transition: transform 0.25s ease;">➔</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acessar Relatórios & PDF", key="btn_card_relatorios", use_container_width=True):
        st.switch_page("pages/3_Relatorios.py")

# Rodapé Executivo
ui_components.render_footer()


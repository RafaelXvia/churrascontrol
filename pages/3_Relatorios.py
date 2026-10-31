import importlib
import streamlit as st
import pandas as pd
import data_manager
importlib.reload(data_manager)
import ui_components
importlib.reload(ui_components)

st.set_page_config(
    page_title="Relatórios e Dashboard - ChurrasControl",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Navbar superior unificada
ui_components.render_navbar(active_tab="relatorios")

# Cabeçalho da Página
c_title, c_act = st.columns([3, 1])
with c_title:
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="margin: 0; font-size: 1.5rem; font-weight: 800; color: #ffffff;">
            Relatórios Financeiros & Auditoria
        </h2>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.88rem;">
            Métricas consolidadas de faturamento, ticket médio, análise por categoria e exportação oficial em PDF.
        </p>
    </div>
    """, unsafe_allow_html=True)

periodo_labels = {
    "1d": "Últimas 24 Horas",
    "7d": "Últimos 7 Dias",
    "15d": "Últimos 15 Dias",
    "30d": "Últimos 30 Dias"
}

c_p1, c_p2 = st.columns([3, 2])
with c_p1:
    periodo_sel = st.segmented_control(
        "Período de Análise",
        options=list(periodo_labels.keys()),
        format_func=lambda x: periodo_labels[x],
        default="7d"
    )
    if not periodo_sel:
        periodo_sel = "7d"

# Dados obtidos instantaneamente do JSON local
dados = data_manager.obter_dashboard_dados(periodo_sel)
resumo = dados.get("resumo", {})

# Botão de Download do PDF no topo
with c_p2:
    st.write("")
    pdf_bytes = data_manager.gerar_pdf_bytes(periodo_sel)
    st.download_button(
        label="Baixar Relatório Oficial em PDF",
        data=pdf_bytes,
        file_name=f"relatorio_churrascontrol_{periodo_sel}.pdf",
        mime="application/pdf",
        use_container_width=True,
        type="primary"
    )

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# KPIs Executivos
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        label="Faturamento Total",
        value=f"R$ {float(resumo.get('faturamento_total', 0.0)):,.2f}"
    )
with k2:
    st.metric(
        label="Mesas Finalizadas",
        value=f"{resumo.get('total_comandas', 0)} comandas"
    )
with k3:
    st.metric(
        label="Ticket Médio / Mesa",
        value=f"R$ {float(resumo.get('ticket_medio', 0.0)):,.2f}"
    )
with k4:
    st.metric(
        label="Clientes Atendidos",
        value=f"{resumo.get('total_pessoas', 0)} pessoas"
    )

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Gráficos Analíticos
g1, g2 = st.columns(2)

with g1:
    st.markdown("""
    <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-bottom: 8px;">
        Evolução Diária da Receita
    </div>
    """, unsafe_allow_html=True)
    evolucao = dados.get("evolucao_diaria", [])
    if evolucao:
        df_evo = pd.DataFrame(evolucao)
        df_evo.rename(columns={"data": "Data", "total": "Faturamento (R$)"}, inplace=True)
        st.line_chart(df_evo.set_index("Data"), color="#f59e0b")
    else:
        st.info("Nenhuma venda finalizada registrada no período selecionado.")

with g2:
    st.markdown("""
    <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-bottom: 8px;">
        Faturamento por Categoria
    </div>
    """, unsafe_allow_html=True)
    cat_data = dados.get("vendas_por_categoria", [])
    if cat_data:
        df_cat = pd.DataFrame(cat_data)
        df_cat.rename(columns={"categoria": "Categoria", "total": "Faturamento (R$)"}, inplace=True)
        st.bar_chart(df_cat.set_index("Categoria")["Faturamento (R$)"], color="#d97706")
    else:
        st.info("Nenhum dado por categoria registrado no período.")

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Tabelas Detalhadas
t1, t2 = st.columns(2)

with t1:
    st.markdown("""
    <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-bottom: 8px;">
        Produtos Mais Vendidos
    </div>
    """, unsafe_allow_html=True)
    top_prods = dados.get("top_produtos", [])
    if top_prods:
        df_top = pd.DataFrame(top_prods)[["nome", "categoria", "quantidade_total", "faturamento_total"]]
        df_top.columns = ["Produto", "Categoria", "Qtd Vendida", "Receita (R$)"]
        st.dataframe(df_top, use_container_width=True, hide_index=True)
    else:
        st.caption("Nenhum produto registrado no período.")

with t2:
    st.markdown("""
    <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-bottom: 8px;">
        Histórico de Comandas Encerradas
    </div>
    """, unsafe_allow_html=True)
    comandas_hist = dados.get("comandas_finalizadas", [])
    if comandas_hist:
        df_com = pd.DataFrame(comandas_hist)[["id", "numero_mesa", "data_fechamento", "qtd_pessoas", "valor_total"]]
        df_com.columns = ["Comanda", "Mesa", "Fechamento", "Clientes", "Total Pago (R$)"]
        st.dataframe(df_com, use_container_width=True, hide_index=True)
    else:
        st.caption("Nenhuma comanda finalizada no período.")

# Rodapé Executivo
ui_components.render_footer()

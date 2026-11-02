import importlib
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import data_manager
importlib.reload(data_manager)
import ui_components
importlib.reload(ui_components)

st.set_page_config(
    page_title="Relatórios e Dashboard - ChurrasControl",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Injetar tema e navbar unificada
ui_components.inject_custom_theme()
ui_components.render_navbar(active_tab="relatorios")

# ================= CABEÇALHO & SELETOR DE PERÍODO =================
periodo_labels = {
    "1d": "Hoje (Últimas 24h)",
    "7d": "Últimos 7 Dias",
    "15d": "Últimos 15 Dias",
    "30d": "Últimos 30 Dias"
}

c_head, c_ctrl = st.columns([3, 2])

with c_head:
    st.markdown("""
    <div style="margin-bottom: 0.5rem;">
        <h2 style="margin: 0; font-size: 1.55rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
            Relatórios Financeiros & Auditoria
        </h2>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.88rem;">
            Acompanhe o faturamento, ticket médio, produtos campeões e histórico de comandas.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c_ctrl:
    col_per, col_pdf = st.columns([1.4, 1.6])
    with col_per:
        periodo_sel = st.selectbox(
            "Período de Análise",
            options=list(periodo_labels.keys()),
            format_func=lambda x: periodo_labels[x],
            index=1,
            label_visibility="collapsed"
        )
        if not periodo_sel:
            periodo_sel = "7d"
    with col_pdf:
        pdf_bytes = data_manager.gerar_pdf_bytes(periodo_sel)
        st.download_button(
            label="Exportar Relatório PDF",
            data=pdf_bytes,
            file_name=f"relatorio_churrascontrol_{periodo_sel}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

# Obter dados consolidados
dados = data_manager.obter_dashboard_dados(periodo_sel)
resumo = dados.get("resumo", {})

fat_total = float(resumo.get("faturamento_total", 0.0))
tot_comandas = int(resumo.get("total_comandas", 0))
ticket_medio = float(resumo.get("ticket_medio", 0.0))
tot_pessoas = int(resumo.get("total_pessoas", 0))
ticket_pessoa = float(resumo.get("ticket_por_pessoa", 0.0))

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# ================= CARDS DE KPIS EXECUTIVOS =================
st.markdown(f"""
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 20px;">
    <!-- KPI 1: Faturamento -->
    <div style="background: linear-gradient(145deg, rgba(245, 158, 11, 0.12) 0%, rgba(15, 23, 42, 0.75) 100%); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 14px; padding: 16px 20px; box-shadow: 0 4px 18px rgba(0,0,0,0.35);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #fbbf24; text-transform: uppercase; letter-spacing: 0.05em;">Faturamento Bruto</span>
            <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(245, 158, 11, 0.2); display: flex; align-items: center; justify-content: center;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="1" x2="12" y2="23"></line>
                    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                </svg>
            </div>
        </div>
        <div style="font-size: 1.65rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
            R$ {fat_total:,.2f}
        </div>
        <div style="font-size: 0.76rem; color: #94a3b8; margin-top: 4px;">
            Receita total fechada no período
        </div>
    </div>

    <!-- KPI 2: Comandas Fechadas -->
    <div style="background: linear-gradient(145deg, rgba(56, 189, 248, 0.1) 0%, rgba(15, 23, 42, 0.75) 100%); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 14px; padding: 16px 20px; box-shadow: 0 4px 18px rgba(0,0,0,0.35);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.05em;">Mesas Atendidas</span>
            <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(56, 189, 248, 0.2); display: flex; align-items: center; justify-content: center;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <line x1="3" y1="9" x2="21" y2="9"></line>
                    <line x1="9" y1="21" x2="9" y2="9"></line>
                </svg>
            </div>
        </div>
        <div style="font-size: 1.65rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
            {tot_comandas} <span style="font-size: 0.95rem; font-weight: 600; color: #94a3b8;">comandas</span>
        </div>
        <div style="font-size: 0.76rem; color: #94a3b8; margin-top: 4px;">
            Contas liquidadas com sucesso
        </div>
    </div>

    <!-- KPI 3: Ticket Médio -->
    <div style="background: linear-gradient(145deg, rgba(52, 211, 153, 0.1) 0%, rgba(15, 23, 42, 0.75) 100%); border: 1px solid rgba(52, 211, 153, 0.25); border-radius: 14px; padding: 16px 20px; box-shadow: 0 4px 18px rgba(0,0,0,0.35);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #34d399; text-transform: uppercase; letter-spacing: 0.05em;">Ticket Médio / Mesa</span>
            <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(52, 211, 153, 0.2); display: flex; align-items: center; justify-content: center;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                </svg>
            </div>
        </div>
        <div style="font-size: 1.65rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
            R$ {ticket_medio:,.2f}
        </div>
        <div style="font-size: 0.76rem; color: #94a3b8; margin-top: 4px;">
            Gasto médio por mesa fechada
        </div>
    </div>

    <!-- KPI 4: Clientes & Ticket/Pessoa -->
    <div style="background: linear-gradient(145deg, rgba(167, 139, 250, 0.1) 0%, rgba(15, 23, 42, 0.75) 100%); border: 1px solid rgba(167, 139, 250, 0.25); border-radius: 14px; padding: 16px 20px; box-shadow: 0 4px 18px rgba(0,0,0,0.35);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #a78bfa; text-transform: uppercase; letter-spacing: 0.05em;">Clientes Atendidos</span>
            <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(167, 139, 250, 0.2); display: flex; align-items: center; justify-content: center;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                    <circle cx="9" cy="7" r="4"></circle>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
            </div>
        </div>
        <div style="font-size: 1.65rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
            {tot_pessoas} <span style="font-size: 0.95rem; font-weight: 600; color: #94a3b8;">pessoas</span>
        </div>
        <div style="font-size: 0.76rem; color: #c4b5fd; margin-top: 4px;">
            Ticket Médio: <strong>R$ {ticket_pessoa:,.2f}</strong> por pessoa
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ================= ABAS ESTRUTURADAS (SEM POLUIÇÃO VISUAL) =================
tab_graficos, tab_produtos, tab_comandas = st.tabs([
    "Painel de Gráficos Analíticos",
    "Ranking de Produtos",
    "Auditoria de Comandas"
])

# ----------------- ABA 1: PAINEL DE GRÁFICOS -----------------
with tab_graficos:
    col_g1, col_g2 = st.columns([1.3, 1])

    with col_g1:
        st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 14px 16px 8px 16px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-size: 0.95rem; font-weight: 700; color: #f8fafc;">
                    Evolução Temporal do Faturamento
                </div>
                <span style="font-size: 0.72rem; background: rgba(245, 158, 11, 0.15); color: #fbbf24; padding: 2px 8px; border-radius: 6px; font-weight: 600;">
                    Diário (R$)
                </span>
            </div>
            <div style="font-size: 0.76rem; color: #94a3b8; margin-bottom: 6px;">
                Receita registrada dia a dia. Passe o cursor para inspecionar os valores sem travar a rolagem.
            </div>
        </div>
        """, unsafe_allow_html=True)

        evolucao = dados.get("evolucao_diaria", [])
        if evolucao:
            df_evo = pd.DataFrame(evolucao)
            # Inverter para exibir ordem cronológica (esquerda para a direita)
            df_evo = df_evo.iloc[::-1].reset_index(drop=True)

            # Gráfico de área + linha limpo e sem scroll zoom
            base = alt.Chart(df_evo).encode(
                x=alt.X("data:N", title=None, axis=alt.Axis(labelColor="#94a3b8", labelAngle=0, grid=False)),
                y=alt.Y("total:Q", title=None, axis=alt.Axis(labelColor="#94a3b8", grid=True, gridColor="#1e293b", format="~s")),
                tooltip=[
                    alt.Tooltip("data:N", title="Data"),
                    alt.Tooltip("total:Q", title="Faturamento (R$)", format=",.2f")
                ]
            )

            area = base.mark_area(
                color="#f59e0b",
                opacity=0.18,
                line=False
            )

            linha = base.mark_line(
                color="#f59e0b",
                size=2.8
            )

            pontos = base.mark_circle(
                size=50,
                color="#fbbf24",
                opacity=1
            )

            chart_final = (area + linha + pontos).properties(
                height=260
            ).configure_view(
                strokeWidth=0
            )

            st.altair_chart(chart_final, use_container_width=True)
        else:
            st.info("Nenhuma venda finalizada no período selecionado.")

    with col_g2:
        st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 14px 16px 8px 16px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-size: 0.95rem; font-weight: 700; color: #f8fafc;">
                    Faturamento por Categoria
                </div>
                <span style="font-size: 0.72rem; background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 2px 8px; border-radius: 6px; font-weight: 600;">
                    Mix de Vendas
                </span>
            </div>
            <div style="font-size: 0.76rem; color: #94a3b8; margin-bottom: 6px;">
                Volume financeiro gerado por segmento do cardápio.
            </div>
        </div>
        """, unsafe_allow_html=True)

        cat_data = dados.get("vendas_por_categoria", [])
        if cat_data:
            df_cat = pd.DataFrame(cat_data)
            # Gráfico de barras horizontais arredondadas sem scroll zoom
            chart_cat = alt.Chart(df_cat).mark_bar(
                cornerRadiusTopRight=6,
                cornerRadiusBottomRight=6,
                color="#d97706",
                height=24
            ).encode(
                y=alt.Y("categoria:N", title=None, sort="-x", axis=alt.Axis(labelColor="#f8fafc", grid=False)),
                x=alt.X("total:Q", title=None, axis=alt.Axis(labelColor="#94a3b8", grid=True, gridColor="#1e293b", format="~s")),
                tooltip=[
                    alt.Tooltip("categoria:N", title="Categoria"),
                    alt.Tooltip("total:Q", title="Faturamento (R$)", format=",.2f")
                ]
            ).properties(
                height=260
            ).configure_view(
                strokeWidth=0
            )

            st.altair_chart(chart_cat, use_container_width=True)
        else:
            st.info("Nenhuma venda por categoria no período.")

# ----------------- ABA 2: RANKING DE PRODUTOS -----------------
with tab_produtos:
    st.markdown("""
    <div style="margin-bottom: 12px;">
        <h4 style="margin: 0; color: #ffffff; font-size: 1.05rem; font-weight: 700;">
            Produtos Mais Vendidos no Período
        </h4>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.82rem;">
            Itens com maior saída e receita agregada durante as operações.
        </p>
    </div>
    """, unsafe_allow_html=True)

    top_prods = dados.get("top_produtos", [])
    if top_prods:
        df_top = pd.DataFrame(top_prods)
        # Selecionar e renomear colunas
        df_top_view = df_top[["nome", "categoria", "quantidade_total", "faturamento_total"]].copy()
        df_top_view.columns = ["Item do Cardápio", "Categoria", "Qtd Vendida (un)", "Receita Total (R$)"]
        
        # Formatação amigável
        st.dataframe(
            df_top_view,
            column_config={
                "Item do Cardápio": st.column_config.TextColumn(width="large"),
                "Categoria": st.column_config.TextColumn(width="medium"),
                "Qtd Vendida (un)": st.column_config.NumberColumn(format="%d un"),
                "Receita Total (R$)": st.column_config.NumberColumn(format="R$ %.2f")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Nenhum item vendido registrado no período selecionado.")

# ----------------- ABA 3: AUDITORIA DE COMANDAS -----------------
with tab_comandas:
    st.markdown("""
    <div style="margin-bottom: 12px;">
        <h4 style="margin: 0; color: #ffffff; font-size: 1.05rem; font-weight: 700;">
            Auditoria de Comandas Encerradas
        </h4>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.82rem;">
            Registro detalhado com data, hora, número da mesa, pessoas e valor pago.
        </p>
    </div>
    """, unsafe_allow_html=True)

    comandas_hist = dados.get("comandas_finalizadas", [])
    if comandas_hist:
        df_com = pd.DataFrame(comandas_hist)
        
        # Converter data ISO para formato legível DD/MM/YYYY HH:MM
        def formatar_data(iso_str):
            try:
                dt = datetime.fromisoformat(str(iso_str).replace("Z", ""))
                return dt.strftime("%d/%m/%Y %H:%M")
            except Exception:
                return str(iso_str)[:16]

        df_com["data_formatada"] = df_com["data_fechamento"].apply(formatar_data)
        
        df_com_view = df_com[["id", "numero_mesa", "data_formatada", "qtd_pessoas", "valor_total"]].copy()
        df_com_view.columns = ["ID Comanda", "Mesa", "Data & Hora", "Clientes", "Total Pago (R$)"]

        # Filtro de busca rápido
        busca_mesa = st.text_input("Filtrar por número da mesa ou ID da comanda:", placeholder="Ex: 888 ou 85")
        if busca_mesa.strip():
            filtro = (
                df_com_view["Mesa"].astype(str).str.contains(busca_mesa.strip(), case=False) |
                df_com_view["ID Comanda"].astype(str).str.contains(busca_mesa.strip(), case=False)
            )
            df_com_view = df_com_view[filtro]

        st.dataframe(
            df_com_view,
            column_config={
                "ID Comanda": st.column_config.NumberColumn(format="#%d", width="small"),
                "Mesa": st.column_config.TextColumn(width="small"),
                "Data & Hora": st.column_config.TextColumn(width="medium"),
                "Clientes": st.column_config.NumberColumn(format="%d pessoas", width="small"),
                "Total Pago (R$)": st.column_config.NumberColumn(format="R$ %.2f", width="medium")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Nenhuma comanda finalizada registrada no período selecionado.")

# ================= RODAPÉ =================
ui_components.render_footer()

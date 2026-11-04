import html
from datetime import datetime
import streamlit as st
import data_manager
import ui_components

st.set_page_config(
    page_title="Relatórios e Dashboard - ChurrasControl",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Injetar tema e navbar unificada
ui_components.inject_custom_theme()
ui_components.render_navbar(active_tab="relatorios")

# ================= FUNÇÕES NATIVAS ULTRA-LEVES DE GRÁFICOS E TABELAS (SEM PANDAS/ALTAIR) =================

def render_svg_line_chart(evolucao: list) -> str:
    """Renderiza gráfico de linha e área responsivo em SVG nativo (0 MB de sobrecarga no servidor)."""
    if not evolucao:
        return "<div style='color: #94a3b8; font-size: 0.85rem; padding: 25px 0; text-align: center;'>Nenhuma venda finalizada no período selecionado.</div>"
    
    items = list(reversed(evolucao))
    totais = [float(it.get("total", 0.0)) for it in items]
    datas = [str(it.get("data", "")) for it in items]
    max_val = max(totais) if totais and max(totais) > 0 else 1.0
    
    width = 620
    height = 230
    padding_x = 50
    padding_y = 35
    
    n = len(items)
    step_x = (width - 2 * padding_x) / (n - 1) if n > 1 else (width - 2 * padding_x) / 2
    
    pontos = []
    for i, val in enumerate(totais):
        x = padding_x + (i * step_x if n > 1 else step_x)
        y = (height - padding_y) - (val / max_val) * (height - 2 * padding_y)
        pontos.append((x, y, val, datas[i]))
        
    pts_str = " ".join([f"{p[0]:.1f},{p[1]:.1f}" for p in pontos])
    primeiro_x = pontos[0][0]
    ultimo_x = pontos[-1][0]
    chao_y = height - padding_y
    area_d = f"M {primeiro_x:.1f},{chao_y:.1f} L " + " L ".join([f"{p[0]:.1f},{p[1]:.1f}" for p in pontos]) + f" L {ultimo_x:.1f},{chao_y:.1f} Z"
    
    svg = f"""
    <div style="width: 100%; overflow-x: auto; background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 12px 14px 6px 14px;">
    <svg viewBox="0 0 {width} {height}" style="width: 100%; max-height: 250px; display: block; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <defs>
            <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.32"/>
                <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.0"/>
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#f59e0b" flood-opacity="0.45"/>
            </filter>
        </defs>
        <!-- Linhas de grade sutis -->
        <line x1="{padding_x}" y1="{chao_y}" x2="{width - padding_x}" y2="{chao_y}" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
        <line x1="{padding_x}" y1="{(height - 2*padding_y)/2 + padding_y}" x2="{width - padding_x}" y2="{(height - 2*padding_y)/2 + padding_y}" stroke="rgba(255,255,255,0.05)" stroke-width="1" stroke-dasharray="4,4"/>
        <line x1="{padding_x}" y1="{padding_y}" x2="{width - padding_x}" y2="{padding_y}" stroke="rgba(255,255,255,0.05)" stroke-width="1" stroke-dasharray="4,4"/>
        
        <!-- Área de Faturamento -->
        <path d="{area_d}" fill="url(#areaGradient)"/>
        
        <!-- Linha de Evolução -->
        <polyline fill="none" stroke="#f59e0b" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" points="{pts_str}" filter="url(#glow)"/>
    """
    
    for px, py, val, dt in pontos:
        svg += f"""
        <circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="#fbbf24" stroke="#0f172a" stroke-width="2.5"/>
        <text x="{px:.1f}" y="{py - 11:.1f}" fill="#f8fafc" font-size="10.5" font-weight="700" text-anchor="middle">R$ {val:,.0f}</text>
        <text x="{px:.1f}" y="{chao_y + 18:.1f}" fill="#94a3b8" font-size="9.5" text-anchor="middle">{dt}</text>
        """
        
    svg += """
    </svg>
    </div>
    """
    return svg

def render_html_category_bars(cat_data: list) -> str:
    """Renderiza barras de mix de vendas com gradientes CSS nativos (0 MB de sobrecarga no servidor)."""
    if not cat_data:
        return "<div style='color: #94a3b8; font-size: 0.85rem; padding: 25px 0; text-align: center;'>Nenhuma venda por categoria no período.</div>"
    
    totais = [float(it.get("total", 0.0)) for it in cat_data]
    max_val = max(totais) if totais and max(totais) > 0 else 1.0
    total_geral = sum(totais) if sum(totais) > 0 else 1.0
    
    html_out = "<div style='display: flex; flex-direction: column; gap: 10px; padding: 4px 0;'>"
    for it in cat_data:
        cat_nome = html.escape(str(it.get("categoria", "Outros")))
        val = float(it.get("total", 0.0))
        pct_rel = (val / max_val) * 100.0
        pct_total = (val / total_geral) * 100.0
        
        html_out += f"""
        <div style="background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 10px 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 0.86rem;">
                <span style="font-weight: 700; color: #f8fafc;">{cat_nome}</span>
                <span style="color: #fbbf24; font-weight: 800;">R$ {val:,.2f} <span style="font-size: 0.72rem; color: #94a3b8; font-weight: 500;">({pct_total:.1f}%)</span></span>
            </div>
            <div style="width: 100%; height: 9px; background: rgba(255, 255, 255, 0.07); border-radius: 999px; overflow: hidden;">
                <div style="width: {pct_rel:.1f}%; height: 100%; background: linear-gradient(90deg, #d97706 0%, #f59e0b 100%); border-radius: 999px;"></div>
            </div>
        </div>
        """
    html_out += "</div>"
    return html_out

def render_ranking_table(top_prods: list) -> str:
    """Tabela de produtos executiva estilizada em HTML/CSS nativo."""
    if not top_prods:
        return "<div style='color: #94a3b8; font-size: 0.85rem; padding: 25px 0; text-align: center;'>Nenhum item vendido registrado no período selecionado.</div>"
    
    html_out = """
    <div style="overflow-x: auto; background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; margin-top: 10px;">
    <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem; color: #f1f5f9;">
        <thead>
            <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.1); background: rgba(255, 255, 255, 0.03);">
                <th style="padding: 12px 16px; font-weight: 700; color: #94a3b8; font-size: 0.76rem; text-transform: uppercase;">Pos</th>
                <th style="padding: 12px 16px; font-weight: 700; color: #94a3b8; font-size: 0.76rem; text-transform: uppercase;">Item do Cardápio</th>
                <th style="padding: 12px 16px; font-weight: 700; color: #94a3b8; font-size: 0.76rem; text-transform: uppercase;">Categoria</th>
                <th style="padding: 12px 16px; font-weight: 700; color: #94a3b8; font-size: 0.76rem; text-transform: uppercase; text-align: center;">Qtd Vendida</th>
                <th style="padding: 12px 16px; font-weight: 700; color: #94a3b8; font-size: 0.76rem; text-transform: uppercase; text-align: right;">Receita Total</th>
            </tr>
        </thead>
        <tbody>
    """
    for idx, p in enumerate(top_prods, 1):
        badge_color = "#f59e0b" if idx == 1 else ("#94a3b8" if idx == 2 else ("#d97706" if idx == 3 else "#64748b"))
        nome = html.escape(str(p.get("nome", "")))
        cat = html.escape(str(p.get("categoria", "")))
        qtd = int(p.get("quantidade_total", 0))
        fat = float(p.get("faturamento_total", 0.0))
        
        html_out += f"""
        <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); transition: background 0.2s;">
            <td style="padding: 12px 16px;"><span style="background: rgba(255,255,255,0.06); color: {badge_color}; font-weight: 800; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem;">#{idx}</span></td>
            <td style="padding: 12px 16px; font-weight: 600; color: #ffffff;">{nome}</td>
            <td style="padding: 12px 16px;"><span style="background: rgba(56, 189, 248, 0.12); color: #38bdf8; font-weight: 600; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem;">{cat}</span></td>
            <td style="padding: 12px 16px; text-align: center; font-weight: 700; color: #f8fafc;">{qtd} un</td>
            <td style="padding: 12px 16px; text-align: right; font-weight: 800; color: #10b981;">R$ {fat:,.2f}</td>
        </tr>
        """
    html_out += """
        </tbody>
    </table>
    </div>
    """
    return html_out

def render_comandas_table(comandas: list, filtro_mesa: str = "") -> str:
    """Tabela de auditoria de comandas estilizada em HTML/CSS nativo."""
    if not comandas:
        return "<div style='color: #94a3b8; font-size: 0.85rem; padding: 25px 0; text-align: center;'>Nenhuma comanda finalizada registrada no período selecionado.</div>"
    
    itens = []
    f = filtro_mesa.strip().lower()
    for c in comandas:
        c_id = str(c.get("id", ""))
        c_mesa = str(c.get("numero_mesa", ""))
        if f and (f not in c_id.lower() and f not in c_mesa.lower()):
            continue
        itens.append(c)
        
    if not itens:
        return "<div style='color: #94a3b8; font-size: 0.85rem; padding: 25px 0; text-align: center;'>Nenhuma comanda corresponde ao filtro informado.</div>"

    html_out = """
    <div style="overflow-x: auto; background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; margin-top: 10px;">
    <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem; color: #f1f5f9;">
        <thead>
            <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.1); background: rgba(255, 255, 255, 0.03);">
                <th style="padding: 12px 16px; font-weight: 700; color: #94a3b8; font-size: 0.76rem; text-transform: uppercase;">ID Comanda</th>
                <th style="padding: 12px 16px; font-weight: 700; color: #94a3b8; font-size: 0.76rem; text-transform: uppercase;">Mesa</th>
                <th style="padding: 12px 16px; font-weight: 700; color: #94a3b8; font-size: 0.76rem; text-transform: uppercase;">Data & Hora</th>
                <th style="padding: 12px 16px; font-weight: 700; color: #94a3b8; font-size: 0.76rem; text-transform: uppercase; text-align: center;">Clientes</th>
                <th style="padding: 12px 16px; font-weight: 700; color: #94a3b8; font-size: 0.76rem; text-transform: uppercase; text-align: right;">Total Pago</th>
            </tr>
        </thead>
        <tbody>
    """
    for c in itens:
        c_id = c.get("id", "")
        c_mesa = c.get("numero_mesa", "")
        dt_raw = str(c.get("data_fechamento", ""))
        try:
            dt_fmt = datetime.fromisoformat(dt_raw.replace("Z", "")).strftime("%d/%m/%Y %H:%M")
        except Exception:
            dt_fmt = dt_raw[:16]
        pessoas = int(c.get("qtd_pessoas", 1))
        val_total = float(c.get("valor_total", 0.0))
        
        html_out += f"""
        <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
            <td style="padding: 12px 16px; font-weight: 700; color: #f59e0b;">#{c_id}</td>
            <td style="padding: 12px 16px; font-weight: 600; color: #ffffff;">Mesa {c_mesa}</td>
            <td style="padding: 12px 16px; color: #94a3b8; font-size: 0.82rem;">{dt_fmt}</td>
            <td style="padding: 12px 16px; text-align: center; color: #cbd5e1;">{pessoas} pessoa(s)</td>
            <td style="padding: 12px 16px; text-align: right; font-weight: 800; color: #34d399;">R$ {val_total:,.2f}</td>
        </tr>
        """
    html_out += """
        </tbody>
    </table>
    </div>
    """
    return html_out

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
            key="filtro_periodo_relatorios",
            label_visibility="collapsed"
        )
        if not periodo_sel:
            periodo_sel = "7d"
            
    with col_pdf:
        # GERAÇÃO SOB DEMANDA: Não instancia o ReportLab até o usuário solicitar expressamente
        if "pdf_gerado" not in st.session_state or st.session_state.get("pdf_periodo") != periodo_sel:
            if st.button("Gerar Relatório PDF", key="btn_preparar_pdf", use_container_width=True, type="primary"):
                with st.spinner("Compilando PDF..."):
                    st.session_state["pdf_gerado"] = data_manager.gerar_pdf_bytes_cached(periodo_sel)
                    st.session_state["pdf_periodo"] = periodo_sel
                    st.rerun()
        else:
            st.download_button(
                label=f"Baixar PDF ({periodo_sel})",
                data=st.session_state["pdf_gerado"],
                file_name=f"relatorio_churrascontrol_{periodo_sel}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )

# Obter dados consolidados (atualizados dinamicamente pelo período)
dados = data_manager.obter_dashboard_dados(periodo_sel)
resumo = dados.get("resumo", {})

fat_total = float(resumo.get("faturamento_total", 0.0))
tot_comandas = int(resumo.get("total_comandas", 0))
ticket_medio = float(resumo.get("ticket_medio", 0.0))
tot_pessoas = int(resumo.get("total_pessoas", 0))
ticket_pessoa = float(resumo.get("ticket_por_pessoa", 0.0))

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# ================= CARDS DE KPIS EXECUTIVOS =================
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""<div style="background: linear-gradient(145deg, rgba(245, 158, 11, 0.14) 0%, rgba(15, 23, 42, 0.85) 100%); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 14px; padding: 16px 18px; box-shadow: 0 4px 18px rgba(0,0,0,0.35); min-height: 125px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
<span style="font-size: 0.76rem; font-weight: 700; color: #fbbf24; text-transform: uppercase; letter-spacing: 0.05em;">Faturamento Bruto</span>
<div style="width: 28px; height: 28px; border-radius: 7px; background: rgba(245, 158, 11, 0.2); display: flex; align-items: center; justify-content: center;">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
</div>
</div>
<div style="font-size: 1.55rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">R$ {fat_total:,.2f}</div>
<div style="font-size: 0.74rem; color: #94a3b8; margin-top: 4px;">Receita total no período</div>
</div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""<div style="background: linear-gradient(145deg, rgba(56, 189, 248, 0.12) 0%, rgba(15, 23, 42, 0.85) 100%); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 14px; padding: 16px 18px; box-shadow: 0 4px 18px rgba(0,0,0,0.35); min-height: 125px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
<span style="font-size: 0.76rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.05em;">Mesas Atendidas</span>
<div style="width: 28px; height: 28px; border-radius: 7px; background: rgba(56, 189, 248, 0.2); display: flex; align-items: center; justify-content: center;">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>
</div>
</div>
<div style="font-size: 1.55rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">{tot_comandas} <span style="font-size: 0.9rem; font-weight: 600; color: #94a3b8;">comandas</span></div>
<div style="font-size: 0.74rem; color: #94a3b8; margin-top: 4px;">Comandas finalizadas</div>
</div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""<div style="background: linear-gradient(145deg, rgba(52, 211, 153, 0.12) 0%, rgba(15, 23, 42, 0.85) 100%); border: 1px solid rgba(52, 211, 153, 0.3); border-radius: 14px; padding: 16px 18px; box-shadow: 0 4px 18px rgba(0,0,0,0.35); min-height: 125px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
<span style="font-size: 0.76rem; font-weight: 700; color: #34d399; text-transform: uppercase; letter-spacing: 0.05em;">Ticket Médio</span>
<div style="width: 28px; height: 28px; border-radius: 7px; background: rgba(52, 211, 153, 0.2); display: flex; align-items: center; justify-content: center;">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
</div>
</div>
<div style="font-size: 1.55rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">R$ {ticket_medio:,.2f}</div>
<div style="font-size: 0.74rem; color: #94a3b8; margin-top: 4px;">Média por mesa atendida</div>
</div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""<div style="background: linear-gradient(145deg, rgba(167, 139, 250, 0.12) 0%, rgba(15, 23, 42, 0.85) 100%); border: 1px solid rgba(167, 139, 250, 0.3); border-radius: 14px; padding: 16px 18px; box-shadow: 0 4px 18px rgba(0,0,0,0.35); min-height: 125px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
<span style="font-size: 0.76rem; font-weight: 700; color: #a78bfa; text-transform: uppercase; letter-spacing: 0.05em;">Pessoas Atendidas</span>
<div style="width: 28px; height: 28px; border-radius: 7px; background: rgba(167, 139, 250, 0.2); display: flex; align-items: center; justify-content: center;">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
</div>
</div>
<div style="font-size: 1.55rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">{tot_pessoas} <span style="font-size: 0.9rem; font-weight: 600; color: #94a3b8;">clientes</span></div>
<div style="font-size: 0.74rem; color: #c4b5fd; margin-top: 4px;">R$ {ticket_pessoa:,.2f} por pessoa</div>
</div>""", unsafe_allow_html=True)

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
                Receita registrada dia a dia. Renderização ultrarrápida nativa em SVG sem sobrecarga de servidor.
            </div>
        </div>
        """, unsafe_allow_html=True)

        evolucao = dados.get("evolucao_diaria", [])
        st.markdown(render_svg_line_chart(evolucao), unsafe_allow_html=True)

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
                Volume financeiro gerado por segmento do cardápio em barras nativas.
            </div>
        </div>
        """, unsafe_allow_html=True)

        cat_data = dados.get("vendas_por_categoria", [])
        st.markdown(render_html_category_bars(cat_data), unsafe_allow_html=True)

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
    st.markdown(render_ranking_table(top_prods), unsafe_allow_html=True)

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
    busca_mesa = st.text_input("Filtrar por número da mesa ou ID da comanda:", placeholder="Ex: 888 ou 85")
    st.markdown(render_comandas_table(comandas_hist, busca_mesa), unsafe_allow_html=True)

# ================= RODAPÉ =================
ui_components.render_footer()

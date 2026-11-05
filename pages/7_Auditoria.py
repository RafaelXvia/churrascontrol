import io
import csv
import streamlit as st
from datetime import datetime
from backend.database import data_manager
from frontend.components import ui_components

st.set_page_config(
    page_title="Auditoria & Segurança — ChurrasControl",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 1. Guarda estrita de segurança: apenas GERENTE pode acessar
usuario_logado = ui_components.verificar_permissao_acesso(["gerente"])

# 2. Barra de navegação superior com aba ativa em 'auditoria'
ui_components.render_navbar(active_tab="auditoria")

# Estilização complementar para a página de auditoria
st.markdown("""
<style>
.cc-audit-header {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 18px 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 14px;
}
.cc-audit-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.cc-audit-sub {
    font-size: 0.84rem;
    color: #94a3b8;
    margin-top: 4px;
}
.cc-kpi-card {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 14px;
    padding: 14px 18px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.cc-kpi-val {
    font-size: 1.6rem;
    font-weight: 800;
    color: #f59e0b;
}
.cc-kpi-lbl {
    font-size: 0.75rem;
    color: #94a3b8;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 2px;
}
.badge-acao-login {
    background: rgba(56, 189, 248, 0.18);
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.4);
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.75rem;
}
.badge-acao-criacao {
    background: rgba(74, 222, 128, 0.18);
    color: #4ade80;
    border: 1px solid rgba(74, 222, 128, 0.4);
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.75rem;
}
.badge-acao-edicao {
    background: rgba(251, 191, 36, 0.18);
    color: #fbbf24;
    border: 1px solid rgba(251, 191, 36, 0.4);
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.75rem;
}
.badge-acao-perigo {
    background: rgba(248, 113, 113, 0.18);
    color: #f87171;
    border: 1px solid rgba(248, 113, 113, 0.4);
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.75rem;
}
</style>
""", unsafe_allow_html=True)

# Cabeçalho da Página
st.markdown(
    '<div class="cc-audit-header">'
    '<div>'
    '<h2 class="cc-audit-title">Trilha de Auditoria & Segurança Operacional</h2>'
    '<div class="cc-audit-sub">'
    'Registro cronológico e imutável de todas as ações executadas no sistema (Logins, Trocas de Senha, Cardápio, Preços, Mesas e Colaboradores).'
    '</div>'
    '</div>'
    '<div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; color: #fbbf24; font-weight: 700;">'
    'Módulo Restrito: Gerência Geral'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

# 3. Painel de Filtros e Busca
c_f1, c_f2, c_f3, c_f4 = st.columns([1.5, 1.5, 2.5, 1.0])

with c_f1:
    modulos_opcoes = ["TODOS", "AUTENTICACAO", "CARDAPIO", "COMANDAS", "MESAS", "MESAS_E_COMANDAS", "COLABORADORES", "CARDAPIO_DIGITAL", "QRCODES"]
    modulo_sel = st.selectbox("Módulo:", modulos_opcoes, index=0)

with c_f2:
    acoes_opcoes = [
        "TODAS", "LOGIN", "FALHA_LOGIN", "LOGOUT", "ALTERAR_SENHA", "RECUPERAR_SENHA",
        "CRIAR_PRODUTO", "EDITAR_PRODUTO", "EXCLUIR_PRODUTO",
        "ABERTURA_MESA", "CANCELAMENTO_COMANDA", "EXCLUSAO_MESA", "FECHAR_COMANDA",
        "ADICIONAR_ITEM", "EDITAR_ITEM", "REMOVER_ITEM", "PEDIDO_CLIENTE",
        "CRIAR_COLABORADOR", "EDITAR_COLABORADOR", "EXCLUIR_COLABORADOR", "GERAR_QRCODE"
    ]
    acao_sel = st.selectbox("Ação:", acoes_opcoes, index=0)

with c_f3:
    busca_texto = st.text_input("Buscar por Detalhes, Nome ou E-mail:", placeholder="Ex: picanha, senha, R$, gerente...")

with c_f4:
    limite_linhas = st.selectbox("Limite:", [100, 250, 500, 1000], index=1)

# Consulta os registros de auditoria com os filtros aplicados
registros = data_manager.listar_auditoria(
    limite=limite_linhas,
    filtro_modulo=modulo_sel if modulo_sel != "TODOS" else None,
    filtro_acao=acao_sel if acao_sel != "TODAS" else None,
    busca=busca_texto if busca_texto.strip() else None
)

# 4. KPIs Rápidos sobre o resultado
total_reg = len(registros)
total_auth = sum(1 for r in registros if r.get("modulo") == "AUTENTICACAO")
total_prod = sum(1 for r in registros if r.get("modulo") == "CARDAPIO")
total_comandas = sum(1 for r in registros if r.get("modulo") in ("COMANDAS", "MESAS", "MESAS_E_COMANDAS", "CARDAPIO_DIGITAL"))

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="cc-kpi-card">
        <div class="cc-kpi-val">{total_reg}</div>
        <div class="cc-kpi-lbl">Eventos Exibidos</div>
    </div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="cc-kpi-card">
        <div class="cc-kpi-val" style="color: #38bdf8;">{total_auth}</div>
        <div class="cc-kpi-lbl">Acessos & Senhas</div>
    </div>
    """, unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="cc-kpi-card">
        <div class="cc-kpi-val" style="color: #4ade80;">{total_prod}</div>
        <div class="cc-kpi-lbl">Alterações Cardápio</div>
    </div>
    """, unsafe_allow_html=True)
with k4:
    st.markdown(f"""
    <div class="cc-kpi-card">
        <div class="cc-kpi-val" style="color: #c084fc;">{total_comandas}</div>
        <div class="cc-kpi-lbl">Mesas & Comandas</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# 5. Tabela / Visor de Auditoria
if not registros:
    st.info("Nenhum registro de auditoria encontrado para os filtros selecionados.")
else:
    # Formatação dos dados para exibição clara
    dados_tabela = []
    for r in registros:
        dt_raw = r.get("criado_em", "")
        dt_formatada = dt_raw
        try:
            dt_obj = datetime.fromisoformat(dt_raw)
            dt_formatada = dt_obj.strftime("%d/%m/%Y %H:%M:%S")
        except Exception:
            pass

        usuario_rotulo = f"{r.get('usuario_nome', '')} ({r.get('usuario_email', '')})" if r.get("usuario_email") else r.get("usuario_nome", "Sistema")
        cargo_rotulo = str(r.get("cargo") or "sistema").upper()

        dados_tabela.append({
            "ID": r["id"],
            "Data / Hora": dt_formatada,
            "Responsável": usuario_rotulo,
            "Cargo": cargo_rotulo,
            "Módulo": r.get("modulo", ""),
            "Ação": r.get("acao", ""),
            "Detalhes da Operação": r.get("detalhes", "")
        })

    st.dataframe(
        dados_tabela,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small"),
            "Data / Hora": st.column_config.TextColumn("Data / Hora", width="medium"),
            "Responsável": st.column_config.TextColumn("Responsável", width="medium"),
            "Cargo": st.column_config.TextColumn("Cargo", width="small"),
            "Módulo": st.column_config.TextColumn("Módulo", width="small"),
            "Ação": st.column_config.TextColumn("Ação", width="medium"),
            "Detalhes da Operação": st.column_config.TextColumn("Detalhes da Operação", width="large"),
        }
    )

    # 6. Botão de Exportação de Auditoria (CSV nativo Zero-Pandas)
    c_exp1, c_exp2 = st.columns([4, 1])
    with c_exp2:
        csv_buffer = io.StringIO()
        if dados_tabela:
            writer = csv.DictWriter(csv_buffer, fieldnames=list(dados_tabela[0].keys()))
            writer.writeheader()
            writer.writerows(dados_tabela)
        csv_data = csv_buffer.getvalue().encode("utf-8-sig")
        st.download_button(
            label="Exportar Log (CSV)",
            data=csv_data,
            file_name=f"churrascontrol_auditoria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
ui_components.render_footer()

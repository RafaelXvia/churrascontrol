import streamlit as st
import data_manager
import ui_components

st.set_page_config(
    page_title="Colaboradores & Acessos - ChurrasControl",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 1. Guarda de segurança restrita estritamente ao perfil 'gerente'
usuario_logado = ui_components.verificar_permissao_acesso(["gerente"])

# 2. Navbar superior ativa na aba 'colaboradores'
ui_components.render_navbar(active_tab="colaboradores")

# ================= MODAL DE CADASTRO DE NOVO COLABORADOR =================
@st.dialog("Cadastrar Novo Colaborador", width="medium")
def dialog_novo_colaborador():
    st.caption("Cadastre os dados de acesso da equipe. No primeiro login, o colaborador deverá definir uma nova senha pessoal.")
    with st.form("form_novo_colab"):
        nome = st.text_input("Nome Completo *", placeholder="Ex: Lucas Ferreira")
        email = st.text_input("E-mail de Login *", placeholder="lucas@churrascontrol.com")
        c1, c2 = st.columns(2)
        with c1:
            senha_inicial = st.text_input("Senha Inicial Provisória *", type="password", placeholder="Mínimo 4 caracteres")
        with c2:
            numero = st.text_input("Telefone / WhatsApp *", placeholder="(31) 98765-4321")
        
        cargo = st.selectbox(
            "Cargo & Nível de Acesso *",
            ["caixa", "gerente"],
            format_func=lambda x: "Operador de Caixa (Acesso: Painel Geral e Mesas)" if x == "caixa" else "Gerente Geral (Acesso Completo a Todos os Módulos)"
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        btn_salvar = st.form_submit_button("Confirmar e Cadastrar Colaborador", type="primary", use_container_width=True)

        if btn_salvar:
            if not nome.strip() or not email.strip() or not senha_inicial.strip() or not numero.strip():
                st.error("Todos os campos marcados com * são obrigatórios.")
            elif len(senha_inicial.strip()) < 4:
                st.error("A senha provisória deve conter ao menos 4 caracteres.")
            else:
                try:
                    data_manager.cadastrar_colaborador(
                        nome=nome,
                        email=email,
                        senha=senha_inicial,
                        numero=numero,
                        cargo=cargo
                    )
                    st.success(f"Colaborador(a) {nome} cadastrado(a) com sucesso!")
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))

# ================= MODAL DE EXCLUSÃO DE COLABORADOR =================
@st.dialog("Confirmar Exclusão de Colaborador")
def dialog_excluir_colaborador(colab: dict):
    st.markdown(f"""
    <div style="color: #cbd5e1; font-size: 0.95rem; margin-bottom: 12px;">
        Tem certeza que deseja remover o acesso do colaborador <b>{colab['nome']}</b> ({colab['email']})?
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Sim, Excluir Acesso", type="primary", use_container_width=True):
            try:
                data_manager.excluir_colaborador(colab["id"])
                st.success("Colaborador removido com sucesso!")
                st.rerun()
            except ValueError as err:
                st.error(str(err))
    with c2:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()

# ================= CABEÇALHO DA PÁGINA =================
col_title, col_btn = st.columns([2.5, 1.5], vertical_alignment="center")

with col_title:
    st.markdown("""
    <div style="margin-bottom: 0.75rem;">
        <h2 style="margin: 0; font-size: 1.55rem; font-weight: 800; color: #ffffff;">
            Gestão de Colaboradores & Acessos
        </h2>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.88rem;">
            Administração de operadores de caixa, gerentes e permissões de segurança com primeiro acesso.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_btn:
    btn_c1, btn_c2 = st.columns([1.2, 1.0])
    with btn_c1:
        if st.button("+ Novo Colaborador", type="primary", use_container_width=True):
            dialog_novo_colaborador()
    with btn_c2:
        if st.button("Sincronizar Xano", use_container_width=True, help="Sincronizar colaboradores criptografados direto do Xano"):
            try:
                qtd_sync = data_manager.sincronizar_colaboradores_xano()
                st.toast(f"{qtd_sync} colaboradores sincronizados do Xano!")
                st.rerun()
            except Exception as ex:
                st.error(f"Erro ao sincronizar: {ex}")

# ================= LISTAGEM DE COLABORADORES =================
colaboradores = data_manager.listar_colaboradores()

if not colaboradores:
    st.info("Nenhum colaborador cadastrado no momento.")
else:
    st.markdown(f"""
    <div style="color: #94a3b8; font-size: 0.82rem; margin-bottom: 12px;">
        Total de Colaboradores Cadastrados: <b>{len(colaboradores)}</b>
    </div>
    """, unsafe_allow_html=True)

    for colab in colaboradores:
        is_me = (colab["id"] == usuario_logado.get("id"))
        is_ger = (colab["cargo"] == "gerente")
        cargo_badge = '<span style="background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700;">GERENTE</span>' if is_ger else '<span style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700;">CAIXA</span>'
        
        status_senha = '<span style="color: #f59e0b; font-size: 0.76rem; font-weight: 600;">⚠️ Aguardando 1º Acesso (Troca Obrigatória)</span>' if colab.get("primeiro_acesso") else '<span style="color: #34d399; font-size: 0.76rem; font-weight: 600;">Ativo (Senha Pessoal Definida)</span>'

        me_tag = '<span style="background: rgba(255, 255, 255, 0.08); color: #e2e8f0; padding: 2px 8px; border-radius: 6px; font-size: 0.70rem; font-weight: 700; margin-left: 6px;">VOCÊ</span>' if is_me else ''

        c1, c2, c3, c4 = st.columns([3.5, 2.5, 3, 1.2], vertical_alignment="center")

        with c1:
            st.markdown(f"""
            <div style="line-height: 1.3;">
                <span style="font-weight: 800; color: #ffffff; font-size: 1.05rem;">{colab['nome']}</span>{me_tag}<br>
                <span style="color: #94a3b8; font-size: 0.85rem;">{colab['email']}</span>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div style="color: #cbd5e1; font-size: 0.85rem;">
                <span style="color: #64748b; font-size: 0.75rem; text-transform: uppercase;">Contato:</span><br>
                <b>{colab['numero']}</b>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                {cargo_badge}
                <div>{status_senha}</div>
            </div>
            """, unsafe_allow_html=True)

        with c4:
            if not is_me:
                if st.button("Excluir", key=f"btn_del_colab_{colab['id']}", help="Remover acesso deste colaborador", use_container_width=True):
                    dialog_excluir_colaborador(colab)
            else:
                st.caption("Sessão ativa")

        st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.06);'>", unsafe_allow_html=True)

# Rodapé Executivo
ui_components.render_footer()

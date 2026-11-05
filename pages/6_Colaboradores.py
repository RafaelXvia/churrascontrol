import streamlit as st
import streamlit.components.v1 as components
from backend.database import data_manager
from frontend.components import ui_components

def _injetar_mascara_telefone():
    """Injeta máscara de telefone brasileiro (XX) XXXXX-XXXX em tempo real enquanto o usuário digita."""
    js_mask = """
    <script>
        (function() {
            var p = (window.parent && window.parent !== window) ? window.parent : window;
            function formatarTel(v) {
                var r = v.replace(/\\D/g, "");
                if (r.length > 11) r = r.substring(0, 11);
                if (r.length > 10) {
                    return "(" + r.substring(0, 2) + ") " + r.substring(2, 7) + "-" + r.substring(7, 11);
                } else if (r.length > 6) {
                    return "(" + r.substring(0, 2) + ") " + r.substring(2, 6) + "-" + r.substring(6, 10);
                } else if (r.length > 2) {
                    return "(" + r.substring(0, 2) + ") " + r.substring(2);
                } else if (r.length > 0) {
                    return "(" + r;
                }
                return "";
            }
            function bindMask() {
                try {
                    var inputs = p.document.querySelectorAll('input[aria-label*="Telefone"], input[placeholder*="(31)"]');
                    inputs.forEach(function(inp) {
                        if (!inp.dataset.ccMaskBound) {
                            inp.dataset.ccMaskBound = "true";
                            inp.setAttribute("maxlength", "15");
                            inp.addEventListener("input", function(e) {
                                var start = inp.selectionStart;
                                var oldLen = inp.value.length;
                                var formatted = formatarTel(inp.value);
                                if (inp.value !== formatted) {
                                    var setter = Object.getOwnPropertyDescriptor(p.HTMLInputElement.prototype, "value").set;
                                    setter.call(inp, formatted);
                                    inp.dispatchEvent(new Event("input", { bubbles: true }));
                                    var newLen = formatted.length;
                                    var newPos = start + (newLen - oldLen);
                                    try { inp.setSelectionRange(newPos, newPos); } catch(err) {}
                                }
                            });
                        }
                    });
                } catch(err) {}
            }
            bindMask();
            setInterval(bindMask, 300);
        })();
    </script>
    """
    components.html(js_mask, height=0, width=0)

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
    _injetar_mascara_telefone()
    st.caption("Cadastre os dados de acesso da equipe. No primeiro login, o colaborador deverá definir uma nova senha pessoal.")
    with st.form("form_novo_colab"):
        nome = st.text_input("Nome Completo *", placeholder="Ex: Lucas Ferreira")
        email = st.text_input("E-mail de Login *", placeholder="lucas@churrascontrol.com")
        c1, c2 = st.columns(2)
        with c1:
            senha_inicial = st.text_input("Senha Inicial Provisória *", type="password", placeholder="Mínimo 4 caracteres")
        with c2:
            numero = st.text_input("Telefone / WhatsApp *", placeholder="(31) 98765-4321", max_chars=15)
        
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
                    numero_formatado = data_manager.formatar_telefone_br(numero)
                    data_manager.cadastrar_colaborador(
                        nome=nome,
                        email=email,
                        senha=senha_inicial,
                        numero=numero_formatado,
                        cargo=cargo
                    )
                    st.success(f"Colaborador(a) {nome} cadastrado(a) com sucesso!")
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))

# ================= MODAL DE EDIÇÃO DE COLABORADOR =================
@st.dialog("Editar Colaborador", width="medium")
def dialog_editar_colaborador(colab: dict):
    _injetar_mascara_telefone()
    st.caption(f"Atualize os dados de acesso de {colab['nome']}. Todas as informações são criptografadas e sincronizadas com o Xano.")
    with st.form(f"form_edit_colab_{colab['id']}"):
        nome = st.text_input("Nome Completo *", value=colab["nome"])
        email = st.text_input("E-mail de Login *", value=colab["email"])
        c1, c2 = st.columns(2)
        with c1:
            numero = st.text_input("Telefone / WhatsApp *", value=data_manager.formatar_telefone_br(colab["numero"]), placeholder="(31) 98765-4321", max_chars=15)
        with c2:
            cargo_idx = 0 if colab["cargo"] == "caixa" else 1
            cargo = st.selectbox(
                "Cargo & Nível de Acesso *",
                ["caixa", "gerente"],
                index=cargo_idx,
                format_func=lambda x: "Operador de Caixa (Salão e Cardápio)" if x == "caixa" else "Gerente Geral (Acesso Completo)"
            )
        
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        st.markdown("<span style='font-size: 0.82rem; color: #cbd5e1; font-weight: 700;'>Redefinição de Senha (Opcional):</span>", unsafe_allow_html=True)
        nova_senha = st.text_input("Nova Senha (deixe em branco para manter a atual)", type="password", placeholder="Preencha apenas se for redefinir")
        forcar_troca = st.checkbox("Exigir troca obrigatória de senha no próximo login", value=colab.get("primeiro_acesso", False))

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        btn_salvar = st.form_submit_button("Salvar Alterações", type="primary", use_container_width=True)

        if btn_salvar:
            if not nome.strip() or not email.strip() or not numero.strip():
                st.error("Nome, e-mail e telefone são campos obrigatórios.")
            elif nova_senha.strip() and len(nova_senha.strip()) < 4:
                st.error("A nova senha deve ter no mínimo 4 caracteres.")
            else:
                try:
                    data_manager.editar_colaborador(
                        usuario_id=colab["id"],
                        nome=nome,
                        email=email,
                        numero=numero,
                        cargo=cargo,
                        nova_senha=nova_senha if nova_senha.strip() else None,
                        primeiro_acesso=forcar_troca
                    )
                    st.success(f"Dados do colaborador {nome} atualizados com sucesso!")
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
            Administração de operadores de caixa, gerentes, edição de dados e redefinição de senhas com criptografia.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_btn:
    btn_c1, btn_c2 = st.columns([1.2, 1.0])
    with btn_c1:
        if st.button("+ Novo Colaborador", type="primary", use_container_width=True):
            dialog_novo_colaborador()
    with btn_c2:
        if st.button("Sincronizar Xano", use_container_width=True, help="Sincronizar e reconciliar colaboradores entre SQLite e Xano"):
            try:
                enviados = data_manager.reconciliar_colaboradores_xano()
                qtd_sync = data_manager.sincronizar_colaboradores_xano()
                st.toast(f"Paridade Xano concluída! ({enviados} reconciliados / {qtd_sync} ativos)")
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
        
        status_senha = '<span style="color: #f59e0b; font-size: 0.76rem; font-weight: 600;">Aguardando 1º Acesso</span>' if colab.get("primeiro_acesso") else '<span style="color: #34d399; font-size: 0.76rem; font-weight: 600;">Ativo (Senha Pessoal)</span>'

        me_tag = '<span style="background: rgba(255, 255, 255, 0.08); color: #e2e8f0; padding: 2px 8px; border-radius: 6px; font-size: 0.70rem; font-weight: 700; margin-left: 6px;">VOCÊ</span>' if is_me else ''

        c1, c2, c3, c4, c5 = st.columns([3.2, 2.3, 2.5, 1.0, 1.0], vertical_alignment="center")

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
            if st.button("Editar", key=f"btn_edit_colab_{colab['id']}", help="Editar todos os dados deste colaborador", use_container_width=True):
                dialog_editar_colaborador(colab)

        with c5:
            if not is_me:
                if st.button("Excluir", key=f"btn_del_colab_{colab['id']}", help="Remover acesso deste colaborador", use_container_width=True):
                    dialog_excluir_colaborador(colab)
            else:
                st.caption("Você")

        st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.06);'>", unsafe_allow_html=True)

# Rodapé Executivo
ui_components.render_footer()

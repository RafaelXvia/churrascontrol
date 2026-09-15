import importlib
import streamlit as st
import data_manager
importlib.reload(data_manager)
import ui_components
importlib.reload(ui_components)

st.set_page_config(
    page_title="Salão e Mesas - ChurrasControl",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Navbar superior unificada
ui_components.render_navbar(active_tab="salao")

if "mesa_selecionada" not in st.session_state:
    st.session_state["mesa_selecionada"] = None

# Sincroniza seleção de mesa via query param APENAS no primeiro acesso
if "mesa_id" in st.query_params and st.session_state["mesa_selecionada"] is None:
    try:
        st.session_state["mesa_selecionada"] = int(st.query_params["mesa_id"])
    except Exception:
        pass

# Modal Dialog Bonito para Abrir Nova Mesa
@st.dialog("🍽️ Abrir Nova Mesa no Salão")
def dialog_abrir_mesa():
    st.markdown("""
    <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 14px;">
        Informe o número da mesa e a quantidade de clientes para iniciar o atendimento:
    </div>
    """, unsafe_allow_html=True)
    
    f_num = st.number_input("Número da Mesa", min_value=1, step=1, value=1, key="dlg_num_mesa")
    f_pax = st.number_input("Quantidade de Pessoas (Pax)", min_value=1, step=1, value=2, key="dlg_pax_mesa")
    
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Confirmar e Abrir", type="primary", use_container_width=True, key="btn_confirm_abrir_mesa"):
            try:
                res = data_manager.abrir_mesa(int(f_num), int(f_pax))
                st.session_state["mesa_selecionada"] = res["comanda_id"]
                st.rerun()
            except ValueError as err:
                st.error(str(err))
    with c2:
        if st.button("Cancelar", use_container_width=True, key="btn_cancel_dlg"):
            st.rerun()

# Operações locais instantâneas
mesas = data_manager.listar_mesas()
produtos = data_manager.listar_produtos()

# Cabeçalho da Página
st.markdown("""
<div style="margin-bottom: 1rem;">
    <h2 style="margin: 0; font-size: 1.55rem; font-weight: 800; color: #ffffff;">
        Salão & Gestão de Comandas
    </h2>
    <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.88rem;">
        Terminal de atendimento em tempo real, controle de ocupação e lançamento ágil de pedidos.
    </p>
</div>
""", unsafe_allow_html=True)

# Layout em duas colunas responsivas: Salão (7) e Comanda (5)
col_salao, col_comanda = st.columns([7, 5], gap="medium")

# ================= COLUNA 1: MAPA DE MESAS =================
with col_salao:
    c_m1, c_m2 = st.columns([3, 2])
    with c_m1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
            <h3 style="margin: 0; font-size: 1.2rem; font-weight: 700; color: #f8fafc;">
                Mesas Ativas
            </h3>
            <span style="font-size: 0.78rem; color: #94a3b8; background: rgba(255,255,255,0.05); padding: 4px 10px; border-radius: 6px;">
                Total: <b>{len(mesas)}</b> mesa(s)
            </span>
        </div>
        """, unsafe_allow_html=True)
    with c_m2:
        if st.button("➕ Abrir Nova Mesa", type="primary", use_container_width=True, key="btn_abrir_nova_mesa"):
            dialog_abrir_mesa()

    if not mesas:
        st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px dashed #334155; border-radius: 12px; padding: 28px; text-align: center; margin-top: 10px;">
            <div style="font-size: 2rem;">🍽️</div>
            <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-top: 6px;">Nenhuma mesa aberta no salão</div>
            <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">Clique em "➕ Abrir Nova Mesa" acima para iniciar o primeiro atendimento.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for i in range(0, len(mesas), 2):
            pair = mesas[i:i+2]
            cols = st.columns(2)
            for col_idx, m in enumerate(pair):
                with cols[col_idx]:
                    is_selected = (st.session_state.get("mesa_selecionada") == m["comanda_id"])
                    card_class = "cc-mesa-card cc-mesa-card-active" if is_selected else "cc-mesa-card"
                    active_style = "border-color: #f59e0b !important; box-shadow: 0 12px 28px -6px rgba(245, 158, 11, 0.35) !important;" if is_selected else ""
                    badge_status = '<span style="background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); padding: 2px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 700;">OCUPADA</span>'
                    sel_indicator = '<span style="color: #f59e0b; font-size: 0.75rem; font-weight: 700; margin-left: 6px;">● SELECIONADA</span>' if is_selected else ''
                    action_text = "Comanda Selecionada ➔" if is_selected else "Clique para abrir comanda ➔"

                    st.markdown(f"""
                    <div class="{card_class}" style="{active_style}" data-comanda-id="{m['comanda_id']}">
                        <div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-weight: 800; color: #f8fafc; font-size: 1.15rem;">
                                    🍽️ MESA {m['numero_mesa']} {sel_indicator}
                                </span>
                                {badge_status}
                            </div>
                            <div style="color: #94a3b8; font-size: 0.82rem; margin: 6px 0 0 0;">
                                👥 Capacidade: {m.get('capacidade', 1)} pessoa(s)
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: flex-end; padding-bottom: 2px;">
                            <div>
                                <div style="font-size: 0.70rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.04em;">Subtotal da Mesa</div>
                                <div style="color: #fbbf24; font-weight: 800; font-size: 1.35rem; line-height: 1.2;">
                                    R$ {float(m.get('total_atual', 0.0)):,.2f}
                                </div>
                            </div>
                            <span style="font-size: 0.75rem; color: #f59e0b; font-weight: 600;">{action_text}</span>
                        </div>
                    </div>
                    <div class="cc-mesa-btn-anchor" style="display: none;"></div>
                    """, unsafe_allow_html=True)
                    if st.button("", key=f"btn_sel_mesa_{m['id']}", use_container_width=True):
                        st.session_state["mesa_selecionada"] = m["comanda_id"]
                        st.rerun()

        st.html("""
        <script>
        (function() {
            function bindMesaClicks() {
                document.querySelectorAll('.cc-mesa-card').forEach(function(card) {
                    if (card.dataset.boundClick) return;
                    card.dataset.boundClick = 'true';
                    card.addEventListener('click', function(ev) {
                        const col = card.closest('[data-testid="stColumn"]');
                        if (col) {
                            const btn = col.querySelector('button');
                            if (btn) btn.click();
                        }
                    });
                });
            }
            bindMesaClicks();
            setTimeout(bindMesaClicks, 300);
            setTimeout(bindMesaClicks, 800);
        })();
        </script>
        """)

# ================= COLUNA 2: PAINEL DA COMANDA =================
with col_comanda:
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <h3 style="margin: 0; font-size: 1.2rem; font-weight: 700; color: #f8fafc;">
            Painel da Comanda
        </h3>
    </div>
    """, unsafe_allow_html=True)

    sel_id = st.session_state.get("mesa_selecionada")
    if not sel_id:
        st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px dashed #334155; border-radius: 12px; padding: 28px; text-align: center;">
            <div style="font-size: 2rem;">👈</div>
            <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-top: 6px;">Nenhuma mesa selecionada</div>
            <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">Clique em qualquer card de mesa ao lado para selecionar e gerenciar o consumo.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        detalhes = data_manager.obter_comanda_detalhes(sel_id)
        if not detalhes:
            st.warning("Comanda não localizada ou finalizada.")
            st.session_state["mesa_selecionada"] = None
        else:
            comanda = detalhes.get("comanda", {})
            itens = detalhes.get("itens", [])
            total_comanda = float(detalhes.get("total", 0.0))

            # Header da Comanda com Design Sofisticado
            st.markdown(f"""
            <div class="cc-card" style="border-color: rgba(245, 158, 11, 0.4); margin-bottom: 14px; padding: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="color: #fbbf24; font-weight: 800; font-size: 1.2rem;">
                            Comanda #{comanda.get('id')} — Mesa {comanda.get('numero_mesa')}
                        </span>
                        <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 2px;">
                            Aberta às: {str(comanda.get('data_abertura', ''))[:16].replace('T', ' ')}
                        </div>
                    </div>
                    <span style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); padding: 4px 10px; border-radius: 8px; font-size: 0.8rem; font-weight: 600;">
                        👥 {comanda.get('qtd_pessoas', 1)} pax
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Lançamento Rápido de Itens no Pedido
            with st.expander("🍽️ Lançar Produto no Pedido", expanded=True):
                if not produtos:
                    st.warning("Nenhum produto cadastrado no cardápio.")
                else:
                    opcoes = {f"#{p['codigo_pdv']} - {p['nome']} (R$ {float(p['preco_unitario']):.2f})": p for p in produtos}
                    with st.form(f"form_item_{sel_id}"):
                        p_selecionado = st.selectbox("Selecione o Item", list(opcoes.keys()))
                        c_it1, c_it2 = st.columns([1, 2])
                        with c_it1:
                            qtd = st.number_input("Quantidade", min_value=1, value=1, step=1)
                        with c_it2:
                            obs = st.text_input("Observação / Ponto", placeholder="Ex: mal passada, sem cebola")
                        btn_lancar = st.form_submit_button("➕ Adicionar à Comanda", type="primary", use_container_width=True)

                        if btn_lancar:
                            prod_obj = opcoes[p_selecionado]
                            data_manager.adicionar_item_comanda(
                                comanda_id=sel_id,
                                produto_id=prod_obj["id"],
                                quantidade=int(qtd),
                                observacao=obs.strip()
                            )
                            st.success(f"✓ {prod_obj['nome']} adicionado!")
                            st.rerun()

            # Lista de Itens Consumidos
            st.markdown("""
            <div style="margin: 1rem 0 0.5rem 0; font-weight: 700; color: #f8fafc; font-size: 0.95rem;">
                📋 Itens Registrados na Comanda
            </div>
            """, unsafe_allow_html=True)

            if not itens:
                st.caption("Nenhum item lançado até o momento.")
            else:
                for it in itens:
                    it_col1, it_col2, it_col3 = st.columns([6, 3, 2])
                    with it_col1:
                        obs_html = f'<div style="font-size: 0.75rem; color: #f59e0b; margin-top: 2px;">💬 {it["observacao"]}</div>' if it.get("observacao") else ''
                        st.markdown(f"""
                        <div style="line-height: 1.2;">
                            <span style="font-weight: 700; color: #ffffff;">{it['quantidade']}x</span>
                            <span style="color: #e2e8f0; margin-left: 4px;">{it['produto_nome']}</span>
                            {obs_html}
                        </div>
                        """, unsafe_allow_html=True)
                    with it_col2:
                        st.markdown(f"<div style='font-weight: 700; color: #fbbf24; text-align: right;'>R$ {float(it['subtotal']):.2f}</div>", unsafe_allow_html=True)
                    with it_col3:
                        if st.button("✖", key=f"rm_it_{it['id']}", help="Remover item", use_container_width=True):
                            data_manager.remover_item_comanda(it["id"])
                            st.rerun()
                    st.divider()

            # Painel de Fechamento de Conta
            st.markdown("""
            <div style="margin: 1rem 0 0.5rem 0; font-weight: 700; color: #f8fafc; font-size: 0.95rem;">
                💳 Fechamento & Pagamento
            </div>
            """, unsafe_allow_html=True)

            taxa_servico = st.checkbox("Aplicar Taxa de Serviço Sugerida (10%)", value=True)
            total_final = total_comanda * 1.10 if taxa_servico else total_comanda
            pax = int(comanda.get("qtd_pessoas", 1)) or 1
            por_pessoa = total_final / pax

            st.markdown(f"""
            <div style="background: rgba(17, 24, 39, 0.9); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 14px 18px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #94a3b8; margin-bottom: 4px;">
                    <span>Consumo Líquido:</span>
                    <span>R$ {total_comanda:.2f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #94a3b8; margin-bottom: 8px;">
                    <span>Serviço (10%):</span>
                    <span>R$ {(total_comanda * 0.10 if taxa_servico else 0.0):.2f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: baseline; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 8px;">
                    <span style="font-weight: 700; font-size: 1.1rem; color: #ffffff;">Total a Pagar:</span>
                    <span style="font-weight: 800; font-size: 1.45rem; color: #f59e0b;">R$ {total_final:.2f}</span>
                </div>
                <div style="text-align: right; font-size: 0.8rem; color: #64748b; margin-top: 4px;">
                    Divisão por pessoa ({pax} pax): <b style="color: #94a3b8;">R$ {por_pessoa:.2f}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

            c_fc1, c_fc2 = st.columns(2)
            with c_fc1:
                if st.button("✅ Confirmar Pagamento & Liberar Mesa", type="primary", use_container_width=True):
                    data_manager.fechar_comanda(sel_id, total_final, taxa_servico)
                    st.session_state["mesa_selecionada"] = None
                    st.query_params.clear()
                    st.success("✓ Comanda encerrada e mesa liberada!")
                    st.rerun()
            with c_fc2:
                with st.popover("❌ Cancelar Comanda", use_container_width=True):
                    st.caption("⚠️ Operação Crítica")
                    st.write("Esta ação cancelará todos os lançamentos e liberará a mesa física.")
                    confirmar_cancel = st.checkbox("Confirmar cancelamento", key=f"chk_canc_{sel_id}")
                    if st.button("Executar Cancelamento", type="secondary", disabled=not confirmar_cancel, use_container_width=True):
                        data_manager.cancelar_comanda(sel_id)
                        st.session_state["mesa_selecionada"] = None
                        st.query_params.clear()
                        st.rerun()

# Rodapé Executivo
ui_components.render_footer()

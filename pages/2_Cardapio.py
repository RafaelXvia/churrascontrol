import streamlit as st
import data_manager
import ui_components

st.set_page_config(
    page_title="Cardápio Comercial - ChurrasControl",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Navbar superior unificada
ui_components.render_navbar(active_tab="cardapio")

# Cabeçalho da Página
c_title, c_act = st.columns([3, 1])
with c_title:
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="margin: 0; font-size: 1.5rem; font-weight: 800; color: #ffffff;">
            Cardápio & Catálogo de Produtos
        </h2>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.88rem;">
            Gestão de produtos do PDV, precificação comercial e controle de códigos de venda.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Formulário para Cadastro de Novo Produto
with st.expander("➕ Cadastrar Novo Produto no Catálogo", expanded=False):
    with st.form("form_novo_prod"):
        c1, c2 = st.columns(2)
        with c1:
            cod_pdv = st.text_input("Código PDV", placeholder="Ex: 105", help="Código de identificação rápida no PDV")
            nome = st.text_input("Nome do Produto", placeholder="Ex: Costela Bovina no Bafo (600g)")
        with c2:
            categoria = st.selectbox("Categoria", ["Carnes", "Comida", "Entradas", "Bebidas", "Sobremesas", "Promoção", "Geral"])
            preco = st.number_input("Preço Unitário (R$)", min_value=0.01, value=35.00, step=0.50)

        btn_salvar = st.form_submit_button("Salvar Produto no Catálogo", type="primary", use_container_width=True)
        if btn_salvar:
            if not cod_pdv.strip() or not nome.strip():
                st.error("Informe o Código PDV e o Nome do produto.")
            else:
                try:
                    data_manager.criar_produto(cod_pdv, nome, categoria, preco)
                    st.success(f"✓ Produto '{nome}' cadastrado com sucesso!")
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# Barra de Pesquisa e Filtros
c_b1, c_b2 = st.columns([5, 1])
with c_b1:
    busca = st.text_input("🔍 Pesquisar no cardápio", placeholder="Digite nome, categoria ou código PDV...")
with c_b2:
    st.write("")
    st.write("")
    if st.button("Limpar", use_container_width=True):
        busca = ""
        st.rerun()

produtos = data_manager.listar_produtos(busca)

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; margin: 1.25rem 0 0.75rem 0;">
    <h3 style="margin: 0; font-size: 1.2rem; font-weight: 700; color: #f8fafc;">
        Produtos Cadastrados ({len(produtos)} itens)
    </h3>
</div>
""", unsafe_allow_html=True)

if not produtos:
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.6); border: 1px dashed #334155; border-radius: 12px; padding: 28px; text-align: center;">
        <div style="font-size: 2rem;">🔍</div>
        <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-top: 6px;">Nenhum produto encontrado</div>
        <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">Tente pesquisar por outro termo ou cadastre um novo item acima.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    categorias = sorted(list(set(p.get("categoria", "Geral") for p in produtos)))

    for cat in categorias:
        itens_cat = [p for p in produtos if p.get("categoria") == cat]
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 8px; margin: 1.25rem 0 0.5rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 6px;">
            <span style="font-size: 1.05rem; font-weight: 700; color: #f59e0b;">🏷️ {cat}</span>
            <span style="font-size: 0.75rem; color: #94a3b8; background: rgba(255,255,255,0.05); padding: 2px 8px; border-radius: 4px;">{len(itens_cat)} item(ns)</span>
        </div>
        """, unsafe_allow_html=True)

        for p in itens_cat:
            with st.container():
                p_c1, p_c2, p_c3, p_c4 = st.columns([2, 5, 2, 2])
                with p_c1:
                    st.markdown(f"""
                    <span style="background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.1); padding: 3px 8px; border-radius: 6px; font-weight: 700; font-size: 0.82rem; color: #cbd5e1;">
                        CÓD {p['codigo_pdv']}
                    </span>
                    """, unsafe_allow_html=True)
                with p_c2:
                    st.markdown(f"<span style='font-weight: 600; color: #f8fafc; font-size: 0.95rem;'>{p['nome']}</span>", unsafe_allow_html=True)
                with p_c3:
                    st.markdown(f"<span style='font-weight: 700; color: #fbbf24; font-size: 1.05rem;'>R$ {float(p['preco_unitario']):,.2f}</span>", unsafe_allow_html=True)
                with p_c4:
                    with st.popover("⚙️ Opções"):
                        st.caption(f"Editar Produto #{p['codigo_pdv']}")
                        with st.form(f"edit_{p['id']}"):
                            novo_nome = st.text_input("Nome", value=p["nome"])
                            cat_opcoes = ["Carnes", "Comida", "Entradas", "Bebidas", "Sobremesas", "Promoção", "Geral"]
                            idx_cat = cat_opcoes.index(p["categoria"]) if p["categoria"] in cat_opcoes else 0
                            nova_cat = st.selectbox("Categoria", cat_opcoes, index=idx_cat)
                            novo_preco = st.number_input("Preço Unitário", min_value=0.01, value=float(p["preco_unitario"]), step=0.50)
                            if st.form_submit_button("Atualizar Informações", type="primary"):
                                data_manager.atualizar_produto(p["id"], str(p["codigo_pdv"]), novo_nome, nova_cat, novo_preco)
                                st.success("Atualizado com sucesso!")
                                st.rerun()

                        st.divider()
                        if st.button("🗑️ Excluir Produto", key=f"del_p_{p['id']}", use_container_width=True):
                            data_manager.excluir_produto(p["id"])
                            st.rerun()
                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

# Rodapé Executivo
ui_components.render_footer()

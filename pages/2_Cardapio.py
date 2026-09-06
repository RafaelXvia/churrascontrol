import streamlit as st
import data_manager
import ui_components

st.set_page_config(
    page_title="Gestão de Cardápio & PDV - ChurrasControl",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Navbar superior unificada
ui_components.render_navbar(active_tab="cardapio")

# CSS personalizado para o Painel de Gestão e Imagens Seguras do Imgur
st.markdown("""
<meta name="referrer" content="no-referrer">
<style>
    .btn-cardapio-digital {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(217, 119, 6, 0.4) !important;
    }
    .img-thumb-container {
        width: 52px;
        height: 52px;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.12);
        background: #0f172a;
    }
    .img-thumb {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho da Página com Botão de Abertura da Tela Separada
c_title, c_actions = st.columns([3, 2.5], vertical_alignment="center")

with c_title:
    st.markdown("""
    <div style="margin-bottom: 0.5rem;">
        <h2 style="margin: 0; font-size: 1.55rem; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 10px;">
            <span>📋</span> Gestão de Cardápio & Catálogo PDV
        </h2>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.88rem;">
            Administração de produtos, códigos PDV, estoque e precificação comercial.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c_actions:
    c_btn1, c_btn2, c_btn3 = st.columns([2.4, 1.6, 1.4])
    with c_btn1:
        # Botão para abrir a tela separada de Cardápio Digital do Cliente
        if st.button("🍽️ Abrir Cardápio Digital", key="btn_open_cardapio_dig", type="primary", use_container_width=True, help="Abre a tela separada com visual de restaurante / delivery"):
            st.switch_page("pages/4_Cardapio_Digital.py")
    with c_btn2:
        if st.button("🔄 Puxar Xano", key="btn_sync_xano", use_container_width=True, help="Sincroniza fotos reais e dados da tabela PRODUTO do Xano"):
            qtd = data_manager.sincronizar_produtos_xano()
            st.success(f"{qtd} produtos sincronizados do Xano!")
            st.rerun()
    with c_btn3:
        with st.popover("📱 QR Code", use_container_width=True):
            share_url = "http://localhost:8501/Cardapio_Digital"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=240x240&margin=10&data={share_url}"
            st.image(qr_url, caption="QR Code da Mesa", use_container_width=True)
            st.code(share_url, language="text")

# Formulário para Cadastro de Novo Produto (Pede TUDO da tabela PRODUTO)
with st.expander("➕ Cadastrar Novo Produto no Catálogo (Cadastro Completo)", expanded=False):
    st.caption("Preencha todos os atributos técnicos e comerciais mapeados na tabela **PRODUTO**.")
    with st.form("form_novo_prod_completo"):
        c1, c2, c3 = st.columns([1.5, 3, 2])
        with c1:
            cod_pdv = st.text_input("Código PDV *", placeholder="Ex: 109", help="Identificador único rápido no terminal PDV")
        with c2:
            nome = st.text_input("Nome do Produto *", placeholder="Ex: Picanha Premium Grelhada na Parrilla (600g)")
        with c3:
            categoria = st.selectbox("Categoria *", ["Carnes", "Comida", "Entradas", "Bebidas", "Sobremesas", "Promoção", "Geral"])

        c4, c5 = st.columns([1.5, 2.5])
        with c4:
            preco = st.number_input("Preço de Venda (R$) *", min_value=0.01, value=45.00, step=0.50)
            qtd_disp = st.number_input("Estoque Disponível (qtd_disp)", min_value=0, value=20, step=1, help="Quantidade em estoque para venda")
        with c5:
            url_imagem = st.text_input("URL da Imagem / Foto do Produto (Imgur)", placeholder="https://i.imgur.com/...", help="Link da foto do prato")

        descricao = st.text_area(
            "Descrição Comercial & Gastronômica",
            placeholder="Ex: Corte nobre com gordura selecionada, assado na brasa forte com flor de sal e servido com farofa crocante e chimichurri artesanal.",
            help="Texto apresentado no cardápio digital do cliente e impresso na comanda"
        )

        c_sw1, c_sw2 = st.columns(2)
        with c_sw1:
            precisa_produzir = st.checkbox("👨‍🍳 Requer Produção / Cozinha (precisa_produzir)", value=True, help="Se marcado, despacha ordem para a grelha/cozinha")
        with c_sw2:
            disponivel = st.checkbox("🟢 Disponível para Venda no Cardápio (disponivel)", value=True, help="Desmarque caso o produto esteja temporariamente pausado")

        btn_salvar = st.form_submit_button("💾 Salvar Produto Completo no Catálogo", type="primary", use_container_width=True)
        if btn_salvar:
            if not cod_pdv.strip() or not nome.strip():
                st.error("Por favor, preencha o Código PDV e o Nome do produto.")
            else:
                try:
                    data_manager.criar_produto(
                        codigo_pdv=cod_pdv,
                        nome=nome,
                        categoria=categoria,
                        preco_unitario=preco,
                        descricao=descricao,
                        url_imagem=url_imagem,
                        qtd_disp=int(qtd_disp),
                        precisa_produzir=precisa_produzir,
                        disponivel=disponivel
                    )
                    st.success(f"✓ Produto '{nome}' cadastrado com sucesso com todos os atributos!")
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# Barra de Pesquisa e Filtros da Visão de Lista
c_b1, c_b2 = st.columns([5, 1])
with c_b1:
    busca = st.text_input("🔍 Pesquisar produtos no catálogo", placeholder="Digite nome, categoria, código PDV ou ingrediente...", label_visibility="collapsed")
with c_b2:
    if st.button("Limpar Filtro", use_container_width=True):
        busca = ""
        st.rerun()

produtos = data_manager.listar_produtos(busca)

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; margin: 1rem 0 0.5rem 0;">
    <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #f8fafc;">
        Produtos Cadastrados ({len(produtos)} itens disponíveis)
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
    categorias = sorted(list(set(p.get("categoria", "Geral") for p in produtos if p.get("categoria"))))

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
                p_img, p_c1, p_c2, p_c3, p_c4 = st.columns([1, 1.5, 4.5, 2, 2], vertical_alignment="center")
                
                with p_img:
                    thumb_url = p.get("url_imagem")
                    if not thumb_url or thumb_url.strip() == "":
                        thumb_url = "https://images.unsplash.com/photo-1544025162-d76694265947?w=100&auto=format&fit=crop&q=80"
                    
                    st.markdown(f"""
                    <div class="img-thumb-container">
                        <img src="{thumb_url}" referrerpolicy="no-referrer" class="img-thumb" alt="{p['nome']}" onerror="this.src='https://images.unsplash.com/photo-1544025162-d76694265947?w=100&auto=format&fit=crop&q=80'">
                    </div>
                    """, unsafe_allow_html=True)

                with p_c1:
                    st.markdown(f"""
                    <span style="background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.1); padding: 3px 8px; border-radius: 6px; font-weight: 700; font-size: 0.82rem; color: #cbd5e1;">
                        CÓD {p['codigo_pdv']}
                    </span>
                    """, unsafe_allow_html=True)

                with p_c2:
                    disp_badge = "🟢 Disponível" if p.get("disponivel", 1) else "🔴 Pausado"
                    prod_badge = "🔥 Produção" if p.get("precisa_produzir", 1) else "⚡ Direto"
                    st.markdown(f"""
                    <div>
                        <span style='font-weight: 600; color: #f8fafc; font-size: 0.98rem;'>{p['nome']}</span>
                        <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 2px;">
                            {disp_badge} • {prod_badge} • Estoque: <strong>{p.get('qtd_disp', 0)} un</strong>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with p_c3:
                    st.markdown(f"<span style='font-weight: 700; color: #fbbf24; font-size: 1.05rem;'>R$ {float(p['preco_unitario']):,.2f}</span>", unsafe_allow_html=True)

                with p_c4:
                    with st.popover("⚙️ Opções"):
                        st.caption(f"Editar Produto #{p['codigo_pdv']}")
                        with st.form(f"edit_{p['id']}"):
                            novo_cod = st.text_input("Código PDV", value=str(p["codigo_pdv"]))
                            novo_nome = st.text_input("Nome", value=p["nome"])
                            cat_opcoes = ["Carnes", "Comida", "Entradas", "Bebidas", "Sobremesas", "Promoção", "Geral"]
                            idx_cat = cat_opcoes.index(p["categoria"]) if p["categoria"] in cat_opcoes else 0
                            nova_cat = st.selectbox("Categoria", cat_opcoes, index=idx_cat)
                            novo_preco = st.number_input("Preço Unitário (R$)", min_value=0.01, value=float(p["preco_unitario"]), step=0.50)
                            nova_desc = st.text_area("Descrição", value=p.get("descricao", ""))
                            nova_foto = st.text_input("URL da Foto (Imgur)", value=p.get("url_imagem", ""))
                            novo_estoque = st.number_input("Estoque (qtd_disp)", min_value=0, value=int(p.get("qtd_disp", 10)))
                            novo_prod = st.checkbox("Requer Produção (precisa_produzir)", value=bool(p.get("precisa_produzir", 1)))
                            novo_disp = st.checkbox("Disponível no Cardápio (disponivel)", value=bool(p.get("disponivel", 1)))

                            if st.form_submit_button("Atualizar Informações", type="primary", use_container_width=True):
                                try:
                                    data_manager.atualizar_produto(
                                        produto_id=p["id"],
                                        codigo_pdv=novo_cod,
                                        nome=novo_nome,
                                        categoria=nova_cat,
                                        preco_unitario=novo_preco,
                                        descricao=nova_desc,
                                        url_imagem=nova_foto,
                                        qtd_disp=int(novo_estoque),
                                        precisa_produzir=novo_prod,
                                        disponivel=novo_disp
                                    )
                                    st.success("Atualizado com sucesso!")
                                    st.rerun()
                                except ValueError as e:
                                    st.error(str(e))

                        st.divider()
                        confirma_del = st.checkbox("Confirmar exclusão deste produto", key=f"chk_del_{p['id']}")
                        if st.button("🗑️ Excluir Produto", key=f"del_p_{p['id']}", disabled=not confirma_del, use_container_width=True):
                            data_manager.excluir_produto(p["id"])
                            st.rerun()

                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

# Rodapé Executivo
ui_components.render_footer()


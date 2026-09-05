import streamlit as st
import data_manager
import ui_components

st.set_page_config(
    page_title="Cardápio Comercial & Digital - ChurrasControl",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Navbar superior unificada
ui_components.render_navbar(active_tab="cardapio")

# CSS personalizado para o Cardápio Delivery & Experiência QR Code
st.markdown("""
<style>
    /* Estilos do Modo Delivery */
    .delivery-hero {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%),
                    url('https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=1200&auto=format&fit=crop&q=80');
        background-size: cover;
        background-position: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 12px 35px -8px rgba(0, 0, 0, 0.6);
    }
    .delivery-badge-open {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.18);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
    }
    .delivery-badge-tag {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #cbd5e1;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 6px;
    }
    .card-delivery {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .card-delivery:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 28px -6px rgba(0, 0, 0, 0.65);
        border-color: rgba(245, 158, 11, 0.4);
    }
    .card-img-container {
        position: relative;
        width: 100%;
        height: 175px;
        overflow: hidden;
        background: #0f172a;
    }
    .card-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.35s ease;
    }
    .card-delivery:hover .card-img {
        transform: scale(1.05);
    }
    .card-badge-float {
        position: absolute;
        top: 10px;
        right: 10px;
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #f59e0b;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
    }
    .card-body {
        padding: 16px;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }
    .card-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 6px 0;
        line-height: 1.25;
    }
    .card-desc {
        font-size: 0.82rem;
        color: #94a3b8;
        line-height: 1.4;
        margin-bottom: 12px;
        flex-grow: 1;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .card-footer-box {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: auto;
        padding-top: 10px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
    }
    .card-price {
        font-size: 1.2rem;
        font-weight: 800;
        color: #fbbf24;
    }
</style>
""", unsafe_allow_html=True)

# Sincronização de visualização com query params (?view=delivery ou ?view=lista)
query_view = st.query_params.get("view", "lista").lower()
default_index = 1 if query_view in ["delivery", "cardapio"] else 0

# Cabeçalho da Página e Alternador de Modo (Switch)
c_title, c_switch = st.columns([3, 2], vertical_alignment="center")

with c_title:
    st.markdown("""
    <div style="margin-bottom: 0.5rem;">
        <h2 style="margin: 0; font-size: 1.55rem; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 10px;">
            <span>📋</span> Cardápio Comercial & Catálogo
        </h2>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.88rem;">
            Gestão operacional de produtos, paridade completa com banco de dados e visualização digital de restaurante.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c_switch:
    # Switch de Modo de Visualização
    modo_selecionado = st.radio(
        "Modo de Visualização",
        options=["📋 Modo Lista (Gestão PDV)", "📱 Modo Cardápio Digital (Delivery & QR Code)"],
        index=default_index,
        horizontal=True,
        label_visibility="collapsed"
    )

is_delivery_mode = "Delivery" in modo_selecionado

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
            url_imagem = st.text_input("URL da Imagem / Foto do Produto", placeholder="https://images.unsplash.com/...", help="Link direto da imagem do prato")

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

# =========================================================================
# SEÇÃO 1: MODO CARDÁPIO DIGITAL / DELIVERY (EXPERIÊNCIA DE RESTAURANTE)
# =========================================================================
if is_delivery_mode:
    # URL de compartilhamento do Cardápio Digital
    share_url = "http://localhost:8501/Cardapio?view=delivery"
    qr_code_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=260x260&margin=10&data={share_url}"

    # Banner Gastronômico do Restaurante
    st.markdown(f"""
    <div class="delivery-hero">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    <span class="delivery-badge-open">● Aberto Agora</span>
                    <span class="delivery-badge-tag">🔥 Parrilla & Defumados</span>
                    <span class="delivery-badge-tag">⭐ 4.9 (1.4k avaliações)</span>
                </div>
                <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #ffffff; letter-spacing: -0.03em;">
                    ChurrasControl • Parrilla Bar & Smokehouse
                </h1>
                <p style="margin: 6px 0 0 0; color: #cbd5e1; font-size: 0.95rem; max-width: 650px;">
                    Cortes nobres preparados na brasa viva, acompanhamentos mineiros tradicionais, cervejas trincando e sobremesas artesanais.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Barra de Ações: Compartilhamento, QR Code e Pesquisa
    c_sh1, c_sh2 = st.columns([3.5, 1.5], vertical_alignment="center")
    with c_sh1:
        busca_cardapio = st.text_input("🔍 Buscar no cardápio...", placeholder="O que você deseja saborear hoje? (Ex: Picanha, Chopp, Feijoada)", label_visibility="collapsed")
    with c_sh2:
        with st.popover("📱 Compartilhar / QR Code", use_container_width=True):
            st.markdown("""
            <div style="text-align: center; padding: 4px 0;">
                <h4 style="margin: 0 0 6px 0; color: #f59e0b; font-size: 1.1rem; font-weight: 800;">
                    📲 Cardápio Digital na Mesa
                </h4>
                <p style="font-size: 0.82rem; color: #94a3b8; margin-bottom: 14px;">
                    Aponte a câmera do seu smartphone para escanear e abrir o cardápio interativo direto no celular!
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Imagem do QR Code
            st.image(qr_code_api_url, caption="QR Code Oficial da Mesa / Delivery", use_container_width=True)

            st.markdown(f"""
            <div style="margin-top: 10px; background: rgba(0,0,0,0.3); border: 1px dashed rgba(255,255,255,0.15); border-radius: 8px; padding: 10px; word-break: break-all; font-size: 0.78rem; color: #cbd5e1;">
                <strong>Link Compartilhável:</strong><br>
                <code>{share_url}</code>
            </div>
            """, unsafe_allow_html=True)
            st.caption("Dica: Copie o link acima para enviar no WhatsApp ou gerar displays impressos nas mesas.")

    # Obter produtos cadastrados
    produtos_todos = data_manager.listar_produtos(busca=busca_cardapio)

    # Filtros de Categorias em Chips
    categorias_disponiveis = ["Todas"] + sorted(list(set(p.get("categoria", "Geral") for p in produtos_todos)))
    cat_filtro = st.pills("Categorias do Cardápio", options=categorias_disponiveis, default="Todas", label_visibility="collapsed")

    if cat_filtro and cat_filtro != "Todas":
        produtos_filtrados = [p for p in produtos_todos if p.get("categoria") == cat_filtro]
    else:
        produtos_filtrados = produtos_todos

    if not produtos_filtrados:
        st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px dashed #334155; border-radius: 16px; padding: 40px; text-align: center; margin-top: 20px;">
            <div style="font-size: 2.5rem;">🍽️</div>
            <h3 style="color: #ffffff; margin: 10px 0 4px 0;">Nenhum item encontrado</h3>
            <p style="color: #94a3b8; font-size: 0.9rem;">Tente pesquisar por outro termo ou selecione outra categoria.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Mesas abertas para permitir lançar pedido direto no modo salão/delivery
        mesas_ativas = [m for m in data_manager.listar_mesas() if m.get("comanda_ativa_id")]

        # Renderização em Grid de 3 Colunas (Mobile e Desktop Friendly)
        cols_per_row = 3
        for i in range(0, len(produtos_filtrados), cols_per_row):
            row_items = produtos_filtrados[i:i + cols_per_row]
            cols = st.columns(cols_per_row)

            for col_idx, p in enumerate(row_items):
                with cols[col_idx]:
                    img_url = p.get("url_imagem") or "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80"
                    badge_prod = "🔥 Na Brasa" if p.get("precisa_produzir") else "⚡ Pronta Entrega"
                    badge_disp = f"⚠️ {p.get('qtd_disp')} un." if p.get("qtd_disp", 0) <= 5 else f"Estoque: {p.get('qtd_disp')} un."
                    is_indisponivel = (p.get("disponivel", 1) == 0)

                    # Card Visual do Produto
                    st.markdown(f"""
                    <div class="card-delivery" style="{'opacity: 0.6;' if is_indisponivel else ''}">
                        <div class="card-img-container">
                            <img src="{img_url}" class="card-img" alt="{p['nome']}" onerror="this.src='https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80'">
                            <span class="card-badge-float">{badge_prod}</span>
                        </div>
                        <div class="card-body">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <span style="font-size: 0.72rem; color: #94a3b8; background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px;">
                                    🏷️ CÓD {p['codigo_pdv']} • {p['categoria']}
                                </span>
                                <span style="font-size: 0.72rem; color: {'#ef4444' if is_indisponivel else '#10b981'}; font-weight: 700;">
                                    {'ESGOTADO' if is_indisponivel else badge_disp}
                                </span>
                            </div>
                            <h4 class="card-title">{p['nome']}</h4>
                            <p class="card-desc">{p.get('descricao') or 'Prato exclusivo preparado com ingredientes frescos e seleção artesanal da casa.'}</p>
                            <div class="card-footer-box">
                                <span class="card-price">R$ {float(p['preco_unitario']):,.2f}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Botão para Lançar na Comanda / Pedir
                    with st.popover(f"🍽️ Pedir #{p['codigo_pdv']}", use_container_width=True):
                        st.markdown(f"**Lançar Pedido: {p['nome']}**")
                        st.caption(f"Valor Unitário: R$ {float(p['preco_unitario']):,.2f}")

                        if not mesas_ativas:
                            st.warning("Nenhuma mesa aberta no salão no momento. Abra uma mesa na página 'Salão & Mesas' para lançar pedidos.")
                        else:
                            opcoes_mesas = {f"Mesa {m['numero_mesa']} (Comanda #{m['comanda_ativa_id']})": m for m in mesas_ativas}
                            mesa_sel = st.selectbox("Selecione a Mesa de Destino", list(opcoes_mesas.keys()), key=f"sel_m_{p['id']}")
                            qtd_pedido = st.number_input("Quantidade", min_value=1, max_value=99, value=1, key=f"qtd_m_{p['id']}")
                            obs_pedido = st.text_input("Observação / Ponto", placeholder="Ex: ao ponto, sem cebola", key=f"obs_m_{p['id']}")

                            if st.button("✓ Confirmar Pedido na Mesa", key=f"btn_ped_{p['id']}", type="primary", use_container_width=True):
                                mesa_obj = opcoes_mesas[mesa_sel]
                                data_manager.adicionar_item_comanda(
                                    comanda_id=mesa_obj["comanda_ativa_id"],
                                    produto_id=p["id"],
                                    quantidade=int(qtd_pedido),
                                    observacao=obs_pedido
                                )
                                st.success(f"✓ {qtd_pedido}x '{p['nome']}' lançado na Mesa {mesa_obj['numero_mesa']}!")
                                st.rerun()

                    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# =========================================================================
# SEÇÃO 2: MODO LISTA (GESTÃO OPERACIONAL DE PDV & CADASTRO)
# =========================================================================
else:
    # Barra de Pesquisa e Filtros da Visão de Lista
    c_b1, c_b2 = st.columns([5, 1])
    with c_b1:
        busca = st.text_input("🔍 Pesquisar produtos no cardápio", placeholder="Digite nome, categoria, código PDV ou ingrediente...", label_visibility="collapsed")
    with c_b2:
        if st.button("Limpar Filtro", use_container_width=True):
            busca = ""
            st.rerun()

    produtos = data_manager.listar_produtos(busca)

    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin: 1.25rem 0 0.75rem 0;">
        <h3 style="margin: 0; font-size: 1.2rem; font-weight: 700; color: #f8fafc;">
            Produtos no Catálogo PDV ({len(produtos)} itens)
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
                    p_img, p_c1, p_c2, p_c3, p_c4 = st.columns([1, 1.5, 4.5, 2, 2], vertical_alignment="center")
                    
                    with p_img:
                        thumb_url = p.get("url_imagem") or "https://images.unsplash.com/photo-1544025162-d76694265947?w=100&auto=format&fit=crop&q=80"
                        st.markdown(f"""
                        <div style="width: 48px; height: 48px; border-radius: 8px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1);">
                            <img src="{thumb_url}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='https://images.unsplash.com/photo-1544025162-d76694265947?w=100&auto=format&fit=crop&q=80'">
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
                                nova_foto = st.text_input("URL da Foto", value=p.get("url_imagem", ""))
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

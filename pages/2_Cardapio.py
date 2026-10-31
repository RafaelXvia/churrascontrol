import importlib
import streamlit as st
import data_manager
importlib.reload(data_manager)
import ui_components
importlib.reload(ui_components)

st.set_page_config(
    page_title="Cardápio & Catálogo - ChurrasControl",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Navbar superior unificada
ui_components.render_navbar(active_tab="cardapio")

# ================= MODAIS SALTADOS NA TELA (ST.DIALOG) =================

@st.dialog("Cadastrar Novo Produto no Catálogo", width="large")
def dialog_novo_produto():
    st.caption("Preencha os atributos cadastrais e gastronômicos para adicionar o produto ao cardápio.")
    with st.form("form_modal_novo_prod"):
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
            url_imagem = st.text_input("URL da Foto do Produto (Imgur)", placeholder="https://i.imgur.com/...", help="Link da foto do prato")

        descricao = st.text_area(
            "Descrição Gastronômica & Comercial",
            placeholder="Ex: Corte nobre com gordura selecionada, assado na brasa viva e servido com farofa crocante e chimichurri artesanal.",
            help="Texto apresentado no cardápio aos clientes"
        )

        c_sw1, c_sw2 = st.columns(2)
        with c_sw1:
            precisa_produzir = st.checkbox("Requer Cozinha / Grelha (precisa_produzir)", value=True)
        with c_sw2:
            disponivel = st.checkbox("Disponível para Venda (disponivel)", value=True)

        btn_salvar = st.form_submit_button("Salvar Produto no Catálogo", type="primary", use_container_width=True)
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
                    st.success(f"Produto '{nome}' cadastrado com sucesso!")
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))


@st.dialog("Gerenciar Produto (Editar / Excluir)", width="large")
def dialog_gerenciar_produto(p):
    img_preview = p.get("url_imagem")
    if not img_preview or img_preview.strip() == "":
        img_preview = "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80"

    # Preview visual rápido do item no cabeçalho do modal
    st.markdown(f"""
    <meta name="referrer" content="no-referrer">
    <div style="display: flex; gap: 16px; align-items: center; margin-bottom: 16px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 12px 16px; border-radius: 12px;">
        <div style="width: 72px; height: 72px; border-radius: 10px; overflow: hidden; background: #0f172a; flex-shrink: 0; border: 1px solid rgba(255,255,255,0.1);">
            <img src="{img_preview}" referrerpolicy="no-referrer" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='https://images.unsplash.com/photo-1544025162-d76694265947?w=100'">
        </div>
        <div style="flex-grow: 1;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 0.74rem; background: rgba(245, 158, 11, 0.15); color: #fbbf24; padding: 2px 8px; border-radius: 5px; font-weight: 700;">
                    CÓD #{p.get('codigo_pdv', '')}
                </span>
                <span style="font-size: 0.74rem; color: #94a3b8;">
                    {p.get('categoria', 'Geral')}
                </span>
            </div>
            <h3 style="margin: 4px 0 0 0; color: #ffffff; font-size: 1.2rem; font-weight: 700;">
                {p.get('nome', '')}
            </h3>
        </div>
        <div style="text-align: right; min-width: 100px;">
            <div style="font-size: 1.35rem; font-weight: 800; color: #fbbf24;">
                R$ {float(p.get('preco_unitario', 0)):,.2f}
            </div>
            <div style="font-size: 0.74rem; color: {'#10b981' if p.get('disponivel', 1) else '#ef4444'}; font-weight: 600;">
                {'Disponível' if p.get('disponivel', 1) else 'Pausado'}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_edit, tab_del = st.tabs(["Editar Dados do Produto", "Excluir Produto"])

    with tab_edit:
        with st.form(f"form_modal_edit_prod_{p['id']}"):
            c1, c2 = st.columns([1.5, 3])
            with c1:
                novo_cod = st.text_input("Código PDV", value=str(p["codigo_pdv"]))
            with c2:
                novo_nome = st.text_input("Nome do Produto", value=p["nome"])

            c3, c4 = st.columns(2)
            with c3:
                cat_opcoes = ["Carnes", "Comida", "Entradas", "Bebidas", "Sobremesas", "Promoção", "Geral"]
                idx_cat = cat_opcoes.index(p["categoria"]) if p["categoria"] in cat_opcoes else 0
                nova_cat = st.selectbox("Categoria", cat_opcoes, index=idx_cat)
                novo_preco = st.number_input("Preço de Venda (R$)", min_value=0.01, value=float(p["preco_unitario"]), step=0.50)
            with c4:
                novo_estoque = st.number_input("Estoque Disponível (qtd_disp)", min_value=0, value=int(p.get("qtd_disp", 10)))
                nova_foto = st.text_input("URL da Foto (Imgur)", value=p.get("url_imagem", ""))

            nova_desc = st.text_area("Descrição Gastronômica", value=p.get("descricao", ""))

            c_s1, c_s2 = st.columns(2)
            with c_s1:
                novo_prod = st.checkbox("Requer Cozinha/Grelha (precisa_produzir)", value=bool(p.get("precisa_produzir", 1)))
            with c_s2:
                novo_disp = st.checkbox("Disponível no Cardápio (disponivel)", value=bool(p.get("disponivel", 1)))

            btn_update = st.form_submit_button("Salvar Alterações", type="primary", use_container_width=True)
            if btn_update:
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
                    st.success("Produto atualizado com sucesso!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

    with tab_del:
        st.warning(f"Atenção: A exclusão de **{p['nome']}** removerá o item permanentemente do cardápio.")
        confirma_del = st.checkbox("Sim, confirmo a exclusão definitiva deste produto", key=f"del_chk_card_{p['id']}")
        if st.button("Confirmar e Excluir Definitivamente", type="primary", disabled=not confirma_del, key=f"del_btn_card_{p['id']}", use_container_width=True):
            data_manager.excluir_produto(p["id"])
            st.success("Produto excluído com sucesso!")
            st.rerun()


# ================= CSS PERSONALIZADO (CARDAPIO MODERNO, RESPONSIVO & SEM F5) =================
st.markdown("""
<meta name="referrer" content="no-referrer">
<style>
    .delivery-hero {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.90) 0%, rgba(15, 23, 42, 0.97) 100%),
                    url('https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=1200&auto=format&fit=crop&q=80');
        background-size: cover;
        background-position: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 22px 28px;
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
    [data-testid="stColumn"] {
        position: relative !important;
    }
    .card-delivery {
        background: rgba(15, 23, 42, 0.88);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        overflow: hidden;
        transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        cursor: pointer !important;
    }
    [data-testid="stColumn"]:hover .card-delivery {
        transform: translateY(-4px);
        box-shadow: 0 16px 32px -6px rgba(0, 0, 0, 0.75), 0 0 18px rgba(245, 158, 11, 0.25);
        border-color: #f59e0b;
    }
    .card-img-container {
        position: relative;
        width: 100%;
        height: 185px;
        overflow: hidden;
        background: #0f172a;
    }
    .card-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.35s ease;
    }
    [data-testid="stColumn"]:hover .card-img {
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
        font-size: 1.08rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 6px 0;
        line-height: 1.25;
    }
    .card-desc {
        font-size: 0.83rem;
        color: #94a3b8;
        line-height: 1.45;
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
        font-size: 1.25rem;
        font-weight: 800;
        color: #fbbf24;
    }
    /* Botão invisível nativo cobrindo 100% da área do card */
    div[class*="st-key-btn_prod_card_"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: 20 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    div[class*="st-key-btn_prod_card_"] div.stButton {
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    div[class*="st-key-btn_prod_card_"] div.stButton > button {
        width: 100% !important;
        height: 100% !important;
        min-height: 100% !important;
        max-height: 100% !important;
        opacity: 0 !important;
        visibility: visible !important;
        cursor: pointer !important;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        position: absolute !important;
        inset: 0 !important;
        z-index: 25 !important;
        pointer-events: auto !important;
        font-size: 0 !important;
        color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        outline: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ================= CABEÇALHO DO CARDÁPIO & AÇÕES =================
st.markdown("""
<div class="delivery-hero">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
        <div>
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span class="delivery-badge-open">Catálogo Oficial</span>
                <span class="delivery-badge-tag">Parrilla & Cozinha Caseira</span>
                <span class="delivery-badge-tag">Cardápio Interativo</span>
            </div>
            <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #ffffff; letter-spacing: -0.03em;">
                ChurrasControl • Cardápio & Catálogo
            </h1>
            <p style="margin: 6px 0 0 0; color: #cbd5e1; font-size: 0.95rem; max-width: 680px;">
                Gerencie todos os pratos, cortes e bebidas. Clique diretamente em qualquer card para <strong>editar informações ou excluir o produto</strong>.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Barra de Ações: Novo Produto, Sincronização Xano e Pesquisa
c_acts1, c_acts2 = st.columns([4, 2.2], vertical_alignment="center")

with c_acts1:
    busca_cardapio = st.text_input(
        "Pesquisar no cardápio",
        placeholder="Digite o nome do prato, corte, categoria ou código PDV...",
        label_visibility="collapsed"
    )

with c_acts2:
    c_btn_novo, c_btn_sync = st.columns([1.3, 1.0])
    with c_btn_novo:
        if st.button("+ Novo Produto", type="primary", use_container_width=True, help="Cadastrar um novo produto com todos os campos da tabela"):
            dialog_novo_produto()
    with c_btn_sync:
        if st.button("Sincronizar Xano", use_container_width=True, help="Sincronizar produtos e fotos reais direto da API do Xano"):
            try:
                qtd_sync = data_manager.sincronizar_produtos_xano()
                st.toast(f"{qtd_sync} produtos sincronizados do Xano!")
                st.rerun()
            except Exception as ex:
                st.error(f"Erro ao sincronizar: {ex}")

# Obter produtos cadastrados com fotos reais do SQLite
produtos_todos = data_manager.listar_produtos(busca=busca_cardapio)

# Filtros de Categorias em Chips
categorias_disponiveis = ["Todas"] + sorted(list(set(p.get("categoria", "Geral") for p in produtos_todos if p.get("categoria"))))
cat_filtro = st.pills("Categorias do Cardápio", options=categorias_disponiveis, default="Todas", label_visibility="collapsed")

if cat_filtro and cat_filtro != "Todas":
    produtos_filtrados = [p for p in produtos_todos if p.get("categoria") == cat_filtro]
else:
    produtos_filtrados = produtos_todos

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; margin: 1.2rem 0 0.8rem 0;">
    <div style="color: #cbd5e1; font-size: 0.92rem; font-weight: 600;">
        Exibindo <strong>{len(produtos_filtrados)}</strong> itens no cardápio
    </div>
    <div style="color: #94a3b8; font-size: 0.8rem;">
        Dica: <em>Clique no card para abrir o modal de edição ou exclusão</em>
    </div>
</div>
""", unsafe_allow_html=True)

if not produtos_filtrados:
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.6); border: 1px dashed #334155; border-radius: 16px; padding: 40px; text-align: center; margin-top: 10px;">
        <h3 style="color: #ffffff; margin: 10px 0 4px 0;">Nenhum produto encontrado</h3>
        <p style="color: #94a3b8; font-size: 0.9rem;">Tente pesquisar por outro termo ou cadastre um novo produto acima.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Renderização em Grid de 3 Colunas com Cards 100% Clicáveis Nativamente (Sem F5)
    cols_per_row = 3
    for i in range(0, len(produtos_filtrados), cols_per_row):
        row_items = produtos_filtrados[i:i + cols_per_row]
        cols = st.columns(cols_per_row)

        for col_idx, p in enumerate(row_items):
            with cols[col_idx]:
                # URL real da foto cadastrada no Xano (Imgur) com fallback
                img_url = p.get("url_imagem")
                if not img_url or img_url.strip() == "":
                    img_url = "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80"

                badge_prod = "Requer Cozinha" if p.get("precisa_produzir") else "Pronta Entrega"
                badge_disp = f"Restam {p.get('qtd_disp')} un." if p.get("qtd_disp", 0) <= 5 else f"Estoque: {p.get('qtd_disp')} un."
                is_indisponivel = (p.get("disponivel", 1) == 0)

                # Card com visual imersivo
                st.markdown(f"""
                <div class="card-delivery" style="{'opacity: 0.6;' if is_indisponivel else ''}">
                    <div class="card-img-container">
                        <img src="{img_url}" referrerpolicy="no-referrer" class="card-img" alt="{p['nome']}" onerror="this.src='https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80'">
                        <span class="card-badge-float">{badge_prod}</span>
                    </div>
                    <div class="card-body">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-size: 0.72rem; color: #94a3b8; background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px;">
                                CÓD {p['codigo_pdv']} • {p['categoria']}
                            </span>
                            <span style="font-size: 0.72rem; color: {'#ef4444' if is_indisponivel else '#10b981'}; font-weight: 700;">
                                {'ESGOTADO' if is_indisponivel else badge_disp}
                            </span>
                        </div>
                        <h4 class="card-title">{p['nome']}</h4>
                        <p class="card-desc">{p.get('descricao') or 'Prato preparado com ingredientes frescos e seleção artesanal da casa.'}</p>
                        <div class="card-footer-box">
                            <span class="card-price">R$ {float(p['preco_unitario']):,.2f}</span>
                            <span style="font-size: 0.78rem; color: #f59e0b; font-weight: 600;">Editar / Excluir</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Botão invisível nativo que aciona o modal sem nenhum F5 ou recarregamento
                if st.button("", key=f"btn_prod_card_{p['id']}", use_container_width=True):
                    dialog_gerenciar_produto(p)

                st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # JavaScript para assegurar que qualquer clique na área do card dispare o botão invisível
    st.html("""
    <script>
    (function() {
        function bindCardClicks() {
            document.querySelectorAll('.card-delivery').forEach(function(card) {
                if (card.dataset.boundClick) return;
                card.dataset.boundClick = 'true';
                card.addEventListener('click', function(ev) {
                    const col = card.closest('[data-testid="stColumn"]');
                    if (col) {
                        const btn = col.querySelector('div[class*="st-key-btn_prod_card_"] button');
                        if (btn) btn.click();
                    }
                });
            });
        }
        bindCardClicks();
        setTimeout(bindCardClicks, 300);
        setTimeout(bindCardClicks, 800);
    })();
    </script>
    """)

# Rodapé Executivo
ui_components.render_footer()

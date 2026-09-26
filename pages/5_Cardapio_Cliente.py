import streamlit as st
import importlib
import html
import data_manager
import ui_components

importlib.reload(data_manager)
importlib.reload(ui_components)

st.set_page_config(
    page_title="Cardápio Digital do Cliente — ChurrasControl",
    page_icon="🥩",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização Mobile-First e Gastronômica Premium
st.markdown("""
<style>
/* Oculta completamente sidebars e barras de navegação administrativas */
[data-testid="stSidebarNav"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }

/* Paleta de Cores e Tipografia */
:root {
    --bg-dark: #12141a;
    --card-bg: #1c202a;
    --primary-orange: #ff6f00;
    --primary-hover: #e65100;
    --gold: #ffb300;
    --text-white: #ffffff;
    --text-muted: #b0bec5;
}

/* Header do Cliente */
.cliente-header {
    background: linear-gradient(135deg, #1e2430 0%, #151820 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 18px 24px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}
.cliente-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}
.cliente-brand h1 {
    font-size: 1.5rem;
    font-weight: 900;
    color: #fff;
    margin: 0;
    letter-spacing: -0.5px;
}
.cliente-brand span {
    color: var(--primary-orange);
}
.mesa-badge-cliente {
    background: linear-gradient(135deg, #e65100 0%, #ff8f00 100%);
    color: #ffffff;
    padding: 8px 18px;
    border-radius: 30px;
    font-weight: 800;
    font-size: 0.95rem;
    box-shadow: 0 4px 14px rgba(230, 81, 0, 0.4);
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

/* Card Gastronômico do Cliente */
.client-card {
    background: #1c202a;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 20px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    display: flex;
    flex-direction: column;
    height: 100%;
}
.client-card:hover {
    transform: translateY(-4px);
    border-color: rgba(255, 111, 0, 0.45);
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.5);
}
.client-img-wrap {
    position: relative;
    width: 100%;
    height: 190px;
    background: #2a2f3d;
    overflow: hidden;
}
.client-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.4s ease;
}
.client-card:hover .client-img {
    transform: scale(1.05);
}
.badge-estoque-ok {
    position: absolute;
    top: 12px;
    right: 12px;
    background: rgba(46, 125, 50, 0.9);
    color: #fff;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 800;
    backdrop-filter: blur(4px);
}
.badge-estoque-off {
    position: absolute;
    top: 12px;
    right: 12px;
    background: rgba(211, 47, 47, 0.92);
    color: #fff;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 800;
    backdrop-filter: blur(4px);
}
.badge-cat {
    position: absolute;
    bottom: 12px;
    left: 12px;
    background: rgba(0, 0, 0, 0.7);
    color: #ffb74d;
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 0.75rem;
    font-weight: 700;
    border: 1px solid rgba(255, 183, 77, 0.3);
}
.client-content {
    padding: 16px;
    display: flex;
    flex-direction: column;
    flex-grow: 1;
}
.client-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 6px 0;
}
.client-desc {
    font-size: 0.86rem;
    color: #90a4ae;
    line-height: 1.4;
    margin-bottom: 14px;
    flex-grow: 1;
}
.client-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    padding-top: 12px;
}
.client-price {
    font-size: 1.25rem;
    font-weight: 900;
    color: #ffb300;
}

/* Barra Flutuante de Pré-Comanda */
.precomanda-bar {
    position: sticky;
    bottom: 16px;
    z-index: 999;
    background: linear-gradient(135deg, #e65100 0%, #ff6f00 100%);
    border-radius: 16px;
    padding: 14px 20px;
    color: #fff;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 10px 30px rgba(230, 81, 0, 0.5);
    margin-top: 20px;
}
.precomanda-info {
    font-weight: 800;
    font-size: 1.05rem;
}

/* Responsividade Mobile Extrema */
@media (max-width: 640px) {
    .cliente-header { padding: 14px; }
    .cliente-brand h1 { font-size: 1.2rem; }
    .client-img-wrap { height: 160px; }
}
</style>
""", unsafe_allow_html=True)

# 1. Recuperação do número da mesa via Query Params ou Seletor
query_params = st.query_params
mesa_param = query_params.get("mesa", "")
try:
    mesa_atual = int(mesa_param) if mesa_param else 6
except ValueError:
    mesa_atual = 6

# Inicializa sessão da Pré-comanda do cliente para a mesa
session_key = f"precomanda_itens_mesa_{mesa_atual}"
if session_key not in st.session_state:
    st.session_state[session_key] = []

# ================= MODAL DE PRÉ-COMANDA =================
@st.dialog(f"🛒 Pré-Comanda — Mesa {mesa_atual:02d}")
def modal_precomanda():
    itens_carrinho = st.session_state[session_key]
    
    if not itens_carrinho:
        st.info("Sua pré-comanda está vazia. Selecione pratos e bebidas do cardápio para adicionar ao carrinho!")
        return

    st.markdown("Revise seus pratos antes de confirmar. **O pedido só será enviado para a cozinha após clicar no botão verde abaixo.**")
    st.markdown("---")

    subtotal_geral = 0.0
    indices_para_remover = []

    for idx, item in enumerate(itens_carrinho):
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            st.markdown(f"**{item['nome']}**")
            st.caption(f"R$ {item['preco_unitario']:.2f} cada")
            obs_digitada = st.text_input(
                f"Observação para {item['nome']}", 
                value=item.get("observacao", ""), 
                key=f"obs_cart_{idx}",
                placeholder="Ex: Sem cebola, ao ponto..."
            )
            item["observacao"] = obs_digitada
        with c2:
            nova_qtd = st.number_input(
                "Qtd", 
                min_value=1, 
                max_value=20, 
                value=int(item["quantidade"]), 
                key=f"qtd_cart_{idx}"
            )
            item["quantidade"] = nova_qtd
            sub_item = nova_qtd * item["preco_unitario"]
            subtotal_geral += sub_item
            st.markdown(f"**Subtotal: R$ {sub_item:.2f}**")
        with c3:
            st.write("")
            st.write("")
            if st.button("🗑️", key=f"del_cart_{idx}", help="Remover do carrinho"):
                indices_para_remover.append(idx)
        st.markdown("<hr style='margin:8px 0; border:0; border-top:1px dashed #37474f;'>", unsafe_allow_html=True)

    if indices_para_remover:
        for rem_idx in sorted(indices_para_remover, reverse=True):
            st.session_state[session_key].pop(rem_idx)
        st.rerun()

    st.markdown(f"""
    <div style="background:#262a34; border-radius:12px; padding:14px; margin:16px 0; display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:1.1rem; color:#b0bec5; font-weight:700;">Total da Pré-Comanda:</span>
        <span style="font-size:1.4rem; color:#ffb300; font-weight:900;">R$ {subtotal_geral:.2f}</span>
    </div>
    """, unsafe_allow_html=True)

    st.warning("⚠️ Ao confirmar, o pedido entrará automaticamente no sistema do restaurante e na fila de preparo.")

    col_btn_fechar, col_btn_confirmar = st.columns([1, 2])
    with col_btn_fechar:
        if st.button("Continuar Escolhendo", use_container_width=True):
            st.rerun()
    with col_btn_confirmar:
        if st.button("🚀 Confirmar e Enviar Pedido", type="primary", use_container_width=True):
            try:
                res = data_manager.confirmar_precomanda_cliente(mesa_atual, st.session_state[session_key])
                st.session_state[session_key] = []
                st.session_state[f"ultimo_pedido_sucesso_mesa_{mesa_atual}"] = res
                st.toast("🎉 Pedido enviado com sucesso para a cozinha!", icon="✅")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao confirmar pedido: {e}")

# ================= MODAL DE ADIÇÃO RÁPIDA =================
@st.dialog("Adicionar ao Pedido")
def modal_adicionar_prato(produto: dict):
    st.markdown(f"""
    <div style="display:flex; gap:16px; align-items:center; margin-bottom:14px;">
        <img src="{produto['url_imagem']}" style="width:80px; height:80px; border-radius:12px; object-fit:cover;"/>
        <div>
            <h3 style="margin:0; color:#fff;">{produto['nome']}</h3>
            <span style="color:#ffb300; font-weight:800; font-size:1.2rem;">R$ {produto['preco_unitario']:.2f}</span>
        </div>
    </div>
    <p style="color:#90a4ae; font-size:0.9rem;">{produto['descricao']}</p>
    """, unsafe_allow_html=True)

    qtd = st.number_input("Quantidade", min_value=1, max_value=max(1, produto.get("qtd_disp") or 10), value=1)
    obs = st.text_input("Alguma observação ou preferência?", placeholder="Ex: Carne ao ponto, sem cebola, etc.")

    if st.button("➕ Colocar na Pré-Comanda", type="primary", use_container_width=True):
        # Verifica se já está na pré-comanda
        achou = False
        for it in st.session_state[session_key]:
            if it["produto_id"] == produto["id"]:
                it["quantidade"] += qtd
                if obs:
                    it["observacao"] = (it.get("observacao", "") + " | " + obs).strip(" | ")
                achou = True
                break
        if not achou:
            st.session_state[session_key].append({
                "produto_id": produto["id"],
                "nome": produto["nome"],
                "preco_unitario": float(produto["preco_unitario"]),
                "quantidade": qtd,
                "observacao": obs
            })
        st.toast(f"✅ {produto['nome']} adicionado à pré-comanda!", icon="🛒")
        st.rerun()

# ================= TELA PRINCIPAL DO CLIENTE =================

# Header do Restaurante e Mesa
st.markdown(f"""
<div class="cliente-header">
    <div class="cliente-brand">
        <span style="font-size:2rem;">🔥</span>
        <div>
            <h1>Churras<span>Control</span></h1>
            <span style="font-size:0.8rem; color:#90a4ae; font-weight:600;">CARDÁPIO DIGITAL DE AUTOATENDIMENTO</span>
        </div>
    </div>
    <div class="mesa-badge-cliente">
        <span>📍</span> MESA {mesa_atual:02d}
    </div>
</div>
""", unsafe_allow_html=True)

# Mensagem de sucesso recente caso tenha confirmado pedido
if f"ultimo_pedido_sucesso_mesa_{mesa_atual}" in st.session_state:
    ped_info = st.session_state.pop(f"ultimo_pedido_sucesso_mesa_{mesa_atual}")
    st.balloons()
    st.success(f"🎉 **Pedido Confirmado com Sucesso!** Sua comanda #{ped_info['comanda_id']} recebeu {ped_info['total_itens']} novos itens que já foram enviados para a cozinha. Fique à vontade para pedir mais pratos a qualquer momento!")

# Barra de Pesquisa e Filtros
col_search, col_mesa_selector = st.columns([3, 1])
with col_search:
    termo_busca = st.text_input("🔍 O que você gostaria de saborear hoje?", placeholder="Pesquisar por nome ou categoria...")
with col_mesa_selector:
    # Permite alternar de mesa caso tenha escaneado errado ou esteja testando
    nova_mesa = st.number_input("Sua Mesa:", min_value=1, max_value=50, value=mesa_atual)
    if nova_mesa != mesa_atual:
        st.query_params["mesa"] = str(nova_mesa)
        st.rerun()

# Categorias Rápidas
categorias = ["Todas", "Carnes", "Comida", "Bebidas", "Sobremesas"]
cat_selecionada = st.pills("Categorias:", categorias, default="Todas")

# Carrega produtos cadastrados
todos_produtos = data_manager.listar_produtos()

# Filtragem de produtos
produtos_filtrados = []
for p in todos_produtos:
    # Filtro de Categoria
    if cat_selecionada != "Todas" and p.get("categoria", "").lower() != cat_selecionada.lower():
        continue
    # Filtro de Busca
    if termo_busca:
        termo = termo_busca.lower()
        if termo not in p.get("nome", "").lower() and termo not in p.get("categoria", "").lower() and termo not in p.get("descricao", "").lower():
            continue
    produtos_filtrados.append(p)

# Itens da Pré-Comanda Atual
carrinho_atual = st.session_state[session_key]
total_carrinho = sum(it["quantidade"] * it["preco_unitario"] for it in carrinho_atual)
qtd_total_carrinho = sum(it["quantidade"] for it in carrinho_atual)

# Botão de visualização do carrinho no topo se houver itens
if qtd_total_carrinho > 0:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, rgba(230,81,0,0.15) 0%, rgba(255,111,0,0.25) 100%); border:1px solid rgba(255,111,0,0.4); border-radius:12px; padding:12px 18px; margin-bottom:18px; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <span style="font-size:1.1rem; font-weight:800; color:#fff;">🛒 Sua Pré-Comanda:</span>
            <span style="color:#ffb74d; font-weight:700; margin-left:8px;">{qtd_total_carrinho} itens (R$ {total_carrinho:.2f})</span>
        </div>
        <span style="font-size:0.85rem; color:#b0bec5;">Itens ainda NÃO enviados à cozinha</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button(f"🛒 Abrir Pré-Comanda e Enviar Pedido ({qtd_total_carrinho} itens • R$ {total_carrinho:.2f})", type="primary", use_container_width=True):
        modal_precomanda()

st.markdown(f"<div style='color:#90a4ae; font-size:0.9rem; margin-bottom:14px;'>Exibindo {len(produtos_filtrados)} pratos disponíveis:</div>", unsafe_allow_html=True)

# Grid Responsivo Gastronômico (3 Colunas em desktop, 1 em celular via Streamlit layout)
cols_per_row = 3
for i in range(0, len(produtos_filtrados), cols_per_row):
    cols = st.columns(cols_per_row)
    for j in range(cols_per_row):
        idx = i + j
        if idx >= len(produtos_filtrados):
            break
        
        prod = produtos_filtrados[idx]
        col = cols[j]
        
        disp = int(prod.get("disponivel", 1))
        saldo_disp = int(prod.get("qtd_disp") or 0)
        esta_esgotado = (disp == 0 or saldo_disp <= 0)
        
        badge_estoque = '<span class="badge-estoque-off">⚠️ Esgotado</span>' if esta_esgotado else f'<span class="badge-estoque-ok">✅ Disponível ({saldo_disp} un)</span>'
        img_url = prod.get("url_imagem") or "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80"
        
        with col:
            st.markdown(f"""
            <div class="client-card">
                <div class="client-img-wrap">
                    <img class="client-img" src="{img_url}" alt="{html.escape(prod['nome'])}"/>
                    {badge_estoque}
                    <span class="badge-cat">{html.escape(prod.get('categoria', 'Geral'))}</span>
                </div>
                <div class="client-content">
                    <div class="client-title">{html.escape(prod['nome'])}</div>
                    <div class="client-desc">{html.escape(prod.get('descricao', ''))}</div>
                    <div class="client-footer">
                        <span class="client-price">R$ {float(prod['preco_unitario']):.2f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão de Ação de Seleção
            if esta_esgotado:
                st.button("🚫 Esgotado", key=f"btn_esgotado_{prod['id']}", disabled=True, use_container_width=True)
            else:
                if st.button("➕ Adicionar à Pré-Comanda", key=f"btn_add_card_{prod['id']}", use_container_width=True):
                    modal_adicionar_prato(prod)

# Barra Flutuante de Pré-Comanda Fixada no Rodapé se houver itens
if qtd_total_carrinho > 0:
    st.markdown("---")
    c_bar1, c_bar2 = st.columns([3, 2])
    with c_bar1:
        st.markdown(f"""
        <div style="padding:8px 0;">
            <div style="font-size:1.15rem; font-weight:800; color:#fff;">🛒 Pré-Comanda da Mesa {mesa_atual:02d}</div>
            <div style="font-size:0.9rem; color:#ffb74d;">{qtd_total_carrinho} itens selecionados • Total: R$ {total_carrinho:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c_bar2:
        if st.button("🚀 Ver Pré-Comanda & Confirmar Pedido", type="primary", use_container_width=True, key="btn_ver_precomanda_bottom"):
            modal_precomanda()

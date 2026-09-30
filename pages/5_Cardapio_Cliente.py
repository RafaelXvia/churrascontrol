import streamlit as st
import importlib
import html
import data_manager
import ui_components

importlib.reload(data_manager)
importlib.reload(ui_components)

st.set_page_config(
    page_title="Cardápio Digital — ChurrasControl",
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

/* Header do Cliente / Navbar */
.cliente-header {
    background: linear-gradient(135deg, #1e2430 0%, #151820 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 16px 22px;
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
    font-size: 1.45rem;
    font-weight: 900;
    color: #fff;
    margin: 0;
    letter-spacing: -0.5px;
}
.cliente-brand span {
    color: var(--primary-orange);
}
.cliente-nav-right {
    display: flex;
    align-items: center;
    gap: 12px;
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
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 12px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
    transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
    display: flex;
    flex-direction: column;
    height: 100%;
    cursor: pointer !important;
}
[data-testid="stColumn"]:hover .client-card {
    transform: translateY(-4px);
    border-color: rgba(255, 111, 0, 0.5);
    box-shadow: 0 14px 28px rgba(0, 0, 0, 0.6), 0 0 18px rgba(255, 111, 0, 0.2);
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
    transition: transform 0.35s ease;
}
[data-testid="stColumn"]:hover .client-img {
    transform: scale(1.05);
}
.badge-estoque-ok {
    position: absolute;
    top: 12px;
    right: 12px;
    background: rgba(46, 125, 50, 0.92);
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
    background: rgba(211, 47, 47, 0.94);
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
    background: rgba(0, 0, 0, 0.75);
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
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.client-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    padding-top: 12px;
    margin-top: auto;
}
.client-price {
    font-size: 1.25rem;
    font-weight: 900;
    color: #ffb300;
}
.client-action-hint {
    font-size: 0.82rem;
    font-weight: 700;
    color: #ff9800;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Permite rolagem suave e livre em todos os dispositivos */
html, body, [data-testid="stAppViewContainer"], section.main {
    overflow-y: auto !important;
    overflow-x: hidden !important;
    height: auto !important;
}

[data-testid="stColumn"] {
    position: relative !important;
}

/* Botão Flutuante do Carrinho (Floating Action Button Fixo na tela) */
div[class*="st-key-btn_fab_carrinho_fixo"] {
    position: fixed !important;
    bottom: 24px !important;
    right: 24px !important;
    z-index: 999999 !important;
    width: auto !important;
}
div[class*="st-key-btn_fab_carrinho_fixo"] button {
    background: linear-gradient(135deg, #e65100 0%, #ff8f00 100%) !important;
    color: #ffffff !important;
    border: 2px solid rgba(255, 255, 255, 0.4) !important;
    border-radius: 40px !important;
    padding: 12px 22px !important;
    font-size: 1.05rem !important;
    font-weight: 800 !important;
    box-shadow: 0 8px 25px rgba(230, 81, 0, 0.65), 0 2px 10px rgba(0, 0, 0, 0.4) !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    cursor: pointer !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
div[class*="st-key-btn_fab_carrinho_fixo"] button:hover {
    transform: scale(1.08) !important;
    box-shadow: 0 12px 32px rgba(230, 81, 0, 0.85) !important;
}

/* Responsividade Mobile Extrema */
@media (max-width: 640px) {
    .cliente-header { padding: 12px 16px; }
    .cliente-brand h1 { font-size: 1.2rem; }
    .client-img-wrap { height: 160px; }
    .mesa-badge-cliente { font-size: 0.85rem; padding: 6px 12px; }
    div[class*="st-key-btn_fab_carrinho_fixo"] {
        bottom: 18px !important;
        right: 18px !important;
    }
    div[class*="st-key-btn_fab_carrinho_fixo"] button {
        padding: 10px 18px !important;
        font-size: 0.95rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# 1. Recuperação e fixação do número da mesa exclusivamente via Query Params
query_params = st.query_params
mesa_param = query_params.get("mesa", "")
try:
    mesa_atual = int(mesa_param) if mesa_param else 6
except ValueError:
    mesa_atual = 6

# Chave de sessão da Pré-comanda para esta mesa física
session_key = f"precomanda_itens_mesa_{mesa_atual}"
if session_key not in st.session_state:
    st.session_state[session_key] = []

# Consulta comanda ativa da mesa para obter histórico de pedidos já confirmados
def obter_historico_comanda_mesa(num_mesa: int):
    try:
        with data_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT c.id FROM comandas c
            JOIN mesas m ON m.id = c.mesa_id
            WHERE m.numero_mesa = ? AND c.status = 'ABERTA'
            """, (num_mesa,))
            row_c = cursor.fetchone()
            if row_c:
                return data_manager.obter_comanda_detalhes(row_c["id"])
    except Exception as e:
        pass
    return None

# ================= MODAL COMPLETO DE CARRINHO & COMANDA =================
@st.dialog(f"🛒 Carrinho & Comanda — Mesa {mesa_atual:02d}")
def modal_carrinho_mesa():
    itens_carrinho = st.session_state[session_key]
    historico = obter_historico_comanda_mesa(mesa_atual)

    tab_novos, tab_historico = st.tabs([
        f"🛒 Pré-Comanda ({len(itens_carrinho)} novos)", 
        f"📜 Histórico da Mesa ({len(historico['itens']) if historico else 0} itens)"
    ])

    with tab_novos:
        if not itens_carrinho:
            st.info("💡 Sua pré-comanda está vazia. Toque em qualquer prato do cardápio para adicioná-lo!")
        else:
            st.markdown("Revise seus novos pratos antes de enviar. **O pedido só irá para a cozinha após clicar em Confirmar.**")
            st.markdown("---")

            subtotal_novos = 0.0
            indices_para_remover = []

            for idx, item in enumerate(itens_carrinho):
                c1, c2, c3 = st.columns([3, 2, 1])
                with c1:
                    st.markdown(f"**{item['nome']}**")
                    st.caption(f"R$ {item['preco_unitario']:.2f} cada")
                    obs_digitada = st.text_input(
                        f"Observação para {item['nome']}", 
                        value=item.get("observacao", ""), 
                        key=f"cart_obs_{idx}",
                        placeholder="Ex: Sem cebola, ao ponto..."
                    )
                    item["observacao"] = obs_digitada
                with c2:
                    nova_qtd = st.number_input(
                        "Qtd", 
                        min_value=1, 
                        max_value=20, 
                        value=int(item["quantidade"]), 
                        key=f"cart_qtd_{idx}"
                    )
                    item["quantidade"] = nova_qtd
                    sub_item = nova_qtd * item["preco_unitario"]
                    subtotal_novos += sub_item
                    st.markdown(f"**Subtotal:** R$ {sub_item:.2f}")
                with c3:
                    st.write("")
                    st.write("")
                    if st.button("🗑️", key=f"cart_del_{idx}", help="Remover prato"):
                        indices_para_remover.append(idx)
                st.markdown("<hr style='margin:6px 0; border:0; border-top:1px dashed #37474f;'>", unsafe_allow_html=True)

            if indices_para_remover:
                for rem_idx in sorted(indices_para_remover, reverse=True):
                    st.session_state[session_key].pop(rem_idx)
                st.rerun()

            st.markdown(f"""
            <div style="background:#262a34; border-radius:12px; padding:12px 16px; margin:14px 0; display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:1.05rem; color:#b0bec5; font-weight:700;">Subtotal Novos Pratos:</span>
                <span style="font-size:1.35rem; color:#ffb300; font-weight:900;">R$ {subtotal_novos:.2f}</span>
            </div>
            """, unsafe_allow_html=True)

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

    with tab_historico:
        if not historico or not historico.get("itens"):
            st.info("Nenhum pedido anterior foi registrado para esta mesa ainda. Assim que você confirmar seus pratos, eles aparecerão aqui!")
        else:
            st.markdown(f"""
            <div style="margin-bottom:12px;">
                <span style="font-size:0.9rem; color:#90a4ae;">Comanda Nº <strong>#{historico['comanda']['id']}</strong> | Status: <strong>{historico['comanda']['status']}</strong></span>
            </div>
            """, unsafe_allow_html=True)

            for it_hist in historico["itens"]:
                c_h1, c_h2, c_h3 = st.columns([3, 1, 2])
                with c_h1:
                    st.markdown(f"**{it_hist['produto_nome']}**")
                    if it_hist.get("observacao"):
                        st.caption(f"Obs: {it_hist['observacao']}")
                with c_h2:
                    st.markdown(f"**{it_hist['quantidade']}x**")
                with c_h3:
                    st.markdown(f"R$ {it_hist['subtotal']:.2f}")
                st.markdown("<hr style='margin:4px 0; border:0; border-top:1px solid rgba(255,255,255,0.06);'>", unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:rgba(46,125,50,0.15); border:1px solid rgba(76,175,80,0.3); border-radius:12px; padding:12px 16px; margin-top:14px; display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:1.05rem; color:#a5d6a7; font-weight:700;">Total Acumulado na Comanda:</span>
                <span style="font-size:1.35rem; color:#81c784; font-weight:900;">R$ {historico['total']:.2f}</span>
            </div>
            """, unsafe_allow_html=True)

# ================= MODAL DE ADIÇÃO RÁPIDA AO CLICAR NO CARD =================
@st.dialog("Adicionar ao Pedido")
def modal_adicionar_prato(produto: dict):
    st.markdown(f"""
    <div style="display:flex; gap:16px; align-items:center; margin-bottom:14px;">
        <img src="{produto['url_imagem']}" style="width:84px; height:84px; border-radius:12px; object-fit:cover;"/>
        <div>
            <h3 style="margin:0; color:#fff;">{produto['nome']}</h3>
            <span style="color:#ffb300; font-weight:800; font-size:1.25rem;">R$ {float(produto['preco_unitario']):.2f}</span>
        </div>
    </div>
    <p style="color:#90a4ae; font-size:0.9rem; line-height:1.4;">{produto.get('descricao', '')}</p>
    """, unsafe_allow_html=True)

    saldo_disp = max(1, produto.get("qtd_disp") or 10)
    qtd = st.number_input("Quantidade Desejada", min_value=1, max_value=saldo_disp, value=1)
    obs = st.text_input("Alguma preferência ou observação?", placeholder="Ex: Carne ao ponto, sem cebola, etc.")

    if st.button("➕ Colocar na Pré-Comanda", type="primary", use_container_width=True):
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
        st.toast(f"✅ {produto['nome']} adicionado ao carrinho!", icon="🛒")
        st.rerun()

# ================= TELA PRINCIPAL DO CLIENTE =================

carrinho_atual = st.session_state[session_key]
qtd_total_carrinho = sum(it["quantidade"] for it in carrinho_atual)
total_carrinho = sum(it["quantidade"] * it["preco_unitario"] for it in carrinho_atual)

# Header Superior com Ícone de Carrinho e Badge da Mesa Fixa
col_header_left, col_header_right = st.columns([3, 2])
with col_header_left:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; padding:6px 0;">
        <span style="font-size:2.2rem;">🔥</span>
        <div>
            <h2 style="margin:0; font-weight:900; color:#fff; font-size:1.5rem; letter-spacing:-0.5px;">Churras<span style="color:#ff6f00;">Control</span></h2>
            <span style="font-size:0.78rem; color:#90a4ae; font-weight:700; letter-spacing:0.5px;">CARDÁPIO DIGITAL DE AUTOATENDIMENTO</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_header_right:
    c_m_badge, c_m_cart = st.columns([1, 1])
    with c_m_badge:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg, #e65100 0%, #ff8f00 100%); color:#ffffff; padding:10px 14px; border-radius:30px; font-weight:800; font-size:0.95rem; text-align:center; box-shadow:0 4px 12px rgba(230,81,0,0.4); margin-top:4px;">
            📍 MESA {mesa_atual:02d}
        </div>
        """, unsafe_allow_html=True)
    with c_m_cart:
        btn_cart_label = f"🛒 Carrinho ({qtd_total_carrinho})" if qtd_total_carrinho > 0 else "🛒 Carrinho"
        if st.button(btn_cart_label, type="primary" if qtd_total_carrinho > 0 else "secondary", use_container_width=True, key="btn_nav_carrinho"):
            modal_carrinho_mesa()

st.markdown("<hr style='margin:10px 0 18px 0; border:0; border-top:1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

# Mensagem de celebração se confirmou pedido recentemente
if f"ultimo_pedido_sucesso_mesa_{mesa_atual}" in st.session_state:
    ped_info = st.session_state.pop(f"ultimo_pedido_sucesso_mesa_{mesa_atual}")
    st.balloons()
    st.success(f"🎉 **Pedido Confirmado com Sucesso!** Sua comanda #{ped_info['comanda_id']} recebeu {ped_info['total_itens']} novos itens que já foram enviados para a cozinha. Você pode acompanhar pelo ícone 🛒 Carrinho no topo a qualquer momento!")

# Barra de Pesquisa de Pratos (100% livre do input de mesa)
termo_busca = st.text_input("🔍 O que você gostaria de saborear hoje?", placeholder="Pesquise por picanha, cerveja, feijoada, porções...")

# Categorias Rápidas em Chips
categorias = ["Todas", "Carnes", "Comida", "Bebidas", "Sobremesas"]
cat_selecionada = st.pills("Filtrar por Categoria:", categorias, default="Todas")

# Carrega produtos cadastrados
todos_produtos = data_manager.listar_produtos()

# Filtragem de produtos
produtos_filtrados = []
for p in todos_produtos:
    if cat_selecionada != "Todas" and p.get("categoria", "").lower() != cat_selecionada.lower():
        continue
    if termo_busca:
        termo = termo_busca.lower()
        if termo not in p.get("nome", "").lower() and termo not in p.get("categoria", "").lower() and termo not in p.get("descricao", "").lower():
            continue
    produtos_filtrados.append(p)

# Indicador visual e atalho para o carrinho se houver itens
if qtd_total_carrinho > 0:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, rgba(230,81,0,0.18) 0%, rgba(255,111,0,0.28) 100%); border:1px solid rgba(255,111,0,0.45); border-radius:14px; padding:12px 18px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
        <div>
            <span style="font-size:1.1rem; font-weight:800; color:#fff;">🛒 Pré-Comanda da Mesa {mesa_atual:02d}:</span>
            <span style="color:#ffb74d; font-weight:800; margin-left:8px;">{qtd_total_carrinho} novos itens (R$ {total_carrinho:.2f})</span>
        </div>
        <span style="font-size:0.85rem; color:#b0bec5;">Toque em qualquer prato para adicionar mais ou clique no Carrinho para enviar</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"<div style='color:#90a4ae; font-size:0.88rem; margin-bottom:12px;'>Exibindo {len(produtos_filtrados)} pratos disponíveis • <em>Toque no prato para escolher</em></div>", unsafe_allow_html=True)

# Grid Gastronômico 100% Clicável (Sem botão de texto avulso)
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
            <div class="client-card {'card-esgotado' if esta_esgotado else ''}" style="{'opacity: 0.55; cursor: not-allowed !important;' if esta_esgotado else 'cursor: pointer;'}">
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
                        <span class="client-action-hint">{'🚫 Esgotado' if esta_esgotado else 'Tocar p/ Pedir ➔'}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão de Ação Integrado (Disparado também ao tocar no card acima)
            if esta_esgotado:
                st.button("🚫 Prato Esgotado", key=f"btn_esgotado_{prod['id']}", disabled=True, use_container_width=True)
            else:
                if st.button("➕ Escolher Prato", key=f"btn_choose_{prod['id']}", use_container_width=True):
                    modal_adicionar_prato(prod)
            
            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# JavaScript Delegado para que tocar no card acione o botão daquela coluna
st.html("""
<script>
(function() {
    function bindClientCards() {
        document.querySelectorAll('.client-card').forEach(function(card) {
            if (card.dataset.boundClick) return;
            card.dataset.boundClick = 'true';
            card.addEventListener('click', function(ev) {
                if (card.classList.contains('card-esgotado')) return;
                const col = card.closest('[data-testid="stColumn"]');
                if (col) {
                    const btn = col.querySelector('button:not([disabled])');
                    if (btn) btn.click();
                }
            });
        });
    }
    bindClientCards();
    setTimeout(bindClientCards, 250);
    setTimeout(bindClientCards, 700);
})();
</script>
""")

# Botão Flutuante Fixo (FAB) visível em qualquer altura de rolagem no celular e PC
fab_cart_label = f"🛒 Carrinho ({qtd_total_carrinho})" if qtd_total_carrinho > 0 else "🛒 Ver Carrinho"
if st.button(fab_cart_label, key="btn_fab_carrinho_fixo", type="primary" if qtd_total_carrinho > 0 else "secondary"):
    modal_carrinho_mesa()

import streamlit as st
import importlib
import html
import data_manager
import ui_components

importlib.reload(data_manager)
importlib.reload(ui_components)

st.set_page_config(
    page_title="Cardápio Digital — ChurrasControl",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização Mobile-First Profissional e Gastronômica Executiva (Sem emojis, com SVGs e estética refinada)
st.markdown("""
<style>
/* 1. Oculta completamente sidebars e barras de navegação administrativas */
[data-testid="stSidebarNav"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }

/* 2. Container Principal Responsivo */
.block-container {
    padding-top: 0.6rem !important;
    padding-bottom: 6.5rem !important;
    padding-left: max(10px, env(safe-area-inset-left, 10px)) !important;
    padding-right: max(10px, env(safe-area-inset-right, 10px)) !important;
    max-width: 1200px !important;
    margin: 0 auto !important;
}

/* Paleta de Cores e Tipografia */
:root {
    --bg-dark: #12141a;
    --card-bg: #1c202a;
    --primary-orange: #ff6f00;
    --primary-hover: #e65100;
    --gold: #ffb300;
    --text-white: #ffffff;
    --text-muted: #94a3b8;
}

/* 3. Header do Cliente Flexível e Adaptativo com SVG Profissional */
.cliente-header-box {
    background: linear-gradient(135deg, #1e2430 0%, #151820 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.4);
}

.cliente-brand-group {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
}

.cliente-brand-icon-wrap {
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, rgba(255, 111, 0, 0.2) 0%, rgba(230, 81, 0, 0.35) 100%);
    border: 1px solid rgba(255, 111, 0, 0.4);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.cliente-brand-text {
    display: flex;
    flex-direction: column;
    min-width: 0;
}

.cliente-brand-title {
    font-size: clamp(1.1rem, 4vw, 1.45rem);
    font-weight: 900;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.5px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.cliente-brand-title span {
    color: var(--primary-orange);
}

.cliente-brand-sub {
    font-size: clamp(0.65rem, 2.2vw, 0.78rem);
    color: var(--text-muted);
    font-weight: 700;
    letter-spacing: 0.5px;
    margin: 2px 0 0 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.mesa-badge-cliente {
    background: linear-gradient(135deg, #e65100 0%, #ff8f00 100%);
    color: #ffffff;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 800;
    font-size: clamp(0.78rem, 2.8vw, 0.92rem);
    box-shadow: 0 3px 10px rgba(230, 81, 0, 0.4);
    display: inline-flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
    flex-shrink: 0;
}

/* 4. Botão de Ação do Topo */
div[class*="st-key-btn_nav_carrinho"] {
    margin-bottom: 12px !important;
}
div[class*="st-key-btn_nav_carrinho"] button {
    border-radius: 12px !important;
    font-weight: 800 !important;
    padding: 10px 16px !important;
    font-size: 0.95rem !important;
}

/* 5. Categorias Pills Touch-Friendly com Scroll Horizontal */
[data-testid="stPills"] {
    display: flex !important;
    overflow-x: auto !important;
    flex-wrap: nowrap !important;
    gap: 8px !important;
    padding-bottom: 6px !important;
    margin-bottom: 14px !important;
    scrollbar-width: none !important;
    -webkit-overflow-scrolling: touch !important;
}
[data-testid="stPills"]::-webkit-scrollbar {
    display: none !important;
}
[data-testid="stPills"] > div {
    flex-shrink: 0 !important;
}

/* 6. Card Gastronômico do Cliente */
.client-card {
    background: #1c202a;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px 16px 0 0;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    transition: transform 0.2s ease, border-color 0.2s ease;
    display: flex;
    flex-direction: column;
    cursor: pointer !important;
}
[data-testid="stColumn"]:hover .client-card {
    border-color: rgba(255, 111, 0, 0.45);
}

.client-img-wrap {
    position: relative;
    width: 100%;
    height: 180px;
    background: #2a2f3d;
    overflow: hidden;
}
.client-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}
[data-testid="stColumn"]:hover .client-img {
    transform: scale(1.04);
}

.badge-estoque-ok {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(46, 125, 50, 0.92);
    color: #fff;
    padding: 4px 8px;
    border-radius: 14px;
    font-size: 0.72rem;
    font-weight: 800;
    backdrop-filter: blur(4px);
    display: inline-flex;
    align-items: center;
    gap: 4px;
}
.badge-estoque-off {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(211, 47, 47, 0.94);
    color: #fff;
    padding: 4px 8px;
    border-radius: 14px;
    font-size: 0.72rem;
    font-weight: 800;
    backdrop-filter: blur(4px);
}
.badge-cat {
    position: absolute;
    bottom: 10px;
    left: 10px;
    background: rgba(0, 0, 0, 0.78);
    color: #ffb74d;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 700;
    border: 1px solid rgba(255, 183, 77, 0.3);
}

.client-content {
    padding: 14px;
    display: flex;
    flex-direction: column;
    flex-grow: 1;
}
.client-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 6px 0;
    line-height: 1.25;
}
.client-desc {
    font-size: 0.82rem;
    color: #94a3b8;
    line-height: 1.35;
    margin-bottom: 12px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.client-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    padding-top: 10px;
    margin-top: auto;
}
.client-price {
    font-size: 1.2rem;
    font-weight: 900;
    color: #ffb300;
}
.client-action-hint {
    font-size: 0.78rem;
    font-weight: 700;
    color: #ff9800;
}

/* 7. Botão Acoplado Perfeitamente ao Card */
[data-testid="stColumn"] > div:has(.client-card) + div button {
    border-top-left-radius: 0 !important;
    border-top-right-radius: 0 !important;
    border-bottom-left-radius: 14px !important;
    border-bottom-right-radius: 14px !important;
    margin-top: -1px !important;
    background: #252b38 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-top: 0 !important;
    color: #ff9800 !important;
    font-weight: 800 !important;
    padding: 9px 12px !important;
    transition: background 0.2s ease !important;
}
[data-testid="stColumn"]:hover > div:has(.client-card) + div button {
    background: #ff6f00 !important;
    color: #ffffff !important;
}

/* 8. Grid Responsivo Universal (1 card/linha em telas <= 768px, 3 em desktop) */
@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"]:has(.client-card) {
        display: flex !important;
        flex-direction: column !important;
        width: 100% !important;
        gap: 16px !important;
    }
    [data-testid="stHorizontalBlock"]:has(.client-card) > [data-testid="stColumn"] {
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        flex: 1 1 100% !important;
    }
    .client-img-wrap {
        height: 190px !important;
    }
}

/* 9. Botão Flutuante do Carrinho (Floating Action Button) */
div[class*="st-key-btn_fab_carrinho_fixo"] {
    position: fixed !important;
    bottom: calc(14px + env(safe-area-inset-bottom, 0px)) !important;
    right: 14px !important;
    z-index: 999999 !important;
    width: auto !important;
    max-width: calc(100vw - 28px) !important;
}
div[class*="st-key-btn_fab_carrinho_fixo"] button {
    background: linear-gradient(135deg, #e65100 0%, #ff8f00 100%) !important;
    color: #ffffff !important;
    border: 2px solid rgba(255, 255, 255, 0.5) !important;
    border-radius: 40px !important;
    padding: 11px 20px !important;
    font-size: clamp(0.85rem, 3.2vw, 1.02rem) !important;
    font-weight: 800 !important;
    box-shadow: 0 8px 24px rgba(230, 81, 0, 0.7), 0 2px 8px rgba(0, 0, 0, 0.4) !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    cursor: pointer !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
div[class*="st-key-btn_fab_carrinho_fixo"] button:hover {
    transform: scale(1.05) !important;
}

/* 10. Ajustes para Telas Ultra-Pequenas (320px até 380px) */
@media (max-width: 380px) {
    .cliente-header-box { padding: 8px 10px; }
    .cliente-brand-icon-wrap { width: 32px; height: 32px; }
    .mesa-badge-cliente { padding: 5px 10px; font-size: 0.75rem; }
    .client-img-wrap { height: 160px !important; }
    .client-content { padding: 10px; }
    .client-title { font-size: 0.98rem; }
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
    except Exception:
        pass
    return None

# ================= MODAL RESPONSIVO DE CARRINHO & COMANDA =================
@st.dialog(f"Pré-Comanda & Histórico — Mesa {mesa_atual:02d}")
def modal_carrinho_mesa():
    itens_carrinho = st.session_state[session_key]
    historico = obter_historico_comanda_mesa(mesa_atual)

    tab_novos, tab_historico = st.tabs([
        f"Novos Pratos ({len(itens_carrinho)})", 
        f"Histórico Confirmado ({len(historico['itens']) if historico else 0})"
    ])

    with tab_novos:
        if not itens_carrinho:
            st.info("Sua pré-comanda está vazia. Toque em qualquer prato do cardápio para adicioná-lo.")
        else:
            st.markdown("Revise seus pratos antes de enviar para a cozinha:")
            st.markdown("---")

            subtotal_novos = 0.0
            indices_para_remover = []

            for idx, item in enumerate(itens_carrinho):
                # Linha 1: Título e Botão de Excluir
                c_top_title, c_top_del = st.columns([5, 1])
                with c_top_title:
                    st.markdown(f"**{item['nome']}**")
                    st.caption(f"Valor unitário: R$ {item['preco_unitario']:.2f}")
                with c_top_del:
                    if st.button("Remover", key=f"cart_del_{idx}", help="Remover prato"):
                        indices_para_remover.append(idx)

                # Linha 2: Campo de Observação com 100% de largura
                obs_digitada = st.text_input(
                    f"Observação:", 
                    value=item.get("observacao", ""), 
                    key=f"cart_obs_{idx}",
                    placeholder="Ex: Sem cebola, carne ao ponto..."
                )
                item["observacao"] = obs_digitada

                # Linha 3: Quantidade e Subtotal lado a lado
                c_sub_qtd, c_sub_tot = st.columns([1, 1])
                with c_sub_qtd:
                    nova_qtd = st.number_input(
                        "Quantidade", 
                        min_value=1, 
                        max_value=20, 
                        value=int(item["quantidade"]), 
                        key=f"cart_qtd_{idx}"
                    )
                    item["quantidade"] = nova_qtd
                with c_sub_tot:
                    sub_item = nova_qtd * item["preco_unitario"]
                    subtotal_novos += sub_item
                    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:right; font-weight:800; color:#ffb300; font-size:1.05rem;'>R$ {sub_item:.2f}</div>", unsafe_allow_html=True)

                st.markdown("<hr style='margin:10px 0; border:0; border-top:1px dashed #37474f;'>", unsafe_allow_html=True)

            if indices_para_remover:
                for rem_idx in sorted(indices_para_remover, reverse=True):
                    st.session_state[session_key].pop(rem_idx)
                st.rerun()

            st.markdown(f"""
            <div style="background:#262a34; border-radius:12px; padding:12px 16px; margin:14px 0; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <span style="font-size:1rem; color:#b0bec5; font-weight:700;">Subtotal Novos Pratos:</span>
                <span style="font-size:1.3rem; color:#ffb300; font-weight:900;">R$ {subtotal_novos:.2f}</span>
            </div>
            """, unsafe_allow_html=True)

            col_btn_fechar, col_btn_confirmar = st.columns([1, 2])
            with col_btn_fechar:
                if st.button("Continuar Escolhendo", use_container_width=True):
                    st.rerun()
            with col_btn_confirmar:
                if st.button("Confirmar e Enviar Pedido", type="primary", use_container_width=True):
                    try:
                        res = data_manager.confirmar_precomanda_cliente(mesa_atual, st.session_state[session_key])
                        st.session_state[session_key] = []
                        st.session_state[f"ultimo_pedido_sucesso_mesa_{mesa_atual}"] = res
                        st.toast("Pedido enviado com sucesso para a cozinha!", icon=None)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao confirmar pedido: {e}")

    with tab_historico:
        if not historico or not historico.get("itens"):
            st.info("Nenhum pedido anterior foi registrado para esta mesa ainda. Assim que você confirmar seus pratos, eles aparecerão aqui.")
        else:
            st.markdown(f"""
            <div style="margin-bottom:12px;">
                <span style="font-size:0.9rem; color:#90a4ae;">Comanda Nº <strong>#{historico['comanda']['id']}</strong> | Status: <strong>{historico['comanda']['status']}</strong></span>
            </div>
            """, unsafe_allow_html=True)

            for it_hist in historico["itens"]:
                c_h1, c_h2 = st.columns([3, 1])
                with c_h1:
                    st.markdown(f"**{it_hist['produto_nome']}** ({it_hist['quantidade']}x)")
                    if it_hist.get("observacao"):
                        st.caption(f"Obs: {it_hist['observacao']}")
                with c_h2:
                    st.markdown(f"<div style='text-align:right; font-weight:700; color:#81c784;'>R$ {it_hist['subtotal']:.2f}</div>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:4px 0; border:0; border-top:1px solid rgba(255,255,255,0.06);'>", unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:rgba(46,125,50,0.15); border:1px solid rgba(76,175,80,0.3); border-radius:12px; padding:12px 16px; margin-top:14px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <span style="font-size:1rem; color:#a5d6a7; font-weight:700;">Total Acumulado na Comanda:</span>
                <span style="font-size:1.3rem; color:#81c784; font-weight:900;">R$ {historico['total']:.2f}</span>
            </div>
            """, unsafe_allow_html=True)

# ================= MODAL DE ADIÇÃO RÁPIDA AO CLICAR NO CARD =================
@st.dialog("Adicionar ao Pedido")
def modal_adicionar_prato(produto: dict):
    st.markdown(f"""
    <div style="display:flex; gap:14px; align-items:center; margin-bottom:12px; flex-wrap:wrap;">
        <img src="{produto['url_imagem']}" style="width:78px; height:78px; border-radius:12px; object-fit:cover;"/>
        <div style="min-width:0; flex:1;">
            <h3 style="margin:0; color:#fff; font-size:1.15rem; line-height:1.2;">{produto['nome']}</h3>
            <span style="color:#ffb300; font-weight:800; font-size:1.2rem;">R$ {float(produto['preco_unitario']):.2f}</span>
        </div>
    </div>
    <p style="color:#94a3b8; font-size:0.86rem; line-height:1.35; margin-bottom:12px;">{produto.get('descricao', '')}</p>
    """, unsafe_allow_html=True)

    saldo_disp = max(1, produto.get("qtd_disp") or 10)
    qtd = st.number_input("Quantidade Desejada", min_value=1, max_value=saldo_disp, value=1)
    obs = st.text_input("Alguma preferência ou observação?", placeholder="Ex: Carne ao ponto, sem cebola, etc.")

    if st.button("Adicionar à Pré-Comanda", type="primary", use_container_width=True):
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
        st.toast(f"{produto['nome']} adicionado ao carrinho!", icon=None)
        st.rerun()

# ================= TELA PRINCIPAL DO CLIENTE =================

carrinho_atual = st.session_state[session_key]
qtd_total_carrinho = sum(it["quantidade"] for it in carrinho_atual)
total_carrinho = sum(it["quantidade"] * it["preco_unitario"] for it in carrinho_atual)

# 1. Header do Cliente Fluído com SVG Profissional
st.markdown(f"""
<div class="cliente-header-box">
    <div class="cliente-brand-group">
        <div class="cliente-brand-icon-wrap">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ff6f00" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>
            </svg>
        </div>
        <div class="cliente-brand-text">
            <h1 class="cliente-brand-title">Churras<span>Control</span></h1>
            <p class="cliente-brand-sub">CARDÁPIO DIGITAL • AUTOATENDIMENTO</p>
        </div>
    </div>
    <div class="mesa-badge-cliente">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
        MESA {mesa_atual:02d}
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Barra Superior de Resumo e Acesso ao Carrinho
btn_top_cart_label = f"Ver Pré-Comanda ({qtd_total_carrinho} itens • R$ {total_carrinho:.2f})" if qtd_total_carrinho > 0 else "Ver Pré-Comanda da Mesa"
if st.button(btn_top_cart_label, type="primary" if qtd_total_carrinho > 0 else "secondary", use_container_width=True, key="btn_nav_carrinho"):
    modal_carrinho_mesa()

# Mensagem de confirmação se enviou pedido recentemente
if f"ultimo_pedido_sucesso_mesa_{mesa_atual}" in st.session_state:
    ped_info = st.session_state.pop(f"ultimo_pedido_sucesso_mesa_{mesa_atual}")
    st.success(f"Pedido confirmado com sucesso! A comanda #{ped_info['comanda_id']} recebeu {ped_info['total_itens']} novos itens enviados para a cozinha.")

# 3. Barra de Pesquisa de Pratos
termo_busca = st.text_input("Buscar no Cardápio:", placeholder="Pesquise por picanha, cortes, bebidas, porções...")

# 4. Categorias Rápidas em Chips (com scroll horizontal touch)
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
    <div style="background:linear-gradient(135deg, rgba(230,81,0,0.18) 0%, rgba(255,111,0,0.28) 100%); border:1px solid rgba(255,111,0,0.45); border-radius:12px; padding:10px 14px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
        <span style="font-size:0.95rem; font-weight:800; color:#fff;">Mesa {mesa_atual:02d}: <span style="color:#ffb74d;">{qtd_total_carrinho} novos itens (R$ {total_carrinho:.2f})</span></span>
        <span style="font-size:0.8rem; color:#b0bec5;">Toque em 'Ver Pré-Comanda' para revisar</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"<div style='color:#94a3b8; font-size:0.84rem; margin-bottom:12px;'>Exibindo <strong>{len(produtos_filtrados)}</strong> opções no cardápio</div>", unsafe_allow_html=True)

# 5. Grid Gastronômico 100% Clicável (Auto-adaptativo para telas de 320px a 4K)
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
        
        badge_estoque = '<span class="badge-estoque-off">Esgotado</span>' if esta_esgotado else f'<span class="badge-estoque-ok"><span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#4ade80;"></span>{saldo_disp} un</span>'
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
                        <span class="client-action-hint">{'Indisponível' if esta_esgotado else 'Pedir'}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão de Ação Integrado (Acoplado à base do card)
            if esta_esgotado:
                st.button("Indisponível", key=f"btn_esgotado_{prod['id']}", disabled=True, use_container_width=True)
            else:
                if st.button("Adicionar ao Pedido", key=f"btn_choose_{prod['id']}", use_container_width=True):
                    modal_adicionar_prato(prod)
            
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

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
fab_cart_label = f"Ver Pré-Comanda ({qtd_total_carrinho})" if qtd_total_carrinho > 0 else "Ver Pré-Comanda"
if st.button(fab_cart_label, key="btn_fab_carrinho_fixo", type="primary" if qtd_total_carrinho > 0 else "secondary"):
    modal_carrinho_mesa()

import importlib
import streamlit as st
import data_manager
importlib.reload(data_manager)
import ui_components
importlib.reload(ui_components)

st.set_page_config(
    page_title="Cardápio Digital - ChurrasControl",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Navbar superior unificada
ui_components.render_navbar(active_tab="cardapio_digital")

# Diálogo Modal Saltado na Tela com Detalhes Completos do Prato
@st.dialog("🍽️ Detalhes do Prato", width="large")
def dialog_detalhes_prato(p):
    img_url = p.get("url_imagem")
    if not img_url or img_url.strip() == "":
        img_url = "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&auto=format&fit=crop&q=80"

    badge_prod = "🔥 Preparado na Brasa Viva" if p.get("precisa_produzir") else "⚡ Servido Imediatamente"
    disp_status = "🟢 Disponível no Cardápio" if p.get("disponivel", 1) else "🔴 Esgotado Temporariamente"

    st.markdown(f"""
    <meta name="referrer" content="no-referrer">
    <div style="border-radius: 14px; overflow: hidden; margin-bottom: 16px; border: 1px solid rgba(255,255,255,0.12); background: #0f172a; max-height: 380px;">
        <img src="{img_url}" referrerpolicy="no-referrer" style="width: 100%; height: 320px; object-fit: cover;" onerror="this.src='https://images.unsplash.com/photo-1544025162-d76694265947?w=800'">
    </div>
    
    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 14px; margin-bottom: 10px;">
        <div>
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 0.76rem; color: #f59e0b; background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.25); padding: 3px 8px; border-radius: 6px; font-weight: 700;">
                    🏷️ {p.get('categoria', 'Geral')}
                </span>
                <span style="font-size: 0.76rem; color: #cbd5e1; background: rgba(255,255,255,0.06); padding: 3px 8px; border-radius: 6px; font-weight: 600;">
                    CÓD #{p.get('codigo_pdv', '')}
                </span>
            </div>
            <h2 style="margin: 0; color: #ffffff; font-size: 1.65rem; font-weight: 800; line-height: 1.2;">
                {p.get('nome', '')}
            </h2>
        </div>
        <div style="text-align: right; min-width: 130px;">
            <div style="font-size: 1.75rem; font-weight: 800; color: #fbbf24;">
                R$ {float(p.get('preco_unitario', 0)):,.2f}
            </div>
            <div style="font-size: 0.78rem; color: #94a3b8;">Preço Comercial</div>
        </div>
    </div>

    <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 14px 0;">

    <div style="margin-bottom: 16px;">
        <h4 style="margin: 0 0 6px 0; color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;">
            📖 Descrição Gastronômica
        </h4>
        <p style="color: #cbd5e1; font-size: 1.02rem; line-height: 1.6; margin: 0; background: rgba(255,255,255,0.02); padding: 12px 14px; border-radius: 10px; border-left: 3px solid #f59e0b;">
            {p.get('descricao') or 'Prato preparado artesanalmente com ingredientes de alta qualidade pela equipe do ChurrasControl.'}
        </p>
    </div>

    <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 18px;">
        <span style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; color: #e2e8f0;">
            {badge_prod}
        </span>
        <span style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; color: {'#10b981' if p.get('disponivel', 1) else '#ef4444'};">
            {disp_status}
        </span>
        <span style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; color: #cbd5e1;">
            📦 Estoque: <strong>{p.get('qtd_disp', 0)} unidades</strong>
        </span>
    </div>
    """, unsafe_allow_html=True)

# CSS exclusivo para o Cardápio Digital (Mobile First, Imgur Safe & Delivery)
st.markdown("""
<meta name="referrer" content="no-referrer">
<style>
    /* Estilos do Modo Delivery e Cardápio de Restaurante */
    .delivery-hero {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.88) 0%, rgba(15, 23, 42, 0.96) 100%),
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
    [data-testid="stColumn"] {
        position: relative !important;
    }
    .card-delivery {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
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
</style>
""", unsafe_allow_html=True)

# URL de compartilhamento da tela de cardápio digital
share_url = "http://localhost:8501/Cardapio_Digital"
qr_code_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=260x260&margin=10&data={share_url}"

# Cabeçalho com ações de retorno ao PDV e QR Code
c_top_voltar, c_top_qr = st.columns([4, 2], vertical_alignment="center")
with c_top_voltar:
    if st.button("⬅️ Voltar para Gestão de Produtos (PDV)", type="secondary"):
        st.switch_page("pages/2_Cardapio.py")
with c_top_qr:
    with st.popover("📱 Compartilhar / QR Code da Mesa", use_container_width=True):
        st.markdown("""
        <div style="text-align: center; padding: 4px 0;">
            <h4 style="margin: 0 0 6px 0; color: #f59e0b; font-size: 1.1rem; font-weight: 800;">
                📲 Escanear Cardápio no Celular
            </h4>
            <p style="font-size: 0.82rem; color: #94a3b8; margin-bottom: 14px;">
                Aponte a câmera do seu smartphone para o QR Code abaixo para abrir este cardápio diretamente no aparelho!
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.image(qr_code_api_url, caption="QR Code Oficial da Mesa / Salão", use_container_width=True)

        st.markdown(f"""
        <div style="margin-top: 10px; background: rgba(0,0,0,0.3); border: 1px dashed rgba(255,255,255,0.15); border-radius: 8px; padding: 10px; word-break: break-all; font-size: 0.78rem; color: #cbd5e1;">
            <strong>Link de Compartilhamento:</strong><br>
            <code>{share_url}</code>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# Banner Gastronômico do Restaurante
st.markdown("""
<div class="delivery-hero">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
        <div>
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span class="delivery-badge-open">● Cozinha Aberta</span>
                <span class="delivery-badge-tag">🔥 Parrilla & Culinária Mineira</span>
                <span class="delivery-badge-tag">⭐ 4.9 (1.4k avaliações)</span>
            </div>
            <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #ffffff; letter-spacing: -0.03em;">
                ChurrasControl • Parrilla Bar & Smokehouse
            </h1>
            <p style="margin: 6px 0 0 0; color: #cbd5e1; font-size: 0.95rem; max-width: 680px;">
                Cortes nobres preparados na brasa viva, tradicionais pratos caseiros mineiros, sucos de frutas naturais frescos e sobremesas artesanais.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Barra de Pesquisa e Filtros
c_sh1, c_sh2 = st.columns([4, 1.2], vertical_alignment="center")
with c_sh1:
    busca_cardapio = st.text_input("🔍 O que você deseja ver hoje?", placeholder="Digite o nome do prato, corte ou bebida (Ex: Picanha, Feijoada, Maracujá)...", label_visibility="collapsed")
with c_sh2:
    if st.button("🔄 Sincronizar Xano", help="Puxar últimas fotos e produtos atualizados no Xano", use_container_width=True):
        try:
            qtd_sync = data_manager.sincronizar_produtos_xano()
            st.toast(f"✓ {qtd_sync} produtos sincronizados do Xano!", icon="✅")
            st.rerun()
        except Exception as ex:
            st.error(f"Erro ao sincronizar com Xano: {ex}")

# Obter produtos cadastrados com fotos reais
produtos_todos = data_manager.listar_produtos(busca=busca_cardapio)

# Filtros de Categorias em Chips
categorias_disponiveis = ["Todas"] + sorted(list(set(p.get("categoria", "Geral") for p in produtos_todos if p.get("categoria"))))
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
        <p style="color: #94a3b8; font-size: 0.9rem;">Tente pesquisar por outro termo ou selecione outra categoria acima.</p>
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

                badge_prod = "🔥 Na Brasa" if p.get("precisa_produzir") else "⚡ Pronta Entrega"
                badge_disp = f"⚠️ Restam {p.get('qtd_disp')} un." if p.get("qtd_disp", 0) <= 5 else f"Estoque: {p.get('qtd_disp')} un."
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
                                🏷️ CÓD {p['codigo_pdv']} • {p['categoria']}
                            </span>
                            <span style="font-size: 0.72rem; color: {'#ef4444' if is_indisponivel else '#10b981'}; font-weight: 700;">
                                {'ESGOTADO' if is_indisponivel else badge_disp}
                            </span>
                        </div>
                        <h4 class="card-title">{p['nome']}</h4>
                        <p class="card-desc">{p.get('descricao') or 'Prato preparado com ingredientes frescos e seleção artesanal da casa.'}</p>
                        <div class="card-footer-box">
                            <span class="card-price">R$ {float(p['preco_unitario']):,.2f}</span>
                            <span style="font-size: 0.78rem; color: #f59e0b; font-weight: 600;">Ver detalhes ✨</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Botão invisível nativo que aciona o modal sem nenhum F5 ou recarregamento
                if st.button("", key=f"btn_prod_card_{p['id']}", use_container_width=True):
                    dialog_detalhes_prato(p)

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

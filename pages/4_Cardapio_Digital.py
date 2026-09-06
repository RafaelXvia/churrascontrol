import streamlit as st
import data_manager
import ui_components

st.set_page_config(
    page_title="Cardápio Digital - ChurrasControl",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Navbar superior unificada
ui_components.render_navbar(active_tab="cardapio_digital")

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
    .card-delivery {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .card-delivery:hover {
        transform: translateY(-4px);
        box-shadow: 0 14px 30px -6px rgba(0, 0, 0, 0.7);
        border-color: rgba(245, 158, 11, 0.45);
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
    busca_cardapio = st.text_input("🔍 O que você deseja pedir hoje?", placeholder="Digite o nome do prato, corte ou bebida (Ex: Picanha, Feijoada, Maracujá)...", label_visibility="collapsed")
with c_sh2:
    if st.button("🔄 Sincronizar Xano", help="Puxar últimas fotos e produtos atualizados no Xano", use_container_width=True):
        qtd_sync = data_manager.sincronizar_produtos_xano()
        st.success(f"{qtd_sync} produtos sincronizados!")
        st.rerun()

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
    # Mesas abertas para permitir lançar pedido direto no salão
    mesas_ativas = [m for m in data_manager.listar_mesas() if m.get("comanda_ativa_id")]

    # Renderização em Grid de 3 Colunas
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

                # Card com referrerpolicy='no-referrer' para carregar Imgur perfeitamente sem bloqueios
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
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Botão interativo para pedir diretamente para a mesa ou simular pedido
                with st.popover(f"🍽️ Pedir #{p['codigo_pdv']}", use_container_width=True):
                    st.markdown(f"**Lançar Pedido: {p['nome']}**")
                    st.caption(f"Valor Unitário: R$ {float(p['preco_unitario']):,.2f}")

                    if not mesas_ativas:
                        st.info("💡 Nenhuma mesa aberta no salão agora. Você pode abrir uma mesa em 'Salão & Mesas' ou simular a seleção.")
                    else:
                        opcoes_mesas = {f"Mesa {m['numero_mesa']} (Comanda #{m['comanda_ativa_id']})": m for m in mesas_ativas}
                        mesa_sel = st.selectbox("Selecione a Mesa de Destino", list(opcoes_mesas.keys()), key=f"sel_m_dig_{p['id']}")
                        qtd_pedido = st.number_input("Quantidade", min_value=1, max_value=99, value=1, key=f"qtd_m_dig_{p['id']}")
                        obs_pedido = st.text_input("Observação / Ponto", placeholder="Ex: ao ponto, bem passada, sem gelo", key=f"obs_m_dig_{p['id']}")

                        if st.button("✓ Confirmar Pedido na Mesa", key=f"btn_ped_dig_{p['id']}", type="primary", use_container_width=True):
                            mesa_obj = opcoes_mesas[mesa_sel]
                            data_manager.adicionar_item_comanda(
                                comanda_id=mesa_obj["comanda_ativa_id"],
                                produto_id=p["id"],
                                quantidade=int(qtd_pedido),
                                observacao=obs_pedido
                            )
                            st.success(f"✓ {qtd_pedido}x '{p['nome']}' lançado com sucesso na Mesa {mesa_obj['numero_mesa']}!")
                            st.rerun()

                st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# Rodapé Executivo
ui_components.render_footer()

import streamlit as st
import importlib
import urllib.parse
import html
import data_manager
import ui_components

importlib.reload(data_manager)
importlib.reload(ui_components)

st.set_page_config(
    page_title="ChurrasControl — QR Codes das Mesas",
    page_icon="🪪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Oculta sidebar nativa para garantir separação total da navegação
st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* Estilos de Cartão de Mesa e QR Code */
.mesa-card {
    background: #181c24;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    transition: transform 0.2s ease, border-color 0.2s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}
.mesa-card:hover {
    transform: translateY(-3px);
    border-color: rgba(230, 81, 0, 0.4);
}
.mesa-title {
    font-size: 1.4rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 6px;
}
.status-badge-livre {
    background: rgba(46, 125, 50, 0.2);
    color: #81c784;
    border: 1px solid rgba(76, 175, 80, 0.4);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
    display: inline-block;
    margin-bottom: 14px;
}
.status-badge-ocupada {
    background: rgba(198, 40, 40, 0.2);
    color: #e57373;
    border: 1px solid rgba(239, 83, 80, 0.4);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
    display: inline-block;
    margin-bottom: 14px;
}
.qr-container {
    background: #ffffff;
    padding: 14px;
    border-radius: 14px;
    display: inline-block;
    margin: 10px 0 16px 0;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}
.token-info {
    font-size: 0.75rem;
    color: #9e9e9e;
    margin-bottom: 12px;
    font-family: monospace;
}
.consumo-info {
    font-size: 0.95rem;
    color: #ffb74d;
    font-weight: 700;
    margin-bottom: 10px;
}
@media print {
    body * { visibility: hidden; }
    .printable-area, .printable-area * { visibility: visible; }
    .printable-area { position: absolute; left: 0; top: 0; width: 100%; }
}
</style>
""", unsafe_allow_html=True)

# Barra de apoio discreta no topo para voltar ao sistema ou ver status
col_back, col_title_head = st.columns([1, 4])
with col_back:
    st.markdown('<a href="/Salao_e_Mesas" target="_self" style="text-decoration:none;"><button style="background:#262a34; color:#fff; border:1px solid #444; border-radius:8px; padding:8px 16px; cursor:pointer; font-weight:600; width:100%;">← Voltar ao Salão</button></a>', unsafe_allow_html=True)
with col_title_head:
    st.markdown('<h2 style="margin:0; color:#fff; font-weight:800;">🪪 Central de QR Codes das Mesas (Simulador Físico)</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-top:4px;">
        <span style="color:#94a3b8; font-size:0.86rem;">Página que simula as placas das mesas físicas. O QR Code só muda quando você clica em Atualizar.</span>
        <div style="background:rgba(34, 197, 94, 0.12); border:1px solid rgba(34, 197, 94, 0.35); border-radius:20px; padding:4px 12px; font-size:0.8rem; color:#86efac; display:inline-flex; align-items:center; gap:6px; font-weight:700;">
            <span style="width:7px; height:7px; border-radius:50%; background:#22c55e; display:inline-block; animation: pulse 2s infinite;"></span>
            ⏱️ Auto-atualização ativa a cada 1m
        </div>
    </div>
    """, unsafe_allow_html=True)

# JavaScript para auto-atualizar a cada 1 minuto (60.000 ms)
st.html("""
<script>
(function() {
    if (window._mesasRefreshTimer) clearTimeout(window._mesasRefreshTimer);
    window._mesasRefreshTimer = setTimeout(function() {
        window.location.reload();
    }, 60000);
})();
</script>
""")

st.divider()

# Carrega mesas e status atual
mesas_qr = data_manager.listar_mesas_qrcodes()

total_mesas = len(mesas_qr)
total_ocupadas = sum(1 for m in mesas_qr if m["status"] == "OCUPADA")
total_livres = total_mesas - total_ocupadas
faturamento_ativo = sum(m["total_atual"] for m in mesas_qr)

# Métricas do Salão
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total de Mesas Físicas", f"{total_mesas} Mesas")
m2.metric("Mesas Livres", f"{total_livres} Livres", delta="Prontas para clientes")
m3.metric("Mesas Ocupadas", f"{total_ocupadas} Ocupadas", delta="- Em atendimento")
m4.metric("Consumo em Aberto", f"R$ {faturamento_ativo:.2f}")

st.markdown("---")

# Obtém a base URL do servidor (padrão local http://localhost:8501)
base_url = "http://localhost:8501"

# Exibe as mesas em grade de 3 colunas
cols_per_row = 3
for i in range(0, len(mesas_qr), cols_per_row):
    cols = st.columns(cols_per_row)
    for j in range(cols_per_row):
        idx = i + j
        if idx >= len(mesas_qr):
            break
        
        m = mesas_qr[idx]
        col = cols[j]
        
        num_mesa = m["numero_mesa"]
        token = m["token_qrcode"]
        status = m["status"]
        consumo = m["total_atual"]
        
        # URL do Cardápio Digital do Cliente para esta mesa
        url_cliente = f"{base_url}/Cardapio_Cliente?mesa={num_mesa}&token={token}"
        url_encoded = urllib.parse.quote(url_cliente)
        qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=260x260&margin=10&data={url_encoded}"
        
        badge_html = f'<span class="status-badge-ocupada">🔴 MESA OCUPADA</span>' if status == "OCUPADA" else f'<span class="status-badge-livre">🟢 MESA LIVRE</span>'
        consumo_html = f'<div class="consumo-info">Consumo Atual: R$ {consumo:.2f}</div>' if status == "OCUPADA" else '<div class="consumo-info" style="color:#78909c;">Sem consumo ativo</div>'

        with col:
            st.markdown(f"""
            <div class="mesa-card">
                <div class="mesa-title">Mesa {num_mesa:02d}</div>
                {badge_html}
                <div class="qr-container">
                    <img src="{qr_image_url}" width="180" height="180" alt="QR Code Mesa {num_mesa}" style="display:block;"/>
                </div>
                {consumo_html}
                <div class="token-info">Token: <code>{token}</code></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Botões de controle no Streamlit
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("🔄 Atualizar QR", key=f"btn_att_qr_{num_mesa}", use_container_width=True, help="Regera um novo token seguro para este QR Code"):
                    novo_tok = data_manager.atualizar_qrcode_mesa(num_mesa)
                    st.toast(f"QR Code da Mesa {num_mesa} atualizado com sucesso! (Novo token: {novo_tok})", icon="✅")
                    st.rerun()
            
            with btn_col2:
                # Botão para simular escaneamento abrindo o cardápio
                st.markdown(f"""
                <a href="{url_cliente}" target="_blank" style="text-decoration:none;">
                    <button style="width:100%; background:#e65100; color:#fff; border:none; padding:8px 10px; border-radius:8px; font-weight:700; cursor:pointer; font-size:0.85rem;">
                        📱 Testar Mesa {num_mesa}
                    </button>
                </a>
                """, unsafe_allow_html=True)
            
            # Link para copiar
            with st.expander("📋 Ver Link do QR Code", expanded=False):
                st.code(url_cliente, language="text")
                st.caption(f"Última alteração do QR: {m.get('atualizado_em', 'Inicial')[:19].replace('T', ' ')}")

import os
import streamlit as st
import importlib
import urllib.parse
import html
import data_manager
import ui_components

importlib.reload(data_manager)
importlib.reload(ui_components)

def detectar_base_url() -> str:
    """Detecta automaticamente o domínio base (Discloud HTTPS, ambiente de produção ou localhost)."""
    # 1. Variável de ambiente explícita
    env_url = os.getenv("APP_BASE_URL", "").strip().rstrip("/")
    if env_url:
        return env_url

    # 2. Detecção automática pelos headers da requisição HTTP no Streamlit
    try:
        if hasattr(st, "context") and hasattr(st.context, "headers") and st.context.headers:
            headers = st.context.headers
            host = headers.get("x-forwarded-host") or headers.get("host")
            proto = headers.get("x-forwarded-proto")
            if host:
                if not proto:
                    proto = "https" if ("discloud" in host or "https" in str(headers.get("referer", ""))) else "http"
                return f"{proto}://{host}".rstrip("/")
    except Exception:
        pass

    # 3. Se estiver em ambiente Discloud ou produção
    if os.getenv("DISCLOUD_APP_ID") or "discloud" in os.getenv("HOSTNAME", "").lower():
        return "https://churrascontrol.discloud.dev"

    # 4. Fallback padrão local
    return "http://localhost:8501"

st.set_page_config(
    page_title="ChurrasControl — QR Codes das Mesas",
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
div[class*="st-key-btn_silent_auto_refresh"] {
    position: absolute !important;
    opacity: 0 !important;
    pointer-events: none !important;
    height: 0px !important;
    width: 0px !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
}
</style>
""", unsafe_allow_html=True)

import streamlit.components.v1 as components

@st.fragment(run_every=60)
def painel_central_qrcodes():
    # Barra de apoio discreta no topo para voltar ao sistema ou ver status
    col_back, col_title_head, col_timer = st.columns([1, 3, 2])
    with col_back:
        st.markdown('<a href="/Salao_e_Mesas" target="_self" style="text-decoration:none;"><button style="background:#262a34; color:#fff; border:1px solid #444; border-radius:8px; padding:8px 16px; cursor:pointer; font-weight:600; width:100%;">← Voltar ao Salão</button></a>', unsafe_allow_html=True)
    with col_title_head:
        st.markdown('<h2 style="margin:0; color:#fff; font-weight:800;">Central de QR Codes das Mesas (Simulador Físico)</h2>', unsafe_allow_html=True)
        st.caption("Página isolada que simula as placas das mesas físicas. O QR Code só muda quando você clica em Atualizar.")
    with col_timer:
        # Componente visual com contagem regressiva viva de 60s descendo segundo a segundo
        components.html("""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        body {
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            justify-content: flex-end;
            align-items: center;
            height: 100%;
            overflow: hidden;
        }
        .timer-badge {
            background: rgba(34, 197, 94, 0.14);
            border: 1px solid rgba(34, 197, 94, 0.45);
            border-radius: 20px;
            padding: 6px 14px;
            font-size: 0.82rem;
            color: #86efac;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-weight: 700;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        }
        .pulse-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #22c55e;
            display: inline-block;
            box-shadow: 0 0 8px #22c55e;
        }
        .countdown-val {
            color: #ffffff;
            font-weight: 900;
            font-size: 0.95rem;
            background: rgba(0, 0, 0, 0.45);
            padding: 3px 10px;
            border-radius: 8px;
            min-width: 38px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
        </style>
        </head>
        <body>
        <div class="timer-badge">
            <span class="pulse-dot"></span>
            <span>Atualizando em:</span>
            <span id="timer_num" class="countdown-val">60s</span>
        </div>

        <script>
        let count = 60;
        const el = document.getElementById("timer_num");
        const interval = setInterval(() => {
            count--;
            if (count > 0) {
                if (el) el.innerText = count + "s";
            } else {
                if (el) el.innerText = "Atualizando...";
                setTimeout(() => {
                    count = 60;
                    if (el) el.innerText = "60s";
                }, 1500);
            }
        }, 1000);
        </script>
        </body>
        </html>
        """, height=48)

    st.divider()

    # Carrega mesas e status atual (leitura 100% no SQLite local, ultra-rápida e sem rate limit)
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

    # Obtém a base URL do servidor (detecta automaticamente Discloud HTTPS ou localhost)
    base_url = detectar_base_url()

    # Expander discreto para conferir ou alterar o domínio base
    with st.expander("Domínio dos QR Codes & Cardápio Digital", expanded=False):
        c_d1, c_d2 = st.columns([3, 1])
        with c_d1:
            base_url = st.text_input(
                "Domínio base para geração dos links e QR Codes",
                value=base_url,
                help="Na Discloud é https://churrascontrol.discloud.dev. Em ambiente local pode ser http://localhost:8501."
            ).rstrip("/")
        with c_d2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Discloud", use_container_width=True, help="Define para https://churrascontrol.discloud.dev"):
                base_url = "https://churrascontrol.discloud.dev"

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
            
            badge_html = f'<span class="status-badge-ocupada">MESA OCUPADA</span>' if status == "OCUPADA" else f'<span class="status-badge-livre">MESA LIVRE</span>'
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
                    if st.button("Atualizar QR", key=f"btn_att_qr_{num_mesa}", use_container_width=True, help="Regera um novo token seguro para este QR Code"):
                        novo_tok = data_manager.atualizar_qrcode_mesa(num_mesa)
                        st.toast(f"QR Code da Mesa {num_mesa} atualizado com sucesso! (Novo token: {novo_tok})")
                        st.rerun()
                
                with btn_col2:
                    # Botão para simular escaneamento abrindo o cardápio
                    st.markdown(f"""
                    <a href="{url_cliente}" target="_blank" style="text-decoration:none;">
                        <button style="width:100%; background:#e65100; color:#fff; border:none; padding:8px 10px; border-radius:8px; font-weight:700; cursor:pointer; font-size:0.85rem;">
                            Acessar Mesa {num_mesa}
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                
                # Link para copiar
                with st.expander("Ver Link do QR Code", expanded=False):
                    st.code(url_cliente, language="text")
                    st.caption(f"Última alteração do QR: {m.get('atualizado_em', 'Inicial')[:19].replace('T', ' ')}")

painel_central_qrcodes()

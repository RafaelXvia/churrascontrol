"""
ChurrasControl — Sistema de Design & Componentes Visuais Premium
Fornece Navbar no topo, Rodapé responsivo, remoção total da sidebar e estilos CSS modernos.
"""
import streamlit as st

def inject_custom_theme():
    """Injeta CSS de alta fidelidade visual, tipografia moderna e responsividade total."""
    st.markdown("""
    <style>
        /* Importação de Tipografia Moderna */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

        /* Ocultação Completa da Barra Lateral (Sidebar) em todas as telas */
        [data-testid="stSidebar"], 
        section[data-testid="stSidebar"], 
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        button[kind="header"] {
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            height: 0 !important;
        }

        /* Ocultação de menus de depuração do Streamlit */
        #MainMenu, footer, header[data-testid="stHeader"] {
            background-color: transparent !important;
        }
        
        /* Ajuste do Container Principal para Responsividade Extrema */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: #080c14 !important;
            color: #f1f5f9 !important;
            letter-spacing: -0.01em;
            -webkit-font-smoothing: antialiased;
        }

        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2.5rem !important;
            padding-left: clamp(0.75rem, 3.5vw, 2.8rem) !important;
            padding-right: clamp(0.75rem, 3.5vw, 2.8rem) !important;
            max-width: 1440px !important;
            margin: 0 auto !important;
        }

        /* ================= TOP NAVBAR UNIFICADA ================= */
        .st-key-cc_navbar_container {
            background: linear-gradient(180deg, rgba(17, 24, 39, 0.95) 0%, rgba(11, 15, 25, 0.92) 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 16px !important;
            padding: 8px 16px !important;
            margin-bottom: 1.25rem !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
        }

        .st-key-cc_navbar_container [data-testid="stHorizontalBlock"] {
            align-items: center !important;
            gap: 8px !important;
        }

        .cc-navbar-brand {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .cc-navbar-logo {
            width: 36px;
            height: 36px;
            border-radius: 9px;
            background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            box-shadow: 0 4px 12px rgba(217, 119, 6, 0.4);
            flex-shrink: 0;
        }

        .cc-navbar-title {
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #ffffff;
            white-space: nowrap;
            line-height: 1.1;
        }

        .cc-navbar-title span {
            color: #f59e0b;
        }

        .cc-navbar-tag {
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            background: rgba(245, 158, 11, 0.18);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.4);
            padding: 2px 6px;
            border-radius: 5px;
            text-transform: uppercase;
            margin-left: 4px;
            vertical-align: middle;
        }

        /* ================= NAVEGAÇÃO RESPONSIVA (DESKTOP & TELÕES) ================= */
        .st-key-cc_nav_desktop div.stButton > button {
            height: 40px !important;
            min-height: 40px !important;
            border-radius: 10px !important;
            font-size: 0.86rem !important;
            font-weight: 600 !important;
            padding: 6px 12px !important;
            white-space: nowrap !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        .st-key-cc_nav_desktop button[kind="primary"] {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.25) 0%, rgba(217, 119, 6, 0.35) 100%) !important;
            color: #fbbf24 !important;
            border: 1.5px solid #f59e0b !important;
            box-shadow: 0 0 16px rgba(245, 158, 11, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
            font-weight: 700 !important;
        }

        .st-key-cc_nav_desktop button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.03) !important;
            color: #94a3b8 !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
        }

        .st-key-cc_nav_desktop button[kind="secondary"]:hover {
            background: rgba(255, 255, 255, 0.08) !important;
            color: #f8fafc !important;
            border-color: rgba(245, 158, 11, 0.4) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }

        /* ================= MENU SANDUÍCHE RESPONSIVO (MOBILE & TABLETS) ================= */
        .st-key-cc_nav_mobile {
            width: 100% !important;
            padding: 4px 0 !important;
        }

        .st-key-cc_nav_mobile div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            justify-content: space-between !important;
            gap: 12px !important;
            width: 100% !important;
        }

        .st-key-cc_nav_mobile div[data-testid="stColumn"],
        .st-key-cc_nav_mobile div[data-testid="column"] {
            width: auto !important;
            min-width: 0 !important;
            flex: unset !important;
        }

        .st-key-cc_nav_mobile div[data-testid="stColumn"]:first-child,
        .st-key-cc_nav_mobile div[data-testid="column"]:first-child {
            flex: 1 1 auto !important;
        }

        .st-key-cc_nav_mobile div[data-testid="stColumn"]:last-child,
        .st-key-cc_nav_mobile div[data-testid="column"]:last-child {
            flex: 0 0 auto !important;
        }

        .st-key-cc_nav_mobile div[data-testid="stPopover"] {
            display: flex !important;
            justify-content: flex-end !important;
            width: 100% !important;
        }

        .st-key-cc_nav_mobile div[data-testid="stPopover"] > button,
        .st-key-cc_nav_mobile div[data-testid="stPopoverButton"] > button {
            height: 42px !important;
            min-height: 42px !important;
            width: 50px !important;
            border-radius: 12px !important;
            font-size: 1.35rem !important;
            font-weight: 800 !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%) !important;
            border: 1.5px solid rgba(245, 158, 11, 0.45) !important;
            color: #fbbf24 !important;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        .st-key-cc_nav_mobile div[data-testid="stPopover"] > button:hover,
        .st-key-cc_nav_mobile div[data-testid="stPopoverButton"] > button:hover {
            border-color: #f59e0b !important;
            color: #ffffff !important;
            background: linear-gradient(135deg, rgba(45, 60, 88, 0.95) 0%, rgba(20, 30, 52, 0.98) 100%) !important;
            box-shadow: 0 0 16px rgba(245, 158, 11, 0.45) !important;
            transform: translateY(-1px) scale(1.02) !important;
        }

        /* Drawer / Painel Aberto do Menu Sanduíche */
        div[data-testid="stPopoverBody"] {
            background: linear-gradient(160deg, #161e31 0%, #0d1321 100%) !important;
            border: 1.5px solid rgba(245, 158, 11, 0.4) !important;
            border-radius: 16px !important;
            box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.8), 0 0 25px rgba(245, 158, 11, 0.25) !important;
            padding: 16px !important;
        }

        div[data-testid="stPopoverBody"] div.stButton > button {
            height: 42px !important;
            min-height: 42px !important;
            border-radius: 10px !important;
            font-size: 0.90rem !important;
            font-weight: 600 !important;
            margin-bottom: 8px !important;
            text-align: left !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            padding: 8px 14px !important;
        }

        /* Estilização Avançada de Cards */
        .cc-card {
            background: linear-gradient(160deg, rgba(22, 30, 49, 0.75) 0%, rgba(13, 19, 33, 0.85) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 18px 22px;
            box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(12px);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            margin-bottom: 14px;
        }

        .cc-card:hover {
            border-color: rgba(245, 158, 11, 0.35);
            transform: translateY(-2px);
            box-shadow: 0 14px 30px -8px rgba(0, 0, 0, 0.6), 0 0 15px rgba(245, 158, 11, 0.1);
        }

        .cc-card-active {
            border: 1.5px solid #f59e0b !important;
            background: linear-gradient(160deg, rgba(31, 41, 68, 0.85) 0%, rgba(17, 24, 42, 0.95) 100%) !important;
            box-shadow: 0 12px 28px -6px rgba(245, 158, 11, 0.25) !important;
        }

        /* ================= CARDS DOS MÓDULOS ================= */
        .cc-module-card {
            background: linear-gradient(160deg, rgba(22, 30, 49, 0.88) 0%, rgba(13, 19, 33, 0.96) 100%) !important;
            border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 18px !important;
            padding: 22px !important;
            box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.45) !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: space-between !important;
            min-height: 200px !important;
            box-sizing: border-box !important;
            cursor: pointer !important;
            transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
            position: relative !important;
        }

        /* Efeitos de Hover Dinâmicos nos Cards de Módulo */
        [data-testid="stColumn"]:hover .cc-module-card,
        [data-testid="stColumn"]:has(div[class*="st-key-btn_card_"]):hover .cc-module-card,
        [data-testid="stColumn"]:has(.cc-module-card):hover .cc-module-card,
        .cc-module-card:hover {
            transform: translateY(-6px) scale(1.01) !important;
        }

        [data-testid="stColumn"]:hover .theme-amber,
        [data-testid="stColumn"]:hover .cc-module-card.theme-amber,
        [data-testid="stColumn"]:has(div[class*="st-key-btn_card_"]):hover .theme-amber,
        [data-testid="stColumn"]:has(.theme-amber):hover .cc-module-card,
        .cc-module-card.theme-amber:hover {
            border-color: #f59e0b !important;
            background: linear-gradient(160deg, rgba(32, 42, 68, 0.95) 0%, rgba(18, 26, 44, 0.98) 100%) !important;
            box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.8), 0 0 30px rgba(245, 158, 11, 0.35) !important;
        }

        [data-testid="stColumn"]:hover .theme-blue,
        [data-testid="stColumn"]:hover .cc-module-card.theme-blue,
        [data-testid="stColumn"]:has(div[class*="st-key-btn_card_"]):hover .theme-blue,
        [data-testid="stColumn"]:has(.theme-blue):hover .cc-module-card,
        .cc-module-card.theme-blue:hover {
            border-color: #3b82f6 !important;
            background: linear-gradient(160deg, rgba(24, 38, 70, 0.95) 0%, rgba(14, 23, 46, 0.98) 100%) !important;
            box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.8), 0 0 30px rgba(59, 130, 246, 0.35) !important;
        }

        [data-testid="stColumn"]:hover .theme-emerald,
        [data-testid="stColumn"]:hover .cc-module-card.theme-emerald,
        [data-testid="stColumn"]:has(div[class*="st-key-btn_card_"]):hover .theme-emerald,
        [data-testid="stColumn"]:has(.theme-emerald):hover .cc-module-card,
        .cc-module-card.theme-emerald:hover {
            border-color: #10b981 !important;
            background: linear-gradient(160deg, rgba(20, 44, 46, 0.95) 0%, rgba(12, 28, 30, 0.98) 100%) !important;
            box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.8), 0 0 30px rgba(16, 185, 129, 0.35) !important;
        }

        /* Hover no chevron e texto de ação dos módulos */
        [data-testid="stColumn"]:hover .cc-module-chevron,
        [data-testid="stColumn"]:has(div[class*="st-key-btn_card_"]):hover .cc-module-chevron,
        .cc-module-card:hover .cc-module-chevron {
            transform: translateX(4px) !important;
            color: #ffffff !important;
            background: rgba(255, 255, 255, 0.12) !important;
        }

        [data-testid="stColumn"]:hover .cc-module-action span:last-child,
        [data-testid="stColumn"]:has(div[class*="st-key-btn_card_"]):hover .cc-module-action span:last-child,
        .cc-module-card:hover .cc-module-action span:last-child {
            transform: translateX(6px) !important;
        }

        /* Overlay do Botão Invisível nos cards de módulo */
        div[class*="st-key-btn_card_"] {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            z-index: 20 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        div[class*="st-key-btn_card_"] div.stButton {
            width: 100% !important;
            height: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        div[class*="st-key-btn_card_"] div.stButton > button {
            width: 100% !important;
            height: 100% !important;
            min-height: 200px !important;
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

        /* ================= CARDS DE MESA CLICÁVEIS ================= */
        [data-testid="stColumn"] {
            position: relative !important;
        }

        .cc-mesa-card {
            background: linear-gradient(160deg, rgba(22, 30, 49, 0.85) 0%, rgba(13, 19, 33, 0.95) 100%) !important;
            border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 16px !important;
            padding: 16px 18px 14px 18px !important;
            box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: space-between !important;
            height: 165px !important;
            min-height: 165px !important;
            max-height: 165px !important;
            box-sizing: border-box !important;
            cursor: pointer !important;
            margin-bottom: 0px !important;
            position: relative !important;
            overflow: hidden !important;
        }

        .cc-mesa-card-active {
            border: 1.5px solid #f59e0b !important;
            background: linear-gradient(160deg, rgba(35, 45, 75, 0.95) 0%, rgba(18, 26, 46, 0.98) 100%) !important;
            box-shadow: 0 12px 28px -6px rgba(245, 158, 11, 0.35) !important;
        }

        /* Hover no Card ativado ao passar o mouse na coluna */
        [data-testid="stColumn"]:hover .cc-mesa-card,
        [data-testid="stColumn"]:has(div[class*="st-key-btn_sel_mesa_"]):hover .cc-mesa-card {
            transform: translateY(-4px) !important;
            border-color: #f59e0b !important;
            background: linear-gradient(160deg, rgba(35, 45, 75, 0.95) 0%, rgba(18, 26, 46, 0.98) 100%) !important;
            box-shadow: 0 16px 36px -8px rgba(0, 0, 0, 0.7), 0 0 20px rgba(245, 158, 11, 0.3) !important;
        }

        [data-testid="stColumn"]:active .cc-mesa-card,
        [data-testid="stColumn"]:has(div[class*="st-key-btn_sel_mesa_"]):active .cc-mesa-card {
            transform: translateY(-1px) scale(0.99) !important;
        }

        /* Overlay do Botão Invisível cobrindo exatamente o Card e eliminando o retângulo abaixo */
        div[class*="st-key-btn_sel_mesa_"] {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 165px !important;
            z-index: 20 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        div[class*="st-key-btn_sel_mesa_"] div.stButton {
            width: 100% !important;
            height: 165px !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        div[class*="st-key-btn_sel_mesa_"] div.stButton > button {
            width: 100% !important;
            height: 165px !important;
            min-height: 165px !important;
            max-height: 165px !important;
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

        .cc-module-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 14px;
        }

        .cc-module-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .cc-module-icon {
            font-size: 1.6rem;
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }

        .icon-amber {
            background: rgba(245, 158, 11, 0.15);
            border: 1px solid rgba(245, 158, 11, 0.35);
        }

        .icon-blue {
            background: rgba(59, 130, 246, 0.15);
            border: 1px solid rgba(59, 130, 246, 0.35);
        }

        .icon-emerald {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.35);
        }

        .cc-module-titles h4 {
            margin: 0;
            color: #ffffff;
            font-size: 1.15rem;
            font-weight: 700;
            letter-spacing: -0.01em;
        }

        .badge-amber {
            font-size: 0.75rem;
            color: #f59e0b;
            font-weight: 600;
        }

        .badge-blue {
            font-size: 0.75rem;
            color: #60a5fa;
            font-weight: 600;
        }

        .badge-emerald {
            font-size: 0.75rem;
            color: #34d399;
            font-weight: 600;
        }

        .cc-module-chevron {
            font-size: 1.1rem;
            color: #64748b;
            transition: all 0.25s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            flex-shrink: 0;
        }

        .cc-module-desc {
            color: #94a3b8;
            font-size: 0.88rem;
            line-height: 1.5;
            margin: 0 0 16px 0;
            min-height: 48px;
        }

        .cc-module-action {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.82rem;
            font-weight: 600;
            padding-top: 14px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            margin-top: auto;
        }

        /* Estilização de Botões do Streamlit para combinar com o Design Premium */
        div.stButton > button {
            background: linear-gradient(140deg, #1e293b 0%, #0f172a 100%) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            letter-spacing: -0.01em !important;
            padding: 8px 18px !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2) !important;
            width: 100% !important;
        }

        div.stButton > button:hover {
            border-color: #f59e0b !important;
            color: #ffffff !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 16px -2px rgba(245, 158, 11, 0.3) !important;
        }

        div.stButton > button:active {
            transform: translateY(0px) !important;
        }

        /* Botões Primários com Gradiente Dourado Flame */
        div.stButton > button[kind="primary"], 
        div.stDownloadButton > button {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
            color: #ffffff !important;
            border: 1px solid #fbbf24 !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 14px rgba(217, 119, 6, 0.4) !important;
        }

        div.stButton > button[kind="primary"]:hover,
        div.stDownloadButton > button:hover {
            background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%) !important;
            box-shadow: 0 6px 20px rgba(217, 119, 6, 0.55) !important;
        }

        /* Botões da Barra de Navegação Superior */
        .cc-nav-btn button {
            height: 44px !important;
            font-size: 0.88rem !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        .cc-nav-btn-active button {
            background: linear-gradient(135deg, rgba(217, 119, 6, 0.3) 0%, rgba(180, 83, 9, 0.45) 100%) !important;
            border: 1.5px solid #f59e0b !important;
            color: #fef3c7 !important;
            font-weight: 700 !important;
            box-shadow: 0 0 16px rgba(245, 158, 11, 0.25) !important;
        }

        /* Métricas Elegantes */
        div[data-testid="stMetric"] {
            background: linear-gradient(145deg, rgba(22, 30, 49, 0.6) 0%, rgba(13, 19, 33, 0.7) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 14px 18px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
        }

        div[data-testid="stMetric"]:hover {
            border-color: rgba(245, 158, 11, 0.3);
        }

        div[data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }

        div[data-testid="stMetricValue"] {
            color: #f8fafc !important;
            font-weight: 800 !important;
            font-size: 1.6rem !important;
            letter-spacing: -0.02em !important;
        }

        /* Inputs e Formulários */
        input, select, textarea {
            background-color: #0f172a !important;
            color: #f8fafc !important;
            border: 1px solid #334155 !important;
            border-radius: 10px !important;
        }

        input:focus, select:focus, textarea:focus {
            border-color: #f59e0b !important;
            box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.2) !important;
        }

        /* Rodapé Premium */
        .cc-footer-wrapper {
            margin-top: 3.5rem;
            padding: 22px 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            background: linear-gradient(180deg, rgba(11, 15, 25, 0.4) 0%, rgba(7, 10, 18, 0.95) 100%);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 16px;
            color: #64748b;
            font-size: 0.8rem;
        }

        .cc-footer-left {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .cc-footer-badges {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }

        .cc-footer-pill {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 3px 10px;
            border-radius: 20px;
            color: #94a3b8;
            font-size: 0.72rem;
            font-weight: 500;
        }

        /* ================= RESPONSIVIDADE COMPLETA: TELAS MENORES ATÉ TELÕES 4K ================= */

        /* 1. TELÕES, SMART TVs E MONITORES ULTRA-WIDE (>= 1920px) */
        @media (min-width: 1920px) {
            .block-container {
                max-width: 1720px !important;
                padding-top: 2rem !important;
                padding-left: 3rem !important;
                padding-right: 3rem !important;
            }
            .cc-navbar-title {
                font-size: 1.35rem !important;
            }
            .st-key-cc_nav_desktop div.stButton > button {
                height: 44px !important;
                font-size: 0.95rem !important;
            }
            div[data-testid="stMetricValue"] {
                font-size: 2.1rem !important;
            }
            .cc-module-card {
                padding: 28px !important;
            }
        }

        /* 2. DESKTOP PADRÃO E NOTEBOOKS (>= 992px) */
        @media (min-width: 992px) {
            .st-key-cc_nav_desktop {
                display: block !important;
            }
            .st-key-cc_nav_mobile {
                display: none !important;
            }
        }

        /* 3. TABLETS E TELAS MÉDIAS (entre 768px e 991px) */
        @media (max-width: 991px) {
            .st-key-cc_nav_desktop {
                display: none !important;
            }
            .st-key-cc_nav_mobile {
                display: block !important;
            }
            .block-container {
                padding-top: 1rem !important;
                padding-left: 1.25rem !important;
                padding-right: 1.25rem !important;
            }
        }

        /* 4. SMARTPHONES E TELAS PEQUENAS (<= 767px até 320px) */
        @media (max-width: 767px) {
            .st-key-cc_nav_desktop {
                display: none !important;
            }
            .st-key-cc_nav_mobile {
                display: block !important;
            }
            .block-container {
                padding-top: 0.75rem !important;
                padding-left: 0.75rem !important;
                padding-right: 0.75rem !important;
                padding-bottom: 2rem !important;
            }
            .cc-navbar-brand {
                gap: 8px !important;
            }
            .cc-navbar-logo {
                width: 38px !important;
                height: 38px !important;
                font-size: 1.15rem !important;
            }
            .cc-navbar-title {
                font-size: 1.02rem !important;
            }
            .cc-navbar-tag {
                font-size: 0.60rem !important;
                padding: 1px 4px !important;
            }
            div[data-testid="stMetric"] {
                padding: 10px 12px !important;
            }
            div[data-testid="stMetricLabel"] {
                font-size: 0.75rem !important;
            }
            div[data-testid="stMetricValue"] {
                font-size: 1.25rem !important;
            }
            .cc-footer-wrapper {
                flex-direction: column !important;
                text-align: center !important;
                gap: 12px !important;
                padding: 16px 12px !important;
            }
            .cc-footer-badges {
                justify-content: center !important;
            }
            .cc-module-card {
                margin-bottom: 12px !important;
            }
        }

        /* 5. SMARTPHONES COMPACTOS (<= 420px) */
        @media (max-width: 420px) {
            .cc-navbar-title {
                font-size: 0.92rem !important;
            }
            .cc-navbar-tag {
                display: none !important;
            }
            .block-container {
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

def render_navbar(active_tab: str = "home"):
    """
    Renderiza a barra superior de navegação moderna e 100% responsiva:
    - Em Telões e Desktop (>= 992px): Exibe a barra executiva completa com abas diretas.
    - Em Tablets e Smartphones (< 992px): Exibe a barra compacta com o botão Menu Sanduíche (☰)
      que abre o painel retrátil de navegação ao ser clicado.
    active_tab: 'home' | 'salao' | 'cardapio' | 'relatorios'
    """
    inject_custom_theme()

    # 1. NAVBAR DESKTOP & TELÕES (>= 992px)
    with st.container(key="cc_nav_desktop"):
        c_brand, c_nav1, c_nav2, c_nav3, c_nav4, c_nav5 = st.columns(
            [2.2, 1.2, 1.3, 1.2, 1.5, 1.2],
            vertical_alignment="center"
        )

        with c_brand:
            st.markdown("""
            <div class="cc-navbar-brand">
                <div class="cc-navbar-logo">🥩</div>
                <div>
                    <div class="cc-navbar-title">
                        CHURRAS<span>CONTROL</span>
                        <span class="cc-navbar-tag">POS</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c_nav1:
            if st.button("📊 Painel", key="nav_desk_home", use_container_width=True, type="primary" if active_tab == "home" else "secondary"):
                st.switch_page("app.py")

        with c_nav2:
            if st.button("🍽️ Mesas", key="nav_desk_salao", use_container_width=True, type="primary" if active_tab == "salao" else "secondary"):
                st.switch_page("pages/1_Salao_e_Mesas.py")

        with c_nav3:
            if st.button("📋 Catálogo", key="nav_desk_cardapio", use_container_width=True, type="primary" if active_tab == "cardapio" else "secondary"):
                st.switch_page("pages/2_Cardapio.py")

        with c_nav4:
            if st.button("📱 Cardápio Digital", key="nav_desk_digital", use_container_width=True, type="primary" if active_tab == "cardapio_digital" else "secondary"):
                st.switch_page("pages/4_Cardapio_Digital.py")

        with c_nav5:
            if st.button("📈 Relatórios", key="nav_desk_relatorios", use_container_width=True, type="primary" if active_tab == "relatorios" else "secondary"):
                st.switch_page("pages/3_Relatorios.py")

    # 2. NAVBAR MOBILE & TABLETS (< 992px com Menu Sanduíche ☰)
    with st.container(key="cc_nav_mobile"):
        m_brand, m_menu = st.columns([3.2, 0.8], vertical_alignment="center")

        with m_brand:
            st.markdown("""
            <div class="cc-navbar-brand">
                <div class="cc-navbar-logo">🥩</div>
                <div>
                    <div class="cc-navbar-title">
                        CHURRAS<span>CONTROL</span>
                        <span class="cc-navbar-tag">POS</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with m_menu:
            with st.popover("☰", use_container_width=True, help="Abrir Menu de Navegação"):
                st.markdown("""
                <div style="padding: 2px 0 8px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 8px;">
                    <span style="font-size: 0.74rem; font-weight: 700; color: #f59e0b; text-transform: uppercase; letter-spacing: 0.06em;">
                        Navegação do Sistema
                    </span>
                </div>
                """, unsafe_allow_html=True)
                if st.button("📊 Painel Geral", key="nav_mob_home", use_container_width=True, type="primary" if active_tab == "home" else "secondary"):
                    st.switch_page("app.py")
                if st.button("🍽️ Salão & Mesas", key="nav_mob_salao", use_container_width=True, type="primary" if active_tab == "salao" else "secondary"):
                    st.switch_page("pages/1_Salao_e_Mesas.py")
                if st.button("📋 Catálogo & PDV", key="nav_mob_cardapio", use_container_width=True, type="primary" if active_tab == "cardapio" else "secondary"):
                    st.switch_page("pages/2_Cardapio.py")
                if st.button("📱 Cardápio Digital (Cliente)", key="nav_mob_digital", use_container_width=True, type="primary" if active_tab == "cardapio_digital" else "secondary"):
                    st.switch_page("pages/4_Cardapio_Digital.py")
                if st.button("📈 Relatórios", key="nav_mob_relatorios", use_container_width=True, type="primary" if active_tab == "relatorios" else "secondary"):
                    st.switch_page("pages/3_Relatorios.py")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

def render_footer():
    """Renderiza um rodapé executivo, técnico e elegante."""
    st.markdown("""
    <div class="cc-footer-wrapper">
        <div class="cc-footer-left">
            <span style="color: #f59e0b; font-weight: 700;">ChurrasControl™</span>
            <span>•</span>
            <span>Gestão Gastronômica & PDV em Alta Disponibilidade</span>
        </div>
        <div class="cc-footer-badges">
            <span class="cc-footer-pill">🗄️ Persistência: SQLite (WAL)</span>
            <span class="cc-footer-pill">⚡ Latência: Imediata</span>
            <span class="cc-footer-pill">🔄 Worker Xano: Fila Persistente</span>
            <span class="cc-footer-pill">© 2026 Innovation Lab</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

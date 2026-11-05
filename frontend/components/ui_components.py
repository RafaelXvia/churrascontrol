"""
ChurrasControl — Sistema de Design & Componentes Visuais Premium
Fornece Navbar no topo, Rodapé responsivo, remoção total da sidebar e estilos CSS modernos.
"""
import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, List, Dict, Any
from backend.database import data_manager

def inject_custom_theme():
    """Injeta CSS de alta fidelidade visual, tipografia moderna e responsividade total."""
    st.markdown("""
    <style>
        /* Importação de Tipografia Moderna */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

        /* Ocultação Completa e Imediata da Barra Lateral (Sidebar) em todas as telas */
        [data-testid="stSidebar"], 
        section[data-testid="stSidebar"], 
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavItems"],
        [data-testid="stSidebarNavLink"],
        button[kind="header"] {
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            min-width: 0 !important;
            max-width: 0 !important;
            height: 0 !important;
            opacity: 0 !important;
            pointer-events: none !important;
            transform: translateX(-100%) !important;
        }

        /* Ocultação e anulação total de sobreposição do header nativo */
        header[data-testid="stHeader"],
        div[data-testid="stHeader"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            pointer-events: none !important;
        }

        #MainMenu, footer {
            display: none !important;
            visibility: hidden !important;
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
        .st-key-cc_nav_desktop,
        .st-key-cc_nav_mobile,
        .st-key-cc_navbar_container {
            position: relative !important;
            z-index: 9999 !important;
            pointer-events: auto !important;
        }

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

        /* 6. ESTILOS DO LOGIN MODERNO E AVATAR CIRCULAR */
        .cc-login-hero-container {
            max-width: 480px;
            margin: 25px auto 16px auto;
            text-align: center;
        }
        .cc-login-icon-box {
            width: 72px;
            height: 72px;
            border-radius: 22px;
            background: linear-gradient(135deg, #f59e0b 0%, #b45309 100%);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 35px rgba(245, 158, 11, 0.5), inset 0 2px 2px rgba(255, 255, 255, 0.3);
            margin-bottom: 14px;
            border: 1.5px solid rgba(251, 191, 36, 0.5);
            animation: cc-pulse-glow 3s infinite alternate;
        }
        @keyframes cc-pulse-glow {
            0% { box-shadow: 0 0 25px rgba(245, 158, 11, 0.4); transform: scale(1); }
            100% { box-shadow: 0 0 45px rgba(245, 158, 11, 0.7); transform: scale(1.02); }
        }
        .cc-login-title {
            margin: 0;
            font-size: 2.1rem;
            font-weight: 900;
            color: #ffffff;
            letter-spacing: -0.03em;
            line-height: 1.1;
        }
        .cc-login-title span {
            color: #f59e0b;
        }
        .cc-login-subtitle {
            margin: 8px 0 14px 0;
            color: #94a3b8;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .cc-login-badge {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.35);
            padding: 5px 16px;
            border-radius: 9999px;
            color: #fbbf24;
            font-size: 0.76rem;
            font-weight: 700;
            margin-top: 6px;
            backdrop-filter: blur(10px);
            letter-spacing: 0.03em;
        }

        /* Estilização Premium do Card de Login */
        .st-key-login_card_box div[data-testid="stForm"] {
            background: linear-gradient(165deg, rgba(22, 30, 48, 0.94) 0%, rgba(12, 17, 30, 0.98) 100%) !important;
            border: 1.5px solid rgba(245, 158, 11, 0.35) !important;
            border-radius: 24px !important;
            padding: 30px 28px 24px 28px !important;
            box-shadow: 0 25px 60px -10px rgba(0, 0, 0, 0.85), 0 0 35px rgba(245, 158, 11, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
        }

        .st-key-login_card_box div[data-testid="stTextInput"] input {
            background: rgba(10, 15, 28, 0.95) !important;
            border: 1.5px solid rgba(255, 255, 255, 0.14) !important;
            border-radius: 12px !important;
            color: #ffffff !important;
            font-size: 0.95rem !important;
            padding: 12px 14px !important;
            height: 48px !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        .st-key-login_card_box div[data-testid="stTextInput"] input:focus {
            border-color: #f59e0b !important;
            box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.25), 0 0 20px rgba(245, 158, 11, 0.2) !important;
            background: rgba(15, 22, 38, 0.98) !important;
        }

        .st-key-login_card_box div[data-testid="stForm"] button[kind="primary"] {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
            color: #0b0f19 !important;
            font-weight: 800 !important;
            font-size: 1rem !important;
            border: none !important;
            border-radius: 12px !important;
            height: 50px !important;
            box-shadow: 0 4px 18px rgba(245, 158, 11, 0.38) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            margin-top: 10px !important;
            letter-spacing: 0.01em !important;
        }

        .st-key-login_card_box div[data-testid="stForm"] button[kind="primary"]:hover {
            background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%) !important;
            box-shadow: 0 8px 25px rgba(245, 158, 11, 0.6) !important;
            transform: translateY(-2px) !important;
            color: #000000 !important;
        }

        .st-key-btn_login_recuperar div.stButton > button {
            background: transparent !important;
            border: none !important;
            color: #94a3b8 !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            padding: 8px 12px !important;
            margin-top: 8px !important;
            box-shadow: none !important;
            transition: all 0.2s ease !important;
        }

        .st-key-btn_login_recuperar div.stButton > button:hover {
            color: #fbbf24 !important;
            text-decoration: underline !important;
            background: rgba(245, 158, 11, 0.08) !important;
            transform: none !important;
            border: none !important;
        }

        .st-key-nav_desk_avatar div.stButton > button,
        .st-key-nav_mob_avatar div.stButton > button {
            border-radius: 50% !important;
            width: 38px !important;
            height: 38px !important;
            min-height: 38px !important;
            padding: 0 !important;
            font-size: 1.05rem !important;
            font-weight: 800 !important;
            background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
            color: #ffffff !important;
            border: 1.5px solid #f59e0b !important;
            box-shadow: 0 0 12px rgba(245, 158, 11, 0.35) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .st-key-nav_desk_avatar div.stButton > button:hover,
        .st-key-nav_mob_avatar div.stButton > button:hover {
            transform: scale(1.08) !important;
            border-color: #fbbf24 !important;
            box-shadow: 0 0 18px rgba(245, 158, 11, 0.6) !important;
        }
    </style>
    """, unsafe_allow_html=True)

def _obter_token_requisicao() -> Optional[str]:
    """
    Recupera o token JWT de sessão persistente a partir de múltiplas fontes com alta resiliência:
    1. st.query_params ('session_token')
    2. st.session_state ('session_token')
    3. st.context.cookies ('cc_session_token')
    4. Header HTTP Cookie ('cc_session_token')
    """
    try:
        if st.session_state.get("logout_realizado"):
            return None
    except Exception:
        pass

    # 1. Query params da URL (Sobrevive imediatamente a F5 / Ctrl+F5)
    try:
        qp_tok = st.query_params.get("session_token")
        if qp_tok and len(str(qp_tok).strip()) >= 20:
            return str(qp_tok).strip()
    except Exception:
        pass

    # 2. Session state local
    try:
        ss_tok = st.session_state.get("session_token")
        if ss_tok and len(str(ss_tok).strip()) >= 20:
            return str(ss_tok).strip()
    except Exception:
        pass

    # 3. Cookies nativos do Streamlit
    try:
        if hasattr(st, "context") and hasattr(st.context, "cookies"):
            c_tok = st.context.cookies.get("cc_session_token")
            if c_tok and len(str(c_tok).strip()) >= 20:
                return str(c_tok).strip()
    except Exception:
        pass

    # 4. Header Cookie HTTP
    try:
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            cookie_header = st.context.headers.get("cookie", "")
            if "cc_session_token=" in cookie_header:
                for part in cookie_header.split(";"):
                    part = part.strip()
                    if part.startswith("cc_session_token="):
                        val = part.split("=", 1)[1].strip()
                        if len(val) >= 20:
                            return val
    except Exception:
        pass

    return None

def _injetar_script_sessao(token: str):
    """
    Persiste o token JWT de sessão tanto nos cookies do navegador quanto no localStorage,
    e assegura que a URL mantenha ?session_token= sem provocar reload na interface.
    """
    safe_token = str(token).strip()
    js_code = f"""
    <script>
        (function() {{
            try {{
                var t = "{safe_token}";
                var exp = new Date(Date.now() + 7 * 864e5).toUTCString();
                var cookieStr = "cc_session_token=" + t + "; path=/; expires=" + exp + "; SameSite=Lax";
                document.cookie = cookieStr;
                var p = (window.parent && window.parent !== window) ? window.parent : window;
                try {{ p.document.cookie = cookieStr; }} catch(e) {{}}
                try {{ p.localStorage.setItem("cc_session_token", t); }} catch(e) {{}}
                try {{
                    var u = new URL(p.location.href);
                    if (u.searchParams.get("session_token") !== t) {{
                        u.searchParams.set("session_token", t);
                        p.history.replaceState(null, "", u.toString());
                    }}
                }} catch(e) {{}}
            }} catch(e) {{
                console.error("Erro ao persistir sessão:", e);
            }}
        }})();
    </script>
    """
    components.html(js_code, height=0, width=0)

def _injetar_script_recuperacao_sessao():
    """
    Restaura a sessão em tempo recorde (<15ms) a partir do localStorage
    caso o usuário tenha acabado de pressionar Ctrl+F5 limpando a URL.
    """
    js_code = """
    <script>
        (function() {
            try {
                var p = (window.parent && window.parent !== window) ? window.parent : window;
                var tok = null;
                try { tok = p.localStorage.getItem("cc_session_token"); } catch(e) {}
                if (!tok) {
                    try {
                        var m = document.cookie.match(/(?:^|;\\s*)cc_session_token=([^;]+)/);
                        if (m) tok = m[1];
                    } catch(e) {}
                }
                if (tok && tok.length >= 20) {
                    var exp = new Date(Date.now() + 7 * 864e5).toUTCString();
                    var cookieStr = "cc_session_token=" + tok + "; path=/; expires=" + exp + "; SameSite=Lax";
                    try { p.document.cookie = cookieStr; } catch(e) {}
                    try { document.cookie = cookieStr; } catch(e) {}
                    try {
                        var u = new URL(p.location.href);
                        if (!u.searchParams.has("session_token")) {
                            u.searchParams.set("session_token", tok);
                            p.location.replace(u.toString());
                        }
                    } catch(e) {}
                }
            } catch(e) {
                console.error("Erro recup sessão:", e);
            }
        })();
    </script>
    """
    components.html(js_code, height=0, width=0)


def _injetar_script_limpeza_sessao():
    """Remove o token dos cookies e do localStorage ao deslogar."""
    js_code = """
    <script>
        (function() {
            try {
                var cookieStr = "cc_session_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax";
                document.cookie = cookieStr;
                var p = (window.parent && window.parent !== window) ? window.parent : window;
                p.document.cookie = cookieStr;
                p.localStorage.removeItem("cc_session_token");
                if (p.location.search.includes("session_token=")) {
                    var u = new URL(p.location.href);
                    u.searchParams.delete("session_token");
                    p.history.replaceState(null, "", u.toString());
                }
            } catch(e) {}
        })();
    </script>
    """
    components.html(js_code, height=0, width=0)

def obter_usuario_logado() -> Optional[dict]:
    """Retorna o dicionário do usuário logado na sessão ou None."""
    return st.session_state.get("usuario_logado")

def fazer_logout():
    """Encerra imediatamente a sessão do usuário no servidor e no navegador e retorna à tela de login."""
    from backend.database import data_manager
    u = st.session_state.get("usuario_logado")
    tok = _obter_token_requisicao() or st.session_state.get("session_token")
    uid = u.get("id") if isinstance(u, dict) else None
    data_manager.encerrar_sessao_token(tok, usuario_id=uid)
    try:
        st.query_params.pop("session_token", None)
    except Exception:
        pass
    if u:
        data_manager.registrar_auditoria("LOGOUT", "AUTENTICACAO", f"Logout efetuado por {u.get('nome')} ({u.get('email')})", usuario=u)
    st.session_state["usuario_logado"] = None
    st.session_state["session_token"] = None
    st.session_state["modal_perfil_aberto"] = False
    st.session_state["logout_realizado"] = True
    _injetar_script_limpeza_sessao()
    st.rerun()

# ================= MODAL DE PERFIL E TROCA DE SENHA =================
@st.dialog("Meu Perfil & Segurança", width="medium")
def dialog_perfil_usuario(usuario: dict):
    inicial = (usuario.get("nome", "U")[0]).upper()
    is_gerente = (str(usuario.get("cargo", "")).lower() == "gerente")
    badge_bg = "rgba(245, 158, 11, 0.2)" if is_gerente else "rgba(56, 189, 248, 0.2)"
    badge_color = "#fbbf24" if is_gerente else "#38bdf8"
    badge_border = "rgba(245, 158, 11, 0.4)" if is_gerente else "rgba(56, 189, 248, 0.4)"

    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 18px; padding: 14px 18px; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 14px;">
        <div style="width: 52px; height: 52px; border-radius: 50%; background: linear-gradient(135deg, #d97706 0%, #b45309 100%); display: flex; align-items: center; justify-content: center; font-size: 1.4rem; font-weight: 800; color: #ffffff; box-shadow: 0 4px 14px rgba(217, 119, 6, 0.4); border: 2px solid rgba(245, 158, 11, 0.5);">
            {inicial}
        </div>
        <div style="min-width: 0; flex: 1;">
            <h3 style="margin: 0; color: #ffffff; font-size: 1.15rem; font-weight: 800; line-height: 1.2;">{usuario.get('nome', '')}</h3>
            <div style="margin-top: 4px; display: flex; align-items: center; gap: 8px;">
                <span style="background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_border}; padding: 2px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 800; text-transform: uppercase;">
                    {usuario.get('cargo', '').upper()}
                </span>
                <span style="color: #94a3b8; font-size: 0.8rem;">Colaborador ID #{usuario.get('id', '')}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_info, tab_senha = st.tabs(["Meus Dados", "Alterar Minha Senha"])

    with tab_info:
        st.caption("Seus dados cadastrais são gerenciados pela administração (Gerente).")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Nome Completo", value=usuario.get("nome", ""), disabled=True, key="prof_ro_nome")
            st.text_input("E-mail de Login", value=usuario.get("email", ""), disabled=True, key="prof_ro_email")
        with c2:
            st.text_input("Telefone / WhatsApp", value=usuario.get("numero", ""), disabled=True, key="prof_ro_numero")
            st.text_input("Cargo & Permissões", value=usuario.get("cargo", "").capitalize(), disabled=True, key="prof_ro_cargo")

    with tab_senha:
        st.caption("Altere sua senha pessoal de acesso ao sistema a qualquer momento:")
        with st.form("form_alterar_minha_senha"):
            senha_atual = st.text_input("Senha Atual *", type="password", placeholder="Digite sua senha atual de acesso")
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                nova_senha = st.text_input("Nova Senha *", type="password", placeholder="Mínimo 4 caracteres")
            with c_s2:
                conf_senha = st.text_input("Confirmar Nova Senha *", type="password", placeholder="Repita a nova senha")
            
            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            btn_salvar_senha = st.form_submit_button("Atualizar Minha Senha", type="primary", use_container_width=True)

            if btn_salvar_senha:
                if not senha_atual or not nova_senha or not conf_senha:
                    st.error("Todos os campos de senha são obrigatórios.")
                elif len(nova_senha) < 4:
                    st.error("A nova senha deve ter no mínimo 4 caracteres.")
                elif nova_senha != conf_senha:
                    st.error("A nova senha e a confirmação digitada não coincidem.")
                else:
                    from backend.database import data_manager
                    u_check = data_manager.autenticar_usuario(usuario["email"], senha_atual)
                    if not u_check:
                        st.error("A senha atual digitada está incorreta.")
                    else:
                        data_manager.atualizar_senha_colaborador(usuario["id"], nova_senha)
                        st.session_state["modal_perfil_aberto"] = False
                        st.toast("Senha pessoal atualizada com sucesso!", )
                        st.rerun()

    st.markdown("<hr style='margin: 16px 0 12px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
    c_close, c_logout = st.columns([1.5, 1])
    with c_close:
        if st.button("Fechar", use_container_width=True, key="btn_close_prof_modal"):
            st.session_state["modal_perfil_aberto"] = False
            st.rerun()
    with c_logout:
        if st.button("Sair da Conta", type="primary", use_container_width=True, key="btn_logout_prof_modal", help="Encerrar sessão"):
            fazer_logout()

@st.dialog("Recuperar Senha & Acesso", width="medium")
def dialog_recuperar_senha():
    """Modal interativo para recuperação autônoma de senha solicitando exclusivamente o e-mail cadastrado."""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 16px;">
        <div style="width: 54px; height: 54px; border-radius: 16px; background: linear-gradient(135deg, #f59e0b 0%, #b45309 100%); display: inline-flex; align-items: center; justify-content: center; margin-bottom: 8px; box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
        </div>
        <h3 style="margin: 0; color: #ffffff; font-weight: 800; font-size: 1.25rem;">Recuperação de Senha & Acesso</h3>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.84rem;">
            Informe o e-mail corporativo cadastrado para receber as instruções e redefinir o acesso com segurança.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_recuperar_senha_modal"):
        email_rec = st.text_input("E-mail Corporativo *", placeholder="ex: gerente@churrascontrol.com")
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        btn_confirmar_rec = st.form_submit_button("Enviar Instruções de Recuperação", type="primary", use_container_width=True)

        if btn_confirmar_rec:
            if not email_rec.strip():
                st.error("Informe o e-mail corporativo para continuar.")
            elif "@" not in email_rec.strip():
                st.error("Formato de e-mail inválido.")
            else:
                try:
                    from backend.database import data_manager
                    base_url = None
                    try:
                        if hasattr(st, "context") and hasattr(st.context, "headers"):
                            origin = st.context.headers.get("origin") or st.context.headers.get("Origin")
                            host = st.context.headers.get("host") or st.context.headers.get("Host")
                            proto = st.context.headers.get("x-forwarded-proto") or "https"
                            if origin:
                                base_url = origin.strip().rstrip("/")
                            elif host:
                                if "localhost" in host or "127.0.0.1" in host:
                                    base_url = f"http://{host.strip()}"
                                else:
                                    base_url = f"{proto}://{host.strip()}"
                    except Exception:
                        pass
                    res_msg = data_manager.processar_recuperacao_por_email(email_rec.strip(), base_url=base_url)
                    st.success(res_msg)
                except ValueError as err:
                    st.error(str(err))

def exigir_autenticacao() -> dict:
    """
    Guarda de segurança: exige que o usuário esteja autenticado.
    Verifica e restaura a sessão ativa via cookies nativos, localStorage ou query params (F5 / recarregar página).
    Se não houver sessão ativa, exibe a tela de login moderna com visual sofisticado e interrompe com st.stop().
    Se estiver com primeiro_acesso == True, exibe a tela de redefinição obrigatória de senha e interrompe.
    """
    inject_custom_theme()
    from backend.database import data_manager

    email_prefill = ""
    try:
        email_prefill = str(st.query_params.get("login_email") or "").strip()
    except Exception:
        pass

    # Se o usuário clicou no botão do e-mail de recuperação (?login_email=...), abre direto na tela de login
    if email_prefill and st.session_state.get("login_email_processado") != email_prefill:
        old_tok = _obter_token_requisicao() or st.session_state.get("session_token")
        old_u = st.session_state.get("usuario_logado")
        if old_tok or old_u:
            data_manager.encerrar_sessao_token(old_tok, usuario_id=old_u.get("id") if isinstance(old_u, dict) else None)
        try:
            st.query_params.pop("session_token", None)
        except Exception:
            pass
        st.session_state["usuario_logado"] = None
        st.session_state["session_token"] = None
        st.session_state["modal_perfil_aberto"] = False
        st.session_state["logout_realizado"] = True
        st.session_state["login_email_processado"] = email_prefill

    # 1. Restauração automática de sessão persistente no F5 através de cookies, headers ou query_params
    usuario = st.session_state.get("usuario_logado")
    tok = _obter_token_requisicao()

    if not usuario and tok:
        u_sess = data_manager.validar_sessao_token(tok)
        if u_sess:
            st.session_state["usuario_logado"] = u_sess
            st.session_state["session_token"] = tok
            st.session_state["modal_perfil_aberto"] = False
            st.session_state["logout_realizado"] = False
            usuario = u_sess
        else:
            try:
                st.query_params.pop("session_token", None)
            except Exception:
                pass
            st.session_state["session_token"] = None
            st.session_state["logout_realizado"] = True

    # 2. Se o usuário já está autenticado, reforça cookies e localStorage para garantir os próximos F5
    if usuario:
        active_tok = tok or st.session_state.get("session_token")
        if active_tok:
            _injetar_script_sessao(active_tok)

        # Fluxo de Primeiro Acesso Obrigatório (ou pós-recuperação de senha):
        if usuario.get("primeiro_acesso"):
            st.markdown(
                '<div style="max-width: 520px; margin: 30px auto 14px auto; text-align: center;">'
                '<h3 style="margin: 0; font-size: 1.45rem; font-weight: 800; color: #ffffff;">Primeiro Acesso — Redefinição de Senha</h3>'
                '<p style="margin: 6px 0 16px 0; color: #94a3b8; font-size: 0.88rem;">'
                'Por políticas de segurança, substitua a senha provisória por uma nova senha pessoal de sua escolha antes de prosseguir para o sistema.'
                '</p>'
                '</div>',
                unsafe_allow_html=True
            )
            col_l, col_center, col_r = st.columns([1, 2, 1])
            with col_center:
                with st.form("form_primeiro_acesso"):
                    nova_senha = st.text_input("Nova Senha Pessoal *", type="password", placeholder="Mínimo 4 caracteres")
                    conf_senha = st.text_input("Confirmar Nova Senha *", type="password", placeholder="Repita a nova senha")
                    btn_trocar = st.form_submit_button("Salvar Nova Senha e Continuar", type="primary", use_container_width=True)
                    if btn_trocar:
                        if not nova_senha or len(nova_senha) < 4:
                            st.error("A nova senha deve ter no mínimo 4 caracteres.")
                        elif nova_senha != conf_senha:
                            st.error("As senhas digitadas não coincidem.")
                        else:
                            data_manager.atualizar_senha_colaborador(usuario["id"], nova_senha)
                            st.session_state["usuario_logado"]["primeiro_acesso"] = False
                            try:
                                st.query_params.pop("login_email", None)
                            except Exception:
                                pass
                            st.success("Senha pessoal atualizada com sucesso! Acesso liberado.")
                            st.rerun()
                if st.button("Sair e Voltar para Tela de Login", key="btn_sair_primeiro_acesso", use_container_width=True):
                    fazer_logout()
            st.stop()

        return usuario

    # 3. Se houve logout ou token revogado, limpa cookies e localStorage; caso contrário, restaura via localStorage no F5
    if st.session_state.get("logout_realizado") or email_prefill:
        _injetar_script_limpeza_sessao()
    else:
        _injetar_script_recuperacao_sessao()

    # 4. Exibe a Tela de Login Sofisticada & Moderna
    st.markdown("""
    <div class="cc-login-hero-container">
        <div class="cc-login-icon-box">
            <svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>
            </svg>
        </div>
        <h1 class="cc-login-title">
            CHURRAS<span>CONTROL</span>
        </h1>
        <p class="cc-login-subtitle">
            TERMINAL OPERACIONAL DE ATENDIMENTO & PDV
        </p>

    </div>
    """, unsafe_allow_html=True)

    col_l, col_center, col_r = st.columns([1, 1.85, 1])
    with col_center:
        with st.container(key="login_card_box"):
            with st.form("form_login_churrascontrol"):
                st.markdown("<div style='font-size: 0.82rem; color: #cbd5e1; font-weight: 700; margin-bottom: 4px;'>E-MAIL CORPORATIVO:</div>", unsafe_allow_html=True)
                email = st.text_input("E-mail", value=email_prefill, placeholder="gerente@churrascontrol.com", label_visibility="collapsed")
                
                st.markdown("<div style='font-size: 0.82rem; color: #cbd5e1; font-weight: 700; margin-bottom: 4px; margin-top: 14px;'>SENHA DE ACESSO:</div>", unsafe_allow_html=True)
                senha = st.text_input("Senha", type="password", placeholder="••••••••", label_visibility="collapsed")
                
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                btn_login = st.form_submit_button("Acessar Terminal Operacional", type="primary", use_container_width=True)

                if btn_login:
                    u = data_manager.autenticar_usuario(email, senha)
                    if u:
                        tok = data_manager.criar_sessao_usuario(u["id"])
                        try:
                            st.query_params.pop("login_email", None)
                        except Exception:
                            pass
                        st.query_params["session_token"] = tok
                        st.session_state["usuario_logado"] = u
                        st.session_state["session_token"] = tok
                        st.session_state["modal_perfil_aberto"] = False
                        st.session_state["logout_realizado"] = False
                        st.session_state["login_email_processado"] = None
                        _injetar_script_sessao(tok)
                        st.success(f"Autenticado com sucesso! Bem-vindo(a), {u['nome']}.")
                        st.rerun()
                    else:
                        st.error("Credenciais inválidas. Verifique o e-mail e a senha informados.")

            with st.container(key="btn_login_recuperar"):
                if st.button("Esqueci minha senha / Recuperar acesso", key="btn_trigger_recuperar_senha", use_container_width=True):
                    dialog_recuperar_senha()

            st.markdown("""
            <div style="text-align: center; color: #64748b; font-size: 0.76rem; padding: 12px 0 6px 0; border-top: 1px solid rgba(255, 255, 255, 0.06); margin-top: 10px;">
                Terminal restrito a Gerentes e Operadores de Caixa credenciados.
            </div>
            """, unsafe_allow_html=True)
    st.stop()

    usuario = st.session_state["usuario_logado"]

    # Fluxo de Primeiro Acesso Obrigatório:
    if usuario.get("primeiro_acesso"):
        st.markdown(
            '<div style="max-width: 520px; margin: 30px auto 14px auto; text-align: center;">'
            '<h3 style="margin: 0; font-size: 1.45rem; font-weight: 800; color: #ffffff;">Primeiro Acesso — Redefinição de Senha</h3>'
            '<p style="margin: 6px 0 16px 0; color: #94a3b8; font-size: 0.88rem;">'
            'Por políticas de segurança, substitua a senha provisória cadastrada pelo gerente por uma nova senha pessoal de sua escolha antes de prosseguir.'
            '</p>'
            '</div>',
            unsafe_allow_html=True
        )
        col_l, col_center, col_r = st.columns([1, 2, 1])
        with col_center:
            with st.form("form_primeiro_acesso"):
                nova_senha = st.text_input("Nova Senha Pessoal *", type="password", placeholder="Mínimo 4 caracteres")
                conf_senha = st.text_input("Confirmar Nova Senha *", type="password", placeholder="Repita a nova senha")
                btn_trocar = st.form_submit_button("Salvar Nova Senha e Continuar", type="primary", use_container_width=True)
                if btn_trocar:
                    if not nova_senha or len(nova_senha) < 4:
                        st.error("A nova senha deve ter no mínimo 4 caracteres.")
                    elif nova_senha != conf_senha:
                        st.error("As senhas digitadas não coincidem.")
                    else:
                        from backend.database import data_manager
                        data_manager.atualizar_senha_colaborador(usuario["id"], nova_senha)
                        st.session_state["usuario_logado"]["primeiro_acesso"] = False
                        st.success("Senha pessoal atualizada com sucesso! Acesso liberado.")
                        st.rerun()
        st.stop()

    return usuario

def verificar_permissao_acesso(cargos_permitidos: list) -> dict:
    """Verifica se o usuário logado tem o cargo necessário. Se não tiver, bloqueia o acesso à tela."""
    usuario = exigir_autenticacao()
    cargo = str(usuario.get("cargo", "")).lower()
    cargos_norm = [c.lower() for c in cargos_permitidos]
    if cargo not in cargos_norm:
        inject_custom_theme()
        st.markdown(
            f'<div style="max-width: 550px; margin: 60px auto; background: rgba(239, 68, 68, 0.1); border: 1.5px solid rgba(239, 68, 68, 0.4); border-radius: 16px; padding: 24px; text-align: center;">'
            f'<h3 style="margin: 0; color: #f87171; font-weight: 800; font-size: 1.35rem;">Acesso Restrito ao Perfil Gerente</h3>'
            f'<p style="margin: 8px 0 18px 0; color: #cbd5e1; font-size: 0.9rem;">'
            f'Seu perfil de acesso atual é <b>{cargo.upper()}</b>. Esta tela só pode ser visualizada por colaboradores com cargo: <b>{", ".join(c.upper() for c in cargos_permitidos)}</b>.'
            f'</p>'
            f'</div>',
            unsafe_allow_html=True
        )
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            if cargo == "caixa":
                if st.button("Ir para Salão e Mesas", type="primary", use_container_width=True):
                    st.switch_page("pages/1_Salao_e_Mesas.py")
            else:
                if st.button("Retornar ao Painel Geral", type="primary", use_container_width=True):
                    st.switch_page("app.py")
        st.stop()
    return usuario

def render_navbar(active_tab: str = "home"):
    """
    Renderiza a barra superior de navegação moderna, adaptada dinamicamente ao cargo do colaborador:
    - Gerente: Vê Painel Geral, Salão & Mesas, Cardápio, Relatórios, Colaboradores e Avatar.
    - Caixa: Vê apenas Salão & Mesas, Cardápio e Avatar (sem Painel Geral, Relatórios ou Colaboradores).
    """
    inject_custom_theme()
    usuario = obter_usuario_logado()
    if usuario:
        active_tok = _obter_token_requisicao() or st.session_state.get("session_token")
        if active_tok:
            _injetar_script_sessao(active_tok)

    is_gerente = (usuario and str(usuario.get("cargo", "")).lower() == "gerente")
    nome_usuario = usuario.get("nome", "").split()[0] if usuario else ""
    cargo_label = usuario.get("cargo", "").upper() if usuario else ""
    inicial = (usuario.get("nome", "U")[0]).upper() if usuario else "U"

    # 1. NAVBAR DESKTOP & TELÕES (>= 992px)
    with st.container(key="cc_nav_desktop"):
        if is_gerente:
            # 7 abas + brand + avatar/user
            cols = st.columns([1.9, 1.0, 1.1, 0.9, 0.9, 1.0, 0.9, 1.2, 1.1], vertical_alignment="center")
            c_brand, c_nav1, c_nav2, c_nav3, c_nav4, c_nav5, c_nav6, c_nav7, c_user = cols
            
            with c_brand:
                st.markdown("""
                <div class="cc-navbar-brand">
                    <div class="cc-navbar-logo">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>
                        </svg>
                    </div>
                    <div>
                        <div class="cc-navbar-title">
                            CHURRAS<span>CONTROL</span>
                            <span class="cc-navbar-tag">POS</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with c_nav1:
                if st.button("Painel Geral", key="nav_desk_home", use_container_width=True, type="primary" if active_tab == "home" else "secondary"):
                    st.switch_page("app.py")

            with c_nav2:
                if st.button("Salão & Mesas", key="nav_desk_salao", use_container_width=True, type="primary" if active_tab == "salao" else "secondary"):
                    st.switch_page("pages/1_Salao_e_Mesas.py")

            with c_nav3:
                if st.button("Cardápio", key="nav_desk_cardapio", use_container_width=True, type="primary" if active_tab == "cardapio" else "secondary"):
                    st.switch_page("pages/2_Cardapio.py")

            with c_nav4:
                if st.button("Relatórios", key="nav_desk_relatorios", use_container_width=True, type="primary" if active_tab == "relatorios" else "secondary"):
                    st.switch_page("pages/3_Relatorios.py")

            with c_nav5:
                if st.button("Colaboradores", key="nav_desk_colabs", use_container_width=True, type="primary" if active_tab == "colaboradores" else "secondary"):
                    st.switch_page("pages/6_Colaboradores.py")

            with c_nav6:
                if st.button("Auditoria", key="nav_desk_auditoria", use_container_width=True, type="primary" if active_tab == "auditoria" else "secondary"):
                    st.switch_page("pages/7_Auditoria.py")

            with c_nav7:
                if st.button("Assistente IA", key="nav_desk_ia", use_container_width=True, type="primary" if active_tab == "assistente_ia" else "secondary"):
                    st.switch_page("pages/8_Assistente_IA.py")

        else:
            # Caixa: Estritamente Salão & Mesas e Cardápio (sem Painel Geral, Relatórios ou Colaboradores)
            cols = st.columns([3.8, 2.2, 2.0, 1.8], vertical_alignment="center")
            c_brand, c_nav1, c_nav2, c_user = cols

            with c_brand:
                st.markdown("""
                <div class="cc-navbar-brand">
                    <div class="cc-navbar-logo">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>
                        </svg>
                    </div>
                    <div>
                        <div class="cc-navbar-title">
                            CHURRAS<span>CONTROL</span>
                            <span class="cc-navbar-tag">CAIXA</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with c_nav1:
                if st.button("Salão & Mesas", key="nav_desk_salao", use_container_width=True, type="primary" if active_tab == "salao" else "secondary"):
                    st.switch_page("pages/1_Salao_e_Mesas.py")

            with c_nav2:
                if st.button("Cardápio", key="nav_desk_cardapio", use_container_width=True, type="primary" if active_tab == "cardapio" else "secondary"):
                    st.switch_page("pages/2_Cardapio.py")

        with c_user:
            if usuario:
                c_av_info, c_av_btn = st.columns([1.6, 1], vertical_alignment="center")
                with c_av_info:
                    badge_color = "#f59e0b" if is_gerente else "#38bdf8"
                    st.markdown(f"""
                    <div style="font-size: 0.74rem; color: #cbd5e1; white-space: nowrap; text-align: right; line-height: 1.15;">
                        <span style="font-weight: 700; color: #fff;">{nome_usuario}</span><br>
                        <span style="color: {badge_color}; font-size: 0.67rem; font-weight: 700;">[{cargo_label}]</span>
                    </div>
                    """, unsafe_allow_html=True)
                with c_av_btn:
                    if st.button(f"{inicial}", key="nav_desk_avatar", help=f"Perfil de {nome_usuario} (Clique para ver dados ou alterar senha)"):
                        st.session_state["modal_perfil_aberto"] = True

    # 2. NAVBAR MOBILE & TABLETS (< 992px com Menu)
    with st.container(key="cc_nav_mobile"):
        m_brand, m_avatar, m_menu = st.columns([3.0, 0.8, 0.8], vertical_alignment="center")

        with m_brand:
            st.markdown("""
            <div class="cc-navbar-brand">
                <div class="cc-navbar-logo">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>
                    </svg>
                </div>
                <div>
                    <div class="cc-navbar-title">
                        CHURRAS<span>CONTROL</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with m_avatar:
            if usuario:
                if st.button(f"{inicial}", key="nav_mob_avatar", help=f"Perfil de {nome_usuario}"):
                    st.session_state["modal_perfil_aberto"] = True

        with m_menu:
            with st.popover("Menu", use_container_width=True, help="Abrir Menu de Navegação"):
                if usuario:
                    st.markdown(f"""
                    <div style="padding: 2px 0 8px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 8px;">
                        <span style="font-size: 0.78rem; font-weight: 700; color: #fff;">{usuario.get('nome', '')}</span>
                        <span style="font-size: 0.70rem; color: #f59e0b; margin-left: 4px;">[{cargo_label}]</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                if is_gerente:
                    if st.button("Painel Geral", key="nav_mob_home", use_container_width=True, type="primary" if active_tab == "home" else "secondary"):
                        st.switch_page("app.py")
                
                if st.button("Salão & Mesas", key="nav_mob_salao", use_container_width=True, type="primary" if active_tab == "salao" else "secondary"):
                    st.switch_page("pages/1_Salao_e_Mesas.py")

                if st.button("Cardápio", key="nav_mob_cardapio", use_container_width=True, type="primary" if active_tab == "cardapio" else "secondary"):
                    st.switch_page("pages/2_Cardapio.py")

                if is_gerente:
                    if st.button("Relatórios", key="nav_mob_relatorios", use_container_width=True, type="primary" if active_tab == "relatorios" else "secondary"):
                        st.switch_page("pages/3_Relatorios.py")
                    if st.button("Colaboradores", key="nav_mob_colabs", use_container_width=True, type="primary" if active_tab == "colaboradores" else "secondary"):
                        st.switch_page("pages/6_Colaboradores.py")
                    if st.button("Auditoria", key="nav_mob_auditoria", use_container_width=True, type="primary" if active_tab == "auditoria" else "secondary"):
                        st.switch_page("pages/7_Auditoria.py")
                    if st.button("Assistente IA", key="nav_mob_ia", use_container_width=True, type="primary" if active_tab == "assistente_ia" else "secondary"):
                        st.switch_page("pages/8_Assistente_IA.py")

                if usuario:
                    st.markdown("<hr style='margin: 8px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
                    if st.button("Meu Perfil & Senha", key="nav_mob_meu_perfil", use_container_width=True):
                        st.session_state["modal_perfil_aberto"] = True
                        st.rerun()
                    if st.button("Sair da Conta", key="nav_mob_logout", use_container_width=True):
                        fazer_logout()

    # Aciona o diálogo de perfil se o avatar foi clicado
    if st.session_state.get("modal_perfil_aberto") and usuario:
        dialog_perfil_usuario(usuario)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

def render_footer():
    """Renderiza um rodapé executivo, técnico e elegante."""
    st.markdown("""
    <div class="cc-footer-wrapper">
        <div class="cc-footer-left">
            <span style="color: #f59e0b; font-weight: 700;">ChurrasControl</span>
            <span>•</span>
            <span>Gestão Gastronômica & PDV em Alta Disponibilidade</span>
        </div>
        <div class="cc-footer-badges">
            <span class="cc-footer-pill">Persistência: SQLite (WAL)</span>
            <span class="cc-footer-pill">Latência: Imediata</span>
            <span class="cc-footer-pill">Worker Xano: Fila Ativa</span>
            <span class="cc-footer-pill">2026 Innovation Lab</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

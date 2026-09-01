"""
Script de Entrada Principal para Hospedagem na Discloud — ChurrasControl
Inicia o servidor Streamlit escutando obrigatoriamente na porta 8080 e host 0.0.0.0.
"""
import sys
import streamlit.web.cli as stcli

if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        "app.py",
        "--server.port=8080",
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ]
    sys.exit(stcli.main())

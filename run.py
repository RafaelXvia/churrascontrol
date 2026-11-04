"""
Script de Entrada Principal para Hospedagem na Discloud — ChurrasControl
Inicia o servidor Streamlit escutando obrigatoriamente na porta 8080 e host 0.0.0.0.
Inclui otimizações de retenção de memória no Linux (cgroups Discloud).
"""
import os
import sys

# Otimização de alocação de memória no Linux (Discloud Container)
os.environ["MALLOC_TRIM_THRESHOLD_"] = "100000"
os.environ["PYTHONUNBUFFERED"] = "1"

import streamlit.web.cli as stcli

if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        "app.py",
        "--server.port=8080",
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--server.fileWatcherType=none",
        "--browser.gatherUsageStats=false"
    ]
    sys.exit(stcli.main())

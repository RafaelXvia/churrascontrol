"""
Script de Entrada Principal para Hospedagem na Discloud — ChurrasControl
Inicia o servidor Streamlit escutando obrigatoriamente na porta 8080 e host 0.0.0.0.
Inclui otimizações de retenção de memória no Linux (cgroups Discloud).
"""
import os
import sys

# Carrega variáveis de ambiente (.env) para o container da Discloud
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Otimização de alocação de memória no Linux (Docker / Discloud Container 512MB RAM)
os.environ["MALLOC_TRIM_THRESHOLD_"] = "65536"
os.environ["PYTHONUNBUFFERED"] = "1"

import streamlit.web.cli as stcli

if __name__ == "__main__":
    is_container = os.environ.get("DISCLOUD", "") == "1" or os.environ.get("DOCKER_CONTAINER", "") == "1"
    file_watcher = "none" if is_container else "auto"

    sys.argv = [
        "streamlit",
        "run",
        "app.py",
        "--server.port=8080",
        "--server.address=0.0.0.0",
        "--server.headless=true",
        f"--server.fileWatcherType={file_watcher}",
        "--client.showSidebarNavigation=false",
        "--browser.gatherUsageStats=false"
    ]
    sys.exit(stcli.main())

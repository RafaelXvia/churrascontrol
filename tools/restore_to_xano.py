"""
Utilitário de Restauração e Carga Inicial para Nova Instância Xano — ChurrasControl
Lê os dados locais do backup e do SQLite e envia automaticamente para a nova instância Xano.

Como usar:
    python tools/restore_to_xano.py [NOVA_URL_XANO] [OPCIONAL_API_KEY]

Exemplo:
    python tools/restore_to_xano.py https://x8ki-letl-twmt.n7.xano.io/api:churrascontrol
"""
import sys
import os
import time
import json
import httpx
import sqlite3

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import data_manager

def main():
    print("=" * 70)
    print("CHURRASCONTROL — CARGA / RESTAURAÇÃO DE DADOS PARA O XANO")
    print("=" * 70)

    # 1. Obter URL de destino
    if len(sys.argv) > 1:
        target_base_url = sys.argv[1].rstrip("/")
    else:
        target_base_url = data_manager.XANO_BASE_URL.rstrip("/")

    api_key = sys.argv[2] if len(sys.argv) > 2 else data_manager.XANO_API_KEY
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    print(f"URL Alvo da API: {target_base_url}")
    print("-" * 70)

    # 2. Carregar produtos do SQLite/Backup
    produtos = data_manager.listar_produtos()
    print(f"\n[PRODUTOS] Enviando {len(produtos)} itens para {target_base_url}/produto...")
    prods_ok = 0
    with httpx.Client(timeout=10.0) as client:
        for p in produtos:
            payload = {
                "codigo_pdv": p.get("codigo_pdv") or str(p["id"]),
                "nome": p["nome"],
                "descricao": p.get("descricao", ""),
                "preco": float(p.get("preco", 10.0)),
                "categoria": p.get("categoria", "Comida"),
                "qtd_disp": int(p.get("qtd_disp", 20)),
                "precisa_produzir": bool(p.get("precisa_produzir", 1)),
                "disponivel": bool(p.get("disponivel", 1)),
                "url_imagem": p.get("url_imagem", "")
            }
            try:
                r = client.post(f"{target_base_url}/produto", json=payload, headers=headers)
                if r.status_code in (200, 201):
                    prods_ok += 1
                elif r.status_code == 429:
                    print("  [RATE LIMIT] Pausando 15s para cooldown do Xano Free...")
                    time.sleep(15)
                    r2 = client.post(f"{target_base_url}/produto", json=payload, headers=headers)
                    if r2.status_code in (200, 201):
                        prods_ok += 1
                else:
                    print(f"  [AVISO] Falha ao enviar '{p['nome']}': HTTP {r.status_code} - {r.text[:80]}")
            except Exception as e:
                print(f"  [ERRO] Exceção ao enviar '{p['nome']}': {e}")
            time.sleep(2.2)
    print(f"  -> Concluído: {prods_ok}/{len(produtos)} produtos cadastrados com sucesso.")

    # 3. Carregar colaboradores criptografados
    print(f"\n[COLABORADORES] Enviando colaboradores criptografados para {target_base_url}/colaborador...")
    colabs_ok = 0
    with data_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, senha_hash, numero, cargo, primeiro_acesso, ativo FROM colaboradores")
        rows = cursor.fetchall()

    with httpx.Client(timeout=10.0) as client:
        for r in rows:
            # Enviamos com nome, numero e cargo já criptografados (prefixo ENC:)
            payload = {
                "nome": r["nome"],
                "email": r["email"],
                "numero": r["numero"],
                "cargo": r["cargo"],
                "senha_hash": r["senha_hash"],
                "primeiro_acesso": bool(r["primeiro_acesso"]),
                "ativo": bool(r["ativo"])
            }
            try:
                res = client.post(f"{target_base_url}/colaborador", json=payload, headers=headers)
                if res.status_code in (200, 201):
                    colabs_ok += 1
                elif res.status_code == 429:
                    print("  [RATE LIMIT] Pausando 15s para cooldown do Xano Free...")
                    time.sleep(15)
                    res2 = client.post(f"{target_base_url}/colaborador", json=payload, headers=headers)
                    if res2.status_code in (200, 201):
                        colabs_ok += 1
                else:
                    print(f"  [AVISO] Endpoint /colaborador retornou HTTP {res.status_code} para {r['email']}: {res.text[:80]}")
            except Exception as e:
                print(f"  [ERRO] Exceção ao enviar colaborador {r['email']}: {e}")
            time.sleep(2.2)
    print(f"  -> Concluído: {colabs_ok}/{len(rows)} colaboradores criptografados enviados.")

    # 4. Carregar mesas
    print(f"\n[MESAS] Verificando sincronização de mesas para {target_base_url}/mesas...")
    mesas_ok = 0
    with httpx.Client(timeout=10.0) as client:
        for m_num in range(1, 11):
            payload = {
                "numero_mesa": m_num,
                "capacidade": 4,
                "status": "LIVRE"
            }
            try:
                res = client.post(f"{target_base_url}/mesas", json=payload, headers=headers)
                if res.status_code in (200, 201):
                    mesas_ok += 1
            except Exception:
                pass
    if mesas_ok > 0:
        print(f"  -> {mesas_ok} mesas criadas no Xano.")
    else:
        print("  -> Endpoint /mesas ainda não publicado no grupo ou requer criação manual.")

    print("\n" + "=" * 70)
    print("PROCESSO DE RESTAURAÇÃO FINALIZADO!")
    print(f"Instância Alvo: {target_base_url}")
    print("=" * 70)

if __name__ == "__main__":
    main()

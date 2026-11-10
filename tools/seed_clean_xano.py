"""
Seed Limpo e Seguro para o Xano — ChurrasControl
Carrega exatamente os 15 produtos e o Gerente Administrador criptografado do SQLite para o Xano.
Usa intervalo seguro de 2.5s entre chamadas para garantir taxa < 10 reqs/20s (evitando 429).
"""
import sys
import os
import time
import httpx
import sqlite3

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from backend.database import data_manager

BASE_URL = data_manager.XANO_BASE_URL.rstrip("/")

def main():
    print("=" * 70)
    print("CHURRASCONTROL — SEED SEGURO E ANTI-RATE-LIMIT NO XANO")
    print(f"URL: {BASE_URL}")
    print("=" * 70)

    # 1. Obter produtos do SQLite
    prods = data_manager.listar_produtos()
    print(f"\n[1/2] Enviando {len(prods)} produtos únicos (intervalo seguro 2.5s)...")
    
    with httpx.Client(timeout=10.0) as client:
        for idx, p in enumerate(prods, start=1):
            payload = {
                "codigo_pdv": str(p.get("codigo_pdv") or p["id"]),
                "nome": p["nome"],
                "categoria": p.get("categoria", "Comida"),
                "preco": float(p.get("preco", 10.0)),
                "descricao": p.get("descricao", ""),
                "qtd_disp": int(p.get("qtd_disp", 20)),
                "url_imagem": p.get("url_imagem", ""),
                "precisa_produzir": bool(p.get("precisa_produzir", 1)),
                "disponivel": bool(p.get("disponivel", 1))
            }
            
            sucesso = False
            for tentativa in range(3):
                try:
                    r = client.post(f"{BASE_URL}/produto", json=payload)
                    if r.status_code in (200, 201):
                        print(f"  [{idx:02d}/{len(prods):02d}] OK: {p['nome']} (ID retornado: {r.json().get('id')})")
                        sucesso = True
                        break
                    elif r.status_code == 429:
                        print("  [429] Rate limit atingido. Pausando 18s...")
                        time.sleep(18)
                    else:
                        print(f"  [ERRO] HTTP {r.status_code}: {r.text[:80]}")
                        break
                except Exception as e:
                    print(f"  [EXCEÇÃO] {e}")
                    time.sleep(3)
            
            time.sleep(2.5)

    # 2. Obter colaboradores do SQLite
    print(f"\n[2/2] Enviando Colaborador Gerente Administrador criptografado...")
    with data_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nome, email, senha_hash, numero, cargo, primeiro_acesso, ativo FROM colaboradores WHERE email='gerente@churrascontrol.com'")
        c = cursor.fetchone()

    if c:
        payload_colab = {
            "nome": c["nome"],
            "email": c["email"],
            "numero": c["numero"],
            "cargo": c["cargo"],
            "senha_hash": c["senha_hash"],
            "primeiro_acesso": bool(c["primeiro_acesso"]),
            "ativo": bool(c["ativo"])
        }
        with httpx.Client(timeout=10.0) as client:
            r = client.post(f"{BASE_URL}/colaborador", json=payload_colab)
            if r.status_code in (200, 201):
                print(f"  OK: Colaborador {c['email']} enviado com sucesso! (ID: {r.json().get('id')})")
            else:
                print(f"  HTTP {r.status_code}: {r.text}")

    # 3. Auditoria final no Xano
    time.sleep(3)
    print("\n" + "=" * 70)
    print("AUDITORIA FINAL DOS DADOS NO XANO:")
    with httpx.Client(timeout=10.0) as client:
        prods_xano = client.get(f"{BASE_URL}/produto").json()
        colabs_xano = client.get(f"{BASE_URL}/colaborador").json()
        print(f"  Total de Produtos no Xano:      {len(prods_xano)} (Esperado: 15)")
        print(f"  Total de Colaboradores no Xano: {len(colabs_xano)} (Esperado: 1)")
        for cl in colabs_xano:
            print(f"    - Email: {cl['email']} | Nome: {cl['nome'][:25]}... | Cargo: {cl['cargo'][:25]}...")
    print("=" * 70)

if __name__ == "__main__":
    main()

import httpx
from backend.database import data_manager as dm

def resetar_e_alinhar():
    dm.init_db()
    with dm._db_lock:
        with dm.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM comandas;")
            cur.execute("DELETE FROM itens_comanda;")
            cur.execute("DELETE FROM mesas;")
            cur.execute("DELETE FROM sessoes_ativas;")
            cur.execute("DELETE FROM fila_sincronizacao;")
            cur.execute("DELETE FROM auditoria;")
            cur.execute("DELETE FROM chat_conversas;")
            cur.execute("DELETE FROM chat_mensagens;")
            cur.execute("DELETE FROM llm_fallback_logs;")
            cur.execute("DELETE FROM colaboradores;")
            cur.execute("DELETE FROM produtos;")
            conn.commit()

            print("SQLite limpo! Carregando espelho fiel do Xano...")

            # 1. Produtos do Xano
            r_p = httpx.get(f"{dm.XANO_BASE_URL}/produto", timeout=20.0)
            prods = r_p.json() if r_p.status_code == 200 else []
            codigos_vistos = set()
            for p in prods:
                pid = int(p["id"])
                cod = str(p.get("codigo_pdv") or f"PDV_{pid}").strip()
                if not cod or cod in codigos_vistos:
                    cod = f"PDV_{pid}"
                codigos_vistos.add(cod)

                cur.execute("""
                INSERT INTO produtos (id, codigo_pdv, nome, categoria, preco_unitario, descricao, url_imagem, qtd_disp, precisa_produzir, disponivel)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pid,
                    cod,
                    p.get("nome", ""),
                    p.get("categoria", "Comida"),
                    float(p.get("preco") or p.get("preco_unitario") or 10.0),
                    p.get("descricao", ""),
                    p.get("url_imagem", ""),
                    int(p.get("qtd_disp") or 15),
                    1 if p.get("precisa_produzir") else 0,
                    1 if p.get("disponivel", True) else 0
                ))

            # 2. Colaboradores do Xano
            r_c = httpx.get(f"{dm.XANO_BASE_URL}/colaborador", timeout=20.0)
            colabs = r_c.json() if r_c.status_code == 200 else []
            for c in colabs:
                cid = int(c["id"])
                cur.execute("""
                INSERT INTO colaboradores (id, nome, email, senha_hash, numero, cargo, primeiro_acesso, ativo, criado_em, atualizado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cid,
                    c.get("nome", ""),
                    str(c.get("email", "")).strip().lower(),
                    c.get("senha_hash", ""),
                    c.get("numero", ""),
                    c.get("cargo", ""),
                    0,
                    1,
                    "2026-11-10T10:00:00",
                    "2026-11-10T10:00:00"
                ))
            conn.commit()

            print(f"Alinhamento concluído com sucesso!")
            print(f"Produtos no SQLite: {cur.execute('SELECT COUNT(*) FROM produtos').fetchone()[0]}")
            print(f"Colaboradores no SQLite: {cur.execute('SELECT COUNT(*) FROM colaboradores').fetchone()[0]}")
            print(f"Mesas no SQLite: {cur.execute('SELECT COUNT(*) FROM mesas').fetchone()[0]}")
            print(f"Comandas no SQLite: {cur.execute('SELECT COUNT(*) FROM comandas').fetchone()[0]}")

if __name__ == "__main__":
    resetar_e_alinhar()


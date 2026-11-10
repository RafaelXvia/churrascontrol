"""
Limpeza e Normalização Estrita do SQLite — ChurrasControl
Deixa estritamente apenas os 15 produtos de catálogo e o Gerente Administrador.
Todas as demais tabelas e sequências são resetadas.

ATENÇÃO: operação DESTRUTIVA (apaga comandas, itens, mesas e colaboradores = histórico de vendas).
Não é mais executada automaticamente pela suíte de testes. Uso manual:
    python tools/clean_sqlite.py --confirmar
"""
import sqlite3
import os
import sys

DB_PATH = os.getenv("CHURRAS_DB_PATH") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "churrascontrol.db"
)

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Puxar produtos existentes únicos
    c.execute("SELECT nome, preco_unitario, categoria, descricao, qtd_disp, precisa_produzir, disponivel, url_imagem FROM produtos ORDER BY id ASC")
    prods = c.fetchall()

    # 2. Puxar gerente administrador
    c.execute("SELECT nome, email, senha_hash, numero, cargo, primeiro_acesso, ativo, criado_em, atualizado_em FROM colaboradores WHERE email='gerente@churrascontrol.com'")
    gerente = c.fetchone()

    # 3. Limpar tabelas
    tabelas = ["comandas", "itens_comanda", "mesas", "qrcodes_mesas", "fila_sincronizacao", "produtos", "colaboradores"]
    for t in tabelas:
        c.execute(f"DELETE FROM {t};")

    c.execute("DELETE FROM sqlite_sequence;")

    # 4. Inserir 15 produtos limpos com IDs 1..15
    for idx, p in enumerate(prods, start=1):
        c.execute("""
        INSERT INTO produtos (id, codigo_pdv, nome, preco_unitario, categoria, descricao, qtd_disp, precisa_produzir, disponivel, url_imagem)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (idx, str(idx), p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7]))

    # 5. Inserir gerente como ID 1
    if gerente:
        c.execute("""
        INSERT INTO colaboradores (id, nome, email, senha_hash, numero, cargo, primeiro_acesso, ativo, criado_em, atualizado_em)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, gerente)

    conn.commit()
    print("=== SQLITE NORMALIZADO COM SUCESSO ===")
    for t in tabelas:
        cnt = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {cnt} registros")
    conn.close()

if __name__ == "__main__":
    if "--confirmar" not in sys.argv:
        print(f"Operação destrutiva sobre: {DB_PATH}")
        print("Isso apaga TODO o histórico de comandas, itens, mesas e colaboradores.")
        print("Para executar, rode: python tools/clean_sqlite.py --confirmar")
        sys.exit(1)
    main()

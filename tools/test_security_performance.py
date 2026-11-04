"""
Teste de Validação de Segurança, Integridade Relacional e Performance — ChurrasControl
Localização: tools/test_security_performance.py
"""
import os
import sys
import sqlite3

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def run_tests():
    print("=" * 70)
    print("TESTE DE VALIDACAO: SEGURANCA, REGRAS SQLITE E PERFORMANCE")
    print("=" * 70)

    import data_manager

    # 1. Testar bloqueio de preço negativo ou zero (Regra de Domínio / CHECK Constraint)
    try:
        data_manager.criar_produto("9999", "Produto Invalido", "Comida", preco_unitario=-10.0)
        print("  [FAIL] Criacao de produto com preco negativo nao foi bloqueada!")
        return False
    except ValueError as e:
        print(f"  [PASS] Bloqueio de preco negativo OK: {e}")

    try:
        data_manager.criar_produto("9998", "Produto Zero", "Comida", preco_unitario=0.0)
        print("  [FAIL] Criacao de produto com preco zero nao foi bloqueada!")
        return False
    except ValueError as e:
        print(f"  [PASS] Bloqueio de preco zero OK: {e}")

    # 2. Testar sanitização contra injeção de HTML / XSS
    prod_xss = data_manager.criar_produto("9997", "<script>alert('hack')</script>", "<b>Carnes</b>", preco_unitario=25.0)
    if "<script>" in prod_xss["nome"] or "<b>" in prod_xss["categoria"]:
        print(f"  [FAIL] Sanitizacao XSS falhou! Nome nao escapado: {prod_xss['nome']}")
        return False
    print(f"  [PASS] Sanitizacao XSS OK: '{prod_xss['nome']}'")
    # Limpar produto de teste
    data_manager.excluir_produto(prod_xss["id"])

    # 3. Testar Regra de Ouro da Mesa (Cardinalidade 1:1 - No máximo 1 comanda aberta por mesa)
    num_mesa_teste = 888
    # Limpar mesa se existir
    with data_manager.get_connection() as c:
        c.execute("DELETE FROM comandas WHERE numero_mesa_historico = ?", (num_mesa_teste,))
        c.execute("DELETE FROM mesas WHERE numero_mesa = ?", (num_mesa_teste,))
        c.commit()

    res1 = data_manager.abrir_mesa(num_mesa_teste, qtd_pessoas=2)
    mesa_id = res1["mesa_id"]
    comanda1_id = res1["comanda_id"]
    print(f"  [PASS] Primeira comanda aberta para Mesa {num_mesa_teste} OK (ID {comanda1_id})")

    # Tentativa de abrir segunda mesa com o mesmo número (deve falhar por validação e unicidade)
    try:
        data_manager.abrir_mesa(num_mesa_teste, qtd_pessoas=2)
        print("  [FAIL] Abertura de mesa duplicada nao foi bloqueada!")
        return False
    except ValueError as e:
        print(f"  [PASS] Bloqueio de mesa duplicada OK: {e}")

    # Testar inserção forçada via SQL para verificar índice condicional único no banco
    with data_manager.get_connection() as c:
        try:
            c.execute("""
            INSERT INTO comandas (mesa_id, numero_mesa_historico, data_abertura, status, taxa_servico, qtd_pessoas, valor_total)
            VALUES (?, ?, '2026-09-29T12:00:00', 'ABERTA', 1, 2, 0.0)
            """, (mesa_id, num_mesa_teste))
            c.commit()
            print("  [FAIL] Constraint idx_comanda_unica_aberta permitiu segunda comanda ABERTA no SQLite!")
            return False
        except sqlite3.IntegrityError:
            print("  [PASS] Restricao do SQLite bloqueou estritamente segunda comanda ABERTA na mesa!")

    # Fechar comanda e liberar mesa
    data_manager.fechar_comanda(comanda1_id, valor_final=10.0, taxa_servico=False)
    with data_manager.get_connection() as c:
        c.execute("DELETE FROM comandas WHERE id = ?", (comanda1_id,))
        c.execute("DELETE FROM fila_sincronizacao")
        c.commit()
    print("  [PASS] Comanda finalizada e mesa liberada.")

    # 4. Testar índices de performance no SQLite
    with data_manager.get_connection() as c:
        cur = c.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indices = [r[0] for r in cur.fetchall()]

    indices_esperados = ["idx_comanda_unica_aberta", "idx_produtos_codigo", "idx_itens_comanda_cid", "idx_comandas_status", "idx_fila_status"]
    for idx in indices_esperados:
        if idx in indices:
            print(f"  [PASS] Indice de performance ativo: {idx}")
        else:
            print(f"  [FAIL] Indice ausente: {idx}")
            return False

    # 5. Testar presença da coluna de auditoria ultimo_erro na fila
    with data_manager.get_connection() as c:
        cur = c.cursor()
        cur.execute("PRAGMA table_info(fila_sincronizacao);")
        colunas = [r["name"] for r in cur.fetchall()]
        if "ultimo_erro" in colunas:
            print("  [PASS] Coluna de auditoria 'ultimo_erro' ativa na fila de sincronizacao.")
        else:
            print("  [FAIL] Coluna 'ultimo_erro' ausente na fila.")
            return False

    print("-" * 70)
    print("RESULTADO: TODOS OS TESTES DE SEGURANCA E PERFORMANCE PASSARAM!")
    return True

if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)

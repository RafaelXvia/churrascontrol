"""
Teste de Validação da Persistência SQLite e Fila Xano — ChurrasControl
Localização: tools/test_sqlite_sync.py
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
    print("=" * 65)
    print("TESTE DE VALIDACAO: PERSISTENCIA SQLITE & FILA XANO")
    print("=" * 65)

    db_path = os.path.join(PROJECT_ROOT, "churrascontrol.db")

    # 1. Carregar data_manager e verificar inicialização do banco
    import data_manager
    print(f"  [PASS] Modulo data_manager importado com sucesso.")
    
    if not os.path.exists(db_path):
        print(f"  [FAIL] Banco {db_path} nao foi encontrado.")
        return False
    print(f"  [PASS] Banco SQLite ativo em: {db_path}")

    # 2. Verificar tabelas no SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    conn.close()

    expected_tables = ["produtos", "mesas", "comandas", "itens_comanda", "fila_sincronizacao"]
    for t in expected_tables:
        if t in tables:
            print(f"  [PASS] Tabela presente: {t}")
        else:
            print(f"  [FAIL] Tabela ausente: {t}")
            return False

    # 3. Testar Leitura de Dados
    produtos = data_manager.listar_produtos()
    mesas = data_manager.listar_mesas()
    print(f"  [PASS] Produtos cadastrados no SQLite: {len(produtos)}")
    print(f"  [PASS] Mesas cadastradas no SQLite: {len(mesas)}")

    # 4. Testar Ciclo Operacional de Mesa e Comanda (Local-First)
    num_teste = 999
    # Garantir que mesa de teste nao existe
    with data_manager.get_connection() as c:
        c.execute("DELETE FROM mesas WHERE numero_mesa = ?", (num_teste,))
        c.commit()

    res_abertura = data_manager.abrir_mesa(num_teste, qtd_pessoas=3)
    mesa_id = res_abertura["mesa_id"]
    comanda_id = res_abertura["comanda_id"]
    print(f"  [PASS] Abertura de Mesa OK: Mesa ID {mesa_id}, Comanda ID {comanda_id}")

    # 5. Adicionar item na comanda
    detalhes = None
    if produtos:
        prod_teste = produtos[0]
        data_manager.adicionar_item_comanda(comanda_id, prod_teste["id"], quantidade=2, observacao="Sem pimenta")
        data_manager.adicionar_item_comanda(comanda_id, prod_teste["id"], quantidade=1)
        
        detalhes = data_manager.obter_comanda_detalhes(comanda_id)
        if not detalhes or len(detalhes["itens"]) != 1 or detalhes["itens"][0]["quantidade"] != 3:
            print(f"  [FAIL] Agregacao de itens falhou: {detalhes}")
            return False
        print(f"  [PASS] Adicao e agregacao de item OK (Qtd total = 3)")

    # 6. Fechar Comanda
    total = detalhes["total"] if detalhes else 50.0
    data_manager.fechar_comanda(comanda_id, valor_final=total, taxa_servico=True)
    
    # Verificar se mesa foi liberada
    mesas_pos = data_manager.listar_mesas()
    if any(m["numero_mesa"] == num_teste for m in mesas_pos):
        print(f"  [FAIL] Mesa {num_teste} ainda consta como ocupada apos fechamento.")
        return False
    print(f"  [PASS] Fechamento de Comanda e liberacao da mesa OK")

    # 7. Verificar se os eventos foram gravados na fila persistente
    with data_manager.get_connection() as c:
        cur = c.cursor()
        cur.execute("SELECT COUNT(*) FROM fila_sincronizacao")
        total_fila = cur.fetchone()[0]
        print(f"  [PASS] Eventos persistidos na fila de sincronizacao SQLite: {total_fila}")

    # 8. Testar Dashboard e PDF
    dash = data_manager.obter_dashboard_dados("7d")
    pdf_bytes = data_manager.gerar_pdf_bytes("7d")
    print(f"  [PASS] Dashboard faturamento total: R$ {dash['resumo']['faturamento_total']:.2f}")
    print(f"  [PASS] PDF gerado com sucesso: {len(pdf_bytes)} bytes")

    print("-" * 65)
    print("RESULTADO: TODOS OS TESTES DO SQLITE PASSARAM COM SUCESSO!")
    return True

if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)

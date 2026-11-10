"""
Ferramenta de Diagnóstico e Auditoria do Banco de Dados SQLite e Fila Xano — ChurrasControl
Localização: tools/db_diagnostics.py

Como usar:
    python tools/db_diagnostics.py
"""
import sys
import os
import sqlite3

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main():
    print("=" * 70)
    print("[DIAGNÓSTICO E SAÚDE DO BANCO DE DADOS — CHURRASCONTROL]")
    print("=" * 70)

    db_path = os.path.join(PROJECT_ROOT, "churrascontrol.db")
    if not os.path.exists(db_path):
        print(f"[ERRO] Banco de dados SQLite não encontrado no caminho:\n   {db_path}")
        sys.exit(1)

    db_size_kb = os.path.getsize(db_path) / 1024
    print(f"[ARQUIVO] Principal: churrascontrol.db ({db_size_kb:.1f} KB)")
    
    wal_path = db_path + "-wal"
    shm_path = db_path + "-shm"
    wal_exists = os.path.exists(wal_path)
    shm_exists = os.path.exists(shm_path)
    print(f"[ARQUIVO] WAL: {'Ativo (' + str(round(os.path.getsize(wal_path)/1024, 1)) + ' KB)' if wal_exists else 'Não criado'}")
    print(f"[ARQUIVO] SHM: {'Ativo' if shm_exists else 'Não criado'}")
    print("-" * 70)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Modo de Journal e Integridade
    cur.execute("PRAGMA journal_mode;")
    j_mode = cur.fetchone()[0]
    print(f"[CONFIG] Modo de Journal: {j_mode.upper()}")

    cur.execute("PRAGMA integrity_check;")
    integrity = cur.fetchone()[0]
    print(f"[STATUS] Integridade Física: {'[OK]' if integrity == 'ok' else '[FALHA] ' + str(integrity)}")

    cur.execute("PRAGMA foreign_key_check;")
    fk_errors = cur.fetchall()
    if not fk_errors:
        print("[STATUS] Integridade Relacional (FKs): [OK] Nenhuma inconsistência encontrada")
    else:
        print(f"[ALERTA] Inconsistências de Chave Estrangeira: {len(fk_errors)} encontrada(s)")

    print("-" * 70)
    print("[TABELAS] Contagem de Registros:")

    try:
        from backend.database import data_manager
        data_manager.init_db()
    except Exception as e:
        pass

    tabelas = [
        "produtos", "mesas", "comandas", "itens_comanda",
        "colaboradores", "sessoes_ativas", "auditoria",
        "qrcodes_mesas", "fila_sincronizacao",
        "ontologia_conceitos", "ontologia_sinonimos", "ontologia_relacoes",
        "chat_conversas", "chat_mensagens", "llm_fallback_logs"
    ]
    for t in tabelas:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cur.fetchone()[0]
            print(f"   * {t:<22}: {cnt} registro(s)")
        except sqlite3.OperationalError as e:
            print(f"   * {t:<22}: [ERRO] ({e})")

    # 2. Detalhamento de Comandas (histórico preservado)
    try:
        cur.execute("SELECT status, COUNT(*) as qtd, COALESCE(SUM(valor_total), 0.0) as total FROM comandas GROUP BY status")
        status_comandas = cur.fetchall()
        print("\n[COMANDAS] Detalhe por Status (Histórico Financeiro):")
        for r in status_comandas:
            print(f"   - {r['status']:<10}: {r['qtd']} comanda(s) | Total: R$ {float(r['total']):,.2f}")
    except Exception as e:
        print(f"   [ERRO] Detalhe de comandas: {e}")

    # 3. Detalhamento das Mesas
    try:
        cur.execute("SELECT status, COUNT(*) as qtd FROM mesas GROUP BY status")
        status_mesas = cur.fetchall()
        print("\n[MESAS] Detalhe por Status:")
        for r in status_mesas:
            print(f"   - {r['status']}: {r['qtd']}")
    except Exception:
        pass

    # 3. Diagnóstico da Fila de Sincronização Xano
    print("\n[FILA] Status da Fila de Sincronização com Xano:")
    try:
        cur.execute("SELECT status, COUNT(*) as qtd FROM fila_sincronizacao GROUP BY status")
        status_fila = cur.fetchall()
        if status_fila:
            for r in status_fila:
                tag = f"[{r['status']}]"
                print(f"   {tag:<14}: {r['qtd']} evento(s)")
        else:
            print("   [INFO] Fila vazia (nenhum evento registrado ainda)")

        # Verificar se há registros com erro
        cur.execute("SELECT id, metodo, rota, tentativas, ultimo_erro FROM fila_sincronizacao WHERE status = 'ERRO' OR tentativas > 3 LIMIT 5")
        erros_fila = cur.fetchall()
        if erros_fila:
            print("\n   [ALERTA] Últimos Erros Registrados na Fila:")
            for ef in erros_fila:
                print(f"      - ID {ef['id']} ({ef['metodo']} {ef['rota']}) | Tentativas: {ef['tentativas']} | Erro: {ef['ultimo_erro']}")
    except Exception as e:
        print(f"   [ERRO] Falha ao consultar fila: {e}")

    conn.close()
    print("=" * 70)
    print("[CONCLUÍDO] Diagnóstico finalizado com sucesso.")
    print("=" * 70)

if __name__ == "__main__":
    main()

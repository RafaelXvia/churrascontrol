"""
Orquestrador Central de Testes Automatizados — ChurrasControl
Executa todas as suítes de testes presentes no diretório tools/.

Como usar:
    python tools/run_all.py
"""
import sys
import os
import shutil
import tempfile
import subprocess
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["TESTING_ENV"] = "1"

# Isolamento do banco: os testes rodam numa CÓPIA temporária do churrascontrol.db.
# O banco real (histórico de vendas, comandas, itens e colaboradores) nunca é alterado pela suíte.
PROD_DB_PATH = os.path.join(PROJECT_ROOT, "churrascontrol.db")
_TEST_DB_DIR = tempfile.mkdtemp(prefix="churras_tests_")
TEST_DB_PATH = os.path.join(_TEST_DB_DIR, "churrascontrol_test_suite.db")
if os.path.exists(PROD_DB_PATH):
    shutil.copy2(PROD_DB_PATH, TEST_DB_PATH)
os.environ["CHURRAS_DB_PATH"] = TEST_DB_PATH

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main():
    print("=" * 70)
    print("[TESTES] CHURRASCONTROL — BATERIA GERAL DE VERIFICAÇÃO")
    print("=" * 70)
    print(f"Diretório Raiz: {PROJECT_ROOT}")
    print(f"Diretório Tools: {TOOLS_DIR}")
    print(f"Banco isolado de testes: {TEST_DB_PATH}")
    print("-" * 70)

    start_t = time.time()
    test_suite_path = os.path.join(TOOLS_DIR, "test_suite.py")

    res = subprocess.run(
        [sys.executable, test_suite_path],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    elapsed = time.time() - start_t

    print(res.stdout)
    if res.stderr and "FAILED" in res.stderr:
        print("--- DETALHES DE ERRO ---")
        print(res.stderr)

    # Descarta o banco temporário; o banco real permanece intacto
    shutil.rmtree(_TEST_DB_DIR, ignore_errors=True)

    print("=" * 70)
    print(f"[RELATÓRIO] SUÍTE CONSOLIDADA DE TESTES: {'PASS' if res.returncode == 0 else 'FAIL'} ({elapsed:.2f}s)")
    print("=" * 70)

    if res.returncode == 0:
        print("[SUCESSO] Todos os módulos de teste passaram com 100% de aproveitamento.")
        sys.exit(0)
    else:
        print(f"[ALERTA] Falhas detectadas na suíte de testes. Verifique o log acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()

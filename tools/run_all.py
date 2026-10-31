"""
Orquestrador Central de Testes Automatizados — ChurrasControl
Executa todas as suítes de testes presentes no diretório tools/.

Como usar:
    python tools/run_all.py
"""
import sys
import os
import subprocess
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["TESTING_ENV"] = "1"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TEST_FILES = [
    "test_app.py",
    "test_sqlite_sync.py",
    "test_security_performance.py",
    "test_cardapio_delivery.py",
    "test_cardapio_cliente_qrcode.py",
]

def main():
    print("=" * 70)
    print("[TESTES] CHURRASCONTROL — BATERIA GERAL DE VERIFICAÇÃO")
    print("=" * 70)
    print(f"Diretório Raiz: {PROJECT_ROOT}")
    print(f"Diretório Tools: {TOOLS_DIR}")
    print("-" * 70)

    sucessos = 0
    falhas = 0
    total_start = time.time()

    for idx, test_file in enumerate(TEST_FILES, start=1):
        test_path = os.path.join(TOOLS_DIR, test_file)
        if not os.path.exists(test_path):
            print(f"[{idx}/{len(TEST_FILES)}] [FALHA] Arquivo não encontrado: {test_file}")
            falhas += 1
            continue

        print(f"\n[{idx}/{len(TEST_FILES)}] Executando {test_file}...")
        start_t = time.time()
        
        # Executa o processo do teste com o mesmo interpretador Python
        res = subprocess.run(
            [sys.executable, test_path],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        elapsed = time.time() - start_t

        if res.returncode == 0:
            print(f"  [PASS] {test_file} concluído com sucesso ({elapsed:.2f}s)")
            sucessos += 1
        else:
            print(f"  [FAIL] {test_file} FALHOU (código {res.returncode}) em {elapsed:.2f}s")
            print("--- LOG DE ERRO ---")
            print(res.stdout)
            print(res.stderr)
            print("-------------------")
            falhas += 1

    total_elapsed = time.time() - total_start
    print("\n" + "=" * 70)
    print("[RELATÓRIO] RESUMO DA EXECUÇÃO:")
    print(f"  Total de Suítes: {len(TEST_FILES)}")
    print(f"  Sucessos:        {sucessos}")
    print(f"  Falhas:          {falhas}")
    print(f"  Tempo Total:     {total_elapsed:.2f}s")
    print("=" * 70)

    if falhas == 0:
        print("[SUCESSO] Todos os testes passaram com 100% de aproveitamento.")
        sys.exit(0)
    else:
        print(f"[ALERTA] {falhas} teste(s) apresentaram falhas. Verifique o log acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()

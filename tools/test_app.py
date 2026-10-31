"""
Teste de Verificação e Integridade Geral da Aplicação e Data Manager — ChurrasControl
Localização: tools/test_app.py
"""
import sys
import os
import py_compile

# Garante que a raiz do projeto (crudfaculdade) esteja no sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def run_tests():
    print("=" * 65)
    print("TESTE DE VERIFICACAO: ESTRUTURA GERAL, TELAS E DATA MANAGER")
    print("=" * 65)
    
    erros = []

    # 1. Testar Compilação de todos os arquivos essenciais e páginas
    arquivos = [
        "data_manager.py",
        "ui_components.py",
        "app.py",
        "run.py",
        os.path.join("pages", "1_Salao_e_Mesas.py"),
        os.path.join("pages", "2_Cardapio.py"),
        os.path.join("pages", "3_Relatorios.py"),
        os.path.join("pages", "4_Mesas_QRCodes.py"),
        os.path.join("pages", "5_Cardapio_Cliente.py"),
    ]

    for arq in arquivos:
        p = os.path.join(PROJECT_ROOT, arq)
        if not os.path.exists(p):
            print(f"  [FAIL] Arquivo ausente: {arq}")
            erros.append(f"Arquivo ausente: {arq}")
            continue
        try:
            py_compile.compile(p, doraise=True)
            print(f"  [PASS] Compilacao OK: {arq}")
        except py_compile.PyCompileError as e:
            print(f"  [FAIL] Erro de sintaxe em {arq}: {e}")
            erros.append(f"Sintaxe {arq}: {e}")

    # 2. Testar Operações do Data Manager
    try:
        import data_manager
        mesas = data_manager.listar_mesas()
        produtos = data_manager.listar_produtos()
        dash = data_manager.obter_dashboard_dados("7d")
        pdf = data_manager.gerar_pdf_bytes("7d")

        print(f"  [PASS] DataManager: {len(mesas)} mesas ativas, {len(produtos)} produtos cadastrados")
        print(f"  [PASS] DataManager Dashboard: Faturamento total R$ {dash['resumo']['faturamento_total']:.2f}")
        print(f"  [PASS] DataManager PDF: Gerado com sucesso ({len(pdf)} bytes)")

        # Validação do cadastro completo de produto
        import time
        cod_teste = f"T{int(time.time()) % 100000}"
        p_test = data_manager.criar_produto(
            codigo_pdv=cod_teste,
            nome="Picanha Teste Smokehouse",
            categoria="Carnes",
            preco_unitario=69.90,
            descricao="Corte nobre com brasa forte.",
            url_imagem="https://images.unsplash.com/photo-1544025162-d76694265947",
            qtd_disp=10,
            precisa_produzir=True,
            disponivel=True
        )
        assert p_test["qtd_disp"] == 10
        data_manager.excluir_produto(p_test["id"])
        print("  [PASS] DataManager: Criacao e exclusao de produto validada com sucesso.")
    except Exception as e:
        print(f"  [FAIL] Erro no DataManager: {e}")
        erros.append(f"DataManager: {e}")

    print("-" * 65)
    if erros:
        print(f"RESULTADO: {len(erros)} falhas.")
        return False
    else:
        print("RESULTADO: TODOS OS TESTES PASSARAM COM SUCESSO!")
        return True

if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)

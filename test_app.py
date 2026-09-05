"""
Teste de Verificação e Integridade do Redesign e Data Manager — ChurrasControl
"""
import sys
import os
import py_compile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def run_tests():
    print("=" * 60)
    print("TESTE DE VERIFICACAO: REDESIGN E DATA MANAGER")
    print("=" * 60)
    
    erros = []
    base_dir = os.path.dirname(__file__)

    # 1. Testar Compilação dos Arquivos
    arquivos = [
        "data_manager.py",
        "ui_components.py",
        "app.py",
        os.path.join("pages", "1_Salao_e_Mesas.py"),
        os.path.join("pages", "2_Cardapio.py"),
        os.path.join("pages", "3_Relatorios.py"),
    ]

    for arq in arquivos:
        p = os.path.join(base_dir, arq)
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

        print(f"  [PASS] DataManager: {len(mesas)} mesas ativas, {len(produtos)} produtos carregados")
        print(f"  [PASS] DataManager Dashboard: Faturamento total R$ {dash['resumo']['faturamento_total']:.2f}")
        print(f"  [PASS] DataManager PDF: Gerado com sucesso ({len(pdf)} bytes)")

        # Validação do cadastro completo do Cardápio Delivery
        p_test = data_manager.criar_produto(
            codigo_pdv="8888",
            nome="Picanha Teste Smokehouse",
            categoria="Carnes",
            preco_unitario=69.90,
            descricao="Corte nobre com brasa forte.",
            url_imagem="https://images.unsplash.com/photo-1558030006-450675393462",
            qtd_disp=10,
            precisa_produzir=True,
            disponivel=True
        )
        assert p_test["qtd_disp"] == 10
        data_manager.excluir_produto(p_test["id"])
        print("  [PASS] DataManager Cardapio Delivery: Cadastro completo validado com sucesso.")
    except Exception as e:
        print(f"  [FAIL] Erro no DataManager: {e}")
        erros.append(f"DataManager: {e}")

    print("-" * 60)
    if erros:
        print(f"RESULTADO: {len(erros)} falhas.")
        return False
    else:
        print("RESULTADO: TODOS OS TESTES PASSARAM COM SUCESSO!")
        return True

if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)

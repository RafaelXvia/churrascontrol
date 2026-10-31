"""
Teste Automatizado: Funcionalidade de Cardápio Delivery & Paridade de Schema de Produto
Localização: tools/test_cardapio_delivery.py
"""
import sys
import os
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import data_manager

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def test_cardapio_delivery():
    print("=" * 65)
    print("TESTE: CARDAPIO DELIVERY & SCHEMA COMPLETO DE PRODUTO")
    print("=" * 65)

    test_code = f"T{int(time.time()) % 100000}"

    # 1. Cadastro com todos os campos da tabela produto
    p = data_manager.criar_produto(
        codigo_pdv=test_code,
        nome="Ancho Especial Parrilla",
        categoria="Carnes",
        preco_unitario=84.50,
        descricao="Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.",
        url_imagem="https://images.unsplash.com/photo-1558030006-450675393462?w=600",
        qtd_disp=14,
        precisa_produzir=True,
        disponivel=True
    )
    assert p["codigo_pdv"] == test_code
    assert p["descricao"] == "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva."
    assert p["qtd_disp"] == 14
    assert p["precisa_produzir"] == 1
    assert p["disponivel"] == 1
    print("  [PASS] Criacao de produto com campos completos OK.")

    # 2. Listagem e Filtro por Categoria
    prods = data_manager.listar_produtos(busca=test_code)
    assert len(prods) == 1
    assert prods[0]["url_imagem"].startswith("https://images.unsplash.com")
    print("  [PASS] Listagem e busca com foto e descricao OK.")

    # 3. Atualizacao de Produto com novos atributos
    data_manager.atualizar_produto(
        produto_id=p["id"],
        codigo_pdv=test_code,
        nome="Ancho Especial Parrilla (Atualizado)",
        categoria="Carnes",
        preco_unitario=89.00,
        descricao="Descricao atualizada para teste.",
        url_imagem="https://images.unsplash.com/photo-atualizada",
        qtd_disp=5,
        precisa_produzir=False,
        disponivel=False
    )
    prods_up = data_manager.listar_produtos(busca=test_code)
    assert prods_up[0]["nome"] == "Ancho Especial Parrilla (Atualizado)"
    assert prods_up[0]["qtd_disp"] == 5
    assert prods_up[0]["precisa_produzir"] == 0
    assert prods_up[0]["disponivel"] == 0
    print("  [PASS] Atualizacao de campos operacionais e cadastrais OK.")

    # 4. Limpeza
    data_manager.excluir_produto(p["id"])
    assert len(data_manager.listar_produtos(busca=test_code)) == 0
    print("  [PASS] Exclusao de produto OK.")

    print("-" * 65)
    print("RESULTADO: TODOS OS TESTES DE CARDAPIO DELIVERY PASSARAM COM SUCESSO!")
    return True

if __name__ == "__main__":
    ok = test_cardapio_delivery()
    sys.exit(0 if ok else 1)

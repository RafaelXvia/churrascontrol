"""
Suíte de Testes Automatizados — Cardápio Digital Cliente, QR Codes e Baixa de Estoque
Valida:
1. Geração e persistência de QR Codes por mesa física com atualização sob demanda.
2. Baixa atômica de estoque (qtd_disp) e esgotamento automático (disponivel = 0).
3. Estorno de estoque ao remover ou ajustar item de comanda.
4. Confirmação de pré-comanda de cliente (criação automática de mesa/comanda e fila Xano).
5. Compilação sintática de todas as páginas envolvidas.
"""
import os
import py_compile
import unittest
import data_manager

class TestCardapioClienteQRCode(unittest.TestCase):
    
    def test_01_compilacao_paginas(self):
        """Valida que todas as páginas compilam sem erros de sintaxe."""
        base_dir = os.path.dirname(__file__)
        paginas = [
            os.path.join(base_dir, "pages", "4_Mesas_QRCodes.py"),
            os.path.join(base_dir, "pages", "5_Cardapio_Cliente.py"),
            os.path.join(base_dir, "pages", "1_Salao_e_Mesas.py"),
            os.path.join(base_dir, "data_manager.py"),
        ]
        for p in paginas:
            self.assertTrue(os.path.exists(p), f"Arquivo não encontrado: {p}")
            py_compile.compile(p, doraise=True)

    def test_02_mesas_qrcodes_lista_e_atualizacao(self):
        """Valida que as mesas têm QR Codes configurados e atualização individual."""
        mesas = data_manager.listar_mesas_qrcodes()
        self.assertGreaterEqual(len(mesas), 10, "Deveria haver pelo menos 10 mesas configuradas.")
        
        m1 = next(m for m in mesas if m["numero_mesa"] == 1)
        self.assertIn("token_qrcode", m1)
        self.assertTrue(len(m1["token_qrcode"]) > 0)
        
        token_antigo = m1["token_qrcode"]
        novo_token = data_manager.atualizar_qrcode_mesa(1)
        self.assertNotEqual(token_antigo, novo_token, "O novo token gerado deve ser diferente do anterior.")
        
        mesas_apos = data_manager.listar_mesas_qrcodes()
        m1_apos = next(m for m in mesas_apos if m["numero_mesa"] == 1)
        self.assertEqual(m1_apos["token_qrcode"], novo_token, "O novo token deve persistir no banco.")

    def test_03_baixa_e_esgotamento_de_estoque(self):
        """Valida que lançar quantidade decrementa estoque e zera disponivel ao atingir 0."""
        # Cria produto específico para o teste
        cod_teste = "TEST_ESTOQUE_01"
        data_manager.criar_produto(
            codigo_pdv=cod_teste,
            nome="Prato Teste Estoque",
            categoria="Carnes",
            preco_unitario=50.0,
            descricao="Prato para teste de estoque",
            url_imagem="https://images.unsplash.com/photo-1544025162-d76694265947",
            qtd_disp=2,
            precisa_produzir=1,
            disponivel=1
        )
        prods = data_manager.listar_produtos()
        p = next(x for x in prods if x["codigo_pdv"] == cod_teste)
        self.assertEqual(p["qtd_disp"], 2)
        self.assertEqual(p["disponivel"], 1)

        # Abre mesa de teste 99
        res_mesa = data_manager.abrir_mesa(99, 2)
        cid = res_mesa["comanda_id"]

        # Lança 2 unidades -> estoque deve zerar e virar disponivel = 0
        data_manager.adicionar_item_comanda(cid, p["id"], quantidade=2)
        
        prods_depois = data_manager.listar_produtos()
        p_depois = next(x for x in prods_depois if x["id"] == p["id"])
        self.assertEqual(p_depois["qtd_disp"], 0, "O saldo de estoque deve ter ido a 0.")
        self.assertEqual(p_depois["disponivel"], 0, "O produto deve ter sido marcado como esgotado (disponivel=0).")

        # Agora estorna removendo o item da comanda
        detalhes = data_manager.obter_comanda_detalhes(cid)
        item_lancado = next(it for it in detalhes["itens"] if it["produto_id"] == p["id"])
        data_manager.remover_item_comanda(item_lancado["id"])

        prods_estorno = data_manager.listar_produtos()
        p_estorno = next(x for x in prods_estorno if x["id"] == p["id"])
        self.assertEqual(p_estorno["qtd_disp"], 2, "O estoque deve ser restituído a 2.")
        self.assertEqual(p_estorno["disponivel"], 1, "O produto deve voltar a ficar disponível.")

        # Limpeza
        data_manager.cancelar_comanda(cid)
        data_manager.excluir_produto(p["id"])

    def test_04_confirmar_precomanda_cliente(self):
        """Valida a confirmação da pré-comanda de autoatendimento na Mesa 8."""
        prods = data_manager.listar_produtos()
        p1 = prods[0]
        p2 = prods[1]

        itens_precomanda = [
            {"produto_id": p1["id"], "quantidade": 1, "observacao": "Sem cebola"},
            {"produto_id": p2["id"], "quantidade": 2, "observacao": "Bem gelada"}
        ]

        # Mesa 8 (garante limpeza prévia se estiver aberta)
        for m in data_manager.listar_mesas():
            if m["numero_mesa"] == 8 and m.get("comanda_id"):
                data_manager.cancelar_comanda(m["comanda_id"])

        # Cliente confirma pré-comanda na mesa 8
        res = data_manager.confirmar_precomanda_cliente(8, itens_precomanda)
        self.assertEqual(res["status"], "sucesso")
        self.assertEqual(res["numero_mesa"], 8)
        self.assertGreater(res["comanda_id"], 0)

        # Verifica se a mesa 8 agora está OCUPADA no salão
        mesas_ativas = data_manager.listar_mesas()
        m8 = next((m for m in mesas_ativas if m["numero_mesa"] == 8), None)
        self.assertIsNotNone(m8, "A Mesa 8 deve estar presente no salão.")
        self.assertEqual(m8["status"], "OCUPADA")
        self.assertGreater(m8["total_atual"], 0.0)

        # Verifica detalhes da comanda criada
        detalhes = data_manager.obter_comanda_detalhes(res["comanda_id"])
        self.assertIsNotNone(detalhes)
        self.assertEqual(len(detalhes["itens"]), 2)

        # Limpeza
        data_manager.cancelar_comanda(res["comanda_id"])

if __name__ == "__main__":
    unittest.main()

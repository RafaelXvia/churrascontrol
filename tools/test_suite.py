"""
Suíte Central e Unificada de Testes Automatizados — ChurrasControl
Localização: tools/test_suite.py

Reúne, em módulos integrados e coesos, todas as validações de:
  1. Integridade Estrutural & Compilação (todas as páginas e módulos)
  2. Operações de Cardápio, Delivery & Catálogo de Produtos
  3. Ciclo de Salão, Mesas, QR Codes & Baixa de Estoque
  4. Segurança, Integridade Relacional & Performance SQLite
  5. Autenticação, RBAC & Criptografia de Ponta a Ponta
  6. Imutabilidade Histórica & Preservação de Vendas pós-Restart
  7. Auditoria Operacional do Sistema

Como executar:
  python tools/test_suite.py
ou através do orquestrador isolado:
  python tools/run_all.py
"""
import os
import sys
import time
import shutil
import sqlite3
import tempfile
import py_compile
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

os.environ["TESTING_ENV"] = "1"

_OWN_TEMP_DIR = None
if not os.environ.get("CHURRAS_DB_PATH"):
    _OWN_TEMP_DIR = tempfile.mkdtemp(prefix="churras_test_direct_")
    _direct_test_db = os.path.join(_OWN_TEMP_DIR, "churrascontrol_direct_test.db")
    _prod_db = os.path.join(PROJECT_ROOT, "churrascontrol.db")
    if os.path.exists(_prod_db):
        shutil.copy2(_prod_db, _direct_test_db)
    os.environ["CHURRAS_DB_PATH"] = _direct_test_db

from unittest.mock import MagicMock, patch
from backend.database import data_manager      # noqa: E402
from backend.ai import ontologia              # noqa: E402
from backend.ai import assistente_ia          # noqa: E402
from frontend.components import ui_components # noqa: E402


class Test01EstruturaECompilacao(unittest.TestCase):
    """Módulo 1: Validação de Sintaxe e Compilação de Telas e Módulos."""

    def test_compilacao_arquivos_principais(self):
        arquivos = [
            os.path.join("backend", "database", "data_manager.py"),
            os.path.join("frontend", "components", "ui_components.py"),
            os.path.join("backend", "ai", "ontologia.py"),
            os.path.join("backend", "ai", "assistente_ia.py"),
            "app.py",
            "run.py",
            os.path.join("pages", "1_Salao_e_Mesas.py"),
            os.path.join("pages", "2_Cardapio.py"),
            os.path.join("pages", "3_Relatorios.py"),
            os.path.join("pages", "4_Mesas_QRCodes.py"),
            os.path.join("pages", "5_Cardapio_Cliente.py"),
            os.path.join("pages", "6_Colaboradores.py"),
            os.path.join("pages", "7_Auditoria.py"),
            os.path.join("pages", "8_Assistente_IA.py"),
        ]
        for arq in arquivos:
            caminho = os.path.join(PROJECT_ROOT, arq)
            self.assertTrue(os.path.exists(caminho), f"Arquivo ausente: {arq}")
            py_compile.compile(caminho, doraise=True)


class Test02CardapioEDelivery(unittest.TestCase):
    """Módulo 2: Gestão do Cardápio, Delivery e Integridade do Produto."""

    def test_crud_produto_completo(self):
        codigo = f"TEST_CARD_{int(time.time() * 1000) % 100000}"
        
        # 1. Criação completa com todos os atributos do schema
        p = data_manager.criar_produto(
            codigo_pdv=codigo,
            nome="Picanha Especial Teste",
            categoria="Carnes",
            preco_unitario=89.90,
            descricao="Corte nobre com brasa intensa.",
            url_imagem="https://images.unsplash.com/photo-1544025162-d76694265947",
            qtd_disp=15,
            precisa_produzir=True,
            disponivel=True
        )
        self.assertEqual(p["codigo_pdv"], codigo)
        self.assertEqual(p["qtd_disp"], 15)
        self.assertEqual(p["disponivel"], 1)

        # 2. Busca e listagem
        encontrados = data_manager.listar_produtos(busca=codigo)
        self.assertEqual(len(encontrados), 1)

        # 3. Atualização de dados
        data_manager.atualizar_produto(
            produto_id=p["id"],
            codigo_pdv=codigo,
            nome="Picanha Especial Atualizada",
            categoria="Carnes",
            preco_unitario=95.00,
            descricao="Nova descrição.",
            url_imagem="https://images.unsplash.com/photo-atualizada",
            qtd_disp=8,
            precisa_produzir=False,
            disponivel=False
        )
        atualizado = data_manager.listar_produtos(busca=codigo)[0]
        self.assertEqual(atualizado["nome"], "Picanha Especial Atualizada")
        self.assertEqual(atualizado["qtd_disp"], 8)
        self.assertEqual(atualizado["disponivel"], 0)

        # 4. Exclusão limpa
        data_manager.excluir_produto(p["id"])
        self.assertEqual(len(data_manager.listar_produtos(busca=codigo)), 0)


class Test03SalaoMesasEQRCode(unittest.TestCase):
    """Módulo 3: Ciclo de Mesas, Lançamento, QR Codes e Baixa de Estoque."""

    def test_ciclo_operacional_mesa_e_qrcode(self):
        num_mesa = 876
        
        # Garantir mesa limpa
        with data_manager.get_connection() as c:
            c.execute("DELETE FROM mesas WHERE numero_mesa = ?", (num_mesa,))
            c.execute("DELETE FROM comandas WHERE numero_mesa_historico = ?", (num_mesa,))
            c.commit()

        # 1. Abertura de Mesa
        abertura = data_manager.abrir_mesa(num_mesa, qtd_pessoas=2)
        comanda_id = abertura["comanda_id"]
        self.assertIsNotNone(comanda_id)

        # 2. Criar produto para consumo
        p = data_manager.criar_produto(
            codigo_pdv=f"ESTQ_{num_mesa}",
            nome="Cerveja Artesanal Teste",
            categoria="Bebidas",
            preco_unitario=15.0,
            qtd_disp=5,
            disponivel=1
        )

        # 3. Lançamento e agregação de item
        data_manager.adicionar_item_comanda(comanda_id, p["id"], quantidade=2, observacao="Bem gelada")
        data_manager.adicionar_item_comanda(comanda_id, p["id"], quantidade=1)
        detalhes = data_manager.obter_comanda_detalhes(comanda_id)
        self.assertEqual(len(detalhes["itens"]), 1)
        self.assertEqual(detalhes["itens"][0]["quantidade"], 3)

        # 4. Fechamento de Comanda e liberação da mesa
        total = detalhes["total"]
        data_manager.fechar_comanda(comanda_id, valor_final=round(total * 1.10, 2), taxa_servico=True)

        mesas_ativas = [m["numero_mesa"] for m in data_manager.listar_mesas()]
        self.assertNotIn(num_mesa, mesas_ativas, "A mesa deveria estar liberada após o pagamento.")

        # Limpeza
        with data_manager.get_connection() as c:
            c.execute("DELETE FROM itens_comanda WHERE comanda_id = ?", (comanda_id,))
            c.execute("DELETE FROM comandas WHERE id = ?", (comanda_id,))
            c.execute("DELETE FROM produtos WHERE id = ?", (p["id"],))
            c.commit()

    def test_qrcodes_mesas_persistencia(self):
        mesas_qr = data_manager.listar_mesas_qrcodes()
        self.assertGreaterEqual(len(mesas_qr), 10)
        tok_antigo = mesas_qr[0]["token_qrcode"]
        tok_novo = data_manager.atualizar_qrcode_mesa(mesas_qr[0]["numero_mesa"])
        self.assertNotEqual(tok_antigo, tok_novo)

    def test_sincronizacao_abertura_comanda_xano(self):
        """Valida que abrir_mesa dispara o push da comanda pai para /comandas no Xano."""
        with patch.object(data_manager, "_sync_push_imediato_ou_enfileirar") as mock_sync:
            # Garantir mesa limpa antes
            with data_manager.get_connection() as c:
                c.execute("DELETE FROM mesas WHERE numero_mesa = 998")
                c.execute("DELETE FROM comandas WHERE numero_mesa_historico = 998")
                c.commit()

            res = data_manager.abrir_mesa(998, qtd_pessoas=3)
            cid = res["comanda_id"]

            chamadas = [call for call in mock_sync.call_args_list if call[0][0] == "POST" and call[0][1] == "/comandas"]
            self.assertTrue(len(chamadas) >= 1)
            payload = chamadas[0][0][2]
            self.assertEqual(payload["id"], cid)
            self.assertEqual(payload["numero_mesa"], 998)
            self.assertEqual(payload["qtd_pessoas"], 3)

            # Limpeza
            data_manager.cancelar_comanda(cid)


class Test04SegurancaEPerformance(unittest.TestCase):
    """Módulo 4: Restrições de Domínio, Sanitização XSS e Cardinalidade Única."""

    def test_restricoes_preco_e_xss(self):
        # Preço negativo ou zero deve ser rejeitado
        with self.assertRaises(ValueError):
            data_manager.criar_produto("ERR_NEG", "Item Negativo", "Comida", preco_unitario=-5.0)
        with self.assertRaises(ValueError):
            data_manager.criar_produto("ERR_ZERO", "Item Zero", "Comida", preco_unitario=0.0)

        # Sanitização XSS em nome e categoria
        p_xss = data_manager.criar_produto("ERR_XSS", "<script>alert(1)</script>", "<b>Carnes</b>", preco_unitario=20.0)
        self.assertNotIn("<script>", p_xss["nome"])
        self.assertNotIn("<b>", p_xss["categoria"])
        data_manager.excluir_produto(p_xss["id"])

    def test_cardinalidade_unica_comanda_aberta(self):
        mesa_teste = 765
        with data_manager.get_connection() as c:
            c.execute("DELETE FROM mesas WHERE numero_mesa = ?", (mesa_teste,))
            c.execute("DELETE FROM comandas WHERE numero_mesa_historico = ?", (mesa_teste,))
            c.commit()

        res = data_manager.abrir_mesa(mesa_teste, qtd_pessoas=2)
        # Segunda abertura para mesma mesa deve falhar
        with self.assertRaises(ValueError):
            data_manager.abrir_mesa(mesa_teste, qtd_pessoas=2)

        data_manager.fechar_comanda(res["comanda_id"], valor_final=10.0, taxa_servico=False)
        with data_manager.get_connection() as c:
            c.execute("DELETE FROM comandas WHERE id = ?", (res["comanda_id"],))
            c.commit()


class Test05AutenticacaoERBAC(unittest.TestCase):
    """Módulo 5: Hashing, Login, Recuperação de Credenciais e Criptografia AES-256."""

    def test_autenticacao_e_rbac_fluxo_completo(self):
        email_gerente_teste = "gerente_suite_test@churrascontrol.com"
        email_caixa_teste = "caixa_suite_test@churrascontrol.com"

        # Limpeza preventiva de colaboradores de teste
        for c in data_manager.listar_colaboradores():
            if c["email"] in (email_gerente_teste, email_caixa_teste):
                data_manager.excluir_colaborador(c["id"])

        # 1. Cadastro de Gerente de teste com senha forte
        gerente_teste = data_manager.cadastrar_colaborador(
            nome="Gerente Teste Suíte",
            email=email_gerente_teste,
            senha="SenhaForteGerente123",
            numero="(31) 99999-1111",
            cargo="gerente"
        )
        self.assertEqual(gerente_teste["cargo"], "gerente")

        # 2. Autentica com sucesso
        auth_ok = data_manager.autenticar_usuario(email_gerente_teste, "SenhaForteGerente123")
        self.assertIsNotNone(auth_ok)
        self.assertEqual(auth_ok["email"], email_gerente_teste)
        self.assertEqual(auth_ok["cargo"], "gerente")

        # 3. Senha inválida é rejeitada
        self.assertIsNone(data_manager.autenticar_usuario(email_gerente_teste, "senha_incorreta"))

        # 4. Cadastro de colaborador Caixa com primeiro acesso
        novo_caixa = data_manager.cadastrar_colaborador(
            nome="Operador Caixa Suíte",
            email=email_caixa_teste,
            senha="temp123Caixa",
            numero="(31) 98888-7777",
            cargo="caixa"
        )
        self.assertEqual(novo_caixa["cargo"], "caixa")
        self.assertTrue(novo_caixa["primeiro_acesso"])

        # 5. Atualização de senha do caixa
        ok_senha = data_manager.atualizar_senha_colaborador(novo_caixa["id"], "novaSenhaCaixa456")
        self.assertTrue(ok_senha)
        self.assertIsNotNone(data_manager.autenticar_usuario(email_caixa_teste, "novaSenhaCaixa456"))

        # 6. Exclusão de colaboradores de teste
        data_manager.excluir_colaborador(novo_caixa["id"])
        data_manager.excluir_colaborador(gerente_teste["id"])


class Test06HistoricoDeVendasEImutabilidade(unittest.TestCase):
    """Módulo 6: Preservação de Itens de Comandas Pagas pós-Restart e Relatórios."""

    def test_itens_pagos_sobrevivem_restart(self):
        mesa_paga = 654
        with data_manager.get_connection() as c:
            c.execute("DELETE FROM mesas WHERE numero_mesa = ?", (mesa_paga,))
            c.execute("DELETE FROM comandas WHERE numero_mesa_historico = ?", (mesa_paga,))
            c.commit()

        p = data_manager.criar_produto(
            codigo_pdv=f"PROD_HIST_{mesa_paga}",
            nome="Corte Angus Imutável",
            categoria="Carnes",
            preco_unitario=75.0,
            qtd_disp=20,
            disponivel=1
        )

        res = data_manager.abrir_mesa(mesa_paga, qtd_pessoas=2)
        cid = res["comanda_id"]
        data_manager.adicionar_item_comanda(cid, p["id"], quantidade=3)
        data_manager.fechar_comanda(cid, valor_final=225.0, taxa_servico=False)

        # Simula restart da aplicação reexecutando init_db
        data_manager._db_initialized = False
        data_manager.init_db()

        # Verifica se os itens continuam intactos
        with data_manager.get_connection() as c:
            qtd = c.execute("SELECT COUNT(*) FROM itens_comanda WHERE comanda_id = ?", (cid,)).fetchone()[0]
        self.assertEqual(qtd, 1, "Itens de comanda PAGA não podem ser apagados pelo init_db()!")

        # Verifica reflexo no dashboard
        dash = data_manager.obter_dashboard_dados("1d")
        self.assertGreaterEqual(dash["resumo"]["faturamento_total"], 225.0)

        # Limpeza
        with data_manager.get_connection() as c:
            c.execute("DELETE FROM itens_comanda WHERE comanda_id = ?", (cid,))
            c.execute("DELETE FROM comandas WHERE id = ?", (cid,))
            c.execute("DELETE FROM produtos WHERE id = ?", (p["id"],))
            c.commit()


class Test07OntologiaERAG(unittest.TestCase):
    """Módulo 7: Ontologia do Churrasco, Catálogo de Ferramentas & RAG."""

    def setUp(self):
        ontologia.seed_ontologia()

    def test_resolucao_sinonimos(self):
        # 'breja' -> cerveja (spec menciona termos informais de cerveja)
        c_breja = ontologia.resolver_termo("breja")
        self.assertIsNotNone(c_breja)
        self.assertEqual(c_breja["id"], "cerveja")

        # 'carne' -> carnes (spec: sinônimo direto)
        c_carne = ontologia.resolver_termo("carne")
        self.assertIsNotNone(c_carne)
        self.assertEqual(c_carne["id"], "carnes")

        # 'suco' -> bebidas (categoria real no banco)
        c_suco = ontologia.resolver_termo("suco")
        self.assertIsNotNone(c_suco)
        self.assertEqual(c_suco["id"], "bebidas")

        # 'refri' NÃO existe mais na ontologia (conceito removido)
        c_refri = ontologia.resolver_termo("refri")
        self.assertIsNone(c_refri)

    def test_mapeamento_mesas_por_setor(self):
        # 3 setores definidos na spec
        varanda = ontologia.obter_mesas_por_setor("varanda")
        self.assertEqual(varanda, [1, 2, 3, 4])

        salao = ontologia.obter_mesas_por_setor("salao_principal")
        self.assertEqual(salao, [5, 6, 7, 8])

        kids = ontologia.obter_mesas_por_setor("kids")
        self.assertEqual(kids, [9, 10])

        # 'vip' NÃO existe mais na ontologia
        vip = ontologia.obter_mesas_por_setor("vip")
        self.assertEqual(vip, [])

    def test_mapeamento_turnos(self):
        # 3 turnos definidos na spec
        almoco = ontologia.obter_intervalo_turno("almoco")
        self.assertIsNotNone(almoco)
        self.assertEqual(almoco["inicio"], "11:30")
        self.assertEqual(almoco["fim"], "15:30")

        jantar = ontologia.obter_intervalo_turno("jantar")
        self.assertIsNotNone(jantar)
        self.assertEqual(jantar["inicio"], "18:30")
        self.assertEqual(jantar["fim"], "23:59")

        happy = ontologia.obter_intervalo_turno("happy hour")
        self.assertIsNotNone(happy)
        self.assertEqual(happy["inicio"], "17:00")
        self.assertEqual(happy["fim"], "19:30")

        # 'madrugada' NÃO existe mais na ontologia
        madrugada = ontologia.obter_intervalo_turno("madrugada")
        self.assertIsNone(madrugada)

    def test_expansao_conceitos_subclasses(self):
        from backend.database import data_manager as dm
        # 'carnes' tem picanha, ancho, costela, vaca_atolada como subclasses (spec)
        subclasses = ontologia.obter_subclasses("carnes")
        self.assertIn("picanha", subclasses)
        self.assertIn("ancho", subclasses)
        self.assertIn("costela", subclasses)
        self.assertIn("vaca_atolada", subclasses)

        # 'carnes_nobres' foi removido — NÃO deve existir em ontologia_conceitos
        with dm.get_connection() as conn:
            r = conn.execute(
                "SELECT id FROM ontologia_conceitos WHERE id = 'carnes_nobres'"
            ).fetchone()
            self.assertIsNone(r, "Conceito 'carnes_nobres' não deveria existir na ontologia")

        # 'vip' foi removido — NÃO deve existir em ontologia_conceitos
        with dm.get_connection() as conn:
            r = conn.execute(
                "SELECT id FROM ontologia_conceitos WHERE id = 'vip'"
            ).fetchone()
            self.assertIsNone(r, "Conceito 'vip' não deveria existir na ontologia")

    def test_ferramentas_analiticas_read_only(self):
        # 1. Resumo financeiro — assinatura: inicio, fim, turno (sem 'dias')
        res_fin = assistente_ia.resumo_financeiro()
        self.assertIn("faturamento_bruto_reais", res_fin)
        self.assertIn("total_comandas_pagas", res_fin)
        self.assertIn("ticket_medio_comanda", res_fin)

        # 2. Ranking de mesas
        res_mesas = assistente_ia.ranking_mesas(limite=5)
        self.assertIn("ranking_mesas", res_mesas)
        self.assertIn("total_mesas_ranqueadas", res_mesas)

        # 3. Ranking de produtos
        res_prod = assistente_ia.ranking_produtos(limite=5)
        self.assertIn("ranking_produtos", res_prod)

        # 4. Vendas por categoria
        res_cat = assistente_ia.vendas_por_categoria()
        self.assertIn("vendas_categorias", res_cat)   # chave real no retorno
        self.assertIn("receita_geral_reais", res_cat)

        # 5. Evolução temporal
        res_evo = assistente_ia.evolucao_temporal(granularidade="dia")
        self.assertIn("serie_temporal", res_evo)

        # 6. Estoque crítico
        res_est = assistente_ia.estoque_critico()
        self.assertIn("produtos_criticos", res_est)
        self.assertIn("total_criticos", res_est)

        # 7. Salão em tempo real
        res_sal = assistente_ia.salao_tempo_real()
        self.assertIn("total_mesas", res_sal)
        self.assertIn("mesas_ocupadas", res_sal)

        # 8. Auditoria operacional
        res_aud = assistente_ia.auditoria_operacional(limite=5)
        self.assertIn("registros_auditoria", res_aud)   # chave real: registros_auditoria
        self.assertIn("total_encontrado", res_aud)

        # 9. Verificação de trava estrita Read-Only no SQLite
        with assistente_ia.get_readonly_connection() as ro_conn:
            with self.assertRaises(sqlite3.OperationalError):
                ro_conn.execute("INSERT INTO produtos (codigo_pdv, nome, categoria, preco_unitario) VALUES ('TEST_RO', 'Bloqueado', 'Carnes', 10)")

    def test_chat_persistencia_e_historico(self):
        # criar_conversa exige (usuario_id, titulo)
        usuario_teste = "gerente_teste_rag"
        cid = assistente_ia.criar_conversa(usuario_teste, "Conversa de Teste RAG")
        self.assertTrue(bool(cid))

        # salvar_mensagem_chat: papel (não 'role'), modelo_utilizado (não 'modelo'), sem 'evidencias'
        assistente_ia.salvar_mensagem_chat(cid, "user", "Qual o faturamento?")
        assistente_ia.salvar_mensagem_chat(
            cid, "assistant", "O faturamento foi R$ 1.000,00.",
            api_origem="Chave 1",
            modelo_utilizado="gemini-2.5-flash",
            tentativas_falhas=0
        )

        mensagens = assistente_ia.carregar_historico_chat(cid)
        self.assertEqual(len(mensagens), 2)
        # coluna no DB é 'papel', não 'role'
        self.assertEqual(mensagens[0]["papel"], "user")
        self.assertEqual(mensagens[1]["papel"], "assistant")
        self.assertEqual(mensagens[1]["api_origem"], "Chave 1")
        self.assertEqual(mensagens[1]["modelo_utilizado"], "gemini-2.5-flash")

        # listar_conversas exige usuario_id
        convs = assistente_ia.listar_conversas(usuario_teste)
        self.assertTrue(any(c["id"] == cid for c in convs))


class Test08CascataFallbackELLM(unittest.TestCase):
    """Módulo 8: Cascata de Fallback LLM Multichave, Descoberta Dinâmica & Segurança."""

    def setUp(self):
        assistente_ia._discovered_models_cache.clear()
        assistente_ia._model_cooldowns.clear()

    def test_descoberta_modelos_filtragem(self):
        m1 = MagicMock()
        m1.name = "models/gemini-2.5-flash"
        m1.supported_actions = ["generateContent"]

        m2 = MagicMock()
        m2.name = "models/text-embedding-004"
        m2.supported_actions = ["embedContent"]

        m3 = MagicMock()
        m3.name = "models/gemini-2.5-pro"
        m3.supported_actions = ["generateContent"]

        m4 = MagicMock()
        m4.name = "models/imagen-3.0"
        m4.supported_actions = ["generateContent"]

        with patch("google.genai.Client") as mock_client_cls:
            inst = MagicMock()
            inst.models.list.return_value = [m1, m2, m3, m4]
            mock_client_cls.return_value = inst

            modelos = assistente_ia.descobrir_modelos_chave("fake_key_123", "Chave 1")
            self.assertIn("gemini-2.5-flash", modelos)
            self.assertIn("gemini-2.5-pro", modelos)
            self.assertNotIn("text-embedding-004", modelos)
            self.assertNotIn("imagen-3.0", modelos)

    def test_fallback_chave1_para_chave2_e_cooldown(self):
        old_k1 = os.environ.get("GOOGLE_API_KEY_1")
        old_k2 = os.environ.get("GOOGLE_API_KEY_2")
        os.environ["GOOGLE_API_KEY_1"] = "sim_key_1"
        os.environ["GOOGLE_API_KEY_2"] = "sim_key_2"

        try:
            def mock_client_factory(api_key=None):
                c = MagicMock()
                m_flash = MagicMock()
                m_flash.name = "models/gemini-2.5-flash"
                m_flash.supported_actions = ["generateContent"]
                c.models.list.return_value = [m_flash]

                if api_key == "sim_key_1":
                    c.models.generate_content.side_effect = Exception("429 Resource Exhausted: Quota exceeded for model")
                else:
                    resp = MagicMock()
                    resp.text = "Relatório executivo gerado com sucesso via Chave 2."
                    resp.function_calls = None
                    c.models.generate_content.return_value = resp
                return c

            with patch("google.genai.Client", side_effect=mock_client_factory):
                res = assistente_ia.executar_pergunta_gerente("Qual o prato mais vendido?")
                self.assertTrue(res["sucesso"])
                self.assertEqual(res["api_origem"], "Chave 2")
                self.assertEqual(res["modelo"], "gemini-2.5-flash")
                self.assertGreaterEqual(res["tentativas_falhas"], 1)
                self.assertIn("Relatório executivo", res["resposta"])
                self.assertTrue(assistente_ia.is_em_cooldown("Chave 1", "gemini-2.5-flash"))
        finally:
            if old_k1 is not None:
                os.environ["GOOGLE_API_KEY_1"] = old_k1
            else:
                os.environ.pop("GOOGLE_API_KEY_1", None)
            if old_k2 is not None:
                os.environ["GOOGLE_API_KEY_2"] = old_k2
            else:
                os.environ.pop("GOOGLE_API_KEY_2", None)

    def test_esgotamento_total_cascata_fail_safe_sem_alucinacao(self):
        old_k1 = os.environ.get("GOOGLE_API_KEY_1")
        old_k2 = os.environ.get("GOOGLE_API_KEY_2")
        os.environ["GOOGLE_API_KEY_1"] = "sim_key_1"
        os.environ["GOOGLE_API_KEY_2"] = "sim_key_2"

        try:
            def mock_fail_factory(api_key=None):
                c = MagicMock()
                m = MagicMock()
                m.name = "models/gemini-2.5-flash"
                m.supported_actions = ["generateContent"]
                c.models.list.return_value = [m]
                c.models.generate_content.side_effect = Exception("503 Service Unavailable")
                return c

            with patch("google.genai.Client", side_effect=mock_fail_factory):
                res = assistente_ia.executar_pergunta_gerente("Qual o faturamento de ontem?")
                self.assertFalse(res["sucesso"])
                # A mensagem fail-safe usa "temporariamente indisponível" (sem inventar dados)
                resposta_lower = res["resposta"].lower()
                self.assertTrue(
                    "temporariamente" in resposta_lower or "indispon" in resposta_lower,
                    f"Mensagem fail-safe inesperada: {res['resposta']}"
                )
                self.assertGreaterEqual(res["tentativas_falhas"], 2)
        finally:
            if old_k1 is not None:
                os.environ["GOOGLE_API_KEY_1"] = old_k1
            else:
                os.environ.pop("GOOGLE_API_KEY_1", None)
            if old_k2 is not None:
                os.environ["GOOGLE_API_KEY_2"] = old_k2
            else:
                os.environ.pop("GOOGLE_API_KEY_2", None)

    def test_seguranca_chaves_nao_gravadas_em_sqlite_ou_logs(self):
        with data_manager.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT api_origem, erro_motivo FROM llm_fallback_logs")
            logs = cur.fetchall()
            for r in logs:
                origem = r["api_origem"]
                motivo = r["erro_motivo"] or ""
                # A chave simulada nunca deve aparecer em nenhum campo de log
                self.assertNotIn("sim_key_1", origem)
                self.assertNotIn("sim_key_2", origem)
                self.assertNotIn("sim_key_1", motivo)
                self.assertNotIn("sim_key_2", motivo)
                self.assertIn(origem, ["Chave 1", "Chave 2", "Nenhuma", "Cascata Esgotada"])

    def test_zero_insercoes_fila_sincronizacao(self):
        # fila_sincronizacao tem colunas: id, metodo, rota, payload_json, status, tentativas, ultimo_erro, criado_em, processado_em
        # Não tem coluna 'tabela'. Verificamos que nenhuma rota de IA foi inserida na fila.
        with data_manager.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT COUNT(*) FROM fila_sincronizacao 
            WHERE rota LIKE '%ontologia%'
               OR rota LIKE '%chat%'
               OR rota LIKE '%llm%'
               OR rota LIKE '%assistente%'
            """)
            qtd = cur.fetchone()[0]
            self.assertEqual(qtd, 0, "Módulos de IA não podem inserir na fila de sincronização Xano!")


class Test09BlindagemOtimizacaoEParidade(unittest.TestCase):
    """Módulo 9: PBKDF2-HMAC-SHA256, Rate Limit, Validação QR Code, Zero-Pandas e WAL."""

    def test_pbkdf2_e_migracao_transparente_legado(self):
        email_mig = "migracao_pbkdf2_test@churrascontrol.com"
        for c in data_manager.listar_colaboradores():
            if c["email"] == email_mig:
                data_manager.excluir_colaborador(c["id"])

        colab = data_manager.cadastrar_colaborador(
            nome="Teste PBKDF2",
            email=email_mig,
            senha="SenhaSegura2026",
            numero="(31) 97777-6666",
            cargo="caixa"
        )
        # Verifica que o hash gerado já nasce no padrão PBKDF2-HMAC-SHA256
        with data_manager.get_connection() as conn:
            h_atual = conn.execute("SELECT senha_hash FROM colaboradores WHERE id = ?", (colab["id"],)).fetchone()["senha_hash"]
            self.assertTrue(h_atual.startswith("pbkdf2_sha256$100000$"))

            # Simula um hash SHA-256 legado e verifica migração transparente no login
            hash_legado = data_manager._gerar_hash_senha_legado("SenhaSegura2026")
            conn.execute("UPDATE colaboradores SET senha_hash = ? WHERE id = ?", (hash_legado, colab["id"]))
            conn.commit()

        u_logado = data_manager.autenticar_usuario(email_mig, "SenhaSegura2026")
        self.assertIsNotNone(u_logado)
        with data_manager.get_connection() as conn:
            h_migrado = conn.execute("SELECT senha_hash FROM colaboradores WHERE id = ?", (colab["id"],)).fetchone()["senha_hash"]
            self.assertTrue(h_migrado.startswith("pbkdf2_sha256$100000$"))

        data_manager.excluir_colaborador(colab["id"])

    def test_rate_limiting_anti_brute_force(self):
        email_rl = "brute_force_target@churrascontrol.com"
        data_manager._limpar_falhas_login(email_rl)
        for _ in range(5):
            self.assertIsNone(data_manager.autenticar_usuario(email_rl, "errada"))
        self.assertTrue(data_manager._esta_bloqueado_rate_limit_login(email_rl))
        data_manager._limpar_falhas_login(email_rl)

    def test_validacao_token_qrcode_e_zero_pandas(self):
        mesas_qr = data_manager.listar_mesas_qrcodes()
        m1 = mesas_qr[0]
        self.assertTrue(data_manager.validar_acesso_cardapio_qr(m1["numero_mesa"], m1["token_qrcode"]))
        self.assertFalse(data_manager.validar_acesso_cardapio_qr(m1["numero_mesa"], "token-falso-invalido"))
        self.assertFalse(data_manager.validar_acesso_cardapio_qr(m1["numero_mesa"], ""))

        # Garante que pages/7_Auditoria.py não importa pandas
        auditoria_path = os.path.join(PROJECT_ROOT, "pages", "7_Auditoria.py")
        with open(auditoria_path, "r", encoding="utf-8") as f:
            conteudo_aud = f.read()
        self.assertNotIn("import pandas", conteudo_aud)


def run_full_suite():
    suite = unittest.TestSuite()
    carregador = unittest.TestLoader()
    classes = [
        Test01EstruturaECompilacao,
        Test02CardapioEDelivery,
        Test03SalaoMesasEQRCode,
        Test04SegurancaEPerformance,
        Test05AutenticacaoERBAC,
        Test06HistoricoDeVendasEImutabilidade,
        Test07OntologiaERAG,
        Test08CascataFallbackELLM,
        Test09BlindagemOtimizacaoEParidade,
    ]
    for cls in classes:
        suite.addTests(carregador.loadTestsFromTestCase(cls))

    executor = unittest.TextTestRunner(verbosity=2)
    resultado = executor.run(suite)
    return resultado.wasSuccessful()


if __name__ == "__main__":
    sucesso = False
    try:
        sucesso = run_full_suite()
    finally:
        if _OWN_TEMP_DIR and os.path.exists(_OWN_TEMP_DIR):
            shutil.rmtree(_OWN_TEMP_DIR, ignore_errors=True)
    sys.exit(0 if sucesso else 1)

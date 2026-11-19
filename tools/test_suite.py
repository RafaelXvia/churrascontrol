"""
Suíte Central e Unificada de Testes Automatizados — ChurrasControl
Localização: tools/test_suite.py

Módulos:
  1. Integridade Estrutural & Sintaxe (todas as páginas e módulos)
  2. Cardápio, Delivery & Catálogo de Produtos
  3. Salão, Mesas, QR Codes & Baixa de Estoque
  4. Segurança, Integridade Relacional & Cardinalidade
  5. Autenticação, RBAC & Hashing
  6. Imutabilidade Histórica & Preservação de Vendas pós-Restart
  7. Ontologia, Ferramentas Analíticas & RAG (Assistente IA)
  8. Cascata de Fallback LLM Multichave & Segurança de Chaves
  9. Blindagem (PBKDF2, Rate Limit, QR Token, Zero-Pandas)

Como executar:
  python tools/test_suite.py
ou:
  python tools/run_all.py

Princípios desta versão:
  - Trava que impede rodar contra o banco de produção.
  - Banco de teste copiado via sqlite3 backup (consistente com WAL).
  - Toda limpeza de dados via addCleanup (roda mesmo se o assert falhar).
  - Estado global do assistente_ia resetado em setUp/tearDown.
  - Variáveis de ambiente via patch.dict (sem try/finally manual).
  - Push ao Xano neutralizado para o módulo inteiro.
"""
import ast
import atexit
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import time
import unittest
import uuid
from contextlib import contextmanager
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

os.environ["TESTING_ENV"] = "1"

# ---------------------------------------------------------------------------
# Banco de teste isolado + trava anti-produção
# ---------------------------------------------------------------------------
_PROD_DB = os.path.abspath(os.path.join(PROJECT_ROOT, "churrascontrol.db"))
_OWN_TEMP_DIR = None

if not os.environ.get("CHURRAS_DB_PATH"):
    _OWN_TEMP_DIR = tempfile.mkdtemp(prefix="churras_test_direct_")
    _direct_test_db = os.path.join(_OWN_TEMP_DIR, "churrascontrol_direct_test.db")
    if os.path.exists(_PROD_DB):
        try:
            # backup() gera uma cópia consistente mesmo com WAL ativo
            _src = sqlite3.connect(Path(_PROD_DB).as_uri() + "?mode=ro", uri=True)
            _dst = sqlite3.connect(_direct_test_db)
            _src.backup(_dst)
            _dst.close()
            _src.close()
        except sqlite3.Error:
            shutil.copy2(_PROD_DB, _direct_test_db)
    os.environ["CHURRAS_DB_PATH"] = _direct_test_db
    atexit.register(shutil.rmtree, _OWN_TEMP_DIR, True)

if os.path.abspath(os.environ["CHURRAS_DB_PATH"]) == _PROD_DB:
    raise SystemExit(
        "RECUSADO: CHURRAS_DB_PATH aponta para o banco de PRODUÇÃO. "
        "Esta suíte apaga/insere dados e só roda em cópia temporária."
    )

from unittest.mock import MagicMock, patch  # noqa: E402
from backend.database import data_manager      # noqa: E402
from backend.ai import ontologia               # noqa: E402
from backend.ai import assistente_ia           # noqa: E402
from frontend.components import ui_components  # noqa: E402,F401

# Piso de segurança aceito para PBKDF2-HMAC-SHA256.
# Suba para 600_000 (recomendação OWASP atual) após atualizar o data_manager.
MIN_PBKDF2_ITER = 100_000

# Nomes de estados globais do assistente_ia que precisam ser zerados entre testes.
# Ajuste/adicione aqui o nome real do conjunto usado por is_chave_desativada().
_ESTADOS_GLOBAIS_IA = (
    "_discovered_models_cache",
    "_model_cooldowns",
    "_key_cooldowns",
    "_incompatible_models",
    "_disabled_keys",
    "_chaves_desativadas",
    "_keys_disabled",
)

_sync_patcher = None


def setUpModule():
    """Neutraliza o push ao Xano em TODA a suíte (nenhum teste toca a rede)."""
    global _sync_patcher
    if hasattr(data_manager, "_sync_push_imediato_ou_enfileirar"):
        _sync_patcher = patch.object(data_manager, "_sync_push_imediato_ou_enfileirar")
        _sync_patcher.start()


def tearDownModule():
    if _sync_patcher:
        _sync_patcher.stop()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _fk_itens():
    """Descobre o nome real da FK de itens_comanda (id_comanda ou comanda_id)."""
    with data_manager.get_connection() as c:
        cols = {r[1] for r in c.execute("PRAGMA table_info(itens_comanda)")}
    for nome in ("id_comanda", "comanda_id"):
        if nome in cols:
            return nome
    raise AssertionError(f"itens_comanda sem coluna FK conhecida: {cols}")


def _purge_mesa(num):
    """Remove itens, comandas e mesa de um número de mesa (idempotente)."""
    fk = _fk_itens()
    with data_manager.get_connection() as c:
        c.execute(
            f"DELETE FROM itens_comanda WHERE {fk} IN "
            "(SELECT id FROM comandas WHERE numero_mesa_historico = ?)", (num,))
        c.execute("DELETE FROM comandas WHERE numero_mesa_historico = ?", (num,))
        c.execute("DELETE FROM mesas WHERE numero_mesa = ?", (num,))
        c.commit()


def _purge_produto(codigo):
    with data_manager.get_connection() as c:
        c.execute("DELETE FROM produtos WHERE codigo_pdv = ?", (codigo,))
        c.commit()


def _remover_colab(email):
    for c in data_manager.listar_colaboradores():
        if c["email"] == email:
            data_manager.excluir_colaborador(c["id"])


def _codigo_unico(prefixo):
    return f"{prefixo}_{uuid.uuid4().hex[:8]}"


def _reset_estado_ia():
    for nome in _ESTADOS_GLOBAIS_IA:
        obj = getattr(assistente_ia, nome, None)
        if hasattr(obj, "clear"):
            obj.clear()


@contextmanager
def _env_chaves(k1, k2=None):
    """Define GOOGLE_API_KEY_1/2 e restaura o ambiente original ao sair."""
    with patch.dict(os.environ, {}, clear=False):
        os.environ["GOOGLE_API_KEY_1"] = k1
        if k2:
            os.environ["GOOGLE_API_KEY_2"] = k2
        else:
            os.environ.pop("GOOGLE_API_KEY_2", None)
        yield


def _fake_modelo(nome, acoes=("generateContent",)):
    m = MagicMock()
    m.name = f"models/{nome}"
    m.supported_actions = list(acoes)
    return m


def _fake_resposta(texto):
    r = MagicMock()
    r.text = texto
    r.function_calls = None  # evita MagicMock truthy sendo lido como tool call
    return r


# ===========================================================================
class Test01EstruturaECompilacao(unittest.TestCase):
    """Módulo 1: Validação de sintaxe (sem gravar __pycache__ no projeto)."""

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
            with self.subTest(arquivo=arq):
                caminho = os.path.join(PROJECT_ROOT, arq)
                self.assertTrue(os.path.exists(caminho), f"Arquivo ausente: {arq}")
                with open(caminho, "r", encoding="utf-8") as f:
                    ast.parse(f.read(), filename=arq)


# ===========================================================================
class Test02CardapioEDelivery(unittest.TestCase):
    """Módulo 2: Gestão do Cardápio e Integridade do Produto."""

    def test_crud_produto_completo(self):
        codigo = _codigo_unico("TEST_CARD")
        self.addCleanup(_purge_produto, codigo)

        p = data_manager.criar_produto(
            codigo_pdv=codigo,
            nome="Picanha Especial Teste",
            categoria="Carnes",
            preco_unitario=89.90,
            descricao="Corte nobre com brasa intensa.",
            url_imagem="https://images.unsplash.com/photo-1544025162-d76694265947",
            qtd_disp=15,
            precisa_produzir=True,
            disponivel=True,
        )
        self.assertEqual(p["codigo_pdv"], codigo)
        self.assertEqual(p["qtd_disp"], 15)
        self.assertEqual(p["disponivel"], 1)

        self.assertEqual(len(data_manager.listar_produtos(busca=codigo)), 1)

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
            disponivel=False,
        )
        atualizado = data_manager.listar_produtos(busca=codigo)[0]
        self.assertEqual(atualizado["nome"], "Picanha Especial Atualizada")
        self.assertEqual(atualizado["qtd_disp"], 8)
        self.assertEqual(atualizado["disponivel"], 0)

        data_manager.excluir_produto(p["id"])
        self.assertEqual(len(data_manager.listar_produtos(busca=codigo)), 0)


# ===========================================================================
class Test03SalaoMesasEQRCode(unittest.TestCase):
    """Módulo 3: Ciclo de mesas, lançamento, QR Codes e baixa de estoque."""

    def test_ciclo_operacional_mesa_e_qrcode(self):
        num_mesa = 876
        codigo = f"ESTQ_{num_mesa}"
        _purge_mesa(num_mesa)
        _purge_produto(codigo)
        # LIFO: a mesa é limpa antes do produto
        self.addCleanup(_purge_produto, codigo)
        self.addCleanup(_purge_mesa, num_mesa)

        abertura = data_manager.abrir_mesa(num_mesa, qtd_pessoas=2)
        comanda_id = abertura["comanda_id"]
        self.assertIsNotNone(comanda_id)

        p = data_manager.criar_produto(
            codigo_pdv=codigo,
            nome="Cerveja Artesanal Teste",
            categoria="Bebidas",
            preco_unitario=15.0,
            qtd_disp=5,
            disponivel=1,
        )

        data_manager.adicionar_item_comanda(comanda_id, p["id"], quantidade=2, observacao="Bem gelada")
        data_manager.adicionar_item_comanda(comanda_id, p["id"], quantidade=1)
        detalhes = data_manager.obter_comanda_detalhes(comanda_id)
        self.assertEqual(len(detalhes["itens"]), 1)
        self.assertEqual(detalhes["itens"][0]["quantidade"], 3)

        total = detalhes["total"]
        data_manager.fechar_comanda(comanda_id, valor_final=round(total * 1.10, 2), taxa_servico=True)

        mesas_ativas = [m["numero_mesa"] for m in data_manager.listar_mesas()]
        self.assertNotIn(num_mesa, mesas_ativas, "A mesa deveria estar liberada após o pagamento.")

        with data_manager.get_connection() as c:
            status = c.execute("SELECT status FROM comandas WHERE id = ?", (comanda_id,)).fetchone()["status"]
        self.assertEqual(status, "PAGA")

        # Baixa de estoque: 5 - 3 = 2 (ajuste se a regra for diferente p/ precisa_produzir)
        estoque = data_manager.listar_produtos(busca=codigo)[0]["qtd_disp"]
        self.assertEqual(estoque, 2, "Estoque deveria ter baixado em 3 unidades.")

    def test_qrcodes_mesas_persistencia(self):
        mesas_qr = data_manager.listar_mesas_qrcodes()
        self.assertGreaterEqual(len(mesas_qr), 10)
        tok_antigo = mesas_qr[0]["token_qrcode"]
        tok_novo = data_manager.atualizar_qrcode_mesa(mesas_qr[0]["numero_mesa"])
        self.assertNotEqual(tok_antigo, tok_novo)

    def test_sincronizacao_abertura_comanda_xano(self):
        """abrir_mesa deve disparar o push da comanda pai para /comandas no Xano."""
        _purge_mesa(998)
        self.addCleanup(_purge_mesa, 998)

        with patch.object(data_manager, "_sync_push_imediato_ou_enfileirar") as mock_sync:
            res = data_manager.abrir_mesa(998, qtd_pessoas=3)
            cid = res["comanda_id"]

            chamadas = [c for c in mock_sync.call_args_list
                        if c[0][0] == "POST" and c[0][1] == "/comandas"]
            self.assertGreaterEqual(len(chamadas), 1)
            payload = chamadas[0][0][2]
            self.assertEqual(payload["id"], cid)
            self.assertEqual(payload["numero_mesa"], 998)
            self.assertEqual(payload["qtd_pessoas"], 3)


# ===========================================================================
class Test04SegurancaEPerformance(unittest.TestCase):
    """Módulo 4: Restrições de domínio, sanitização XSS e cardinalidade única."""

    def test_restricoes_preco_e_xss(self):
        with self.assertRaises(ValueError):
            data_manager.criar_produto("ERR_NEG", "Item Negativo", "Comida", preco_unitario=-5.0)
        with self.assertRaises(ValueError):
            data_manager.criar_produto("ERR_ZERO", "Item Zero", "Comida", preco_unitario=0.0)

        codigo = _codigo_unico("ERR_XSS")
        self.addCleanup(_purge_produto, codigo)
        p_xss = data_manager.criar_produto(codigo, "<script>alert(1)</script>", "<b>Carnes</b>", preco_unitario=20.0)
        self.assertNotIn("<script>", p_xss["nome"])
        self.assertNotIn("<b>", p_xss["categoria"])

    def test_cardinalidade_unica_comanda_aberta(self):
        mesa_teste = 765
        _purge_mesa(mesa_teste)
        self.addCleanup(_purge_mesa, mesa_teste)

        data_manager.abrir_mesa(mesa_teste, qtd_pessoas=2)
        with self.assertRaises(ValueError):
            data_manager.abrir_mesa(mesa_teste, qtd_pessoas=2)


# ===========================================================================
class Test05AutenticacaoERBAC(unittest.TestCase):
    """Módulo 5: Hashing, login, troca de senha e cargos."""

    def test_autenticacao_e_rbac_fluxo_completo(self):
        email_gerente = "gerente_suite_test@churrascontrol.com"
        email_caixa = "caixa_suite_test@churrascontrol.com"
        for e in (email_gerente, email_caixa):
            _remover_colab(e)
            self.addCleanup(_remover_colab, e)

        gerente = data_manager.cadastrar_colaborador(
            nome="Gerente Teste Suíte", email=email_gerente,
            senha="SenhaForteGerente123", numero="(31) 99999-1111", cargo="gerente")
        self.assertEqual(gerente["cargo"], "gerente")

        auth_ok = data_manager.autenticar_usuario(email_gerente, "SenhaForteGerente123")
        self.assertIsNotNone(auth_ok)
        self.assertEqual(auth_ok["email"], email_gerente)
        self.assertEqual(auth_ok["cargo"], "gerente")

        self.assertIsNone(data_manager.autenticar_usuario(email_gerente, "senha_incorreta"))

        caixa = data_manager.cadastrar_colaborador(
            nome="Operador Caixa Suíte", email=email_caixa,
            senha="temp123Caixa", numero="(31) 98888-7777", cargo="caixa")
        self.assertEqual(caixa["cargo"], "caixa")
        self.assertTrue(caixa["primeiro_acesso"])

        self.assertTrue(data_manager.atualizar_senha_colaborador(caixa["id"], "novaSenhaCaixa456"))
        self.assertIsNotNone(data_manager.autenticar_usuario(email_caixa, "novaSenhaCaixa456"))


# ===========================================================================
class Test06HistoricoDeVendasEImutabilidade(unittest.TestCase):
    """Módulo 6: Itens de comandas pagas sobrevivem ao restart."""

    def test_itens_pagos_sobrevivem_restart(self):
        mesa_paga = 654
        codigo = f"PROD_HIST_{mesa_paga}"
        _purge_mesa(mesa_paga)
        _purge_produto(codigo)
        self.addCleanup(_purge_produto, codigo)
        self.addCleanup(_purge_mesa, mesa_paga)

        p = data_manager.criar_produto(
            codigo_pdv=codigo, nome="Corte Angus Imutável", categoria="Carnes",
            preco_unitario=75.0, qtd_disp=20, disponivel=1)

        res = data_manager.abrir_mesa(mesa_paga, qtd_pessoas=2)
        cid = res["comanda_id"]
        data_manager.adicionar_item_comanda(cid, p["id"], quantidade=3)
        data_manager.fechar_comanda(cid, valor_final=225.0, taxa_servico=False)

        # Simula restart reexecutando init_db
        data_manager._db_initialized = False
        data_manager.init_db()

        fk = _fk_itens()
        with data_manager.get_connection() as c:
            qtd = c.execute(f"SELECT COUNT(*) FROM itens_comanda WHERE {fk} = ?", (cid,)).fetchone()[0]
        self.assertEqual(qtd, 1, "Itens de comanda PAGA não podem ser apagados pelo init_db()!")

        dash = data_manager.obter_dashboard_dados("1d")
        self.assertGreaterEqual(dash["resumo"]["faturamento_total"], 225.0)


# ===========================================================================
class Test07OntologiaERAG(unittest.TestCase):
    """Módulo 7: Ontologia, ferramentas analíticas read-only e chat."""

    def setUp(self):
        ontologia.seed_ontologia()
        _reset_estado_ia()
        self.addCleanup(_reset_estado_ia)

    def test_resolucao_sinonimos(self):
        self.assertEqual(ontologia.resolver_termo("breja")["id"], "cerveja")
        self.assertEqual(ontologia.resolver_termo("carne")["id"], "carnes")
        self.assertEqual(ontologia.resolver_termo("suco")["id"], "bebidas")
        self.assertIsNone(ontologia.resolver_termo("refri"))

    def test_mapeamento_mesas_por_setor(self):
        self.assertEqual(ontologia.obter_mesas_por_setor("varanda"), [1, 2, 3, 4])
        self.assertEqual(ontologia.obter_mesas_por_setor("salao_principal"), [5, 6, 7, 8])
        self.assertEqual(ontologia.obter_mesas_por_setor("kids"), [9, 10])
        self.assertEqual(ontologia.obter_mesas_por_setor("vip"), [])

    def test_mapeamento_turnos(self):
        almoco = ontologia.obter_intervalo_turno("almoco")
        self.assertEqual((almoco["inicio"], almoco["fim"]), ("11:30:00", "15:30:00"))

        jantar = ontologia.obter_intervalo_turno("jantar")
        self.assertEqual((jantar["inicio"], jantar["fim"]), ("18:30:00", "23:59:59"))

        # happy hour: aceita variações de grafia, sem sobreposição com o jantar
        for chave in ("happy hour", "happy_hour"):
            with self.subTest(chave=chave):
                hh = ontologia.obter_intervalo_turno(chave)
                self.assertIsNotNone(hh)
                self.assertEqual((hh["inicio"], hh["fim"]), ("17:00:00", "18:29:59"))

        self.assertIsNone(ontologia.obter_intervalo_turno("madrugada"))

    def test_expansao_conceitos_subclasses(self):
        subclasses = ontologia.obter_subclasses("carnes")
        for esperado in ("picanha", "ancho", "costela", "vaca_atolada"):
            self.assertIn(esperado, subclasses)

        with data_manager.get_connection() as conn:
            for removido in ("carnes_nobres", "vip"):
                r = conn.execute("SELECT id FROM ontologia_conceitos WHERE id = ?", (removido,)).fetchone()
                self.assertIsNone(r, f"Conceito '{removido}' não deveria existir na ontologia")

    def test_ferramentas_analiticas_read_only(self):
        res_fin = assistente_ia.resumo_financeiro()
        for k in ("faturamento_bruto_reais", "total_comandas_pagas", "ticket_medio_comanda"):
            self.assertIn(k, res_fin)

        res_mesas = assistente_ia.ranking_mesas(limite=5)
        self.assertIn("ranking_mesas", res_mesas)
        self.assertIn("total_mesas_ranqueadas", res_mesas)

        self.assertIn("ranking_produtos", assistente_ia.ranking_produtos(limite=5))

        res_cat = assistente_ia.vendas_por_categoria()
        self.assertIn("vendas_categorias", res_cat)
        self.assertIn("receita_geral_reais", res_cat)

        self.assertIn("serie_temporal", assistente_ia.evolucao_temporal(granularidade="dia"))

        res_est = assistente_ia.estoque_critico()
        self.assertIn("produtos_criticos", res_est)
        self.assertIn("total_criticos", res_est)

        res_sal = assistente_ia.salao_tempo_real()
        self.assertIn("total_mesas", res_sal)
        self.assertIn("mesas_ocupadas", res_sal)

        res_aud = assistente_ia.auditoria_operacional(limite=5)
        self.assertIn("registros_auditoria", res_aud)
        self.assertIn("total_encontrado", res_aud)

    def test_conexao_readonly_bloqueia_escrita(self):
        with assistente_ia.get_readonly_connection() as ro_conn:
            cur = ro_conn.cursor()
            cur.execute("SELECT COUNT(*) FROM produtos")
            self.assertGreaterEqual(cur.fetchone()[0], 0)
            with self.assertRaises(sqlite3.OperationalError):
                cur.execute("INSERT INTO produtos (codigo_pdv, nome, categoria, preco_unitario) "
                            "VALUES ('TEST_RO', 'Bloqueado', 'Carnes', 10)")
            with self.assertRaises(sqlite3.OperationalError):
                cur.execute("UPDATE produtos SET disponivel = 1 WHERE id = 1")

    def test_chat_persistencia_e_historico(self):
        usuario = "gerente_teste_rag"
        cid = assistente_ia.criar_conversa(usuario, "Conversa de Teste RAG")
        self.assertTrue(bool(cid))
        self.addCleanup(assistente_ia.excluir_conversa, cid)

        assistente_ia.salvar_mensagem_chat(cid, "user", "Qual o faturamento?")
        assistente_ia.salvar_mensagem_chat(
            cid, "assistant", "O faturamento foi R$ 1.000,00.",
            api_origem="Chave 1", modelo_utilizado="gemini-2.5-flash", tentativas_falhas=0)

        mensagens = assistente_ia.carregar_historico_chat(cid)
        self.assertEqual(len(mensagens), 2)
        self.assertEqual(mensagens[0]["papel"], "user")
        self.assertEqual(mensagens[1]["papel"], "assistant")
        self.assertEqual(mensagens[1]["api_origem"], "Chave 1")
        self.assertEqual(mensagens[1]["modelo_utilizado"], "gemini-2.5-flash")

        self.assertTrue(any(c["id"] == cid for c in assistente_ia.listar_conversas(usuario)))

    def test_ontologia_meia_noite_e_setores(self):
        with data_manager.get_connection() as conn:
            r = conn.execute("SELECT id FROM ontologia_conceitos WHERE id = 'regra_turno_meia_noite'").fetchone()
            self.assertIsNotNone(r, "Axioma 'regra_turno_meia_noite' deve existir na ontologia")

        self.assertEqual(ontologia.obter_mesas_por_setor("deck"), [1, 2, 3, 4])
        self.assertEqual(ontologia.obter_mesas_por_setor("salao principal"), [5, 6, 7, 8])
        self.assertEqual(ontologia.obter_mesas_por_setor("area kids"), [9, 10])

        self.assertEqual(ontologia.obter_setor_da_mesa(1), "Varanda")
        self.assertEqual(ontologia.obter_setor_da_mesa(5), "Salão Interno")
        self.assertEqual(ontologia.obter_setor_da_mesa(9), "Kids")
        self.assertEqual(ontologia.obter_setor_da_mesa(999), "Sem setor")

    def test_perguntas_ambiguas_premissa_declarada(self):
        res_fin = assistente_ia.resumo_financeiro()
        self.assertIsNotNone(res_fin.get("premissa_adotada"))
        self.assertIn("Hoje", res_fin["premissa_adotada"])
        self.assertIsNotNone(assistente_ia.ranking_produtos().get("premissa_adotada"))

    def test_resposta_sem_dados(self):
        res_fin = assistente_ia.resumo_financeiro(inicio="1990-01-01", fim="1990-01-02")
        self.assertTrue(res_fin["sem_dados"])
        self.assertEqual(res_fin["total_comandas_pagas"], 0)
        self.assertEqual(res_fin["faturamento_bruto_reais"], 0.0)

        res_prod = assistente_ia.ranking_produtos(inicio="1990-01-01", fim="1990-01-02")
        self.assertTrue(res_prod["sem_dados"])
        self.assertEqual(res_prod["total_itens_ranqueados"], 0)

    def test_isolamento_vendas_demo_flag(self):
        # Data antiga e exclusiva: não conflita com dados da cópia de produção
        data = "2001-02-03"
        _purge_mesa(999)
        self.addCleanup(_purge_mesa, 999)
        self.addCleanup(assistente_ia._set_ignorar_demo, True)

        with data_manager.get_connection() as conn:
            conn.execute(
                "INSERT INTO comandas (numero_mesa_historico, data_abertura, status, valor_total, is_demo) "
                "VALUES (999, ?, 'PAGA', 100.0, 0)", (f"{data} 12:00",))
            conn.execute(
                "INSERT INTO comandas (numero_mesa_historico, data_abertura, status, valor_total, is_demo) "
                "VALUES (999, ?, 'PAGA', 500.0, 1)", (f"{data} 12:30",))
            conn.commit()

        assistente_ia._set_ignorar_demo(True)
        res_real = assistente_ia.resumo_financeiro(inicio=data, fim=data)
        assistente_ia._set_ignorar_demo(False)
        res_tudo = assistente_ia.resumo_financeiro(inicio=data, fim=data)

        self.assertAlmostEqual(res_real["faturamento_bruto_reais"], 100.0, places=2)
        self.assertAlmostEqual(res_tudo["faturamento_bruto_reais"], 600.0, places=2)

    def test_gerenciamento_conversas_renomear_excluir_titulo_auto(self):
        u_id = "gerente_crud_conv"
        cid = assistente_ia.criar_conversa(u_id, "Titulo Antigo")
        self.assertTrue(bool(cid))
        self.addCleanup(assistente_ia.excluir_conversa, cid)

        self.assertTrue(assistente_ia.renomear_conversa(cid, "Novo Titulo Executivo"))
        atual = next(c for c in assistente_ia.listar_conversas(u_id) if c["id"] == cid)
        self.assertEqual(atual["titulo"], "Novo Titulo Executivo")

        tit_auto = assistente_ia.gerar_titulo_automatico("Quanto faturamos hoje no almoco?")
        self.assertLessEqual(len(tit_auto), 35)
        self.assertNotIn("quanto faturamos", tit_auto.lower())

        self.assertTrue(assistente_ia.excluir_conversa(cid))
        self.assertFalse(any(c["id"] == cid for c in assistente_ia.listar_conversas(u_id)))

    def test_ferramentas_turno_e_setor_combinados(self):
        res_fin = assistente_ia.resumo_financeiro(turno="almoco", setor="varanda")
        self.assertNotIn("erro", res_fin)
        self.assertIn("faturamento_bruto_reais", res_fin)
        self.assertEqual(res_fin.get("setor_aplicado"), "Varanda")
        self.assertEqual(res_fin.get("turno_aplicado"), "almoco")

        res_mesas = assistente_ia.ranking_mesas(turno="jantar", setor="salao interno")
        self.assertNotIn("erro", res_mesas)
        self.assertIn("ranking_mesas", res_mesas)

        res_prod = assistente_ia.ranking_produtos(turno="happy_hour", setor="deck")
        self.assertNotIn("erro", res_prod)
        self.assertIn("ranking_produtos", res_prod)

        res_cat = assistente_ia.vendas_por_categoria(turno="almoco", setor="kids")
        self.assertNotIn("erro", res_cat)
        self.assertIn("vendas_categorias", res_cat)

        res_evo = assistente_ia.evolucao_temporal(turno="jantar", setor="varanda")
        self.assertNotIn("erro", res_evo)
        self.assertIn("serie_temporal", res_evo)

    def test_ferramentas_turno_ou_setor_invalido_gera_erro(self):
        res_t = assistente_ia.resumo_financeiro(turno="madrugada_falsa")
        self.assertIn("Turno 'madrugada_falsa' nao reconhecido", res_t["erro"])

        res_s = assistente_ia.ranking_mesas(setor="telhado_fantasma")
        self.assertIn("Setor 'telhado_fantasma' nao reconhecido", res_s["erro"])

    def test_verificacao_dono_conversa(self):
        cid = assistente_ia.criar_conversa("dono_original", "Conversa Original")
        self.addCleanup(assistente_ia.excluir_conversa, cid)

        self.assertFalse(assistente_ia.renomear_conversa(cid, "Tentativa Invasao", usuario_id="outro_usuario"))
        self.assertTrue(assistente_ia.renomear_conversa(cid, "Nome Autorizado", usuario_id="dono_original"))
        self.assertFalse(assistente_ia.excluir_conversa(cid, usuario_id="outro_usuario"))
        self.assertTrue(assistente_ia.excluir_conversa(cid, usuario_id="dono_original"))

    def test_valores_faturamento_e_receita_itens_e_soma_categorias(self):
        data = "2001-02-04"
        fk = _fk_itens()
        _purge_mesa(888)
        self.addCleanup(_purge_mesa, 888)
        self.addCleanup(assistente_ia._set_ignorar_demo, True)

        with data_manager.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO comandas (numero_mesa_historico, data_abertura, status, valor_total, is_demo) "
                "VALUES (888, ?, 'PAGA', 110.0, 0)", (f"{data} 13:00",))
            comanda_id = cur.lastrowid
            cur.execute(
                f"INSERT INTO itens_comanda ({fk}, nome_produto_historico, quantidade, preco_momento) "
                "VALUES (?, 'Picanha Teste', 1, 100.0)", (comanda_id,))
            conn.commit()

        assistente_ia._set_ignorar_demo(True)
        res_fin = assistente_ia.resumo_financeiro(inicio=data, fim=data)
        self.assertAlmostEqual(res_fin["faturamento_comandas_valor_total"], 110.0, places=2)
        self.assertAlmostEqual(res_fin["receita_total_itens"], 100.0, places=2)

        res_cat = assistente_ia.vendas_por_categoria(inicio=data, fim=data)
        soma_cat = sum(c["receita_total"] for c in res_cat["vendas_categorias"])
        self.assertAlmostEqual(soma_cat, res_cat["receita_itens_total_reais"], places=2)

    def test_axioma_meia_noite_contabil(self):
        """Comanda aberta na madrugada (00:00-05:59) deve contar no Jantar do dia contabil anterior."""
        _purge_mesa(887)
        self.addCleanup(_purge_mesa, 887)
        self.addCleanup(assistente_ia._set_ignorar_demo, True)

        with data_manager.get_connection() as conn:
            conn.execute(
                "INSERT INTO comandas (numero_mesa_historico, data_abertura, status, valor_total, is_demo) "
                "VALUES (887, '2001-02-06 01:30:00', 'PAGA', 150.0, 0)"
            )
            conn.commit()

        assistente_ia._set_ignorar_demo(True)
        res_dia_ant = assistente_ia.resumo_financeiro(inicio="2001-02-05", fim="2001-02-05", turno="jantar")
        self.assertAlmostEqual(res_dia_ant["faturamento_comandas_valor_total"], 150.0, places=2)

        res_dia_cal = assistente_ia.resumo_financeiro(inicio="2001-02-06", fim="2001-02-06", turno="jantar")
        self.assertAlmostEqual(res_dia_cal["faturamento_comandas_valor_total"], 0.0, places=2)


# ===========================================================================
class Test08CascataFallbackELLM(unittest.TestCase):
    """Módulo 8: Cascata de fallback LLM multichave, descoberta e segurança."""

    def setUp(self):
        _reset_estado_ia()
        self.addCleanup(_reset_estado_ia)

    # -- descoberta ---------------------------------------------------------
    def test_descoberta_modelos_filtragem(self):
        modelos_fake = [
            _fake_modelo("gemini-2.5-flash"),
            _fake_modelo("text-embedding-004", ("embedContent",)),
            _fake_modelo("gemini-2.5-pro"),
            _fake_modelo("imagen-3.0"),
        ]
        with patch("google.genai.Client") as cls:
            cls.return_value.models.list.return_value = modelos_fake
            modelos = assistente_ia.descobrir_modelos_chave("fake_key_123", "Chave 1")
        self.assertIn("gemini-2.5-flash", modelos)
        self.assertIn("gemini-2.5-pro", modelos)
        self.assertNotIn("text-embedding-004", modelos)
        self.assertNotIn("imagen-3.0", modelos)

    def test_ordem_configuravel_modelos(self):
        pref = "gemini-2.0-flash, gemini-2.5-pro, gemini-2.5-flash"
        with patch.dict(os.environ, {"GEMINI_MODELS_PREFERENCE": pref}):
            assistente_ia._discovered_models_cache.clear()
            with patch("google.genai.Client") as cls:
                cls.return_value.models.list.return_value = [
                    _fake_modelo("gemini-2.5-flash"),
                    _fake_modelo("gemini-2.5-pro"),
                    _fake_modelo("gemini-2.0-flash"),
                ]
                modelos = assistente_ia.descobrir_modelos_chave("fake_key_pref", "Chave 1")
        self.assertEqual(modelos, ["gemini-2.0-flash", "gemini-2.5-pro", "gemini-2.5-flash"])

    # -- cascata ------------------------------------------------------------
    def test_fallback_chave1_para_chave2_e_cooldown(self):
        def factory(api_key=None):
            c = MagicMock()
            c.models.list.return_value = [_fake_modelo("gemini-2.5-flash")]
            if api_key == "sim_key_1":
                c.models.generate_content.side_effect = Exception("429 Resource Exhausted: Quota exceeded for model")
            else:
                c.models.generate_content.return_value = _fake_resposta(
                    "Relatório executivo gerado com sucesso via Chave 2.")
            return c

        with _env_chaves("sim_key_1", "sim_key_2"), patch("google.genai.Client", side_effect=factory):
            res = assistente_ia.executar_pergunta_gerente("Qual o prato mais vendido?")

        self.assertTrue(res["sucesso"])
        self.assertEqual(res["api_origem"], "Chave 2")
        self.assertEqual(res["modelo"], "gemini-2.5-flash")
        self.assertGreaterEqual(res["tentativas_falhas"], 1)
        self.assertIn("Relatório executivo", res["resposta"])
        self.assertTrue(assistente_ia.is_em_cooldown("Chave 1", "gemini-2.5-flash"))

    def test_esgotamento_total_cascata_fail_safe_sem_alucinacao(self):
        def factory(api_key=None):
            c = MagicMock()
            c.models.list.return_value = [_fake_modelo("gemini-2.5-flash")]
            c.models.generate_content.side_effect = Exception("503 Service Unavailable")
            return c

        with _env_chaves("sim_key_1", "sim_key_2"), patch("google.genai.Client", side_effect=factory):
            res = assistente_ia.executar_pergunta_gerente("Qual o faturamento de ontem?")

        self.assertFalse(res["sucesso"])
        resposta = res["resposta"].lower()
        self.assertTrue("temporariamente" in resposta or "indispon" in resposta,
                        f"Mensagem fail-safe inesperada: {res['resposta']}")
        self.assertGreaterEqual(res["tentativas_falhas"], 2)

    def test_classificacao_erros_chave_invalida_pula_chave(self):
        chamadas = {"invalid_key_k1": 0, "valid_key_k2": 0}

        def factory(api_key=None):
            c = MagicMock()
            c.models.list.return_value = [_fake_modelo("gemini-2.5-flash"), _fake_modelo("gemini-2.5-pro")]

            def gen(*args, **kwargs):
                chamadas[api_key] += 1
                if api_key == "invalid_key_k1":
                    raise Exception("401 API_KEY_INVALID: API key not valid. Please pass a valid API key.")
                return _fake_resposta("Relatório executivo gerado com sucesso via Chave 2.")

            c.models.generate_content.side_effect = gen
            return c

        with _env_chaves("invalid_key_k1", "valid_key_k2"), patch("google.genai.Client", side_effect=factory):
            res = assistente_ia.executar_pergunta_gerente("Qual o prato mais vendido?")

        self.assertTrue(res["sucesso"])
        self.assertEqual(res["api_origem"], "Chave 2")
        # Chave inválida: tenta 1 modelo e pula a chave inteira
        self.assertEqual(chamadas["invalid_key_k1"], 1)
        self.assertTrue(assistente_ia.is_chave_desativada("Chave 1"))

    def test_classificacao_erros_requisicao_malformada_interrompe(self):
        total = [0]

        def factory(api_key=None):
            c = MagicMock()
            c.models.list.return_value = [_fake_modelo("gemini-2.5-flash")]

            def gen(*args, **kwargs):
                total[0] += 1
                raise Exception("400 INVALID_ARGUMENT: Schema structure is malformed or invalid")

            c.models.generate_content.side_effect = gen
            return c

        with _env_chaves("sim_key_1", "sim_key_2"), patch("google.genai.Client", side_effect=factory):
            res = assistente_ia.executar_pergunta_gerente("Pergunta de teste malformada")

        self.assertFalse(res["sucesso"])
        self.assertEqual(total[0], 2, "Deve confirmar a malformação em 2 tentativas e interromper")
        self.assertIn("invalida ou nao suportada", res["resposta"])

    def test_modelo_incompativel_ferramentas_eh_pulado_e_cascata_continua(self):
        chamados = []
        pref = "gemini-incompativel, gemini-2.5-flash"

        def factory(api_key=None):
            c = MagicMock()
            c.models.list.return_value = [_fake_modelo("gemini-incompativel"), _fake_modelo("gemini-2.5-flash")]

            def gen(model=None, *args, **kwargs):
                chamados.append(model)
                if model == "gemini-incompativel":
                    raise Exception("400 INVALID_ARGUMENT: Tool use is not supported for this model")
                return _fake_resposta("Resposta bem-sucedida do segundo modelo")

            c.models.generate_content.side_effect = gen
            return c

        with _env_chaves("sim_key_1"), \
             patch.dict(os.environ, {"GEMINI_MODELS_PREFERENCE": pref}), \
             patch("google.genai.Client", side_effect=factory):
            assistente_ia._discovered_models_cache.clear()
            res = assistente_ia.executar_pergunta_gerente("Qual o prato mais vendido?")

        self.assertTrue(res["sucesso"])
        self.assertEqual(res["modelo"], "gemini-2.5-flash")
        self.assertIn("gemini-incompativel", assistente_ia._incompatible_models)
        self.assertEqual(chamados, ["gemini-incompativel", "gemini-2.5-flash"])

    def test_resposta_vazia_modelo_continua_cascata(self):
        chamados = []
        # Define preferencia explícita para garantir ordem: gemini-vazio primeiro
        pref = "gemini-vazio, gemini-2.5-flash"

        def factory(api_key=None):
            c = MagicMock()
            c.models.list.return_value = [_fake_modelo("gemini-vazio"), _fake_modelo("gemini-2.5-flash")]

            def gen(model=None, *args, **kwargs):
                chamados.append(model)
                if model == "gemini-vazio":
                    return _fake_resposta("")
                return _fake_resposta("Resposta do modelo que sucedeu o modelo vazio")

            c.models.generate_content.side_effect = gen
            return c

        with _env_chaves("sim_key_1"), \
             patch.dict(os.environ, {"GEMINI_MODELS_PREFERENCE": pref}), \
             patch("google.genai.Client", side_effect=factory):
            assistente_ia._discovered_models_cache.clear()
            res = assistente_ia.executar_pergunta_gerente("Qual o prato mais vendido?")

        self.assertTrue(res["sucesso"])
        self.assertEqual(res["modelo"], "gemini-2.5-flash")
        self.assertEqual(chamados, ["gemini-vazio", "gemini-2.5-flash"])

    def test_status_servico_reflete_cooldown_e_esgotamento(self):
        assistente_ia._key_cooldowns["Chave 1"] = 9999999999.0
        assistente_ia._key_cooldowns["Chave 2"] = 9999999999.0
        st = assistente_ia.obter_status_servico()
        self.assertEqual(st["status"], "indisponivel")
        self.assertIn("Indisponivel", st["rotulo"])

    # -- classificação de erros --------------------------------------------
    def test_classificacao_erro_429_com_numero_400(self):
        err = Exception("ResourceExhausted: 429 Quota limit of 1400 tokens per minute exceeded. Please retry in 15s.")
        tipo, cd, motivo = assistente_ia.classificar_erro(err)
        self.assertEqual(tipo, assistente_ia.TIPO_ERRO_TRANSIENT)
        self.assertEqual(cd, 15)
        self.assertIn("429", motivo)

    def test_classificacao_erro_cota_diaria_perday(self):
        err = Exception("ResourceExhausted: 429 Daily request quota perDay exceeded")
        tipo, cd, _ = assistente_ia.classificar_erro(err)
        self.assertEqual(tipo, assistente_ia.TIPO_ERRO_TRANSIENT)
        self.assertEqual(cd, assistente_ia.DEFAULT_COOLDOWN_DAILY_QUOTA)

    def test_classificacao_erro_com_objeto_sdk_code(self):
        class MockSDKError(Exception):
            def __init__(self, code, status, message):
                super().__init__(message)
                self.code = code
                self.status = status

        tipo, _, _ = assistente_ia.classificar_erro(MockSDKError(401, "UNAUTHENTICATED", "Invalid API key provided"))
        self.assertEqual(tipo, assistente_ia.TIPO_ERRO_AUTH)

        tipo_rate, cd_rate, _ = assistente_ia.classificar_erro(MockSDKError(429, "RESOURCE_EXHAUSTED", "Rate limit reached"))
        self.assertEqual(tipo_rate, assistente_ia.TIPO_ERRO_TRANSIENT)
        self.assertEqual(cd_rate, assistente_ia.DEFAULT_COOLDOWN_TRANSIENT)

    # -- segurança ---------------------------------------------------------
    def test_sanitizacao_chaves_em_log_e_resposta(self):
        raw = ("Falha ao conectar com chave AIzaSyD1234567890abcdef-XYZ na URL "
               "https://generativelanguage.googleapis.com/v1beta?key=AIzaSySecretKey")
        s = assistente_ia.sanitizar_texto(raw)
        self.assertNotIn("AIzaSyD1234567890abcdef-XYZ", s)
        self.assertNotIn("AIzaSySecretKey", s)
        self.assertIn("[CHAVE_PROTEGIDA]", s)

    def test_seguranca_chaves_nao_gravadas_em_sqlite_ou_logs(self):
        """Gera uma falha real com chave vazando na exceção e inspeciona os logs."""
        vazada = "AIzaSyFAKE1234567890abcdefghijk"

        def factory(api_key=None):
            c = MagicMock()
            c.models.list.return_value = [_fake_modelo("gemini-2.5-flash")]
            c.models.generate_content.side_effect = Exception(f"503 Unavailable key={vazada}")
            return c

        with data_manager.get_connection() as conn:
            antes = conn.execute("SELECT COUNT(*) FROM llm_fallback_logs").fetchone()[0]

        with _env_chaves("sim_key_1"), patch("google.genai.Client", side_effect=factory):
            res = assistente_ia.executar_pergunta_gerente("Teste de vazamento de chave")

        self.assertNotIn(vazada, res["resposta"])

        with data_manager.get_connection() as conn:
            logs = conn.execute("SELECT api_origem, erro_motivo FROM llm_fallback_logs").fetchall()
        self.assertGreater(len(logs), antes, "A falha deveria ter gerado ao menos um log")

        for r in logs:
            origem = r["api_origem"]
            motivo = r["erro_motivo"] or ""
            for segredo in ("sim_key_1", "sim_key_2", vazada):
                self.assertNotIn(segredo, origem)
                self.assertNotIn(segredo, motivo)
            self.assertNotRegex(motivo, r"AIza[0-9A-Za-z_-]{10,}")
            self.assertIn(origem, ["Chave 1", "Chave 2", "Nenhuma", "Cascata Esgotada"])

    def test_zero_insercoes_fila_sincronizacao(self):
        """Nenhuma operação de IA pode enfileirar algo para o Xano."""
        with data_manager.get_connection() as conn:
            antes = conn.execute("SELECT COUNT(*) FROM fila_sincronizacao").fetchone()[0]

        assistente_ia.resumo_financeiro()
        assistente_ia.ranking_produtos(limite=3)
        cid = assistente_ia.criar_conversa("usuario_fila_test", "Conversa fila")
        assistente_ia.salvar_mensagem_chat(cid, "user", "Olá")
        assistente_ia.excluir_conversa(cid)
        ontologia.seed_ontologia()

        with data_manager.get_connection() as conn:
            depois = conn.execute("SELECT COUNT(*) FROM fila_sincronizacao").fetchone()[0]
        self.assertEqual(depois, antes, "Módulos de IA não podem inserir na fila de sincronização Xano!")


# ===========================================================================
class Test09BlindagemOtimizacaoEParidade(unittest.TestCase):
    """Módulo 9: PBKDF2, rate limit, token QR e regra Zero-Pandas."""

    def test_pbkdf2_e_migracao_transparente_legado(self):
        email = "migracao_pbkdf2_test@churrascontrol.com"
        _remover_colab(email)
        self.addCleanup(_remover_colab, email)

        colab = data_manager.cadastrar_colaborador(
            nome="Teste PBKDF2", email=email, senha="SenhaSegura2026",
            numero="(31) 97777-6666", cargo="caixa")

        def _hash_atual():
            with data_manager.get_connection() as conn:
                return conn.execute("SELECT senha_hash FROM colaboradores WHERE id = ?",
                                    (colab["id"],)).fetchone()["senha_hash"]

        def _checar_formato(h):
            partes = h.split("$")
            self.assertEqual(partes[0], "pbkdf2_sha256")
            self.assertGreaterEqual(int(partes[1]), MIN_PBKDF2_ITER)

        _checar_formato(_hash_atual())

        # Simula hash legado SHA-256 e verifica migração transparente no login
        with data_manager.get_connection() as conn:
            conn.execute("UPDATE colaboradores SET senha_hash = ? WHERE id = ?",
                         (data_manager._gerar_hash_senha_legado("SenhaSegura2026"), colab["id"]))
            conn.commit()

        self.assertIsNotNone(data_manager.autenticar_usuario(email, "SenhaSegura2026"))
        _checar_formato(_hash_atual())

    def test_rate_limiting_anti_brute_force(self):
        email = "brute_force_target@churrascontrol.com"
        data_manager._limpar_falhas_login(email)
        self.addCleanup(data_manager._limpar_falhas_login, email)

        for _ in range(5):
            self.assertIsNone(data_manager.autenticar_usuario(email, "errada"))
        self.assertTrue(data_manager._esta_bloqueado_rate_limit_login(email))

    def test_rate_limiting_expira_apos_janela(self):
        """Bloqueio deve expirar. Ajuste o patch se o relógio usado não for time.time()."""
        email = "brute_force_expira@churrascontrol.com"
        data_manager._limpar_falhas_login(email)
        self.addCleanup(data_manager._limpar_falhas_login, email)

        for _ in range(5):
            data_manager.autenticar_usuario(email, "errada")
        self.assertTrue(data_manager._esta_bloqueado_rate_limit_login(email))

        futuro = time.time() + 24 * 3600
        with patch("time.time", return_value=futuro):
            self.assertFalse(data_manager._esta_bloqueado_rate_limit_login(email))

    def test_validacao_token_qrcode(self):
        m1 = data_manager.listar_mesas_qrcodes()[0]
        self.assertTrue(data_manager.validar_acesso_cardapio_qr(m1["numero_mesa"], m1["token_qrcode"]))
        self.assertFalse(data_manager.validar_acesso_cardapio_qr(m1["numero_mesa"], "token-falso-invalido"))
        self.assertFalse(data_manager.validar_acesso_cardapio_qr(m1["numero_mesa"], ""))

    def test_auditoria_nao_importa_pandas(self):
        caminho = os.path.join(PROJECT_ROOT, "pages", "7_Auditoria.py")
        with open(caminho, "r", encoding="utf-8") as f:
            arvore = ast.parse(f.read())
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                for alias in no.names:
                    self.assertFalse(alias.name.split(".")[0] == "pandas", "7_Auditoria.py importa pandas")
            elif isinstance(no, ast.ImportFrom):
                self.assertFalse((no.module or "").split(".")[0] == "pandas", "7_Auditoria.py importa pandas")


# ===========================================================================
def run_full_suite():
    carregador = unittest.TestLoader()
    suite = carregador.loadTestsFromModule(sys.modules[__name__])
    resultado = unittest.TextTestRunner(verbosity=2).run(suite)
    return resultado.wasSuccessful()


if __name__ == "__main__":
    sucesso = False
    try:
        sucesso = run_full_suite()
    finally:
        if _OWN_TEMP_DIR and os.path.exists(_OWN_TEMP_DIR):
            shutil.rmtree(_OWN_TEMP_DIR, ignore_errors=True)
    sys.exit(0 if sucesso else 1)

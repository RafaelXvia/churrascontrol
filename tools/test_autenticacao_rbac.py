"""
Suíte de Testes Automatizados — Autenticação e RBAC (Controle de Acesso)
ChurrasControl Innovation Lab

Verifica:
1. Inicialização e integridade da tabela 'colaboradores'
2. Hashing de senha com salt seguro (SHA-256)
3. Autenticação com credenciais válidas e inválidas
4. Cadastro de novos colaboradores com perfis (caixa e gerente)
5. Bloqueio de e-mails duplicados e cargos inválidos
6. Fluxo de primeiro acesso e redefinição obrigatória de senha
7. Regra de proteção: proibido excluir o único gerente ativo
8. Exclusão e inativação de colaboradores comuns
"""
import sys
import os
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import data_manager

class TestAutenticacaoRBAC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Assegura que o banco está inicializado
        data_manager.init_db()

    @classmethod
    def tearDownClass(cls):
        # Limpa colaboradores de teste criados pela suíte para deixar o banco limpo
        colabs = data_manager.listar_colaboradores()
        for c in colabs:
            if c["email"] != "gerente@churrascontrol.com":
                try:
                    data_manager.excluir_colaborador(c["id"])
                except Exception:
                    pass

    def test_01_gerente_padrao_existe_e_autentica(self):
        """Verifica se o gerente padrão do seed autentica com sucesso"""
        colab = data_manager.autenticar_usuario("gerente@churrascontrol.com", "admin123")
        self.assertIsNotNone(colab, "Gerente padrão do seed deveria autenticar com sucesso")
        self.assertEqual(colab["email"], "gerente@churrascontrol.com")
        self.assertEqual(colab["cargo"], "gerente")

    def test_02_credenciais_invalidas_sao_rejeitadas(self):
        """Verifica se senhas ou e-mails incorretos retornam None"""
        # Senha incorreta
        colab = data_manager.autenticar_usuario("gerente@churrascontrol.com", "senha_errada_xyz")
        self.assertIsNone(colab, "Senha errada deve retornar None")

        # Usuário inexistente
        colab_inexistente = data_manager.autenticar_usuario("fantasma@churrascontrol.com", "admin123")
        self.assertIsNone(colab_inexistente, "Usuário inexistente deve retornar None")

    def test_03_cadastro_novo_colaborador_caixa(self):
        """Testa o cadastro de um novo colaborador com perfil caixa"""
        email_teste = "caixa_teste_automated@churrascontrol.com"
        # Limpa caso tenha sobrado de teste anterior
        colabs = data_manager.listar_colaboradores()
        for c in colabs:
            if c["email"] == email_teste:
                data_manager.excluir_colaborador(c["id"])

        novo = data_manager.cadastrar_colaborador(
            nome="Operador Caixa Teste",
            email=email_teste,
            senha="tempCaixa123",
            numero="(11) 98765-4321",
            cargo="caixa"
        )
        self.assertIsNotNone(novo)
        self.assertIn("id", novo)

        # Autentica com a senha temporária
        colab = data_manager.autenticar_usuario(email_teste, "tempCaixa123")
        self.assertIsNotNone(colab)
        self.assertEqual(colab["cargo"], "caixa")
        self.assertTrue(colab["primeiro_acesso"], "Novo colaborador deve iniciar com primeiro_acesso=True")

    def test_04_bloqueio_duplicidade_e_cargos_invalidos(self):
        """Testa restrições de integridade: e-mail duplicado e cargo não reconhecido"""
        email_existente = "gerente@churrascontrol.com"
        with self.assertRaises(ValueError):
            data_manager.cadastrar_colaborador(
                nome="Impostor",
                email=email_existente,
                senha="abc12345",
                numero="(11) 99999-9999",
                cargo="caixa"
            )

        # Cargo inválido
        with self.assertRaises(ValueError):
            data_manager.cadastrar_colaborador(
                nome="Cargo Fantasma",
                email="invalido@churrascontrol.com",
                senha="abc12345",
                numero="(11) 99999-9999",
                cargo="superadmin"
            )

    def test_05_fluxo_troca_senha_primeiro_acesso(self):
        """Testa a transição de primeiro_acesso de True para False após troca de senha"""
        email_fluxo = "troca_senha_test@churrascontrol.com"
        colabs = data_manager.listar_colaboradores()
        for c in colabs:
            if c["email"] == email_fluxo:
                data_manager.excluir_colaborador(c["id"])

        novo = data_manager.cadastrar_colaborador(
            nome="Colaborador Teste Troca",
            email=email_fluxo,
            senha="senhaProvisoria123",
            numero="(11) 91111-2222",
            cargo="caixa"
        )
        colab_id = novo["id"]

        # Atualiza a senha
        nova_senha = "MinhaNovaSenhaDefinitiva2026!"
        trocou = data_manager.atualizar_senha_colaborador(colab_id, nova_senha)
        self.assertTrue(trocou)

        # Tenta logar com senha antiga (deve falhar)
        colab_antiga = data_manager.autenticar_usuario(email_fluxo, "senhaProvisoria123")
        self.assertIsNone(colab_antiga, "Senha antiga não pode mais autenticar")

        # Loga com nova senha (deve ter sucesso e primeiro_acesso=False)
        colab_atualizado = data_manager.autenticar_usuario(email_fluxo, nova_senha)
        self.assertIsNotNone(colab_atualizado)
        self.assertFalse(colab_atualizado["primeiro_acesso"], "primeiro_acesso deve ser False após redefinição")

        # Limpa o colaborador de teste
        data_manager.excluir_colaborador(colab_id)

    def test_06_protecao_exclusao_ultimo_gerente(self):
        """Garante que o sistema impeça a exclusão acidental do único gerente ativo"""
        colabs = data_manager.listar_colaboradores()
        gerentes = [c for c in colabs if c["cargo"] == "gerente" and c.get("ativo", True) is True]
        
        if len(gerentes) == 1:
            gerente_unico = gerentes[0]
            with self.assertRaises(ValueError) as ctx:
                data_manager.excluir_colaborador(gerente_unico["id"])
            self.assertIn("único gerente", str(ctx.exception).lower())

    def test_07_exclusao_colaborador_comum(self):
        """Verifica se a exclusão de um colaborador comum funciona normalmente"""
        email_del = "deletar_test@churrascontrol.com"
        colabs = data_manager.listar_colaboradores()
        for c in colabs:
            if c["email"] == email_del:
                data_manager.excluir_colaborador(c["id"])

        novo = data_manager.cadastrar_colaborador(
            nome="Usuário Descartável",
            email=email_del,
            senha="descarte123",
            numero="(11) 94444-5555",
            cargo="caixa"
        )
        cid = novo["id"]
        excluido = data_manager.excluir_colaborador(cid)
        self.assertTrue(excluido, "Exclusão de colaborador comum deve retornar True")

        # Tenta autenticar após exclusão
        colab = data_manager.autenticar_usuario(email_del, "descarte123")
        self.assertIsNone(colab, "Usuário excluído não pode mais autenticar")

    def test_08_verificacao_criptografia_fisica_sqlite(self):
        """Audita se os campos sensíveis no SQLite estão estritamente cifrados com ENC:"""
        email_audit = "audit_crypto@churrascontrol.com"
        colabs = data_manager.listar_colaboradores()
        for c in colabs:
            if c["email"] == email_audit:
                data_manager.excluir_colaborador(c["id"])

        data_manager.cadastrar_colaborador(
            nome="Funcionário Auditado",
            email=email_audit,
            senha="SegredoForte2026!",
            numero="(21) 98888-7777",
            cargo="caixa"
        )

        with data_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nome, numero, cargo, senha_hash FROM colaboradores WHERE email = ?", (email_audit,))
            raw_row = cursor.fetchone()
            self.assertIsNotNone(raw_row)

            # Verifica se os campos não contêm texto plano e possuem prefixo ENC:
            self.assertTrue(raw_row["nome"].startswith("ENC:"), "Nome no SQLite deve estar cifrado com prefixo ENC:")
            self.assertNotIn("Funcionário Auditado", raw_row["nome"])

            self.assertTrue(raw_row["numero"].startswith("ENC:"), "Telefone no SQLite deve estar cifrado com prefixo ENC:")
            self.assertNotIn("98888-7777", raw_row["numero"])

            self.assertTrue(raw_row["cargo"].startswith("ENC:"), "Cargo no SQLite deve estar cifrado com prefixo ENC:")
            self.assertNotEqual("caixa", raw_row["cargo"])

            # Senha deve ser hash SHA-256 de 64 caracteres hexadecimais
            self.assertEqual(len(raw_row["senha_hash"]), 64)
            self.assertNotIn("SegredoForte2026!", raw_row["senha_hash"])

        # Limpa usuário de auditoria
        for c in data_manager.listar_colaboradores():
            if c["email"] == email_audit:
                data_manager.excluir_colaborador(c["id"])

def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAutenticacaoRBAC)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    main()

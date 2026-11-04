# autenticacao-e-acesso Specification

## Purpose
Prover autenticação segura de colaboradores, controle de acesso baseado em perfis (RBAC - Gerente e Caixa), política de redefinição obrigatória de senha no primeiro acesso e governança administrativa de colaboradores no SQLite e Xano.

## Requirements

### Requirement: Autenticação Segura e Sessão
O sistema SHALL autenticar colaboradores através de email e senha, validando o hash criptográfico seguro (SHA-256 com salt) e mantendo a sessão do usuário em `st.session_state`.

#### Scenario: Credenciais válidas
- **WHEN** o colaborador informa email e senha corretos
- **THEN** o sistema SHALL autenticar com sucesso e carregar as permissões do cargo associado (`gerente` ou `caixa`).

#### Scenario: Credenciais inválidas
- **WHEN** o colaborador informa email ou senha incorretos
- **THEN** o sistema SHALL rejeitar a autenticação com mensagem de erro sem vazar informações sobre a existência do email.

---

### Requirement: Controle de Acesso Baseado em Perfis (RBAC)
O sistema SHALL restringir as funcionalidades e telas com base no cargo do colaborador:
- Cargo **`gerente`**: Acesso completo (Painel Geral, Salão & Mesas, Cardápio, Relatórios, QR Codes e Gerenciamento de Colaboradores).
- Cargo **`caixa`**: Acesso restrito exclusivamente ao **Painel Geral** e **Salão & Mesas**. Tentativas de acessar outras telas SHALL ser bloqueadas.

#### Scenario: Operador com perfil Caixa acessa a tela de Relatórios
- **WHEN** um usuário autenticado com cargo `caixa` tenta acessar `pages/3_Relatorios.py` ou `pages/2_Cardapio.py`
- **THEN** o sistema SHALL bloquear a visualização dos dados, exibir alerta de permissão negada e fornecer atalho de retorno ao Painel Geral.

---

### Requirement: Política Obrigatória de Primeiro Acesso
Colaboradores cadastrados pelo Gerente possuem a flag `primeiro_acesso = 1`. No primeiro login, o sistema SHALL exigir que o colaborador defina uma nova senha pessoal antes de permitir a utilização de qualquer tela do sistema.

#### Scenario: Colaborador logando pela primeira vez
- **WHEN** um colaborador com `primeiro_acesso = 1` realiza login com a senha temporária
- **THEN** o sistema SHALL exibir modal obrigatório para definição da nova senha pessoal, impedindo a navegação no sistema até que a nova senha seja cadastrada e confirmada.

#### Scenario: Atualização com sucesso da senha pessoal
- **WHEN** o colaborador define uma nova senha válida e confirma
- **THEN** o sistema SHALL atualizar a senha com novo hash, alterar `primeiro_acesso` para `0` e liberar o acesso às funcionalidades do cargo.

---

### Requirement: Cadastro e Gestão de Colaboradores pelo Gerente
O sistema SHALL disponibilizar ao Gerente interface e operações para cadastrar colaboradores (`nome`, `email`, `senha`, `numero`, `cargo`), listar colaboradores ativos e desativar ou excluir colaboradores.

#### Scenario: Cadastro de novo colaborador com email duplicado
- **WHEN** o gerente tenta cadastrar um colaborador com email já registrado
- **THEN** o sistema SHALL rejeitar a operação levantando `ValueError` de unicidade.

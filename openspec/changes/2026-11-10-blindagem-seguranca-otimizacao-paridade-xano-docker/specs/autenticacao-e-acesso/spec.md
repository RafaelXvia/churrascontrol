# Especificação Delta: Autenticação, RBAC, Criptografia e Paridade de Colaboradores

## Requisitos Modificados e Adicionados

### Requisito 1: Hash Criptográfico de Senha com PBKDF2-HMAC-SHA256 e Migração Transparente
O sistema DEVE derivar hashes de senha utilizando `PBKDF2-HMAC-SHA256` com no mínimo `100.000` iterações e salt derivado de `CHURRAS_SALT`.

#### Cenário: Autenticação com migração transparente de hash legado
- **DADO** um colaborador com hash legado SHA-256 armazenado em `colaboradores.senha_hash`
- **QUANDO** o colaborador realizar login com a senha correta
- **ENTÃO** o sistema DEVE validar a senha, atualizar automaticamente `senha_hash` para o formato `pbkdf2_sha256$100000$...` no SQLite e enfileirar a atualização para o Xano.

### Requisito 2: Externalização de Chaves Criptográficas e Remoção de Backdoors de Recuperação
Nenhuma chave mestre Fernet (`FERNET_MASTER_KEY`) ou código de recuperação administrativa (`ADMIN_RECOVERY_CODE`) DEVE ser hardcoded ou exibido na interface gráfica.

#### Cenário: Recuperação de senha sem exposição de segredo na UI
- **DADO** que um colaborador acessa a aba "Recuperar Senha" na tela de login
- **QUANDO** visualizar o formulário de recuperação
- **ENTÃO** nenhum código mestre estático (como `CHURRAS-REC-2026`) DEVE ser exibido na tela, exigindo código enviado via SMTP (se configurado) ou código de autorização administrativo lido exclusivamente de variável de ambiente.

### Requisito 3: Rate Limiting contra Força Bruta no Login
O sistema DEVE limitar tentativas falhas de autenticação por conta de e-mail.

#### Cenário: Bloqueio temporário após 5 tentativas inválidas
- **DADO** que um endereço de e-mail acumulou 5 tentativas de login com senha incorreta em menos de 5 minutos
- **QUANDO** uma 6ª tentativa for submetida dentro da janela de bloqueio
- **ENTÃO** o sistema DEVE rejeitar imediatamente a tentativa com aviso de bloqueio temporário sem processar verificação criptográfica.

### Requisito 4: Guarda RBAC Obrigatória em Gestão de Mesas e QR Codes (`pages/4_Mesas_QRCodes.py`)
A página `pages/4_Mesas_QRCodes.py` DEVE invocar `verificar_permissao_acesso(["gerente", "caixa"])` antes de renderizar qualquer controle administrativo.

#### Cenário: Garçom tenta acessar página de Gestão de Mesas e QR Codes
- **DADO** um colaborador autenticado com cargo `garcom`
- **QUANDO** acessar `pages/4_Mesas_QRCodes.py`
- **ENTÃO** o sistema DEVE bloquear a visualização e exibir alerta de acesso restrito.


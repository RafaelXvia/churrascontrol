# Proposta — Criptografia de Dados de Colaboradores e Saneamento do Xano

## 1. Contexto & Motivação
Em conformidade com as melhores práticas de segurança da informação (LGPD e privacidade de dados) e otimização de infraestrutura no-code:
1. **Proteção Criptográfica Total de Colaboradores**: Dados pessoais e sensíveis como `nome`, `numero` (telefone), `senha_hash` e `cargo` não devem ser armazenados em texto plano no banco de dados local (`churrascontrol.db`) nem nos servidores remotos do Xano. Caso ocorra uma violação ou dump do banco, um invasor não conseguirá extrair números de telefone, nomes de funcionários ou seus níveis de privilégio (Caixa vs Gerente).
2. **Saneamento e Faxina da Instância Xano**: A pasta de definições do Xano e a própria instância continham mais de 30 tabelas legadas de templates (como `cartaotoknzd`, `oe`, `op`, `faq`, `ttokenizacao`, `transacao`, etc.) que poluem a estrutura, consomem cotas de armazenamento desnecessárias e geram ruído operacional. É necessário realizar o backup integral de tudo o que existe, manter o SQLite totalmente íntegro e reconstruir o repositório `xano/` contendo somente o ecossistema essencial do ChurrasControl (`mesas`, `comandas`, `itens_comanda`, `produto`, `colaborador`).

## 2. Objetivos
- [x] Extrair backup completo das tabelas em uso no Xano e no SQLite para o diretório `backups/`.
- [ ] Implementar módulo criptográfico simétrico autenticado (Fernet AES-128-CBC + HMAC-SHA256) em `data_manager.py`.
- [ ] Criptografar `nome`, `numero`, `cargo` e proteger `senha_hash` nas operações de cadastro, listagem, autenticação e sincronização.
- [ ] Migrar e reencriptar dados existentes na tabela `colaboradores`.
- [ ] Limpar e reestruturar o diretório `crudfaculdade/xano/`, mantendo exclusivamente as 5 tabelas ativas e seus respectivos endpoints.
- [ ] Disponibilizar script de upload/restauração (`tools/restore_to_xano.py`) para popular a nova instância do Xano automaticamente com os dados do backup.
- [ ] Validar e cobrir todas as novas funcionalidades na suíte de testes automatizados com 100% de aprovação.

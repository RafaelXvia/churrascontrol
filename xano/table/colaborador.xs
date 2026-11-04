// Tabela de Colaboradores e Perfis RBAC (Caixa e Gerente) com Criptografia de Ponta a Ponta — ChurrasControl
table colaborador {
  auth = true

  schema {
    int id
    timestamp created_at?=now
    // Nome do colaborador (armazenado com criptografia Fernet AES-128-CBC + HMAC-SHA256, prefixo ENC:)
    text nome filters=trim
    // E-mail de autenticação e busca (único)
    email email filters=trim|lower
    // Telefone/contato (armazenado com criptografia Fernet, prefixo ENC:)
    text numero filters=trim
    // Cargo/papel: caixa ou gerente (armazenado com criptografia Fernet, prefixo ENC:)
    text cargo filters=trim
    // Hash criptográfico da senha (SHA-256 com salt estático da aplicação)
    text senha_hash filters=trim
    // Flag de controle para forçar redefinição de senha provisória no primeiro acesso
    bool primeiro_acesso?=true
    // Status do colaborador no sistema (ativo/inativo)
    bool ativo?=true
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "email", op: "asc"}]}
    {type: "btree", field: [{name: "ativo", op: "asc"}]}
  ]

  tags = [
    "churrascontrol"
    "autenticacao"
    "rbac"
    "criptografia"
  ]
  guid = "UQgpVcSzjblHNfxgrFwQZnqL65U"
}

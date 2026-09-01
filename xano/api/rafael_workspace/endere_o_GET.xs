// Query all ENDERECO records (legacy endpoint with special character)
// Retorna todos os registros da tabela endereco (endpoint endere_o)
query endere_o verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    // Busca todos os registros da tabela endereco
    db.query ENDERECO {
      return = {type: "list"}
    } as $endere_o
  }

  response = $endere_o
  guid = "crg0fxQeeOjgp7G6gT1Ta0bSs08"
}
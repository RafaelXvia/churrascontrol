// Query all ENDERECO records
// Retorna todos os registros da tabela endereco
query endereco verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    // Busca todos os registros da tabela endereco
    db.query ENDERECO {
      return = {type: "list"}
    } as $endereco
  }

  response = $endereco
  guid = "-AfqtcouniS5ys81I_AWQQmDljs"
}
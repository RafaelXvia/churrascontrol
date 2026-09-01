// Query all SOLCANCELAMENTO records
query solcancelamento verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query SOLCANCELAMENTO {
      return = {type: "list"}
    } as $solcancelamento
  }

  response = $solcancelamento
  guid = "n_T6rllQtEP0-2nxMXpKLAEz510"
}
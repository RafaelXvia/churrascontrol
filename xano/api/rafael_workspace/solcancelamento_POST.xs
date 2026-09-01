// Add SOLCANCELAMENTO record
query solcancelamento verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "SOLCANCELAMENTO"
    }
  }

  stack {
    db.add SOLCANCELAMENTO {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $solcancelamento
  }

  response = $solcancelamento
  guid = "VlOUyNd8YhUiqGelcraTvXIr_nQ"
}
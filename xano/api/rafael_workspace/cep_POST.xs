// Add CEP record
query cep verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "CEP"
    }
  }

  stack {
    db.add CEP {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $cep
  }

  response = $cep
  guid = "JzdYtfy0bRmKM4id0TvVu-K-fRs"
}
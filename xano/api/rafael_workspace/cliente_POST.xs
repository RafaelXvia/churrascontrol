// Add CLIENTE record
query cliente verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "CLIENTE"
    }
  }

  stack {
    db.add CLIENTE {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $cliente
  }

  response = $cliente
  guid = "8EHbFrrkNibga3ikOvKkapoAAxM"
}
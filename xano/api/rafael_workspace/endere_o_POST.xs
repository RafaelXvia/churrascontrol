// Add ENDEREÇO record
query endere_o verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = ""
    }
  }

  stack {
    db.add "" {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $endere_o
  }

  response = $endere_o
  guid = "sPiRUEuT5w9E6OpNSkefVuLjcME"
}
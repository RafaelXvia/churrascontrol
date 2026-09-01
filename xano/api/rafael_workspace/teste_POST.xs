// Add teste record
query teste verb=POST {
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
    } as $teste
  }

  response = $teste
  guid = "2GhCV1gROK9i-I2IAssJin2a-GI"
}
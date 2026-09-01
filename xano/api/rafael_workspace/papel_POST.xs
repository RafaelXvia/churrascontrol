// Add PAPEL record
query papel verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "PAPEL"
    }
  }

  stack {
    db.add PAPEL {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $papel
  }

  response = $papel
  guid = "2ErUFu2Gi5Fl8fEUHr3jrlDjy2Q"
}
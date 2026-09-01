// Add PRODUTO record
query produto verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "PRODUTO"
    }
  }

  stack {
    db.add PRODUTO {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $produto
  }

  response = $produto
  guid = "jdJBxcdilBCjKSA6oY3kBqreeIs"
}
// Query all PRODUTO records
query produto verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query PRODUTO {
      return = {type: "list"}
    } as $produto
  }

  response = $produto
  guid = "XUNjMKabGpoGU756fqrK5EpjpXw"
}
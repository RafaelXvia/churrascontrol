// Get PRODUTO record
query "produto/{produto_id}" verb=GET {
  api_group = "Rafael_Workspace"

  input {
    int produto_id? filters=min:1
  }

  stack {
    db.get PRODUTO {
      field_name = "id"
      field_value = $input.produto_id
    } as $produto
  
    precondition ($produto != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $produto
  guid = "8qEkJCx29b-e-Z_JM9xBoU7x-3U"
}
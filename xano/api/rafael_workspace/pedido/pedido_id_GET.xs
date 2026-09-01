// Get PEDIDO record
query "pedido/{pedido_id}" verb=GET {
  api_group = "Rafael_Workspace"

  input {
    int pedido_id? filters=min:1
  }

  stack {
    db.get PEDIDO {
      field_name = "id"
      field_value = $input.pedido_id
    } as $pedido
  
    precondition ($pedido != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $pedido
  guid = "90enTB3SXPcezb5iokECK3ae7UU"
}
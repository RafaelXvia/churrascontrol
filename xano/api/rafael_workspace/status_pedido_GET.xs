// Query all STATUS_PEDIDO records
query status_pedido verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query STATUS_PEDIDO {
      return = {type: "list"}
    } as $status_pedido
  }

  response = $status_pedido
  guid = "3MfZyfgi09rGSqqSjF4EbkSkq7Y"
}
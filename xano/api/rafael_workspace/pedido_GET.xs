// Query all PEDIDO records
query pedido verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query PEDIDO {
      return = {type: "list"}
    } as $pedido
  }

  response = $pedido
  guid = "j7p5ZvbDvcKbzfcXkxhAhbF5JSs"
}
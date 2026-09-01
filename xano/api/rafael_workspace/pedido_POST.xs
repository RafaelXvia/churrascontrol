// Add PEDIDO record
query pedido verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "PEDIDO"
    }
  }

  stack {
    db.add PEDIDO {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $pedido
  }

  response = $pedido
  guid = "yZ3vNsEH5rDA0ZYnwJpSSoff_2Y"
}
// Delete PEDIDO record.
query "pedido/{pedido_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int pedido_id? filters=min:1
  }

  stack {
    db.del PEDIDO {
      field_name = "id"
      field_value = $input.pedido_id
    }
  }

  response = null
  guid = "zRHkvRUyp-lQ67eDuNn_1xlkQtE"
}
// Delete PRODUTO record.
query "produto/{produto_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int produto_id? filters=min:1
  }

  stack {
    db.del PRODUTO {
      field_name = "id"
      field_value = $input.produto_id
    }
  }

  response = null
  guid = "CLvblCwVVJA8qb04_W_bcwb_fQQ"
}
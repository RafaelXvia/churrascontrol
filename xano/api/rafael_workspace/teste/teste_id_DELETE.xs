// Delete teste record.
query "teste/{teste_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int teste_id? filters=min:1
  }

  stack {
    db.del "" {
      field_name = "id"
      field_value = $input.teste_id
    }
  }

  response = null
  guid = "EsMa7mqG_KVpw-qcIIqAhDa_5NY"
}
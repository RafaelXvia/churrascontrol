// Delete ENDEREÇO record.
query "endere_o/{endere_o_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int endere_o_id? filters=min:1
  }

  stack {
    db.del "" {
      field_name = "id"
      field_value = $input.endere_o_id
    }
  }

  response = null
  guid = "DhOYyNSLWZqTI67jAUSfJQN4H38"
}
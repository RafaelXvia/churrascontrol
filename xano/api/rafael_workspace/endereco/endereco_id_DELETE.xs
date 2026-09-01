// Delete ENDERECO record.
query "endereco/{endereco_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int endereco_id? filters=min:1
  }

  stack {
    db.del "" {
      field_name = "id"
      field_value = $input.endereco_id
    }
  }

  response = null
  guid = "e20I7xk6_vL5t9IJwEMhxXSDdMY"
}
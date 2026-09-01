// Delete CEP record.
query "cep/{cep_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int cep_id? filters=min:1
  }

  stack {
    db.del CEP {
      field_name = "id"
      field_value = $input.cep_id
    }
  }

  response = null
  guid = "iG8v4d-ZGtU8s2H3Sg_1CJ1mGxE"
}
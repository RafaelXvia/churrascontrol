// Delete STATUS record.
query "status/{status_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int status_id? filters=min:1
  }

  stack {
    db.del "" {
      field_name = "id"
      field_value = $input.status_id
    }
  }

  response = null
  guid = "8lgCViBIY4YPsEF-9yhDLCptqp4"
}
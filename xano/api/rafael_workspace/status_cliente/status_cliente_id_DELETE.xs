// Delete STATUS_CLIENTE record.
query "status_cliente/{status_cliente_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int status_cliente_id? filters=min:1
  }

  stack {
    db.del STATUS_CLIENTE {
      field_name = "id"
      field_value = $input.status_cliente_id
    }
  }

  response = null
  guid = "QsKIjFORAtEQy7Ra0LtvrIu0tqE"
}
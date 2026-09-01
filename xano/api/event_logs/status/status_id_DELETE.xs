// Delete status record.
query "status/{status_id}" verb=DELETE {
  api_group = "Event Logs"

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
  guid = "uracmjCI-gvHJrdqb-5W2hYlE4o"
}
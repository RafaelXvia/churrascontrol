// Get status record
query "status/{status_id}" verb=GET {
  api_group = "Event Logs"

  input {
    int status_id? filters=min:1
  }

  stack {
    db.get "" {
      field_name = "id"
      field_value = $input.status_id
    } as $status
  
    precondition ($status != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $status
  guid = "8xcEJL3o_7ivY86er45a20WL-oM"
}
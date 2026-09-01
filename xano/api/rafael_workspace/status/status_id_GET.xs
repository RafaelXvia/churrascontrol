// Get STATUS record
query "status/{status_id}" verb=GET {
  api_group = "Rafael_Workspace"

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
  guid = "B4F-HKiXZpYtB6L0qmVquxUkhuo"
}
// Get STATUS_OP record
query "status_op/{status_op_id}" verb=GET {
  api_group = "Rafael_Workspace"

  input {
    int status_op_id? filters=min:1
  }

  stack {
    db.get STATUS_OP {
      field_name = "id"
      field_value = $input.status_op_id
    } as $status_op
  
    precondition ($status_op != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $status_op
  guid = "U2X5q6J1a_3YhLRs-BW0-_ET8L8"
}
// Query all STATUS_OP records
query status_op verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query STATUS_OP {
      return = {type: "list"}
    } as $status_op
  }

  response = $status_op
  guid = "RPV5taEfo1PDcyWFIjwhHqPFdj0"
}
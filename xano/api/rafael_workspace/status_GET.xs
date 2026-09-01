// Query all STATUS records
query status verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query "" {
      return = {type: "list"}
    } as $status
  }

  response = $status
  guid = "C_GrULmZ4HuG3m0d3pCcZAjkLHw"
}
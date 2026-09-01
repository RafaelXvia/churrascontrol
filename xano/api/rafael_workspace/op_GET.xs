// Query all OP records
query op verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query OP {
      return = {type: "list"}
    } as $op
  }

  response = $op
  guid = "n-31pCTeSbJIXHOAmiw8F0pEEkk"
}
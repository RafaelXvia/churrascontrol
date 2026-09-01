// Query all teste records
query teste verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query "" {
      return = {type: "list"}
    } as $teste
  }

  response = $teste
  guid = "V1IresV_p6nX3I6o24aHEA_YEOk"
}
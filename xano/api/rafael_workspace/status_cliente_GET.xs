// Query all STATUS_CLIENTE records
query status_cliente verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query STATUS_CLIENTE {
      return = {type: "list"}
    } as $status_cliente
  }

  response = $status_cliente
  guid = "0OZCNrCCp1lu602G6crWw4EY8Wc"
}
// Query all TRANSACAO records
query transacao verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query TRANSACAO {
      return = {type: "list"}
    } as $transacao
  }

  response = $transacao
  guid = "z9wzfnsIS1lfEPNqoBZkQjbm9Go"
}
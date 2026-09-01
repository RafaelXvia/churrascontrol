// Query all STATUS_TRANSACAO records
query status_transacao verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query STATUS_TRANSACAO {
      return = {type: "list"}
    } as $status_transacao
  }

  response = $status_transacao
  guid = "PuFX98nYPaJ__dbhOlh-Vd0jmgo"
}
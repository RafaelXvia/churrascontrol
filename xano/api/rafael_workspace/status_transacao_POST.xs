// Add STATUS_TRANSACAO record
query status_transacao verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "STATUS_TRANSACAO"
    }
  }

  stack {
    db.add STATUS_TRANSACAO {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $status_transacao
  }

  response = $status_transacao
  guid = "QWZZTf6jhg8kfvilySbpb-7DBcY"
}
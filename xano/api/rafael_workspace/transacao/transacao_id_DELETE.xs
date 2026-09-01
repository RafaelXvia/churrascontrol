// Delete TRANSACAO record.
query "transacao/{transacao_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int transacao_id? filters=min:1
  }

  stack {
    db.del TRANSACAO {
      field_name = "id"
      field_value = $input.transacao_id
    }
  }

  response = null
  guid = "RvVDaJ3JoRA1qde3OCUiv-0wAhs"
}
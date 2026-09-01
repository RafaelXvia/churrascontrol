// Edit TRANSACAO record
query "transacao/{transacao_id}" verb=PATCH {
  api_group = "Rafael_Workspace"

  input {
    int transacao_id? filters=min:1
    dblink {
      table = "TRANSACAO"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch TRANSACAO {
      field_name = "id"
      field_value = $input.transacao_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $transacao
  }

  response = $transacao
  guid = "fJ9TH54i03Gbw8jf1NOmRxFuQqU"
}
// Edit teste record
query "teste/{teste_id}" verb=PATCH {
  api_group = "Rafael_Workspace"

  input {
    int teste_id? filters=min:1
    dblink {
      table = ""
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch "" {
      field_name = "id"
      field_value = $input.teste_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $teste
  }

  response = $teste
  guid = "_20vgoco5qG3oyiovya5NjJGNtU"
}
// Edit STATUS record
query "status/{status_id}" verb=PATCH {
  api_group = "Rafael_Workspace"

  input {
    int status_id? filters=min:1
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
      field_value = $input.status_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $status
  }

  response = $status
  guid = "iuW3hzBuzAW30MpHRmXybKfbYc8"
}
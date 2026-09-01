// Delete STATUS_TESTORNO record.
query "status_testorno/{status_testorno_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int status_testorno_id? filters=min:1
  }

  stack {
    db.del STATUS_TESTORNO {
      field_name = "id"
      field_value = $input.status_testorno_id
    }
  }

  response = null
  guid = "DR9oYBgtMRj34N6mUYVKs0XWV_E"
}
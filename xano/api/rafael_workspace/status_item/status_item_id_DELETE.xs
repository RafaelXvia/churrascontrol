// Delete STATUS_ITEM record.
query "status_item/{status_item_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int status_item_id? filters=min:1
  }

  stack {
    db.del STATUS_ITEM {
      field_name = "id"
      field_value = $input.status_item_id
    }
  }

  response = null
  guid = "7_axl_VXX7TgJxob99ZJ7IjEP2I"
}
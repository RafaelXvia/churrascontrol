// Delete ITEM record.
query "item/{item_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int item_id? filters=min:1
  }

  stack {
    db.del ITEM {
      field_name = "id"
      field_value = $input.item_id
    }
  }

  response = null
  guid = "rmXK3g1thqSW8_-phlJB2aQOCiU"
}
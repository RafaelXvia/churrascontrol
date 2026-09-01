// Get ITEM record
query "item/{item_id}" verb=GET {
  api_group = "Rafael_Workspace"

  input {
    int item_id? filters=min:1
  }

  stack {
    db.get ITEM {
      field_name = "id"
      field_value = $input.item_id
    } as $item
  
    precondition ($item != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $item
  guid = "uLyvmiW6z9SlLDSzSFMAqoxA7TM"
}
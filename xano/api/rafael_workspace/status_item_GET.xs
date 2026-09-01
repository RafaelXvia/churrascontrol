// Query all STATUS_ITEM records
query status_item verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query STATUS_ITEM {
      return = {type: "list"}
    } as $status_item
  }

  response = $status_item
  guid = "54OVwCd0OD3q0NcwiUepizpRWFg"
}
// Add ITEM record
query item verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "ITEM"
    }
  }

  stack {
    db.add ITEM {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $item
  }

  response = $item
  guid = "EpsUcEeD6FM9FF9lQRjaj0Q7ErU"
}
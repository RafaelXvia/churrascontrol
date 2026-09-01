// Query all ITEM records
query item verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query ITEM {
      return = {type: "list"}
    } as $item
  }

  response = $item
  guid = "UHyFkn_CD5DLFjydH_92LwgnUnw"
}
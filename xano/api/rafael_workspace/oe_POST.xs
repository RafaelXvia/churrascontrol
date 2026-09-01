// Add OE record
query oe verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "OE"
    }
  }

  stack {
    db.add OE {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $oe
  }

  response = $oe
  guid = "8BzNt3-mUrGgftPkmNYZnvfKvaM"
}
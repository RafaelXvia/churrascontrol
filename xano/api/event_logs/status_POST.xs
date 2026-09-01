// Add status record
query status verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = ""
    }
  }

  stack {
    db.add "" {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $status
  }

  response = $status
  guid = "m347asCI7zB3Lzm9pHGNog7JRZQ"
}
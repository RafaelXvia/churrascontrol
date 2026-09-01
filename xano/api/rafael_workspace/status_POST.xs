// Add STATUS record
query status verb=POST {
  api_group = "Rafael_Workspace"

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
  guid = "VBxMswY37mKNNUBucqIS-H5evQA"
}
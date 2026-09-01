// Add TESTORNO record
query testorno verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "TESTORNO"
    }
  }

  stack {
    db.add TESTORNO {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $testorno
  }

  response = $testorno
  guid = "RbH5Ndu34YpbTbxDfIX0ye-A5sc"
}
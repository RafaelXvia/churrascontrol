// Add STATUS_TESTORNO record
query status_testorno verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "STATUS_TESTORNO"
    }
  }

  stack {
    db.add STATUS_TESTORNO {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $status_testorno
  }

  response = $status_testorno
  guid = "lamlYNyvbdShFh6WAy6WhqeGGUI"
}
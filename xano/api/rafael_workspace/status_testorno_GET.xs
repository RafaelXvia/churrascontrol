// Query all STATUS_TESTORNO records
query status_testorno verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query STATUS_TESTORNO {
      return = {type: "list"}
    } as $status_testorno
  }

  response = $status_testorno
  guid = "ZLWZG9WL10jVAkNnKBT9Mk7PWZU"
}
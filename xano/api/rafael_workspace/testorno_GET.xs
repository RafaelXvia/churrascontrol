// Query all TESTORNO records
query testorno verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query TESTORNO {
      return = {type: "list"}
    } as $testorno
  }

  response = $testorno
  guid = "Yeyz0YcoZpElprgzEc3acm-ynOQ"
}
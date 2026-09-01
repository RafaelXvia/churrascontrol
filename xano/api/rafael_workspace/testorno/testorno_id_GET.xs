// Get TESTORNO record
query "testorno/{testorno_id}" verb=GET {
  api_group = "Rafael_Workspace"

  input {
    int testorno_id? filters=min:1
  }

  stack {
    db.get TESTORNO {
      field_name = "id"
      field_value = $input.testorno_id
    } as $testorno
  
    precondition ($testorno != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $testorno
  guid = "OQxdGmezpwuLfg9_7w4pPEAtX_I"
}
// Delete TESTORNO record.
query "testorno/{testorno_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int testorno_id? filters=min:1
  }

  stack {
    db.del TESTORNO {
      field_name = "id"
      field_value = $input.testorno_id
    }
  }

  response = null
  guid = "ZhRbzU62UDzxikfo2nAkv00X2nU"
}
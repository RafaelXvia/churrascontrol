// Query all CLIENTE records
query cliente verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query CLIENTE {
      return = {type: "list"}
      addon = [
        {
          name : "user_1"
          input: {user_id: $output.user_id}
          as   : "_user_1"
        }
      ]
    } as $cliente
  }

  response = $cliente
  guid = "yY8oglciNxgZGl8Dl4RNC649_HU"
}
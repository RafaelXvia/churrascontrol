// Query all TOKENS records
query tokens verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query TOKENS {
      return = {type: "list"}
    } as $tokens
  }

  response = $tokens
  guid = "ru9QVCqrCWVUQrGgZGSGgwTF89Y"
}
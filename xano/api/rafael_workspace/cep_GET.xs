// Query all CEP records
query cep verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query CEP {
      return = {type: "list"}
    } as $cep
  }

  response = $cep
  guid = "xNQMVNxfv8Kbs1Icmqhbn6TNchw"
}
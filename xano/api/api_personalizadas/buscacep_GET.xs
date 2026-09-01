query buscacep verb=GET {
  api_group = "ApiPersonalizadas"

  input {
    text cep? filters=trim
  }

  stack {
    db.query CEP {
      where = $db.CEP.cep == $input.cep
      return = {type: "list"}
    } as $CEP1
  }

  response = $CEP1
  guid = "gmhY7kB8m22G2LB97WaOW1JywW0"
}
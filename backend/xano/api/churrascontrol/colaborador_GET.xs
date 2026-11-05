query colaborador verb=GET {
  api_group = "ChurrasControl"
  input {
    int? limit?=50
  }
  stack {
    db.query colaborador {
      return = {type: "list"}
    } as $colaboradores
  }
  response = $colaboradores
  guid = "Ajo1B693dWLn9U1zx3ktuC9o1MY"
}

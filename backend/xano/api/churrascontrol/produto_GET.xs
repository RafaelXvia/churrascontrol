query produto verb=GET {
  api_group = "ChurrasControl"
  input {
    text busca? filters=trim
  }
  stack {
    db.query PRODUTO {
      return = {type: "list"}
    } as $produtos
  }
  response = $produtos
  guid = "KBQvcutUDyklaNxVfEpZMFr_1OY"
}
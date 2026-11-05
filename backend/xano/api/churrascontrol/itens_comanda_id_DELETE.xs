query "itens_comanda/{item_id}" verb=DELETE {
  api_group = "ChurrasControl"
  input {
    int item_id
  }
  stack {
    db.del itens_comanda {
      field_name  = "id"
      field_value = $input.item_id
    }
  }
  response = {
    status: "ok"
  }
  guid = "9tGnkakiuRMW_roEAKsBwSb75Xs"
}
query "produto/{produto_id}" verb=DELETE {
  api_group = "ChurrasControl"
  input {
    int produto_id
  }
  stack {
    db.del PRODUTO {
      field_name  = "id"
      field_value = $input.produto_id
    }
  }
  response = {
    status: "ok"
  }
  guid = "VgPEeUwtUNlHenN40_golRCnfAQ"
}
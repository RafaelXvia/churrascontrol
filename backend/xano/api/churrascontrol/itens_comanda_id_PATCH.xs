query "itens_comanda/{item_id}" verb=PATCH {
  api_group = "ChurrasControl"
  input {
    int item_id
    int quantidade
    decimal preco_momento
    text observacao? filters=trim
  }
  stack {
    db.patch itens_comanda {
      field_name  = "id"
      field_value = $input.item_id
      data = {
        quantidade   : $input.quantidade,
        preco_momento: $input.preco_momento,
        observacao   : ($input.observacao || "")
      }
    } as $item_editado
  }
  response = {
    status: "ok",
    item  : $item_editado
  }
  guid = "jVmQ3IFrd00Bspg_WwPG12Hw5FU"
}
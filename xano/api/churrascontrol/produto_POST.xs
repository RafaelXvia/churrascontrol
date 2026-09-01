query produto verb=POST {
  api_group = "ChurrasControl"
  input {
    text codigo_pdv filters=trim
    text nome filters=trim
    text categoria filters=trim
    decimal preco
  }
  stack {
    db.add PRODUTO {
      enforce_hidden_fields = false
      data = {
        created_at: "now",
        codigo_pdv: $input.codigo_pdv,
        nome      : $input.nome,
        categoria : $input.categoria,
        preco     : $input.preco
      }
    } as $novo_produto
  }
  response = {
    status: "ok",
    id    : $novo_produto.id
  }
  guid = "XjFT0cXsioCt2C8ppiLCbrdIsJU"
}
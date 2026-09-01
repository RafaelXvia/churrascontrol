query "produto/{produto_id}" verb=PATCH {
  api_group = "ChurrasControl"
  input {
    int produto_id
    text? codigo_pdv filters=trim
    text? nome filters=trim
    text? categoria filters=trim
    decimal? preco
  }
  stack {
    db.patch PRODUTO {
      field_name  = "id"
      field_value = $input.produto_id
      data = {
        codigo_pdv: $input.codigo_pdv,
        nome      : $input.nome,
        categoria : $input.categoria,
        preco     : $input.preco
      }
    } as $produto_atualizado
  }
  response = {
    status: "ok",
    produto: $produto_atualizado
  }
  guid = "tFVPH_38nySzGja-4qPrdAW9kP8"
}
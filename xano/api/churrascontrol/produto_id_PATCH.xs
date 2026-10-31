query "produto/{produto_id}" verb=PATCH {
  api_group = "ChurrasControl"
  input {
    int produto_id
    text? codigo_pdv filters=trim
    text? nome filters=trim
    text? categoria filters=trim
    decimal? preco
    text? descricao filters=trim
    int? qtd_disp filters=min:0
    text? url_imagem filters=trim
    bool? precisa_produzir
    bool? disponivel
  }
  stack {
    db.patch PRODUTO {
      field_name  = "id"
      field_value = $input.produto_id
      data = {
        codigo_pdv       : $input.codigo_pdv,
        nome             : $input.nome,
        categoria        : $input.categoria,
        preco            : $input.preco,
        descricao        : $input.descricao,
        qtd_disp         : $input.qtd_disp,
        url_imagem       : $input.url_imagem,
        precisa_produzir : $input.precisa_produzir,
        disponivel       : $input.disponivel
      }
    } as $produto_atualizado
  }
  response = {
    status: "ok",
    produto: $produto_atualizado
  }
  guid = "tFVPH_38nySzGja-4qPrdAW9kP8"
}
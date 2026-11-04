query produto verb=POST {
  api_group = "ChurrasControl"
  input {
    text codigo_pdv filters=trim
    text nome filters=trim
    text categoria filters=trim
    decimal preco
    text? descricao filters=trim
    int? qtd_disp filters=min:0
    text? url_imagem filters=trim
    bool? precisa_produzir
    bool? disponivel
  }
  stack {
    db.query PRODUTO {
      where  = ($db.PRODUTO.codigo_pdv == $input.codigo_pdv || $db.PRODUTO.nome == $input.nome)
      return = {type: "single"}
    } as $existente

    conditional {
      if ($existente != null) {
        db.patch PRODUTO {
          field_name  = "id"
          field_value = $existente.id
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
        } as $prod_salvo
      }
      else {
        db.add PRODUTO {
          enforce_hidden_fields = false
          data = {
            created_at       : "now",
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
        } as $prod_salvo
      }
    }
  }
  response = {
    status : "ok",
    id     : $prod_salvo.id
  }
  guid = "XjFT0cXsioCt2C8ppiLCbrdIsJU"
}
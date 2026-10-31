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
    } as $novo_produto
  }
  response = {
    status: "ok",
    id    : $novo_produto.id
  }
  guid = "XjFT0cXsioCt2C8ppiLCbrdIsJU"
}
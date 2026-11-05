table PRODUTO {
  auth = false
  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
    text? codigo_pdv filters=trim
    text nome? filters=trim
    text descricao? filters=trim
    int qtd_disp? filters=min:0
    text url_imagem? filters=trim
    decimal preco?
    bool precisa_produzir?
    text categoria? filters=trim
    bool disponivel?
  }
  index = [
    {type: "primary", field: [{name: "id"}]},
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]
  tags = ["modulo 03"]
  guid = "jK0buo7fFXifKLiqRjANsAdCRYs"
}
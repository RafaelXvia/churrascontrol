table itens_comanda {
  auth = false
  schema {
    int id
    timestamp created_at?=now { visibility = "private" }
    int comanda_id { table = "comandas" }
    int? produto_id { table = "PRODUTO" }
    text? nome_produto_historico filters=trim
    text? categoria_historico filters=trim
    int quantidade filters=min:1
    decimal preco_momento
    text? observacao filters=trim
  }
  index = [
    { type: "primary", field: [{ name: "id" }] },
    { type: "btree", field: [{ name: "comanda_id", op: "asc" }] }
  ]
  guid = "0ca1-gJn5PB-xDBwesc6RJADaA8"
}
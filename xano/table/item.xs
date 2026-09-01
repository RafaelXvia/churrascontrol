table ITEM {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int pedido_id? {
      table = "PEDIDO"
    }
  
    int qtd? filters=min:1
    decimal valor_unit?
    int produto_id? {
      table = "PRODUTO"
    }
  
    int status_item_id?=3 {
      table = "STATUS_ITEM"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {
      type : "btree|unique"
      field: [
        {name: "pedido_id", op: "asc"}
        {name: "produto_id", op: "asc"}
      ]
    }
  ]

  tags = ["modulo 03"]
  guid = "QMPvbHodP2BA0INXHGb0lwQGfLI"
}
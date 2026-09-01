table CLIENTE {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int user_id? {
      table = "user"
    }
  
    text celular? filters=trim
    text cpf? filters=trim
    int status_cliente_id?=1 {
      table = "STATUS_CLIENTE"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "cpf", op: "asc"}]}
  ]

  tags = ["modulo 01"]
  guid = "4VHnaTcY6Mc3XJ3cHm-AI6UR_jY"
}
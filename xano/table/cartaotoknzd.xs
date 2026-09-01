table CARTAOTOKNZD {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int cliente_id? {
      table = "CLIENTE"
    }
  
    text token? filters=trim
    text codigoclientessas? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "token", op: "asc"}]}
  ]

  tags = ["modulo 02"]
  guid = "de4ZRpND8YXt7_zoRXQn25529mw"
}
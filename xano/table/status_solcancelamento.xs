table STATUS_SOLCANCELAMENTO {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text status? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "status", op: "asc"}]}
  ]

  tags = ["modulo 05"]
  guid = "mTFb5GuF8990FXK5ofFLGdvDZrM"
}
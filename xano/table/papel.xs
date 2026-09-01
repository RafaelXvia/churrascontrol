table PAPEL {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text papel? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "papel", op: "asc"}]}
  ]

  tags = ["modulo 01"]
  guid = "Z1aiQ7oPvqFXO9-yBg6v3jPVZoA"
}
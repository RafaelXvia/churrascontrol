// Query all PAPEL records
query papel verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query PAPEL {
      return = {type: "list"}
    } as $papel
  }

  response = $papel
  guid = "2YwAP1GLdIjVNhZt10PWX98uzkw"
}
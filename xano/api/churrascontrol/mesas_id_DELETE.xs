query "mesas/{mesa_id}" verb=DELETE {
  api_group = "ChurrasControl"
  input {
    int mesa_id
  }
  stack {
    db.del mesas {
      field_name  = "id"
      field_value = $input.mesa_id
    }
  }
  response = {
    status: "ok"
  }
  guid = "64ubvjg6ABsoAxlnhVipU3cPmo0"
}
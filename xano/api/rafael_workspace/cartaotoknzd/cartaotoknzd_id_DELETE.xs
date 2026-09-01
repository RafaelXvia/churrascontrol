// Delete CARTAOTOKNZD record.
query "cartaotoknzd/{cartaotoknzd_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int cartaotoknzd_id? filters=min:1
  }

  stack {
    db.del CARTAOTOKNZD {
      field_name = "id"
      field_value = $input.cartaotoknzd_id
    }
  }

  response = null
  guid = "LIyiXuJ4X2jCvQkBavzfEslid3Q"
}
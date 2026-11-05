query "colaborador/{colaborador_id}" verb=DELETE {
  api_group = "ChurrasControl"
  input {
    int colaborador_id
  }
  stack {
    db.del colaborador {
      field_name = "id"
      field_value = $input.colaborador_id
    }
  }
  response = {
    status: "ok"
  }
  guid = "yuZTBUUFvGlKLpZO1RUO5rdpx1w"
}

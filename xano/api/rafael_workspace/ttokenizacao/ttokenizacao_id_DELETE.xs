// Delete TTOKENIZACAO record.
query "ttokenizacao/{ttokenizacao_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int ttokenizacao_id? filters=min:1
  }

  stack {
    db.del TTOKENIZACAO {
      field_name = "id"
      field_value = $input.ttokenizacao_id
    }
  }

  response = null
  guid = "yEwIycnee33-4Rk_W1zoYd5-wyk"
}
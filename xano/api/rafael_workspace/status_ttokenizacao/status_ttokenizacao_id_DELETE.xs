// Delete STATUS_TTOKENIZACAO record.
query "status_ttokenizacao/{status_ttokenizacao_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int status_ttokenizacao_id? filters=min:1
  }

  stack {
    db.del STATUS_TTOKENIZACAO {
      field_name = "id"
      field_value = $input.status_ttokenizacao_id
    }
  }

  response = null
  guid = "5OGyunAF_bNbHiN9i_u0u1hI3QM"
}
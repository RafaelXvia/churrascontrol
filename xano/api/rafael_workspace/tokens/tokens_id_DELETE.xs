// Delete TOKENS record.
query "tokens/{tokens_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int tokens_id? filters=min:1
  }

  stack {
    db.del TOKENS {
      field_name = "id"
      field_value = $input.tokens_id
    }
  }

  response = null
  guid = "8CoHCjIrGXuqG40_356pL_rCfDk"
}
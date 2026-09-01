// Delete OP record.
query "op/{op_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int op_id? filters=min:1
  }

  stack {
    db.del OP {
      field_name = "id"
      field_value = $input.op_id
    }
  }

  response = null
  guid = "sxJS9wyw-0xizi97f6siQlUZ2hM"
}
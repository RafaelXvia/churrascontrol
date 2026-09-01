// Delete PAPEL record.
query "papel/{papel_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int papel_id? filters=min:1
  }

  stack {
    db.del PAPEL {
      field_name = "id"
      field_value = $input.papel_id
    }
  }

  response = null
  guid = "J2Q1dfGGYzAS83CrkO_vG6xSrl0"
}
// Get PAPEL record
query "papel/{papel_id}" verb=GET {
  api_group = "Rafael_Workspace"

  input {
    int papel_id? filters=min:1
  }

  stack {
    db.get PAPEL {
      field_name = "id"
      field_value = $input.papel_id
    } as $papel
  
    precondition ($papel != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $papel
  guid = "DdOl2ToUkMs6pK_w1wxGZpgFeMo"
}
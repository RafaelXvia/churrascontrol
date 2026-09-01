// Get ENDEREÇO record
query "endere_o/{endere_o_id}" verb=GET {
  api_group = "Rafael_Workspace"

  input {
    int endere_o_id? filters=min:1
  }

  stack {
    db.get "" {
      field_name = "id"
      field_value = $input.endere_o_id
    } as $endere_o
  
    precondition ($endere_o != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $endere_o
  guid = "aeGKLbx3eUcasfqgfsu0naGZgvk"
}
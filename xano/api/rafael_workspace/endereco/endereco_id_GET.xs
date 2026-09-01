// Get ENDERECO record
query "endereco/{endereco_id}" verb=GET {
  api_group = "Rafael_Workspace"

  input {
    int endereco_id? filters=min:1
  }

  stack {
    db.get "" {
      field_name = "id"
      field_value = $input.endereco_id
    } as $endereco
  
    precondition ($endereco != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $endereco
  guid = "jv5jacM0xEKmyhRh798qQgri_Y8"
}
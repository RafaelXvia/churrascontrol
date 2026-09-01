// Get TOKENS record
query "tokens/{tokens_id}" verb=GET {
  api_group = "Rafael_Workspace"

  input {
    int tokens_id? filters=min:1
  }

  stack {
    db.get TOKENS {
      field_name = "id"
      field_value = $input.tokens_id
    } as $tokens
  
    precondition ($tokens != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $tokens
  guid = "Yf_I1YKad3kXepGDdidSBfu06iQ"
}
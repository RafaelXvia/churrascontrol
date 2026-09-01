// Add TOKENS record
query tokens verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "TOKENS"
    }
  }

  stack {
    db.add TOKENS {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $tokens
  }

  response = $tokens
  guid = "iU4_qny3zFFU-kpG0cQ2N5pvEt0"
}
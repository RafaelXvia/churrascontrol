// Add TTOKENIZACAO record
query ttokenizacao verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "TTOKENIZACAO"
    }
  }

  stack {
    db.add TTOKENIZACAO {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $ttokenizacao
  }

  response = $ttokenizacao
  guid = "H0Y6dwobVgY0Bj_mw6iBRf_bP30"
}
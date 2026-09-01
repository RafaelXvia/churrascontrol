// Add TRANSACAO record
query transacao verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "TRANSACAO"
    }
  }

  stack {
    db.add TRANSACAO {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $transacao
  }

  response = $transacao
  guid = "u_Ft72rHV4khGC1iBcs51BPOb2c"
}
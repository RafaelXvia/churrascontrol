// Add ENDERECO record
query endereco verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "ENDERECO"
    }
  }

  stack {
    db.add ENDERECO {
      enforce_hidden_fields = false
      data = {created_at: now}
    } as $endereco
  }

  response = $endereco
  guid = "Md2z70t-6JAqAbt5MPXIFJpV2rw"
}
// Add FAQ record
query faq verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "FAQ"
    }
  }

  stack {
    db.add FAQ {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $faq
  }

  response = $faq
  guid = "ssXDPZHYjBYgeNtYNAMOa54-TRg"
}
// Delete FAQ record.
query "faq/{faq_id}" verb=DELETE {
  api_group = "Rafael_Workspace"

  input {
    int faq_id? filters=min:1
  }

  stack {
    db.del FAQ {
      field_name = "id"
      field_value = $input.faq_id
    }
  }

  response = null
  guid = "GEDU29a98h4NHCKG15xnmaCoH-w"
}
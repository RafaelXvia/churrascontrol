// Query all FAQ records
query faq verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query FAQ {
      return = {type: "list"}
    } as $faq
  }

  response = $faq
  guid = "fyyk0zHYXAhEFS0UeioYkNEmKKo"
}
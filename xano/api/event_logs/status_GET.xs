// Query all status records
query status verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query "" {
      return = {type: "list"}
    } as $status
  }

  response = $status
  guid = "7J2-86u00iQIRJW0HN18K7F9KFw"
}
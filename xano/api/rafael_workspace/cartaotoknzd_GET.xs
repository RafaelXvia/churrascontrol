// Query all CARTAOTOKNZD records
query cartaotoknzd verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query CARTAOTOKNZD {
      return = {type: "list"}
    } as $cartaotoknzd
  }

  response = $cartaotoknzd
  guid = "aDG32t_az13BllWqfH3kExq3VSo"
}
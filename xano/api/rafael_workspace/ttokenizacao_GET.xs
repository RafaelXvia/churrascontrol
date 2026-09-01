// Query all TTOKENIZACAO records
query ttokenizacao verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query TTOKENIZACAO {
      return = {type: "list"}
    } as $ttokenizacao
  }

  response = $ttokenizacao
  guid = "vfNd77h3A8fmW0n1yR64vQ8djNw"
}
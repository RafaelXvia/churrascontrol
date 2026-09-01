// Add OP record
query op verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "OP"
    }
  }

  stack {
    db.add OP {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $op
  }

  response = $op
  guid = "VUXFP1iQqIKUgqpn4c8UmAhc7iU"
}
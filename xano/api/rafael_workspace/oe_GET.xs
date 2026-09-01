// Query all OE records
query oe verb=GET {
  api_group = "Rafael_Workspace"

  input {
  }

  stack {
    db.query OE {
      return = {type: "list"}
    } as $oe
  }

  response = $oe
  guid = "KErHWFCX2p-eD9j_UJpl2wW2RRI"
}
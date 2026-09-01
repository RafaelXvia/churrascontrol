// Add CARTAOTOKNZD record
query cartaotoknzd verb=POST {
  api_group = "Rafael_Workspace"

  input {
    dblink {
      table = "CARTAOTOKNZD"
    }
  }

  stack {
    db.add CARTAOTOKNZD {
      enforce_hidden_fields = false
      data = {
        created_at       : "now"
        cliente_id       : $input.cliente_id
        token            : $input.token
        codigoclientessas: $input.codigoclientessas
      }
    } as $cartaotoknzd
  }

  response = $cartaotoknzd
  guid = "S70C2JADIr9fGUTZkFydm4gxyVA"
}
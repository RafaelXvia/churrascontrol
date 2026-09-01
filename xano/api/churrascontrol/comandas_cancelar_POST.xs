query "comandas/{comanda_id}/cancelar" verb=POST {
  api_group = "ChurrasControl"
  input {
    int comanda_id
  }
  stack {
    db.get comandas {
      field_name  = "id"
      field_value = $input.comanda_id
    } as $comanda

    precondition ($comanda != null) {
      error_type = "notfound"
      error      = "Comanda não encontrada."
    }

    db.patch comandas {
      field_name  = "id"
      field_value = $input.comanda_id
      data = {
        status         : "CANCELADA",
        data_fechamento: "now",
        mesa_id        : null
      }
    } as $comanda_cancelada

    conditional {
      if ($comanda.mesa_id != null) {
        db.del mesas {
          field_name  = "id"
          field_value = $comanda.mesa_id
        }
      }
    }
  }
  response = {
    status: "ok"
  }
  guid = "dMg95m990eDlJ0xY0fsxFhggDg0"
}
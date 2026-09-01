query "comandas/{comanda_id}/fechar" verb=POST {
  api_group = "ChurrasControl"
  input {
    int comanda_id
    decimal valor_final
    bool taxa_servico?=true
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
        status         : "PAGA",
        data_fechamento: "now",
        valor_total    : $input.valor_final,
        taxa_servico   : $input.taxa_servico,
        mesa_id        : null
      }
    } as $comanda_paga

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
    status     : "ok",
    total_final: $input.valor_final
  }
  guid = "pasDjLi7TR6F03FhgBD0zXwfMtA"
}
query comandas verb=POST {
  api_group = "ChurrasControl"
  input {
    int id
    int numero_mesa
    int? qtd_pessoas?=1
    bool? taxa_servico?=true
  }
  stack {
    db.query mesas {
      where  = ($db.mesas.numero_mesa == $input.numero_mesa)
      return = {type: "single"}
    } as $mesa_existente

    conditional {
      if ($mesa_existente != null) {
        db.patch mesas {
          field_name  = "id"
          field_value = $mesa_existente.id
          data = {
            capacidade: $input.qtd_pessoas,
            status    : "OCUPADA"
          }
        } as $mesa_salva
      }
      else {
        db.add mesas {
          enforce_hidden_fields = false
          data = {
            created_at : "now",
            numero_mesa: $input.numero_mesa,
            capacidade : $input.qtd_pessoas,
            status     : "OCUPADA"
          }
        } as $mesa_salva
      }
    }

    db.get comandas {
      field_name  = "id"
      field_value = $input.id
    } as $existente

    conditional {
      if ($existente != null) {
        db.patch comandas {
          field_name  = "id"
          field_value = $existente.id
          data = {
            mesa_id              : $mesa_salva.id,
            numero_mesa_historico: $input.numero_mesa,
            qtd_pessoas          : $input.qtd_pessoas,
            taxa_servico         : $input.taxa_servico
          }
        } as $comanda_salva
      }
      else {
        db.add comandas {
          enforce_hidden_fields = false
          data = {
            id                   : $input.id,
            created_at           : "now",
            mesa_id              : $mesa_salva.id,
            numero_mesa_historico: $input.numero_mesa,
            data_abertura        : "now",
            status               : "ABERTA",
            taxa_servico         : $input.taxa_servico,
            qtd_pessoas          : $input.qtd_pessoas,
            valor_total          : 0.00
          }
        } as $comanda_salva
      }
    }
  }
  response = {
    status    : "ok",
    mesa_id   : $mesa_salva.id,
    comanda_id: $comanda_salva.id
  }
  guid = "gWjzGGJmy4QsMXfrStM-NJQ3oq8"
}

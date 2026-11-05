query "comandas/{comanda_id}" verb=PATCH {
  api_group = "ChurrasControl"
  input {
    int comanda_id
    bool? taxa_servico
    int? qtd_pessoas?=null
    decimal? valor_total?=null
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
        taxa_servico: ($input.taxa_servico != null ? $input.taxa_servico : $comanda.taxa_servico),
        qtd_pessoas : ($input.qtd_pessoas != null ? $input.qtd_pessoas : $comanda.qtd_pessoas),
        valor_total : ($input.valor_total != null ? $input.valor_total : $comanda.valor_total)
      }
    } as $comanda_atualizada
  }
  response = {
    status      : "ok",
    taxa_servico: $comanda_atualizada.taxa_servico,
    comanda_id  : $comanda_atualizada.id
  }
  guid = "R7XKJGezEBQZt_sZRWpyGbZJLp4"
}

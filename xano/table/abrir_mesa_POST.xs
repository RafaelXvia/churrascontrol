query abrir_mesa verb=POST {
  api_group = "ChurrasControl"
  input {
    int numero_mesa
    int qtd_pessoas?=1
  }
  stack {
    // 1. Verifica se mesa ja existe
    db.query mesas {
      where = $db.mesas.numero_mesa == $input.numero_mesa
      return = { type: "single" }
    } as $mesa_existente

    precondition ($mesa_existente == null) {
      error_type = "inputerror"
      error = "Mesa já está aberta!"
    }

    // 2. Insere mesa
    db.add mesas {
      data = {
        numero_mesa: $input.numero_mesa,
        capacidade : $input.qtd_pessoas,
        status     : "OCUPADA"
      }
    } as $nova_mesa

    // 3. Abre comanda
    db.add comandas {
      data = {
        mesa_id               : $nova_mesa.id,
        numero_mesa_historico : $input.numero_mesa,
        qtd_pessoas           : $input.qtd_pessoas,
        status                : "ABERTA"
      }
    } as $nova_comanda
  }
  response = {
    status: "ok",
    mesa_id: $nova_mesa.id,
    comanda_id: $nova_comanda.id
  }
  guid = "riNo17GRQyF_xm_hVgoa0MlHd-s"
}
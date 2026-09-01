query "comandas/{comanda_id}" verb=GET {
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

    db.query itens_comanda {
      where  = ($db.itens_comanda.comanda_id == $input.comanda_id)
      return = {type: "list"}
    } as $itens

    array.map ($itens) {
      by = {
        id                 : $this.id,
        comanda_id         : $this.comanda_id,
        produto_id         : $this.produto_id,
        produto_nome       : $this.nome_produto_historico,
        categoria_historico: $this.categoria_historico,
        quantidade         : $this.quantidade,
        preco_momento      : $this.preco_momento,
        subtotal           : ($this.quantidade | multiply:$this.preco_momento),
        observacao         : $this.observacao
      }
    } as $itens_formatados
  }
  response = {
    comanda: {
      id                   : $comanda.id,
      mesa_id              : $comanda.mesa_id,
      numero_mesa          : $comanda.numero_mesa_historico,
      numero_mesa_historico: $comanda.numero_mesa_historico,
      data_abertura        : $comanda.data_abertura,
      status               : $comanda.status,
      qtd_pessoas          : $comanda.qtd_pessoas,
      taxa_servico         : $comanda.taxa_servico,
      valor_total          : ($comanda.valor_total || 0.00)
    },
    itens  : $itens_formatados,
    total  : ($comanda.valor_total || 0.00)
  }
  guid = "MdhCcLvz2kiv_uecL_aKc87RkDw"
}
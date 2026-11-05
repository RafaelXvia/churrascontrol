query "comandas/{comanda_id}/itens" verb=POST {
  api_group = "ChurrasControl"
  input {
    int comanda_id
    text produto_query filters=trim
    int quantidade?=1
    text observacao? filters=trim
  }
  stack {
    db.query PRODUTO {
      where  = ($db.PRODUTO.nome == $input.produto_query)
      return = {type: "single"}
    } as $produto

    precondition ($produto != null) {
      error_type = "notfound"
      error      = "Produto não encontrado no cardápio."
    }

    db.get comandas {
      field_name  = "id"
      field_value = $input.comanda_id
    } as $comanda_pai

    conditional {
      if ($comanda_pai == null) {
        db.add comandas {
          enforce_hidden_fields = false
          data = {
            id                   : $input.comanda_id,
            created_at           : "now",
            numero_mesa_historico: 1,
            data_abertura        : "now",
            status               : "ABERTA",
            taxa_servico         : true,
            qtd_pessoas          : 1,
            valor_total          : 0.00
          }
        } as $comanda_auto_criada
      }
    }

    db.query itens_comanda {
      where  = ($db.itens_comanda.comanda_id == $input.comanda_id && $db.itens_comanda.produto_id == $produto.id)
      return = {type: "single"}
    } as $item_existente

    conditional {
      if ($item_existente != null) {
        var $nova_qtd {
          value = $item_existente.quantidade | add:$input.quantidade
        }
        db.patch itens_comanda {
          field_name  = "id"
          field_value = $item_existente.id
          data = {
            quantidade: $nova_qtd,
            observacao: ($input.observacao || $item_existente.observacao)
          }
        } as $item_atualizado
      }
      else {
        db.add itens_comanda {
          enforce_hidden_fields = false
          data = {
            created_at            : "now",
            comanda_id            : $input.comanda_id,
            produto_id            : $produto.id,
            nome_produto_historico: $produto.nome,
            categoria_historico   : $produto.categoria,
            quantidade            : $input.quantidade,
            preco_momento         : $produto.preco,
            observacao            : ($input.observacao || "")
          }
        } as $novo_item
      }
    }
  }
  response = {
    status : "ok",
    produto: $produto.nome
  }
  guid = "wWU3A9tBvUoowMdTZb7mE_LxFq8"
}
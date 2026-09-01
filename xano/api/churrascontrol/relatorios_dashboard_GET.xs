query "relatorios/dashboard" verb=GET {
  api_group = "ChurrasControl"
  input {
    text? periodo filters=trim
  }
  stack {
    db.query comandas {
      where  = ($db.comandas.status == "PAGA")
      return = {type: "list"}
    } as $pagas

    var $qtd_comandas {
      value = $pagas | count
    }

    var $resumo {
      value = {
        faturamento_total: 0.00,
        total_comandas   : $qtd_comandas,
        ticket_medio     : 0.00,
        total_pessoas    : $qtd_comandas,
        ticket_por_pessoa: 0.00
      }
    }
  }
  response = {
    periodo             : ($input.periodo || "7d"),
    resumo              : $resumo,
    evolucao_diaria     : [],
    vendas_por_categoria: [],
    top_produtos        : [],
    comandas_finalizadas: $pagas
  }
  guid = "zJZd0nlX8DNeG5sOaJe-A8dyWL4"
}
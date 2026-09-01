table TRANSACAO {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text CLIENTEASSAS? filters=trim
    text idpayment? filters=trim
    text tipo? filters=trim
    decimal valor?
    text datavenc? filters=trim
    text descricao? filters=trim
    int status_transacao_id? {
      table = "STATUS_TRANSACAO"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "Tv5uKPCa46siTET_VpFrhOShhS4"
}
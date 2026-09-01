query marcarEnderecoPadrao verb=PATCH {
  api_group = "ApiPersonalizadas"

  input {
    int endereco_id?
  }

  stack {
    db.get ENDERECO {
      field_name = "id"
      field_value = $input.endereco_id
    } as $ENDERECO1
  
    db.patch ENDERECO {
      field_name = "id"
      field_value = $input.endereco_id
      data = {padrao: true}
    } as $ENDERECO2
  
    db.query ENDERECO {
      where = $ENDERECO1.cliente_id == $db.ENDERECO.cliente_id && $ENDERECO1.id != $db.ENDERECO.id
      return = {type: "list"}
    } as $ENDERECO3
  
    array.map ($ENDERECO3) {
      by = {id: $this.id, padrao: false}
    } as $x1
  
    db.bulk.patch ENDERECO {
      items = $x1
    } as $ENDERECO4
  }

  response = {padrao: $ENDERECO2, naoPadrao: $ENDERECO4}
  guid = "f8anTEcTiYqA_eeCYBr1cHRPLN4"
}
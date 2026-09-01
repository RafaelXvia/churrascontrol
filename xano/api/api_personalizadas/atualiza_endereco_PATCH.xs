query atualizaEndereco verb=PATCH {
  api_group = "ApiPersonalizadas"

  input {
    int endereco_id?
    text logradouro? filters=trim
    text numero? filters=trim
    text complemento? filters=trim
    text bairro? filters=trim
    text referencia? filters=trim
    text cep? filters=trim
    text cidade? filters=trim
    text estado? filters=trim
    bool padrao?
    int cliente_id?
  }

  stack {
    db.add_or_edit CEP {
      field_name = "cep"
      field_value = $input.cep
      enforce_hidden_fields = false
      data = {
        cep   : $input.cep
        cidade: $input.cidade
        uf    : $input.estado
      }
    } as $cep_record
  
    db.edit ENDERECO {
      field_name = "id"
      field_value = $input.endereco_id
      enforce_hidden_fields = false
      data = {
        cliente_id : $input.cliente_id
        logradouro : $input.logradouro
        numero     : $input.numero
        complemento: $input.complemento
        bairro     : $input.bairro
        referencia : $input.referencia
        cep_id     : $cep_record.id
        padrao     : $input.padrao
      }
    } as $endereco_atualizado
  }

  response = {
    logradouro : $endereco_atualizado.logradouro
    numero     : $endereco_atualizado.numero
    complemento: $endereco_atualizado.complemento
    bairro     : $endereco_atualizado.bairro
    referencia : $endereco_atualizado.referencia
    padrao     : $endereco_atualizado.padrao
    cliente_id : $endereco_atualizado.cliente_id
    cep        : ```
      {
        cep_id: $cep_record.id
        cidade: $cep_record.cidade
        estado: $cep_record.uf
      }
      ```
  }

  guid = "0T-9kPpwTIEcJvoK5ps6LfKXawU"
}
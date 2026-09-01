query consultaEnderecoDoCliente verb=GET {
  api_group = "ApiPersonalizadas"

  input {
    text authtoken? filters=trim
  }

  stack {
    api.request {
      url = "https://x8ki-letl-twmt.n7.xano.io/api:QwdDhaBT/buscaCliente"
      method = "GET"
      params = {authtoken: $input.authtoken}
      headers = [
        "Authorization: Bearer " ~$input.authtoken
        "Content-Type: application/json"
      ]
    
    } as $api1
  
    db.query ENDERECO {
      where = ( $var.api1.response.result.id ) == $db.ENDERECO.cliente_id
      return = {type: "list"}
      output = [
        "id"
        "created_at"
        "cliente_id"
        "logradouro"
        "numero"
        "complemento"
        "bairro"
        "referencia"
        "padrao"
      ]
    
      addon = [
        {name: "CEP", input: {CEP_id: $output.cep_id}, as: "_cep"}
      ]
    } as $ENDERECO1
  }

  response = $ENDERECO1
  guid = "zgENkhIpa2rfAyicfRmi1TXib64"
}
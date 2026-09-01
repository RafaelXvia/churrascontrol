query salvaEndereco verb=POST {
  api_group = "ApiPersonalizadas"

  input {
    text logradouro? filters=trim
    text numero? filters=trim
    text complemento? filters=trim
    text referencia? filters=trim
    text cep? filters=trim
    text cidade? filters=trim
    text uf? filters=trim
    bool padrao?
    int cliente_id?
    text bairro? filters=trim
  }

  stack {
    api.request {
      url = "https://x8ki-letl-twmt.n7.xano.io/api:QwdDhaBT/UpsertCEP"
      method = "POST"
      params = {cep: $input.cep, cidade: $input.cidade, uf: $input.uf}
      headers = ["Content-Type: application/json"]
    } as $api1
  
    api.request {
      url = "https://x8ki-letl-twmt.n7.xano.io/api:wU5v4o31/endereco"
      method = "POST"
      params = {
        logradouro : $input.logradouro
        numero     : $input.numero
        complemento: $input.complemento
        referencia : $input.referencia
        bairro     : $input.bairro
        padrao     : $input.padrao
        cliente_id : $input.cliente_id
        cep_id     : $api1.response.result.id
      }
    
      headers = ["Content-Type: application/json"]
    } as $api2
  }

  response = {
    logradouro : $api2.response.result.logradouro
    numero     : $api2.response.result.numero
    complemento: $api2.response.result.complemento
    referencia : $api2.response.result.referencia
    bairro     : $api2.response.result.bairro
    padrao     : $api2.response.result.padrao
    cliente_id : $api2.response.result.cliente_id
    cep        : ```
      {
        "cep_id": $var.api1.response.result.id,
        "cidade": $var.api1.response.result.cidade,
        "uf": $var.api1.response.result.uf
      }
      ```
  }

  guid = "AewStAh0nrSpi5GaY8ckwTlYPzM"
}
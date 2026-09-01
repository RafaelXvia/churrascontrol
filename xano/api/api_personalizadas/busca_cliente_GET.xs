query buscaCliente verb=GET {
  api_group = "ApiPersonalizadas"

  input {
    text authtoken? filters=trim
  }

  stack {
    api.request {
      url = "https://x8ki-letl-twmt.n7.xano.io/api:50i3eKwR/auth/me"
      method = "GET"
      headers = [
        "Authorization: Bearer " ~ $input.authtoken
        "Content-Type: application/json"
      ]
    } as $api1
  
    conditional {
      if ($api1.response.status == 200) {
        // Removidas as aspas e o $var para acessar o objeto corretamente
        db.get CLIENTE {
          field_name = "user_id"
          field_value = $api1.response.result.id
        } as $CLIENTE1
      }
    
      else {
        var $CLIENTE1 {
          value = {}
        }
      }
    }
  }

  response = $CLIENTE1
  guid = "d8qBcTq6s5BdaiHiovtI28rby2A"
}
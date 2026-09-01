// Resposta limpa e organizada
query cadastraCliente verb=POST {
  api_group = "ApiPersonalizadas"

  input {
    text nome? filters=trim
    text email? filters=trim
    text senha? filters=trim
    text celular? filters=trim
    text cpf? filters=trim
    text status? filters=trim
    text papel? filters=trim
  }

  stack {
    // Validação de segurança da senha
    precondition (($input.senha|strlen) >= 8) {
      error_type = "inputerror"
      error = "A senha deve ter pelo menos 8 caracteres."
    }
  
    precondition ("/.*[a-zA-Z].*/"|regex_matches:$input.senha) {
      error_type = "inputerror"
      error = "A senha deve conter pelo menos uma letra."
    }
  
    precondition ("/.*\\d.*/"|regex_matches:$input.senha) {
      error_type = "inputerror"
      error = "A senha deve conter pelo menos um número."
    }
  
    // Define IDs padrão
    var $status_id {
      value = 1
    }
  
    var $papel_id {
      value = 6
    }
  
    // Busca o ID do status pelo nome
    conditional {
      if ($input.status != null) {
        db.get STATUS_CLIENTE {
          field_name = "status"
          field_value = $input.status
        } as $status_record
      
        precondition ($status_record != null) {
          error_type = "inputerror"
          error = "O status fornecido não foi encontrado."
        }
      
        var.update $status_id {
          value = $status_record.id
        }
      }
    }
  
    // Busca o ID do papel pelo nome (ex: admin, cozinheiro, etc)
    conditional {
      if ($input.papel != null) {
        db.get PAPEL {
          field_name = "papel"
          field_value = $input.papel
        } as $papel_record
      
        precondition ($papel_record != null) {
          error_type = "inputerror"
          error = "O papel fornecido não foi encontrado."
        }
      
        var.update $papel_id {
          value = $papel_record.id
        }
      }
    }
  
    // Adiciona o registro na tabela local 'user'
    db.add user {
      enforce_hidden_fields = false
      data = {
        name    : $input.nome
        email   : $input.email
        password: $input.senha
        papel_id: $papel_id
      }
    } as $local_user
  
    // Gera o token de autenticação
    security.create_auth_token {
      table = "user"
      extras = {}
      expiration = 86400
      id = $local_user.id
    } as $authToken
  
    // Adiciona o registro na tabela 'CLIENTE' vinculando ao id do 'user'
    db.add CLIENTE {
      enforce_hidden_fields = false
      data = {
        created_at       : "now"
        user_id          : $local_user.id
        celular          : $input.celular
        cpf              : $input.cpf
        status_cliente_id: $status_id
      }
    } as $CLIENTE1
  }

  response = {
    user     : ```
      {
        id   : $local_user.id
        name : $local_user.name
        email: $local_user.email
        papel: $input.papel
      }
      ```
    cliente  : $CLIENTE1
    authToken: $authToken
  }

  guid = "yrbpYj2hQcTEyBKYvN0VwSzy0Kw"
}
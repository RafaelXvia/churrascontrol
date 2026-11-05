query colaborador verb=POST {
  api_group = "ChurrasControl"
  input {
    text nome filters=trim
    text email filters=trim|lower
    text numero filters=trim
    text cargo filters=trim
    text senha_hash filters=trim
    bool? primeiro_acesso?=true
    bool? ativo?=true
  }
  stack {
    db.query colaborador {
      where  = ($db.colaborador.email == $input.email)
      return = {type: "single"}
    } as $existente

    conditional {
      if ($existente != null) {
        db.patch colaborador {
          field_name  = "id"
          field_value = $existente.id
          data = {
            nome            : $input.nome,
            numero          : $input.numero,
            cargo           : $input.cargo,
            senha_hash      : $input.senha_hash,
            primeiro_acesso : $input.primeiro_acesso,
            ativo           : $input.ativo
          }
        } as $colab_salvo
      }
      else {
        db.add colaborador {
          enforce_hidden_fields = false
          data = {
            created_at      : "now",
            nome            : $input.nome,
            email           : $input.email,
            numero          : $input.numero,
            cargo           : $input.cargo,
            senha_hash      : $input.senha_hash,
            primeiro_acesso : $input.primeiro_acesso,
            ativo           : $input.ativo
          }
        } as $colab_salvo
      }
    }
  }
  response = {
    status : "ok",
    id     : $colab_salvo.id
  }
  guid = "3GMWw7-zyum2UFPgCvG-fqj8s3c"
}

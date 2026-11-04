query "colaborador/{colaborador_id}" verb=PATCH {
  api_group = "ChurrasControl"
  input {
    int colaborador_id
    text? senha_hash filters=trim
    bool? primeiro_acesso
    bool? ativo
  }
  stack {
    db.edit colaborador {
      field_name = "id"
      field_value = $input.colaborador_id
      data = {
        senha_hash      : $input.senha_hash,
        primeiro_acesso : $input.primeiro_acesso,
        ativo           : $input.ativo
      }
    } as $colaborador_atualizado
  }
  response = {
    status: "ok",
    id    : $colaborador_atualizado.id
  }
  guid = "NVnA5nTZvXw2G_13W3Tjb4t5ELo"
}

// Esta API lista todos os funcionários da empresa.
// Filtra usuários cujo papel_id NÃO seja o ID do papel "Cliente".
// Retorna todos os dados do usuário, com o nome do papel no campo papel_id.
query busca_funcionario verb=GET {
  api_group = "ApiPersonalizadas"

  input {
  }

  stack {
    // Buscamos o ID do papel "Cliente" na tabela PAPEL
    db.query PAPEL {
      where = ($db.PAPEL.papel == "Cliente")
      return = {type: "single"}
    } as $cliente_role
  
    // Buscamos os usuários na tabela user
    // Filtramos para ignorar quem for "Cliente" e garantir que possuam um papel (papel_id não nulo)
    db.query user {
      join = {
        papel: {table: "PAPEL", where: ($db.user.papel_id == $db.papel.id)}
      }
    
      where = ($db.user.papel_id != $cliente_role.id && $db.user.papel_id != null)
      eval = {papel_id: $db.papel.papel}
      return = {type: "list"}
    } as $funcionarios
  }

  response = $funcionarios
  guid = "9JJTiSfaau7UE3QZ-HxCD4IUaqg"
}
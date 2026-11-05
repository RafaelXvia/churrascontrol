query mesas_ativas verb=GET {
  api_group = "ChurrasControl"
  input {
  }
  stack {
    db.query mesas {
      where = ($db.mesas.status == "OCUPADA" || $db.mesas.status == "CONTA")
      sort = {mesas.numero_mesa: "asc"}
      return = {type: "list"}
    } as $mesas_lista

    array.map ($mesas_lista) {
      by = {
        id         : $this.id,
        numero_mesa: $this.numero_mesa,
        capacidade : $this.capacidade,
        status     : $this.status,
        comanda_id : $this.id,
        total_atual: 0.00
      }
    } as $mesas_formatadas
  }
  response = $mesas_formatadas
  guid = "pLsvyGc2Gcg1cAZw4opfDWkMUW0"
}
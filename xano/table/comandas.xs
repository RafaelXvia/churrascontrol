table comandas {
  auth = false
  schema {
    int id
    timestamp created_at?=now { visibility = "private" }
    int? mesa_id { table = "mesas" }
    int numero_mesa_historico
    timestamp data_abertura?=now
    timestamp? data_fechamento
    enum status?="ABERTA" {
      values = ["ABERTA", "PAGA", "CANCELADA"]
    }
    bool taxa_servico?=true
    int qtd_pessoas?=1
    decimal valor_total?=0.00
  }
  index = [
    { type: "primary", field: [{ name: "id" }] },
    { type: "btree", field: [{ name: "data_fechamento", op: "desc" }] }
  ]
  guid = "79D-sgV1FC8mAV5e6dyvSF3oTwM"
}
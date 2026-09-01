table mesas {
  auth = false
  schema {
    int id
    timestamp created_at?=now { visibility = "private" }
    int numero_mesa
    int capacidade?=4
    enum status?="LIVRE" {
      values = ["LIVRE", "OCUPADA", "CONTA"]
    }
  }
  index = [
    { type: "primary", field: [{ name: "id" }] },
    { type: "btree|unique", field: [{ name: "numero_mesa", op: "asc" }] }
  ]
  guid = "mzyqnseG9N4V9eh0r1PbY_0obRI"
}
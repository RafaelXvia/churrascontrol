## 1. Documentação de Domínio e Arquitetura

- [x] 1.1 Criar o arquivo `docs/project-overview.md` definindo escopo, problemas de negócio e atores do ChurrasControl.
- [x] 1.2 Criar o arquivo `docs/domain-model.md` com a especificação das entidades Mesa, Produto, Comanda e ItemComanda.
- [x] 1.3 Estabelecer formalmente a regra de imutabilidade de consumo histórico na comanda.

## 2. Modelagem Relacional no Xano

- [x] 2.1 Criar schemas das tabelas em `xano/table/`: `mesas.xs`, `comandas.xs`, `itens_comanda.xs` e `produto.xs`.
- [x] 2.2 Configurar campos de relacionamento `mesa_id`, `comanda_id` e atributos de auditoria contábil.
- [x] 2.3 Exportar definições auxiliares de entidades do ecossistema Xano (`cliente.xs`, `user.xs`, `pedido.xs`).

## 3. Validação e Verificação

- [x] 3.1 Revisar consistência dos tipos de dados e nulabilidade entre a documentação de domínio e os esquemas Xano.
- [x] 3.2 Validar conformidade com as diretrizes da disciplina Innovation Lab e princípios SDD do OpenSpec.

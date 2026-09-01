## Why

Início oficial do projeto ChurrasControl na disciplina Innovation Lab: Advanced No/Low Code (13/09/2026). Para sustentar as operações de automação de salão, gestão de comandas e fechamento financeiro, é imperativo definir a modelagem conceitual de domínio do sistema e implementar os schemas relacionais no backend No-Code (Xano), garantindo integridade referencial e imutabilidade dos registros contábeis de consumo.

## What Changes

- **Documentação de Domínio e Arquitetura**:
  - Elaboração de `docs/project-overview.md` estabelecendo visão geral, atores (Garçom, Caixa, Administrador), escopo e stack tecnológica.
  - Elaboração de `docs/domain-model.md` especificando as entidades `Mesa`, `Produto`, `Comanda` e `ItemComanda`, com suas regras estruturais e de imutabilidade.
- **Modelagem Relacional no Xano**:
  - Definição dos schemas das tabelas em formato Script Xano (`.xs`): `mesas.xs`, `comandas.xs`, `itens_comanda.xs`, `produto.xs`, `cliente.xs`, `user.xs`, `pedido.xs`.
  - Configuração de campos chave: `numero_mesa`, `capacidade`, `status` para mesas; `mesa_id`, `numero_mesa_historico`, `data_abertura`, `status`, `taxa_servico`, `valor_total` para comandas; `preco_momento`, `nome_produto_historico`, `quantidade`, `observacao` para itens da comanda; `codigo_pdv`, `nome`, `categoria`, `preco_unitario` para produtos.
- **Regra de Imutabilidade Histórica**:
  - Estabelecimento do princípio pelo qual itens lançados em comanda preservam o preço e denominação vigentes no instante do pedido, tornando o fechamento independente de alterações cadastrais futuras no catálogo.

## Capabilities

### New Capabilities
- `modelagem-dados-e-schemas-xano`: Especificação formal das entidades de domínio e schemas de dados no Xano para sustentação de todas as operações do ChurrasControl.

### Modified Capabilities

## Impact

- `docs/project-overview.md`: Definição de escopo, atores e arquitetura de sistema.
- `docs/domain-model.md`: Formalização dos relacionamentos e imutabilidade do modelo de negócio.
- `xano/table/`: Criação dos esquemas de dados relacionais para o backend No-Code.

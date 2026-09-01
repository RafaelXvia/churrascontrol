# catalogo-produtos-e-codigo-pdv Specification

## Purpose
Gerenciar o catálogo comercial de produtos do ChurrasControl, assegurando unicidade e integridade dos códigos de identificação rápida de venda (PDV), categorização gastronômica e busca multi-campo de alta velocidade.

## Requirements

### Requirement: Criação e Unicidade de Código PDV
O sistema SHALL disponibilizar a operação `criar_produto(codigo_pdv, nome, categoria, preco_unitario)` que valida se o `codigo_pdv` fornecido já está cadastrado em outro produto, rejeitando duplicidades com `ValueError` e atribuindo identificador numérico autoincremental através de `data["seq"]["produto_id"]`.

#### Scenario: Cadastro com código PDV conflitante
- **WHEN** o operador tenta cadastrar um produto utilizando um código PDV já existente
- **THEN** o sistema SHALL impedir a criação e retornar mensagem de erro indicando que o código já está em uso.

#### Scenario: Cadastro bem-sucedido de produto
- **WHEN** todos os campos obrigatórios forem preenchidos com código PDV inédito e preço positivo
- **THEN** o sistema SHALL gravar o novo produto no catálogo e retornar os dados consolidados.

### Requirement: Busca Flexível Multi-Atributo
O sistema SHALL disponibilizar `listar_produtos(busca)` retornando todos os produtos quando o parâmetro for nulo, ou filtrando itens onde o termo digitado coincida parcialmente com `nome`, `categoria` ou `codigo_pdv`.

#### Scenario: Pesquisa por código numérico ou parte do nome
- **WHEN** o operador digita "Feijoada" ou o código "3" no campo de busca
- **THEN** o sistema SHALL retornar imediatamente os produtos correspondentes para seleção rápida.

### Requirement: Atualização e Exclusão no Catálogo
O sistema SHALL permitir editar nome, categoria, código e preço de produtos existentes via `atualizar_produto(produto_id, ...)`, e desativar produtos através de `excluir_produto(produto_id)`.

#### Scenario: Reajuste cadastral de preço
- **WHEN** o preço de um produto cadastrado for atualizado pelo administrador
- **THEN** as consultas futuras ao cardápio SHALL refletir o novo valor unitário sem corromper pedidos já finalizados.

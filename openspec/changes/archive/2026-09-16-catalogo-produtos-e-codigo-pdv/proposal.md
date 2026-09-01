## Why

A agilidade do ponto de venda (PDV) e a assertividade dos pedidos dependem de um catálogo de produtos bem estruturado, com precificação precisa e identificação rápida por código de venda (`codigo_pdv`). Erros de lançamento causados por códigos duplicados ou dificuldades na busca de itens no cardápio geram lentidão no salão e falhas contábeis.

## What Changes

- **CRUD Completo de Produtos (`data_manager.py`)**:
  - Implementação de `criar_produto(codigo_pdv, nome, categoria, preco_unitario)` com verificação estrita de duplicidade de código PDV (`ValueError: Código PDV 'X' já cadastrado`).
  - Implementação de `listar_produtos(busca=None)` com busca multi-atributo insensível a maiúsculas/minúsculas abrangendo nome, categoria e código PDV.
  - Implementação de `atualizar_produto(produto_id, codigo_pdv, nome, categoria, preco_unitario)` para reajuste de preço e manutenção de dados.
  - Implementação de `excluir_produto(produto_id)` para remoção segura de itens do cardápio ativo.
- **Estruturação de Categorias Gastronômicas**:
  - Padronização das categorias comerciais: "Carnes", "Comida", "Entradas", "Bebidas", "Sobremesas", "Promoção" e "Geral".
- **Carga Inicial de Dados**:
  - Povoamento inicial de `churras_data.json` com pratos tradicionais de churrascaria e culinária mineira/brasileira (Feijoada, Tropeiro, Tutu à Mineira, Bambá de Couve, Carnes Nobres).

## Capabilities

### New Capabilities
- `catalogo-produtos-e-codigo-pdv`: Gestão de produtos comerciais, integridade de códigos PDV exclusivos e busca dinâmica para operação de vendas.

### Modified Capabilities

## Impact

- `data_manager.py`: Novas funções de CRUD e busca no catálogo de produtos.
- `churras_data.json`: Inicialização da coleção de produtos com IDs e códigos PDV padronizados.

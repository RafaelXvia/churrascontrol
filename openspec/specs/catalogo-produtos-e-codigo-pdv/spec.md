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
O sistema SHALL permitir editar nome, categoria, código, preço, descrição e foto de produtos existentes via `atualizar_produto(produto_id, ...)`, e desativar produtos através de `excluir_produto(produto_id)`.

#### Scenario: Reajuste cadastral de preço
- **WHEN** o preço de um produto cadastrado for atualizado pelo administrador
- **THEN** as consultas futuras ao cardápio SHALL refletir o novo valor unitário sem corromper pedidos já finalizados.

### Requirement: Layout Visual Gastronômico de Cardápio e Modais Interativos
A interface do Cardápio SHALL renderizar produtos em formato de cards visuais gastronômicos responsivos, contendo imagem ilustrativa, nome, código PDV, categoria, badges de identificação e preço formatado. Cada card SHALL permitir interação direta de clique que abre um diálogo modal (`@st.dialog`) para visualização, edição de dados cadastrais ou exclusão com confirmação sem requerer recarregamento completo da página (F5).

#### Scenario: Clique em card de produto
- **WHEN** o operador clica no card de um produto do cardápio
- **THEN** o sistema SHALL abrir o modal `@st.dialog("⚙️ Gerenciar Produto (Editar / Excluir)")` instantaneamente com abas de detalhes/edição e opção segura de exclusão.

#### Scenario: Cadastro via modal saltado
- **WHEN** o operador clica no botão "➕ Novo Produto" no cabeçalho do cardápio
- **THEN** o sistema SHALL exibir o modal saltado de cadastro com todos os atributos (código PDV, nome, categoria, preço, descrição e URL da imagem).

### Requirement: Sincronização Sob Demanda com Xano
A tela de Cardápio SHALL disponibilizar um botão de sincronização manual com o Xano (`🔄 Xano`) no cabeçalho, permitindo processar a fila local e forçar reconciliação bidirecional do catálogo de produtos com a API remota.

#### Scenario: Operador aciona sincronização manual
- **WHEN** o operador clica em `🔄 Xano` no topo do cardápio
- **THEN** o sistema SHALL invocar `sincronizar_com_xano()`, exibir o status do processamento (itens sincronizados ou falhas) e atualizar a visualização em tela.


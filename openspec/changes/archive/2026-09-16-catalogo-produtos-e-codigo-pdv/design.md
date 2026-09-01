## Context

Em ambientes de restaurante de alto giro, garçons e operadores de caixa utilizam códigos numéricos curtos (ex: "1", "105", "42") para memorizar e lançar produtos velozmente. Portanto, o sistema deve tratar o `codigo_pdv` como chave natural única, sem permitir colisões.

## Goals / Non-Goals

**Goals:**
- Prover operações completas de criação, leitura, atualização e exclusão (CRUD) de produtos no arquivo local.
- Impor validação em tempo real de unicidade de `codigo_pdv`.
- Viabilizar filtro textual instantâneo capaz de encontrar produtos por qualquer fragmento de seu nome, categoria ou código.
- Garantir que preços unitários sejam valores numéricos positivos.

**Non-Goals:**
- Lançamento dos produtos em comandas (tratado na change de itens de consumo).
- Interface de cardápio digital voltada para o cliente final.

## Decisions

- **Decisão 1: Busca em Memória com Baixa Latência**:
  - *Contexto*: Durante o atendimento, a busca por itens precisa retornar em milissegundos.
  - *Decisão*: Implementar o filtro diretamente em Python iterando sobre a lista deserializada em memória.
- **Decisão 2: Validação Case-Insensitive e Trim no Código PDV**:
  - *Contexto*: Evitar duplicidades causadas por espaços acidentais ou variações de caixa.
  - *Decisão*: Aplicar `.strip().lower()` na checagem de existência prévia do código.

## Risks / Trade-offs

- [Exclusão de Produtos Cadastrados] Excluir um produto não pode quebrar comandas passadas que já o continham → Mitigação: Como as comandas guardam `nome_produto_historico` e `preco_momento`, a remoção do produto do catálogo ativo não compromete relatórios contábeis históricos.

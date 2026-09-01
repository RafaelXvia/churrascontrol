## Context

O lançamento de pedidos em comandas de salão exige tolerância a pedidos frequentes e fragmentados (ex: pedir uma cerveja, dez minutos depois outra cerveja). Se o sistema criasse uma linha para cada cerveja individual sem agrupar, a visualização da conta ficaria ilegível para o cliente e para o caixa. Adicionalmente, proteger os dados contra reajustes de preço posteriores é essencial para conformidade fiscal e auditoria.

## Goals / Non-Goals

**Goals:**
- Acumular quantidade automaticamente em itens idênticos na mesma comanda.
- Gravar snapshot histórico dos dados do produto no momento exato do lançamento (`preco_momento`, `nome_produto_historico`).
- Oferecer campo flexível de observações para orientações de preparo.
- Permitir edição de itens lançados (ex: garçom errou a quantidade digitada).

**Non-Goals:**
- Fechamento financeiro da conta ou cobrança de taxa de serviço (tratado na change de fechamento e relatórios).
- Roteamento automatizado de pedidos para impressoras térmicas de cozinha.

## Decisions

- **Decisão 1: Acumulação de Quantidades por Comanda e Produto**:
  - *Contexto*: Evitar multiplicação desordenada de linhas idênticas.
  - *Decisão*: Antes de criar novo item, verificar `it["comanda_id"] == comanda_id and it["produto_id"] == produto_id`. Se existir, somar `quantidade`.
- **Decisão 2: Cópia Estática de Dados Comerciais**:
  - *Contexto*: Garantir que o valor total de uma comanda aberta ou encerrada nunca mude por alteração de preço no cardápio.
  - *Decisão*: Gravar `preco_momento` float e `nome_produto_historico` string diretamente no dicionário do item.

## Risks / Trade-offs

- [Itens Iguais com Observações Diferentes] Se o cliente pede 1 bife mal passado e depois 1 bife bem passado, a acumulação sobrescreveria a observação → Mitigação: O garçom pode utilizar a função de edição de item ou incluir a instrução combinada (ex: "1 mal passado, 1 bem passado").

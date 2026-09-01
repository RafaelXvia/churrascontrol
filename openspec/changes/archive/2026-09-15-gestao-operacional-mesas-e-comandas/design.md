## Context

Para que o salão opere sem atritos, é necessário um módulo com autoridade estrita sobre a ocupação de mesas. Duplicações acidentais de mesas ou falhas de sincronização no cancelamento geram prejuízos contábeis e confusão no atendimento dos clientes.

## Goals / Non-Goals

**Goals:**
- Fornecer operações em memória com persistência imediata em JSON local para abertura, listagem e cancelamento de mesas.
- Prevenir abertura duplicada de mesas com o mesmo número.
- Calcular em tempo real o subtotal de consumo da mesa somando os itens da comanda ativa.
- Manter histórico mesmo quando a mesa for liberada ou cancelada.

**Non-Goals:**
- Implementação de layouts visuais ou componentes Streamlit (tratados nas changes de frontend).
- Lançamento granular de itens individuais na comanda (tratado na change subsequente de consumo).

## Decisions

- **Decisão 1: Validação Síncrona Impeditiva de Duplicidade de Mesa**:
  - *Contexto*: Se dois operadores tentarem abrir a Mesa 5 ao mesmo tempo, apenas um deve obter sucesso.
  - *Decisão*: Levantar explicitamente `ValueError(f"Mesa {numero_mesa} já está aberta no salão.")` antes de criar o registro.
- **Decisão 2: Subtotal Dinâmico Calculado no `listar_mesas`**:
  - *Contexto*: Evitar inconsistência de total pré-calculado armazenado na entidade mesa.
  - *Decisão*: Calcular `total_atual` dinamicamente iterando sobre os `itens_comanda` vinculados à comanda ativa da mesa.

## Risks / Trade-offs

- [Concorrência de Arquivo] Múltiplas leituras e gravações simultâneas em disco poderiam corromper o JSON → Mitigação: Uso de `threading.Lock()` no `load_data()` e `save_data()`.

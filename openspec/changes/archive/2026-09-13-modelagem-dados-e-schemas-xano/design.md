## Context

O desenvolvimento do ChurrasControl exige fundações sólidas para suportar o fluxo completo de atendimento de salão em restaurantes e churrascarias. O backend No-Code (Xano) foi selecionado como a fonte primária de verdade em nuvem, exigindo modelagem explícita de schemas relacionais e documentação de domínio que sirva de guia para as implementações subsequentes guiadas por OpenSpec.

## Goals / Non-Goals

**Goals:**
- Mapear e documentar as entidades fundamentais do negócio (`Mesa`, `Produto`, `Comanda`, `ItemComanda`).
- Implementar as definições de tabelas correspondentes no diretório `xano/table/`.
- Garantir que itens de comanda salvem cópia histórica de atributos comerciais (`preco_momento`, `nome_produto_historico`).
- Registrar o domínio em `docs/domain-model.md` e a visão do produto em `docs/project-overview.md`.

**Non-Goals:**
- Implementar as telas visuais ou rotinas de sincronização em tempo real (etapas tratadas em changes futuras).
- Configurar autenticação OAuth ou serviços externos de pagamento neste primeiro estágio.

## Decisions

- **Decisão 1: Desacoplamento entre Mesa e Comanda Histórica**:
  - *Contexto*: Quando a comanda é finalizada com status `PAGA`, a mesa deve ser liberada imediatamente para novos clientes, sem que o histórico da comanda perca a informação de qual mesa ela atendeu.
  - *Decisão*: Manter um campo relacional `mesa_id` (anulado no fechamento) e um campo `numero_mesa_historico` permanente na comanda.
- **Decisão 2: Imutabilidade de Consumo**:
  - *Contexto*: Reajustes de preço no cardápio poderiam corromper relatórios financeiros retroativos.
  - *Decisão*: Gravar `preco_momento` e `nome_produto_historico` na tabela `itens_comanda`.

## Risks / Trade-offs

- [Consistência Eventual] O uso de uma base remota no Xano com limitação de requisições no plano gratuito exige que as operações do cliente não façam chamadas síncronas bloqueantes → Mitigação: Planejada camada de cache local e fila desacoplada em segundo plano.

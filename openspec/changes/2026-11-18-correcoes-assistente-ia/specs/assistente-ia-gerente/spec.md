## Purpose

Prover uma interface conversacional analitica e executiva de alta precisao contabil para o Gerente do restaurante ChurrasControl, respondendo perguntas sobre faturamento, desempenho por setor e turno, ranking de pratos, estoque critico e auditoria, com base em dados reais do SQLite guiados por Ontologia Relacional, ferramentas deterministicas, cascata resiliente de modelos LLM e total higiene de credenciais.

## MODIFIED Requirements

### Requirement: Fallback em Cascata de Provedor LLM (Multi-Key e Multi-Model Google Gemini)
O sistema SHALL implementar um roteador em cascata resiliente com duas chaves de API (`GOOGLE_API_KEY_1` e `GOOGLE_API_KEY_2`). A descoberta de modelos SHALL aceitar exclusivamente modelos iniciados por `gemini-` com suporte a `generateContent`, excluindo modelos de imagem, voz, audio, live, embedding, gemma, learnlm, robotics e computer-use. A classificacao de excecoes SHALL priorizar os atributos estruturados do SDK (`code`, `status_code`, `status`), avaliando erros 429/quota antes de 400, e utilizando analise textual apenas como reserva com word boundaries (`\b401\b`, `\b400\b`).

#### Scenario: Deteccao de cota diaria com cooldown estendido
- **WHEN** uma requisicao falhar por estouro de cota diaria (contendo termos como "PerDay" ou "daily")
- **THEN** o sistema SHALL aplicar o tempo de cooldown de cota diaria (`LLM_COOLDOWN_DAILY_QUOTA_SECONDS`, padrao 3600 segundos) para aquele modelo.

#### Scenario: Modelo incompativel com tools
- **WHEN** um modelo retornar erro 400 por nao suportar function calling ou system instruction
- **THEN** o sistema SHALL marcar o modelo como incompativel e seguir para o proximo modelo da fila. A cascata so SHALL ser interrompida se 2 modelos distintos confirmarem erro 400.

#### Scenario: Resposta vazia tratada como falha
- **WHEN** um modelo responder com texto vazio ou nulo
- **THEN** o sistema SHALL registrar a tentativa como falha e avancar imediatamente para o proximo modelo da cascata.

### Requirement: Resolução Semântica por Ontologia Relacional (Graph-over-SQLite)
O sistema SHALL disponibilizar uma camada de Ontologia Relacional que mapeia conceitos de negocio, turnos de atendimento sem sobreposicao (*Almoco*, *Happy Hour*, *Jantar*), setores fisicos (*Varanda*, *Salao Interno*, *Kids*) e regras de transicao de meia-noite e madrugada.

#### Scenario: Turnos operacionais sem sobreposicao
- **WHEN** consultas filtrarem por turno
- **THEN** a ontologia SHALL aplicar: Almoco (11:30:00 as 15:30:00), Happy Hour (17:00:00 as 18:29:59) e Jantar (18:30:00 as 23:59:59).

#### Scenario: Atribuicao de comandas da madrugada
- **WHEN** uma comanda for aberta entre 00:00:00 e 05:59:59
- **THEN** a ontologia SHALL atribuir contabilmente a comanda ao turno Jantar do dia anterior.

#### Scenario: Mapeamento de setor 100% via ontologia
- **WHEN** uma ferramenta analitica exibir o setor de uma mesa
- **THEN** ela SHALL consultar `ontologia.obter_setor_da_mesa` no banco de dados SQLite, atribuindo "Sem setor" caso a mesa nao possua setor mapeado.

### Requirement: Roteamento Semântico e Execução Determinística (RAG Estruturado)
Todas as ferramentas analiticas de vendas (`resumo_financeiro`, `ranking_mesas`, `ranking_produtos`, `vendas_por_categoria`, `evolucao_temporal`) SHALL aceitar simultaneamente os parametros `turno` e `setor`. O parametro `ignorar_demo` SHALL ser repassado via contexto thread-local, nao sendo exposto na assinatura apresentada ao modelo.

#### Scenario: Validacao estrita de filtros
- **WHEN** um turno ou setor informado nao for reconhecido pela ontologia
- **THEN** a ferramenta SHALL retornar erro claro com as opcoes validas, sem ignorar silenciosamente o filtro.

#### Scenario: Discriminacao de faturamento e receita de itens
- **WHEN** o assistente calcular o resumo financeiro ou vendas por categoria
- **THEN** ele SHALL apresentar expressamente o faturamento total das comandas (incluindo taxa de servico) e a receita de itens (quantidade vezes preco praticado), garantindo que a soma das categorias coincida com a receita de itens.

### Requirement: Higiene Estrita e Sanitizacao Centralizada de Credenciais
O sistema SHALL disponibilizar a funcao centralizada `sanitizar_texto(texto: str) -> str` que remove padroes de chaves de API (`AIza...`, `key=...`). A sanitizacao SHALL ser aplicada em todas as emissoes de log e em todas as mensagens exibidas na interface do usuario. Em falhas 400, o sistema SHALL emitir mensagem amigavel generica sem exibir detalhes brutos da requisicao.

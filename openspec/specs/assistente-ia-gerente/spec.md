## Purpose

Prover uma interface conversacional inteligente e de alta precisão contábil para o Gerente do restaurante, respondendo perguntas analíticas sobre faturamento, desempenho por mesa/setor, ranking de pratos, turnos, estoque e auditoria com base em dados reais do SQLite guiados por uma Ontologia Relacional de Domínio e ferramentas determinísticas.

## ADDED Requirements

### Requirement: Resolução Semântica por Ontologia Relacional (Graph-over-SQLite)
O sistema SHALL disponibilizar uma camada de Ontologia Relacional armazenada no SQLite que mapeia conceitos de negócio, sinônimos informais, turnos de atendimento (*Almoço*, *Jantar*, *Happy Hour*), setores físicos do salão (*Varanda*, *Salão Principal*, *Espaço Kids*) e axiomas contábeis, desambiguando as intenções do Gerente antes da execução de consultas financeiras.

#### Scenario: Tradução de setor físico para mesas correspondentes
- **WHEN** o Gerente pergunta "Como foi o faturamento na varanda ontem?"
- **THEN** a ontologia SHALL traduzir o conceito "varanda" para a lista exata de mesas físicas associadas (Mesas 1, 2, 3 e 4) e fornecer esses identificadores para a ferramenta analítica correspondente.

#### Scenario: Tradução de turno para intervalo de horas
- **WHEN** o Gerente pergunta "Vendemos mais carne no almoço ou no jantar de domingo?"
- **THEN** a ontologia SHALL mapear "almoço" para o intervalo `11:30 às 15:30` e "jantar" para `18:30 às 23:59`, permitindo comparação precisa de receitas entre os turnos.

#### Scenario: Resolução de sinônimos de cardápio
- **WHEN** o Gerente pergunta "Quantas geladas ou cervejinhas foram pedidas hoje?"
- **THEN** a ontologia SHALL mapear os termos informais para a classe "cerveja" e selecionar os produtos correspondentes no catálogo ("Chopp", "Cerveja Artesanal", "Long Neck").

### Requirement: Roteamento Semântico e Execução Determinística (RAG Estruturado)
O sistema SHALL disponibilizar um orquestrador analítico que recebe perguntas em linguagem natural do Gerente, identifica a intenção operacional com auxílio da ontologia, invoca exclusivamente ferramentas determinísticas em conexão somente-leitura com o SQLite e sintetiza a resposta sem efetuar cálculos matemáticos aproximados internamente no modelo de linguagem.

#### Scenario: Pergunta sobre faturamento de período
- **WHEN** o Gerente pergunta "Quanto faturamos no último fim de semana?"
- **THEN** o sistema SHALL resolver as datas exatas do período, acionar a ferramenta `resumo_financeiro`, somar apenas comandas com status `PAGA` e responder com o valor exato em Reais, quantidade de comandas e ticket médio apurados no banco.

#### Scenario: Pergunta sobre preferência de mesas e setores
- **WHEN** o Gerente pergunta "Quais mesas mais vendem ou onde os clientes mais gostam de sentar?"
- **THEN** o sistema SHALL acionar a ferramenta `ranking_mesas`, agregar o faturamento histórico e a contagem de atendimentos por `numero_mesa_historico` das comandas pagas e agrupar por setor do salão (Varanda vs Salão Principal).

#### Scenario: Pergunta sobre pratos mais vendidos
- **WHEN** o Gerente pergunta "Qual foi o prato mais vendido em setembro?"
- **THEN** o sistema SHALL acionar a ferramenta `ranking_produtos`, filtrar por período e ordenar os itens pelo somatório de `quantidade`, exibindo o total de unidades e a receita gerada a partir dos preços históricos (`preco_momento`).

#### Scenario: Pergunta sobre itens com estoque crítico
- **WHEN** o Gerente pergunta "Tem algum produto acabando ou com estoque baixo?"
- **THEN** o sistema SHALL acionar a ferramenta `estoque_critico`, consultar `produtos` com `qtd_disp <= 5` ou `disponivel = 0` e listar os itens com a quantidade restante e indicação se necessita produção.

### Requirement: Fallback em Cascata de Provedor LLM (Multi-Key e Multi-Model Google Gemini)
O sistema SHALL implementar um mecanismo resiliente de roteamento em cascata com duas chaves de API do Google Gemini (`GOOGLE_API_KEY_1` e `GOOGLE_API_KEY_2`), lidas exclusivamente de variáveis de ambiente. O sistema SHALL descobrir dinamicamente na inicialização os modelos suportados por cada chave (filtrando modelos que suportem `generateContent` e chamadas de ferramentas / *function calling*) e encadear a execução primeiro por todos os modelos elegíveis da Chave 1 e, sucessivamente, por todos os modelos elegíveis da Chave 2. Chaves de API NUNCA SHALL ser persistidas em código, arquivos de especificação, banco de dados SQLite, logs de execução ou exibidas na interface.

#### Scenario: Descoberta dinâmica de modelos na inicialização
- **WHEN** o serviço do assistente de IA é inicializado
- **THEN** o sistema SHALL consultar a API do Google GenAI para `GOOGLE_API_KEY_1` e `GOOGLE_API_KEY_2`, filtrar apenas os modelos com capacidade de `generateContent` e suporte a chamadas de ferramentas (*function calling*), e montar a fila de cascata priorizando todos os modelos elegíveis da Chave 1 seguidos por todos os modelos elegíveis da Chave 2.

#### Scenario: Fallback automático após erro de rate limit (429) ou cota na Chave 1
- **WHEN** uma requisição enviada ao modelo ativo da Chave 1 falha com erro 429 (Too Many Requests), estouro de cota, timeout, erro 5xx, indisponibilidade ou erro de API
- **THEN** o sistema SHALL colocar o modelo com falha em cooldown curto temporário, avançar imediatamente para o próximo modelo da fila em cascata e repetir a requisição com o mesmo contexto e ferramentas determinísticas.

#### Scenario: Transição para Chave 2 após esgotamento da Chave 1
- **WHEN** todos os modelos elegíveis associados à `GOOGLE_API_KEY_1` falham ou esgotam suas cotas/limites
- **THEN** o sistema SHALL alternar transparentemente para os modelos mapeados sob a `GOOGLE_API_KEY_2`, continuando a cascata sem perda de contexto da conversa e sem intervenção do usuário.

#### Scenario: Cooldown temporário de modelos com falha
- **WHEN** um modelo de IA falha durante uma chamada operacional
- **THEN** o sistema SHALL marcar o modelo em estado de cooldown por um período breve (evitando novas requisições imediatas contra um endpoint com limite estourado) e reabilitá-lo automaticamente após a expiração do intervalo.

#### Scenario: Esgotamento total da cascata de modelos
- **WHEN** todas as tentativas em todos os modelos e chaves configuradas falham
- **THEN** o sistema SHALL exibir uma mensagem amigável e explicativa ao Gerente informando a indisponibilidade momentânea do serviço de IA, sem gerar cálculos aproximados ou inventar respostas numéricas (*zero alucinação / fail-safe*).

#### Scenario: Higiene estrita de chaves de API
- **WHEN** o sistema carrega, executa ou registra eventos das APIs de LLM
- **THEN** o sistema SHALL ler as credenciais exclusivamente de `GOOGLE_API_KEY_1` e `GOOGLE_API_KEY_2` em tempo de execução e NUNCA SHALL gravar valores brutos de chaves em código, arquivos de spec, banco de dados SQLite, logs de console/disco ou payloads de interface.

### Requirement: Painel de Transparência e Evidência ("Como Calculei")
O sistema SHALL acompanhar cada resposta do assistente com metadados auditáveis contendo os conceitos ontológicos resolvidos, a ferramenta acionada, os parâmetros temporais aplicados, o tempo de execução, a identificação opaca da API utilizada ("Chave 1" ou "Chave 2", omitindo expressamente o valor secreto da chave), o nome do modelo que concluiu a resposta, a contagem de tentativas que falharam na cascata e a listagem tabular das linhas do banco utilizadas para compor o resultado.

#### Scenario: Inspeção das evidências da resposta e telemetria de LLM
- **WHEN** o Gerente expande o painel "Como calculei" da mensagem gerada
- **THEN** o sistema SHALL exibir o intervalo de datas considerado, a ferramenta invocada, as traduções ontológicas aplicadas, a identificação da API utilizada (apenas "Chave 1" ou "Chave 2", sem valor de chave), o nome do modelo que respondeu com sucesso, a contagem de tentativas que falharam até a conclusão e a tabela estruturada correspondente aos registros retornados pelo SQLite.

### Requirement: Controle de Acesso Estrito (RBAC) e Isolamento
A funcionalidade do Assistente IA SHALL estar disponível unicamente para usuários autenticados com cargo `gerente`. O sistema SHALL bloquear o acesso de colaboradores com perfil `caixa` ou acessos não autenticados.

#### Scenario: Tentativa de acesso por operador de caixa
- **WHEN** um colaborador com cargo `caixa` tenta acessar a tela do Assistente IA
- **THEN** o sistema SHALL bloquear o acesso imediatamente, exibir mensagem de restrição de permissão e redirecionar para `pages/1_Salao_e_Mesas.py`.

### Requirement: Isolamento da Fila de Sincronização Xano
As interações, conversas, mensagens do Assistente IA e logs locais de tentativas/falhas de chamadas LLM SHALL ser persistidas localmente no SQLite e NUNCA SHALL ser enviadas para a `fila_sincronizacao` ou disparadas para o backend do Xano, preservando a cota de requisições da nuvem.

#### Scenario: Registro de mensagem de chat e telemetria de fallback
- **WHEN** uma mensagem é enviada ou respondida no assistente, ou ocorrem tentativas de fallback do LLM
- **THEN** os registros SHALL ser gravados exclusivamente nas tabelas locais de chat e auditoria do SQLite (`chat_conversas`, `chat_mensagens`, `llm_fallback_logs`) sem gerar qualquer entrada com status `PENDENTE` na tabela `fila_sincronizacao`.

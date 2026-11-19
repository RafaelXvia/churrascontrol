## Purpose

Prover uma interface conversacional inteligente e de alta precisao contabil para o Gerente do restaurante, respondendo perguntas analiticas sobre faturamento, desempenho por mesa/setor, ranking de pratos, turnos, estoque e auditoria com base em dados reais do SQLite guiados por uma Ontologia Relacional de Dominio, ferramentas deterministicas, cascata resiliente de modelos LLM e gerenciamento visual corporativo de sessoes.

## MODIFIED Requirements

### Requirement: Fallback em Cascata de Provedor LLM (Multi-Key e Multi-Model Google Gemini)
O sistema SHALL implementar um mecanismo resiliente de roteamento em cascata com duas chaves de API do Google Gemini (`GOOGLE_API_KEY_1` e `GOOGLE_API_KEY_2`), lidas exclusivamente de variáveis de ambiente. O sistema SHALL ordenar os modelos descobertos segundo prioridade configurável via `GEMINI_MODELS_PREFERENCE` (ou padrão documentado com modelos rápidos e estáveis primeiro), classificar os erros distinguindo falhas transientes (429/5xx), erros de autenticação da chave (401/403) e requisições malformadas (400), e aplicar cooldown proporcional respeitando tempos de retry quando fornecidos pelo provedor.

#### Scenario: Prioridade configurável de modelos na descoberta
- **WHEN** o sistema descobre os modelos disponíveis para cada chave
- **THEN** ele SHALL ordenar a fila de modelos aplicando a lista de preferências especificada na variável de ambiente `GEMINI_MODELS_PREFERENCE` ou, na sua ausência, priorizando modelos estáveis rápidos com function calling (`gemini-2.5-flash`, `gemini-3.7-flash`, `gemini-2.0-flash`), seguidos por contingência leve (`gemini-1.5-flash`), modelos Pro (`gemini-2.5-pro`, `gemini-3.7-pro`) e modelos experimentais por último.

#### Scenario: Detecção de chave inválida e avanço imediato para a próxima chave
- **WHEN** uma chamada de API retorna erro de autenticação, chave inválida ou falta de permissão (códigos 401, 403, `API_KEY_INVALID`, `CONSUMER_SUSPENDED`)
- **THEN** o sistema SHALL desativar imediatamente todos os modelos daquela chave, emitir aviso opaco e transparente no resultado e prosseguir diretamente para a próxima chave configurada, sem tentar os outros modelos da chave inválida.

#### Scenario: Interrupção imediata em requisição malformada
- **WHEN** uma chamada de API retorna erro de requisição malformada do cliente (código 400 ou erro de schema não ligado a credenciais)
- **THEN** o sistema SHALL interromper a cascata imediatamente sem tentar outros modelos ou chaves, registrar o motivo em `llm_fallback_logs` e informar o erro de formato ao usuário.

#### Scenario: Cooldown respeitando Retry-After
- **WHEN** uma requisição falha com 429 ou erro temporário e contém indicação de tempo de retry
- **THEN** o sistema SHALL aplicar o cooldown baseado no tempo informado ou no valor configurado em `LLM_COOLDOWN_TRANSIENT_SECONDS`, evitando requisições precipitadas.

### Requirement: Resolução Semântica por Ontologia Relacional (Graph-over-SQLite)
O sistema SHALL disponibilizar uma camada de Ontologia Relacional armazenada no SQLite que mapeia conceitos de negócio, sinônimos informais, turnos de atendimento (*Almoço*, *Jantar*, *Happy Hour*), setores físicos do salão (*Varanda*, *Salão Interno*, *Kids*), regras de transição de meia-noite e axiomas contábeis.

#### Scenario: Formalização do turno Happy Hour
- **WHEN** o Gerente pergunta sobre vendas ou consumo no Happy Hour
- **THEN** a ontologia SHALL aplicar o intervalo formal de `17:00 às 19:30`.

#### Scenario: Comandas que cruzam a meia-noite
- **WHEN** uma comanda foi aberta antes da meia-noite (ex: 23:45) e encerrada na madrugada seguinte
- **THEN** o turno e a data contábil da comanda SHALL ser atribuídos estritamente com base na `data_abertura` da comanda.

#### Scenario: Alinhamento de setores e sinônimos
- **WHEN** o Gerente menciona qualquer variação de setor ("varanda", "lá fora", "deck", "salão principal", "interno", "espaço kids", "área kids")
- **THEN** a ontologia SHALL mapear com precisão para os setores oficiais: Varanda (mesas 1 a 4), Salão Interno (mesas 5 a 8) e Kids (mesas 9 e 10).

## ADDED Requirements

### Requirement: Tratamento de Ambiguidades e Consultas Vazias
O sistema SHALL adotar premissas determinísticas para perguntas ambíguas sem período ou setor especificado, declarar a premissa adotada na resposta e tratar consultas sem dados de forma explícita.

#### Scenario: Pergunta sem período definido
- **WHEN** o Gerente faz uma pergunta genérica sem explicitar datas (ex: "Qual o faturamento?")
- **THEN** o assistente SHALL assumir a premissa de "Hoje" (ou "Últimos 7 dias" para comparativos/rankings), declarar expressamente no texto a premissa adotada e registrá-la no painel "Como calculei".

#### Scenario: Consulta com zero registros
- **WHEN** uma ferramenta determinística retorna zero linhas para os filtros informados
- **THEN** o assistente SHALL informar com clareza que nenhum registro foi encontrado, sem inventar valores ou criar estimativas.

### Requirement: Segregação e Filtro de Vendas de Demonstração
O sistema SHALL segregar vendas simuladas geradas para teste daquelas geradas por operação real, através da coluna `is_demo` na tabela `comandas`, permitindo filtrar ou incluir dados demo sob comando do Gerente.

#### Scenario: Marcação de vendas demo
- **WHEN** o script de geração de dados de demonstração (`seed_vendas_demo.py`) executa
- **THEN** todas as comandas geradas SHALL ser gravadas com `is_demo = 1`.

#### Scenario: Filtro padrão nas ferramentas do assistente
- **WHEN** o assistente consulta faturamento, mesas ou rankings
- **THEN** ele SHALL por padrão considerar apenas comandas com `is_demo = 0`, a menos que o parâmetro de inclusão de demonstração esteja ativado.

### Requirement: Gerenciador de Conversas e Redesign Visual
A interface do Assistente IA SHALL fornecer gerenciador lateral de conversas com opções de criação, renomeação, exclusão e geração automática de título descritivo, além de exibição de gráficos nativos leves e painel de auditoria estruturado.

#### Scenario: Gerenciador lateral de conversas
- **WHEN** o Gerente acessa a tela do Assistente IA
- **THEN** ele SHALL visualizar a lista lateral com as conversas existentes, botão para nova conversa, opção de renomear título e exclusão com confirmação.

#### Scenario: Título automático sintetizado
- **WHEN** uma nova conversa recebe a primeira pergunta do Gerente
- **THEN** o sistema SHALL sintetizar automaticamente um título curto e relevante baseado no tema da pergunta, substituindo títulos genéricos.

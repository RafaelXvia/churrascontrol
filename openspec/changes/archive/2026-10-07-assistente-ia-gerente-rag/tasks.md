## 1. Fundação de Dados, Ontologia e Preservação de Histórico

- [x] 1.1 Corrigir exclusão indevida de itens de comandas pagas no `init_db()` em `data_manager.py` e isolar ambiente de testes por `CHURRAS_DB_PATH` (verificado com `tools/test_suite.py`).
- [x] 1.2 Implementar tabelas da Ontologia Relacional (`ontologia_conceitos`, `ontologia_sinonimos`, `ontologia_relacoes`), tabelas de chat (`chat_conversas`, `chat_mensagens`) e tabela local de telemetria de tentativas (`llm_fallback_logs`) no `init_db()` de `data_manager.py`, com índices direcionados e sem sincronização com o Xano (verificar com `python tools/db_diagnostics.py`).
- [x] 1.3 Criar rotina de seed ontológico padrão do restaurante em `ontologia.py`: setores (Varanda: Mesas 1..4, Salão Interno: Mesas 5..8, Kids: Mesas 9..10), turnos (Almoço, Jantar, Happy Hour) e sinônimos de cardápio (verificar consulta de triplas ontológicas via script de teste).
- [x] 1.4 Adicionar dependências `google-genai`, `pydantic` e `python-dotenv` ao `requirements.txt` (verificar instalação e importação limpa via script Python).
- [x] 1.5 Criar script de geração de massa de dados realista `tools/seed_vendas_demo.py` com 60 dias de histórico contendo mesas 1..10, comandas pagas com itens variados, distribuição por turnos de almoço/jantar e setores do salão (verificar com contagem de comandas em `tools/db_diagnostics.py`).

## 2. Motor Ontológico e Catálogo de Ferramentas (Backend RAG)

- [x] 2.1 Criar módulo `ontologia.py` com motor de inferência relacional:
  - `resolver_termo(termo)`: mapeamento de sinônimos para conceitos formais.
  - `obter_mesas_por_setor(setor)`: retorno da lista de números de mesas físicas de um setor.
  - `obter_intervalo_turno(turno)`: retorno do range de horários (início e fim) de um turno.
  - `obter_produtos_por_conceito(conceito)`: expansão de termos genéricos (ex: "churrasco") para itens do catálogo.
  - `obter_subclasses(conceito)`: expansão transitiva de subclasses via predicado `subclasse_de`.
  (verificar cada função com asserções diretas).
- [x] 2.2 Criar módulo `assistente_ia.py` com gerenciador de conexão somente-leitura ao SQLite (`mode=ro`) e esquemas Pydantic para validação de filtros temporais e ontológicos.
- [x] 2.3 Implementar ferramentas analíticas determinísticas em `assistente_ia.py`:
  - `resumo_financeiro(inicio, fim, turno?)`: faturamento bruto, contagem de comandas pagas, ticket médio e ticket por pessoa.
  - `ranking_mesas(inicio, fim, setor?, limite)`: mesas físicas mais rentáveis e mais frequentadas, com agrupamento por setor do salão (Varanda vs Salão Interno).
  - `ranking_produtos(inicio, fim, conceito_ontologico?, limite)`: pratos e bebidas mais vendidos e receita por produto.
  - `vendas_por_categoria(inicio, fim)`: distribuição de receita por categoria de produto.
  - `evolucao_temporal(inicio, fim, granularidade)`: série temporal por dia/semana e turnos de pico.
  - `estoque_critico()`: alerta de produtos com baixa disponibilidade ou esgotados.
  - `salao_tempo_real()`: ocupação atual de mesas e consumo aberto no salão.
  - `auditoria_operacional(termo, limite)`: busca via SQLite em logs de cancelamentos e alterações.
  (verificar cada ferramenta com chamadas de teste unitário via script de asserção direta).

## 3. Orquestração Gemini, Fallback em Cascata e Salvaguardas Anti-Alucinação

- [x] 3.1 Implementar descoberta dinâmica de modelos elegíveis e construtor de cascata em `assistente_ia.py`:
  - Leitura das variáveis de ambiente `GOOGLE_API_KEY_1` e `GOOGLE_API_KEY_2` (com salvaguarda estrita: nunca registrar chaves no código, specs, SQLite ou logs).
  - Descoberta via `client.models.list()`, filtrando modelos que suportam `generateContent` e *function calling*.
  - Construção da fila em cascata ordenada: todos os modelos elegíveis da Chave 1 em ordem; se esgotados, todos os modelos elegíveis da Chave 2.
  (verificar descoberta de modelos e ordenação correta da fila via script de teste com mock).
- [x] 3.2 Implementar loop de execução da cascata com tolerância a falhas e cooldown em `assistente_ia.py`:
  - Interceptação de rate limit (429), quota excedida, timeout, 5xx, chave inválida ou modelo indisponível.
  - Registro da tentativa e erro no SQLite local (`llm_fallback_logs`) com campos `api_origem` ('Chave 1' ou 'Chave 2'), `modelo`, `sucesso`, `codigo_status`, `erro_motivo` e `duracao_ms`, NUNCA enviando para `fila_sincronizacao`.
  - Ativação de cooldown curto temporário (60s a 120s) para o modelo com falha, avançando imediatamente para a próxima opção da fila.
  - Tratamento de esgotamento total da cascata: retorno de mensagem amigável e explicativa ao Gerente informando indisponibilidade momentânea, sem alucinação numérica.
  (verificar transição de modelo por 429 simulado e respeito ao cooldown via teste automatizado).
- [x] 3.3 Implementar orquestração RAG e registro de ferramentas determinísticas via Function Calling com prompt do sistema enriquecido com conceitos da ontologia, timezone de Brasília (`America/Sao_Paulo`) e resolução de datas relativas (verificar tool call e resposta estruturada).
- [x] 3.4 Implementar mecanismo de conferência e salvaguarda: montagem do payload de evidências para o painel *"Como calculei"*, incluindo `api_origem` ('Chave 1' ou 'Chave 2', sem segredos), `modelo_utilizado`, contagem de tentativas falhas e dataframe das consultas SQLite.
- [x] 3.5 Implementar funções de persistência de conversas `salvar_mensagem_chat` e `carregar_historico_chat` no `assistente_ia.py` vinculadas ao colaborador logado, persistindo também os metadados de telemetria da resposta no SQLite.

## 4. Interface do Usuário Streamlit e Navegação

- [x] 4.1 Criar a página `pages/8_Assistente_IA.py` com interface conversacional moderna usando `st.chat_message` e `st.chat_input`, botões de perguntas rápidas ("Quais mesas mais vendem?", "Vendas na varanda no almoço", "Estoque crítico"), exibição de mensagem amigável de fallback caso o serviço esteja indisponível, painel expansível *"Como calculei"* exibindo parâmetros, dataframe de evidências, API utilizada ("Chave 1" ou "Chave 2"), modelo respondente e total de tentativas falhas, e gerenciador de novas conversas.
- [x] 4.2 Proteger a página `pages/8_Assistente_IA.py` com `ui_components.verificar_permissao_acesso(["gerente"])` e tratamento elegante para `GOOGLE_API_KEY_1` e `GOOGLE_API_KEY_2` ausentes (card informativo com orientações de configuração sem expor segredos).
- [x] 4.3 Atualizar `ui_components.render_navbar` e o dashboard geral em `app.py` para incluir o módulo *"8. Assistente IA"* exclusivamente na visualização do Gerente, ocultando do perfil Caixa.

## 5. Bateria de Testes e Validação Executiva

- [x] 5.1 Adicionar testes do motor ontológico e das ferramentas do assistente na suíte unificada `tools/test_suite.py`, contendo Golden Set de perguntas gerenciais e validação de precisão matemática com turnos e setores.
- [x] 5.2 Adicionar testes unitários para a cascata de fallback do LLM em `tools/test_suite.py`:
  - Teste de descoberta dinâmica e filtragem de capacidades (`generateContent` e function calling).
  - Teste de transição automática Chave 1 -> Chave 2 diante de mock de erro 429 / quota.
  - Teste de ativação e expiração de cooldown de modelo com falha.
  - Teste de fail-safe amigável quando toda a cascata falhar.
  - Asserção de segurança estrita: assegurar que nenhuma string de chave de API seja salva em `llm_fallback_logs`, `chat_mensagens`, logs ou telas.
  - Asserção de isolamento: certificar que nenhuma entrada de LLM seja inserida em `fila_sincronizacao`.
- [x] 5.3 Executar `python tools/run_all.py` e verificar 100% de aproveitamento de toda a bateria de testes do sistema.

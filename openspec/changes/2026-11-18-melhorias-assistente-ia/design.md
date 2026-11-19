# Decisoes de Arquitetura e Design: Melhorias do Assistente IA

**Change ID**: `2026-11-18-melhorias-assistente-ia`  
**Data**: 2026-11-18  

## 1. Arquitetura Geral do Sistema
O Assistente IA do Gerente e estruturado em tres camadas estritamente desacopladas:
1. **Camada de Dados & Persistencia**: SQLite em modo WAL com leitura analitica via conexao somente-leitura (`mode=ro` + `PRAGMA query_only = ON`), sem mutacao ou reflexos na sincronizacao Xano.
2. **Camada de Dominio & Orquestracao RAG**: Ontologia relacional (conceitos, sinonimos e relacoes em SQLite), catalogo de ferramentas deterministicas analiticas, classificador de erros e cascata de fallback multi-chave / multi-modelo Google Gemini.
3. **Camada de Apresentacao (Frontend Streamlit)**: Interface conversacional executiva com gerenciador lateral de sessoes, cartoes tematicos de perguntas, chat estilizado com formatacao monetaria, graficos nativos leves e painel de auditoria dividido em secoes.

```
+-----------------------------------------------------------------------------------+
|                           STREAMLIT (pages/8_Assistente_IA.py)                     |
|  +--------------------+  +-----------------------------------------------------+  |
|  | Lista Lateral      |  | Status Conexao | Chat Executivo | Graficos Nativos  |  |
|  | Nova / Renomear /  |  | Cartoes Tematicos de Perguntas Sugeridas             |  |
|  | Apagar / Auto-Name |  | Painel "Como Calculei" (Secoes, Evidencias, Fallback)|  |
|  +--------------------+  +-----------------------------------------------------+  |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                        ORQUESTRADOR (backend/ai/assistente_ia.py)                 |
|  - Ordem Configuravel de Modelos (GEMINI_MODELS_PREFERENCE)                       |
|  - Classificador de Erros (429/5xx -> Proximo Modelo; 401/403 -> Proxima Chave;   |
|                            400 -> Interrompe Cascata)                             |
|  - Cooldown Formalizado & Parser de Retry-After                                   |
|  - Janela Deslizante de Contexto Conversacional                                   |
|  - Catalogo de Ferramentas com Filtro de Dados Demo (is_demo = 0)                 |
+---------------------+---------------------------------------+---------------------+
                      |                                       |
                      v                                       v
+----------------------------------+    +------------------------------------------+
|  ONTOLOGIA (backend/ai/ontologia) |    |   SQLITE WAL (churrascontrol.db)         |
|  - Happy Hour: 17:00 as 19:30    |    |   - Conexao mode=ro + query_only = ON    |
|  - Meia-Noite: data_abertura     |    |   - Tabelas: comandas (com is_demo),     |
|  - Setores: Varanda, Salao       |    |     produtos, itens_comanda, mesas,      |
|    Interno, Kids e Sinonimos     |    |     chat_conversas, chat_mensagens,      |
|  - Desambiguacao com Premissa    |    |     llm_fallback_logs                    |
+----------------------------------+    +------------------------------------------+
```

## 2. Camada de Dados e Paridade de Schema

### 2.1 Schema Real do SQLite vs Documentacao Legada
- **Tabela `produtos`**:
  - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
  - `codigo_pdv`: TEXT UNIQUE NOT NULL
  - `nome`: TEXT NOT NULL
  - `categoria`: TEXT NOT NULL
  - `preco_unitario`: REAL NOT NULL (nome oficial do preco de catalogo)
  - `qtd_disp`: INTEGER DEFAULT 15 (nome oficial do estoque disponivel)
  - `precisa_produzir`: INTEGER DEFAULT 1
  - `disponivel`: INTEGER DEFAULT 1
- **Tabela `itens_comanda`**:
  - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
  - `comanda_id`: INTEGER NOT NULL
  - `produto_id`: INTEGER
  - `nome_produto_historico`: TEXT NOT NULL
  - `categoria_historico`: TEXT
  - `quantidade`: INTEGER NOT NULL DEFAULT 1
  - `preco_momento`: REAL NOT NULL (preco historico imutavel registrado no consumo)
- **Tabela `comandas`**:
  - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
  - `mesa_id`: INTEGER
  - `numero_mesa_historico`: INTEGER NOT NULL
  - `data_abertura`: TEXT NOT NULL
  - `data_fechamento`: TEXT
  - `status`: TEXT DEFAULT 'ABERTA' (PAGA, ABERTA, CANCELADA)
  - `taxa_servico`: INTEGER DEFAULT 1
  - `qtd_pessoas`: INTEGER DEFAULT 1
  - `valor_total`: REAL DEFAULT 0.0
  - **`is_demo`**: INTEGER DEFAULT 0 (NOVA COLUNA: identifica vendas simuladas de demonstracao)

### 2.2 Isolamento de Dados Demo (`seed_vendas_demo.py`)
- O script `tools/seed_vendas_demo.py` agora grava estritamente `is_demo = 1` nas comandas geradas.
- Todas as ferramentas deterministicas (`resumo_financeiro`, `ranking_mesas`, `ranking_produtos`, `vendas_por_categoria`, `evolucao_temporal`) recebem o argumento opcional `ignorar_demo: bool = True` (padrao: ativado), aplicando a clausula `is_demo = 0` na selecao.
- O Gerente pode, atraves de um controle visual discreto na barra lateral, optar por visualizar apenas dados reais ou incluir os dados de demonstracao.

### 2.3 Conexao Somente-Leitura em Modo WAL
- O caminho do banco e normalizado com formato URI universal:
  `file:{os.path.abspath(db_path).replace(os.sep, '/')}?mode=ro`
- Ambas as camadas de seguranca sao aplicadas:
  1. Conexao aberta com flag `uri=True` e `mode=ro`.
  2. Execucao de `PRAGMA query_only = ON;` imediatamente apos conectar.
- Em caso de falha de URI (ex: restricoes especificas de ambiente), executa fallback para conexao tradicional com `PRAGMA query_only = ON;`.
- Tentativas de `INSERT`, `UPDATE`, `DELETE` ou `DROP` sao interceptadas e rejeitadas pelo proprio motor SQLite com `sqlite3.OperationalError: attempt to write a readonly database`.

## 3. Motor de Cascata e Classificacao de Erros

### 3.1 Ordem de Modelos Configuravel
- A ordem de preferencia dentro de cada chave e resolvida dinamicamente:
  1. Leitura da variavel de ambiente `GEMINI_MODELS_PREFERENCE` (lista separada por virgulas).
  2. Se vazia ou ausente, adota a ordem padrao documentada:
     - Nivel 1 (Estaveis rapidos modernos): `gemini-2.5-flash`, `gemini-3.7-flash`, `gemini-2.0-flash`.
     - Nivel 2 (Menores / contingencia): `gemini-1.5-flash`, `gemini-1.5-flash-8b`.
     - Nivel 3 (Modelos Pro / raciocinio denso): `gemini-2.5-pro`, `gemini-3.7-pro`, `gemini-1.5-pro`.
     - Nivel 4 (Modelos experimentais/preview): modelos contendo `exp` ou `preview`.

### 3.2 Classificacao Inteligente de Erros no Fallback
A cascata classifica as excecoes em tres categorias de severidade:

1. **Erros Transientes de Servico / Modelo**:
   - Codigos / Padroes: 429, Resource Exhausted, Quota exceeded, Timeout, Deadline Exceeded, 500, 502, 503, 504, Service Unavailable, Model Not Found.
   - **Comportamento**: Coloca o modelo atual em cooldown temporario (padrao: 60s ou tempo extraido de Retry-After) e avanca imediatamente para o proximo modelo da mesma chave. Se todos os modelos da chave falharem, avanca para a Chave 2.

2. **Erros Fatais de Autenticacao / Chave de API**:
   - Codigos / Padroes: 401, 403, API_KEY_INVALID, Permission Denied, Consumer Suspended, Forbidden.
   - **Comportamento**: A chave inteira e considerada invalida. Desativa a chave atual imediatamente, **nao tenta os outros modelos dessa chave**, registra o motivo de forma opaca (sem expor a chave) e salta diretamente para a outra chave configurada. Adiciona mensagem de aviso amigavel ao resultado informando que a Chave X esta sem permissao.

3. **Erros de Requisicao Malformada / Cliente**:
   - Codigos / Padroes: 400 Bad Request, Malformed Request, Schema Error, Argument Error (nao associado a credencial).
   - **Comportamento**: Interrompe a cascata imediatamente. Nao adianta tentar outro modelo ou outra chave se a requisicao foi estruturada incorretamente. Registra o erro em `llm_fallback_logs` e retorna mensagem fail-safe de formato invalido.

### 3.3 Cooldown Formalizado e Extracao de Retry-After
- Configuracoes via variaveis de ambiente:
  - `LLM_COOLDOWN_TRANSIENT_SECONDS`: padrao `60` segundos (limites de taxa e 5xx).
  - `LLM_COOLDOWN_DAILY_QUOTA_SECONDS`: padrao `3600` segundos (1 hora).
  - `LLM_COOLDOWN_AUTH_ERROR_SECONDS`: padrao `86400` segundos (24 horas).
- Algoritmo de parser: verifica na mensagem ou nos metadados da excecao expressoes como `retry after (\d+)` ou `in (\d+)s`. Caso identificado um valor numerico valido entre 1 e 3600 segundos, ele substitui o tempo padrao de cooldown daquele modelo.

## 4. Ontologia e Regras de Negocio

### 4.1 Definicao Formal do Turno Happy Hour
- Intervalo padrao: **17:00 as 19:30**.
- Relacoes triplas registradas no SQLite:
  - `("happy_hour", "horario_inicio", "17:00")`
  - `("happy_hour", "horario_fim", "19:30")`
- Descricao ontologica: "Horario promocional de bebidas e petiscos no final da tarde das 17:00 as 19:30".

### 4.2 Axioma Contabil de Meia-Noite
- **Regra**: O turno e o dia de faturamento de uma comanda sao atribuidos estritamente pela data e hora de **abertura** da comanda (`data_abertura`).
- Exemplo: uma mesa aberta as 23:45 que consumiu ate as 01:30 do dia seguinte pertence ao turno **Jantar** da data de abertura. Essa regra elimina a distorcao de registrar consumo de madrugada em turnos inexistentes ou dividir artificialmente uma conta entre dois dias.

### 4.3 Alinhamento de Setores e Sinonimos
- Setores oficiais e faixas de mesas:
  - **Varanda**: Mesas 1, 2, 3 e 4.
  - **Salao Interno**: Mesas 5, 6, 7 e 8.
  - **Kids**: Mesas 9 e 10.
- Sinonimos incorporados:
  - Para `varanda`: "varanda", "varandinha", "deck", "ar livre", "area externa", "ao ar livre", "la fora", "lá fora".
  - Para `salao_interno`: "salao", "salão", "salao principal", "salão principal", "salao interno", "salão interno", "climatizado", "interno", "dentro".
  - Para `espaco_kids`: "kids", "espaco kids", "espaço kids", "area kids", "área kids", "criancas", "crianças", "familias", "famílias", "brinquedoteca".

### 4.4 Resolucao de Ambiguidade e Consultas Vazias
- Se o Gerente fizer pergunta sem indicar periodo ou turno (ex: "Qual o faturamento?"):
  - O sistema assume **Hoje** para faturamento diario ou **Ultimos 7 dias** para comparativos.
  - O texto da resposta inicia declarando a premissa adotada.
  - O painel "Como calculei" registra o periodo sob "Premissa assumida (pergunta sem data explicita)".
- Se a ferramenta retornar zero linhas:
  - O assistente responde explicitamente que nenhum registro foi encontrado no periodo ou setor especificado, sem extrapolar valores ou inventar numeros.

### 4.5 Contexto da Conversa (Janela Deslizante)
- O orquestrador recupera as ultimas 6 mensagens da sessao ativa no SQLite.
- Monta o historico no formato do SDK (`types.Content` com papeis `user` e `model`), truncando mensagens individuais em no maximo 1000 caracteres para preservar a janela de contexto e economizar tokens.

## 5. Design Visual da Pagina 8 (`pages/8_Assistente_IA.py`)

### 5.1 Layout em Duas Colunas
- Proporcao: `st.columns([1.1, 3.2])`.
- **Coluna Lateral (Gerenciador de Conversas)**:
  - Botao "Nova Conversa".
  - Toggle de filtro "Ocultar dados de demonstracao (Demo)".
  - Lista de conversas anteriores com status visual da conversa ativa.
  - Botoes de acao por conversa: **Renomear** (dialog de edicao) e **Apagar** (dialog de confirmacao).
  - Titulagem automatica: na primeira pergunta do usuario em uma nova conversa, o titulo e gerado automaticamente baseado no tema da pergunta (ex: "Faturamento de hoje", "Mesas da varanda").
- **Coluna Principal (Chat e Visualizacoes)**:
  - Cabecalho corporativo com indicador de status da API (ativo Chave 1, ativo Chave 2, indisponivel).
  - Estado vazio: Grade de 5 cartoes tematicos de perguntas sugeridas (Faturamento, Mesas e Setores, Cardapio, Estoque, Auditoria).
  - Fluxo de chat: mensagens do Gerente e Assistente estilizadas com baloes contrastantes.
  - Formatacao de moeda: `R$ X.XXX,XX` com separador de milhar e centavos.
  - Graficos nativos leves (`st.bar_chart` para rankings e `st.line_chart` para evolucao temporal).
  - Painel "Como calculei" estruturado em 6 secoes e recolhido por padrao.

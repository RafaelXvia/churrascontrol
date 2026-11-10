## Context

O ChurrasControl opera com persistência relacional em SQLite embutido (`churrascontrol.db`), hospedado no Discloud (container Linux com limite restrito de 512 MB de RAM) e interface Streamlit.
O banco armazena entidades transacionais (`produtos`, `mesas`, `comandas`, `itens_comanda`, `auditoria`). O catálogo de produtos e os colaboradores também são sincronizados com o backend Xano sob janela deslizante máxima de 8 requisições por 20 segundos.
A motivação detalhada, o diagnóstico de integridade de dados e o guia didático de **RAG e Ontologia** estão documentados em `proposal.md`.

## Goals / Non-Goals

**Goals:**
- **Zero Alucinação Numérica**: Toda agregação matemática (soma, média, contagem, percentual) é processada deterministicamente pelo motor SQLite através de ferramentas tipadas em Python/Pydantic.
- **Camada Ontológica de Domínio (Graph-over-SQLite)**: Modelar conceitos de negócio, sinônimos informais, turnos de horários, setores de mesas físicas e regras contábeis em tabelas locais no SQLite, permitindo desambiguação semântica antes de qualquer execução de consulta.
- **Roteamento Inteligente (Text-to-Tool)**: Utilização do LLM Google Gemini via SDK moderno `google-genai` com Function Calling estruturado para mapear a intenção do Gerente e resolver referências temporais para datas absolutas (com fuso horário de Brasília `America/Sao_Paulo`).
- **Resiliência e Fallback em Cascata Multi-Chave e Multi-Modelo**: Roteamento tolerante a falhas utilizando duas chaves de API (`GOOGLE_API_KEY_1` e `GOOGLE_API_KEY_2`) lidas exclusivamente de variáveis de ambiente. Descoberta dinâmica na inicialização dos modelos que suportam `generateContent` e *function calling*. Execução encadeada: todos os modelos da Chave 1 em ordem; se esgotados, todos os modelos da Chave 2. Em caso de 429 (rate limit), cota, timeout, 5xx, chave inválida ou indisponibilidade, colocar o modelo em cooldown curto e saltar para o próximo.
- **Fail-Safe Amigável Sem Alucinação**: Se todas as chaves e modelos da cascata falharem, responder ao Gerente com mensagem amigável e explicativa de indisponibilidade momentânea, nunca inventando ou chutando dados contábeis.
- **Higiene e Segurança Estrita de Credenciais**: Chaves de API lidas unicamente de variáveis de ambiente em tempo de execução; estritamente proibido gravar chaves no código, specs, SQLite ou logs. A identificação nas telas e logs restringe-se a rótulos opacos ("Chave 1" ou "Chave 2").
- **Transparência de Raciocínio e Telemetria no Painel "Como Calculei"**: Renderização de painel colapsável no Streamlit contendo intervalo temporal, ferramenta invocada, parâmetros, dataframe de linhas de evidência, além de metadados da execução do LLM: qual API respondeu ("Chave 1" ou "Chave 2"), qual modelo concluiu a resposta e a quantidade de tentativas falhas na cascata.
- **Leitura em Modo Seguro**: Conexão com SQLite estritamente somente-leitura (`file:churrascontrol.db?mode=ro`) para as execuções do assistente, impedindo qualquer mutação ou injeção acidental de dados.
- **Preservação de Memória RAM**: Nenhuma dependência pesada de servidores de grafos externos (Neo4j) ou modelos locais pesados de embeddings (PyTorch/SentenceTransformers); a ontologia e as queries rodam de forma nativa e leve no SQLite em < 2ms.
- **Isolamento de Nuvem**: Interações do chat e logs de tentativas do LLM (`llm_fallback_logs`) são estritamente locais no SQLite; jamais disparam eventos para a `fila_sincronizacao` do Xano.

**Non-Goals:**
- Permitir escrita ou alteração de comandas/mesas/cardápio através de comandos de texto no chat nesta versão (o assistente é estritamente analítico e consultivo).
- Execução de comandos SQL livres arbitrários gerados pelo modelo sem validação (descartado para evitar injeção SQL e quebras de cardinalidade).
- Permitir acesso a colaboradores com cargo diferente de `gerente`.
- Suporte a áudio/voz em tempo real nesta fase.

---

## Fundamentos Teóricos: RAG Estruturado, Ontologia e Cascata de Fallback

Para apoiar a discussão técnica da equipe e a fundamentação acadêmica do trabalho, esta seção detalha a arquitetura de como a **Ontologia**, o **RAG Estruturado** e a **Cascata de Fallback de LLM** se conectam com o SQLite e o Xano:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                 ARQUITETURA DE DADOS: RAG + ONTOLOGIA NO SQLITE                 │
│                                                                                 │
│   [ Gerente digita: "Quanto vendemos de carne na varanda no almoço de ontem?" ]  │
│                                      │                                          │
│                                      ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ 1. CAMADA ONTOLÓGICA (ontologia.py / SQLite: ontologia_*)               │   │
│   │    • Desambiguação de termos:                                           │   │
│   │      - 'carne'   -> Subclasses: ['Picanha', 'Ancho', 'Costela']         │   │
│   │      - 'varanda' -> Mesas físicas associadas: [1, 2, 3, 4]              │   │
│   │      - 'almoço'  -> Range de horário: 11:30 às 15:30                    │   │
│   │      - 'ontem'   -> Data calculada: 2026-10-06                          │   │
│   │    • Axioma aplicado: status = 'PAGA' (exclui canceladas e abertas)     │   │
│   └──────────────────────────────────┬──────────────────────────────────────┘   │
│                                      │                                          │
│                                      ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ 2. CAMADA RAG ESTRUTURADA (assistente_ia.py / SQLite: mode=ro)          │   │
│   │    • Invocação de ferramenta determinística:                            │   │
│   │      vendas_periodo_setor(mesas=[1,2,3,4], produtos=[...], data=...)     │   │
│   │    • Execução SQL segura e isolada -> Retorna dados exatos:             │   │
│   │      [ { "produto": "Picanha", "qtd": 14, "total": 1258.60 }, ... ]     │   │
│   └──────────────────────────────────┬──────────────────────────────────────┘   │
│                                      │                                          │
│                                      ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ 3. CAMADA GENERATIVA COM FALLBACK EM CASCATA (Google Gemini SDK genai)  │   │
│   │    • Execução em cascata ordenada:                                      │   │
│   │      - Chave 1: Modelos elegíveis (generateContent + Function Calling)  │   │
│   │      - Chave 2: Modelos elegíveis de reserva                            │   │
│   │    • Em falha (429/cota/5xx/timeout): cooldown curto e tenta próximo    │   │
│   │    • Se todos falham: fail-safe amigável (zero chutes!)                 │   │
│   │    • Registra telemetria de tentativas no SQLite (llm_fallback_logs)    │   │
│   │    • Gera metadados auditáveis para o painel "Como Calculei"            │   │
│   └──────────────────────────────────┬──────────────────────────────────────┘   │
│                                      │                                          │
│                                      ▼                                          │
│   [ Resposta Streamlit: Texto executivo + Dataframe + Telemetria de LLM ]       │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Fluxo Detalhado da Cascata de Fallback do LLM

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                 MÁQUINA DE ESTADOS DA CASCATA DE FALLBACK DO LLM                │
│                                                                                 │
│  [ Inicialização do Sistema ]                                                   │
│    ├─ Lê GOOGLE_API_KEY_1 e GOOGLE_API_KEY_2 das variáveis de ambiente          │
│    ├─ client.models.list() para cada chave ativa                                │
│    ├─ Filtra modelos: suporte a generateContent E function calling              │
│    └─ Constrói a Fila da Cascata:                                               │
│       [ (Chave 1, M1), (Chave 1, M2), ... ] -> [ (Chave 2, M1), (Chave 2, M2) ] │
│                                                                                 │
│  [ Execução de Requisição do Assistente ]                                       │
│    ┌───────────────┐                                                            │
│    │ Próximo par   │◄────────────────────────────────────────┐                  │
│    │ (Chave, Mod.) │                                         │                  │
│    └───────┬───────┘                                         │ (Falha capturada)│
│            ▼                                                 │ Registra log no  │
│    Está em cooldown ativo? ──[SIM]──► Avança para o próximo  │ SQLite local e   │
│            │ [NÃO]                                           │ aplica cooldown  │
│            ▼                                                 │ curto (60-120s)  │
│    Envia requisição com ferramentas determinísticas          │                  │
│      ├─ Erro 429 / Cota / Timeout / 5xx / Indisponível? ─────┘                  │
│      │                                                                          │
│      └─ [SUCESSO] ──────────────────────────────────────────────┐               │
│                                                                 ▼               │
│  [ Esgotamento Total da Cascata ]               Retorna resposta executiva e    │
│    Todos os modelos e chaves falharam?          preenche painel "Como Calculei":│
│    Exibe mensagem amigável ao Gerente           • API utilizada: "Chave 1"|"2"  │
│    informando indisponibilidade temporária.     • Modelo: ex. gemini-2.5-flash  │
│    Zero alucinação numérica!                    • Tentativas que falharam: N    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Por que NÃO usamos RAG Vetorial Puro (ChromaDB / FAISS)?
No RAG vetorial clássico, os registros do banco são transformados em parágrafos de texto e indexados por vetores de embedding. Quando o usuário faz uma pergunta, o sistema busca os *k* textos mais "semelhantes".
- **A Falha no Domínio Financeiro**: Se o restaurante teve 50 comandas no domingo e o gerente pergunta *"qual foi o total faturado?"*, o RAG vetorial traz apenas 5 ou 10 pedaços de texto e pede para o modelo somar. O modelo não tem acesso a todas as linhas e ainda é ruim em aritmética, gerando **alucinação matemática**.
- **Nossa Solução (RAG Estruturado / Text-to-Tool)**: O modelo de IA **nunca soma números**. Ele apenas escolhe a ferramenta certa com os parâmetros certos, e o **SQLite** faz a agregação determinística via `SELECT SUM(...)`.

### Por que NÃO usamos Neo4j ou Protégé Externos?
- O Neo4j e servidores de ontologia OWL/RDF (como Apache Jena) exigem máquinas virtuais Java dedicadas que consomem mais de 1 GB de RAM cada. Como o nosso deploy no Discloud é limitado a **512 MB de RAM total**, rodar um banco de grafos separado derrubaria a aplicação por Out of Memory (OOM).
- A abordagem **Graph-over-SQLite (Triple Store)** implementa a mesma estrutura de grafos (*Sujeito $\rightarrow$ Predicado $\rightarrow$ Objeto*) em tabelas relacionais indexadas no próprio `churrascontrol.db`, rodando com **menos de 10 MB de RAM** e resposta em **menos de 2 milissegundos**.

---

## Modelagem das Tabelas no SQLite

```sql
-- 1. Conceitos do Domínio (Nós do Grafo)
CREATE TABLE IF NOT EXISTS ontologia_conceitos (
    id TEXT PRIMARY KEY,               -- ex: 'picanha', 'almoco', 'varanda', 'churrasco'
    tipo TEXT NOT NULL,                 -- 'PRODUTO', 'CATEGORIA', 'SETOR_SALAO', 'TURNO', 'REGRA'
    nome_legivel TEXT NOT NULL,         -- 'Picanha Parrilla', 'Almoço Executivo', 'Varanda Externa'
    descricao TEXT                      -- Metadado explicativo para o LLM
);

-- 2. Sinônimos e Mapeamento de Linguagem Natural
CREATE TABLE IF NOT EXISTS ontologia_sinonimos (
    termo TEXT PRIMARY KEY,             -- ex: 'cervejinha', 'drinque', 'carne nobre', 'lá fora', 'varandinha'
    conceito_id TEXT NOT NULL,          -- aponta para 'cerveja', 'bebidas', 'carnes', 'varanda'
    FOREIGN KEY(conceito_id) REFERENCES ontologia_conceitos(id) ON DELETE CASCADE
);

-- 3. Relações Semânticas (Arestas Triplas: Sujeito -> Predicado -> Objeto)
CREATE TABLE IF NOT EXISTS ontologia_relacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sujeito_id TEXT NOT NULL,           -- ex: 'varanda'
    predicado TEXT NOT NULL,            -- ex: 'contem_mesa', 'subclasse_de', 'horario_inicio', 'horario_fim'
    objeto_id TEXT NOT NULL,            -- ex: 'mesa_1', 'carnes', '11:30', '15:30'
    peso REAL DEFAULT 1.0,
    FOREIGN KEY(sujeito_id) REFERENCES ontologia_conceitos(id)
);
CREATE INDEX IF NOT EXISTS idx_ontologia_busca ON ontologia_relacoes(sujeito_id, predicado);
CREATE INDEX IF NOT EXISTS idx_ontologia_inversa ON ontologia_relacoes(objeto_id, predicado);

-- 4. Histórico Local de Sessões de Chat (Sem sincronização com Xano)
CREATE TABLE IF NOT EXISTS chat_conversas (
    id TEXT PRIMARY KEY,
    titulo TEXT NOT NULL,
    usuario_id TEXT NOT NULL,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_mensagens (
    id TEXT PRIMARY KEY,
    conversa_id TEXT NOT NULL,
    papel TEXT NOT NULL,                -- 'user', 'assistant', 'system'
    conteudo TEXT NOT NULL,
    ferramentas_json TEXT,              -- Metadados de evidências e ferramentas
    api_origem TEXT,                    -- 'Chave 1' ou 'Chave 2' (sempre sem o valor da chave)
    modelo_utilizado TEXT,              -- ex: 'gemini-2.5-flash'
    tentativas_falhas INTEGER DEFAULT 0,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(conversa_id) REFERENCES chat_conversas(id) ON DELETE CASCADE
);

-- 5. Telemetria e Logs de Fallback do LLM (Local no SQLite / Sem Xano)
CREATE TABLE IF NOT EXISTS llm_fallback_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversa_id TEXT,
    mensagem_id TEXT,
    api_origem TEXT NOT NULL,           -- 'Chave 1' ou 'Chave 2' (NUNCA o segredo da chave)
    modelo TEXT NOT NULL,               -- ex: 'gemini-2.5-flash', 'gemini-3.7-flash'
    sucesso INTEGER NOT NULL,            -- 1 para sucesso, 0 para falha
    codigo_status INTEGER,              -- ex: 429, 500, 503, etc.
    erro_motivo TEXT,                   -- mensagem sanitizada de erro (sem segredos)
    duracao_ms INTEGER,                 -- tempo decorrido da requisição
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_llm_fallback_criado ON llm_fallback_logs(criado_em);
CREATE INDEX IF NOT EXISTS idx_llm_fallback_busca ON llm_fallback_logs(api_origem, modelo, sucesso);
```

### Instâncias Iniciais da Ontologia (Seed do Domínio)
- **Setores do Salão**:
  - `varanda` $\rightarrow$ `contem_mesa` $\rightarrow$ Mesas `1`, `2`, `3`, `4`.
  - `salao_interno` $\rightarrow$ `contem_mesa` $\rightarrow$ Mesas `5`, `6`, `7`, `8`.
  - `espaco_kids` $\rightarrow$ `contem_mesa` $\rightarrow$ Mesas `9`, `10`.
- **Turnos Operacionais**:
  - `turno_almoco` $\rightarrow$ Horário entre `11:30` e `15:30`.
  - `turno_jantar` $\rightarrow$ Horário entre `18:30` e `23:59`.
  - `happy_hour` $\rightarrow$ Horário entre `17:00` e `19:30`.
- **Hierarquia de Cardápio**:
  - `picanha`, `ancho`, `costela`, `vaca_atolada` $\rightarrow$ `subclasse_de` $\rightarrow$ `churrasco` / `carnes`.
  - `cerveja`, `chopp`, `suco`, `refrigerante` $\rightarrow$ `subclasse_de` $\rightarrow$ `bebidas`.

---

## Decisions

### 1. RAG Estruturado com Resolução Ontológica (Ontology-Guided Tooling)
- *Decisão*: Antes de executar qualquer query, o orquestrador passa os termos do usuário pelo módulo `ontologia.py`, resolvendo sinônimos, setores de mesas e faixas de horários de turno.
- *Racional*: Evita falhas onde o gerente pergunta por *"churrasco"* ou *"varanda"* e uma busca simples SQL retornaria zero resultados porque no banco os produtos se chamam *"Picanha"* e as mesas são números `1..10`.

### 2. Provedor de LLM: Fallback em Cascata Multi-Chave e Multi-Modelo (Google Gemini via `google-genai`)
- *Decisão*: Utilizar o SDK moderno `google-genai` com orquestração em cascata baseada em duas chaves de API (`GOOGLE_API_KEY_1` e `GOOGLE_API_KEY_2`) e múltiplos modelos descobertos dinamicamente.
- *Racional*:
  - **Descoberta Dinâmica no Boot**: O sistema executa `client.models.list()` para cada chave configurada e filtra modelos com capacidade `generateContent` e suporte a Function Calling, permitindo flexibilidade sem hardcode de nomes fixos que possam ser descontinuados.
  - **Ordem Sequencial Determinística**: A cascata prioriza todos os modelos elegíveis da Chave 1; somente após o esgotamento destes passa para todos os modelos da Chave 2.
  - **Tratamento de Falhas e Cooldown**: Qualquer erro 429 (rate limit), estouro de quota, timeout, erro 5xx, indisponibilidade ou chave inválida aciona a transição imediata para o próximo modelo da fila. O modelo com falha recebe cooldown temporário (60s a 120s) para evitar sobrecarga repetitiva inútil.
  - **Segurança e Higiene de Chaves**: Chaves residem exclusivamente em variáveis de ambiente. Nenhuma chave é salva em arquivos de código, spec, banco SQLite ou logs.
  - **Fail-Safe Amigável**: Caso todas as combinações de chave e modelo falhem, o sistema responde educadamente ao Gerente explicando a indisponibilidade momentânea, mantendo o princípio inegociável de zero alucinação contábil.
  - **Isolamento de Nuvem e Auditoria Local**: Logs de tentativas de fallback são gravados unicamente na tabela local `llm_fallback_logs` no SQLite, sem envio para o Xano (`fila_sincronizacao`).

### 3. Resolução de Datas Relativas no Prompt do Sistema
- *Decisão*: Injetar a data/hora local atual com timezone `America/Sao_Paulo` (ex: `Hoje é quarta-feira, 07/10/2026 10:30`) nas instruções do sistema do modelo.
- *Racional*: O modelo consegue mapear "ontem", "este mês", "último domingo" para intervalos ISO precisos `inicio` e `fim`, validados por esquemas Pydantic antes de tocar o SQLite.

### 4. Análise Específica de Preferência de Mesas (`ranking_mesas`)
- *Decisão*: Ferramenta analítica dedicada que agrupa comandas pagas por `numero_mesa_historico` e setor ontológico.
- *Racional*: Atende diretamente à dor apontada pelo Gerente ("quais mesas mais têm venda e onde os clientes mais gostam de sentar?").

### 5. Busca Textual Híbrida via SQLite FTS5 (Full-Text Search)
- *Decisão*: Utilizar tabela virtual FTS5 embutida no SQLite para consultas sobre registros de auditoria e descrições de produtos.
- *Racional*: Desempenho em milissegundos com BM25 nativo, sem bibliotecas externas e com overhead de disco/RAM insignificante.

### 6. Persistência de Conversas e Telemetria no SQLite Local
- *Decisão*: Criar tabelas `chat_conversas`, `chat_mensagens` e `llm_fallback_logs` no SQLite local sem sincronização com o Xano.
- *Racional*: Permite histórico de conversas no Streamlit e rastreabilidade total de performance/falhas do LLM sem consumir a cota de 8 req/20s do Xano.

---

## Risks / Trade-offs

- **[Risk] Ausência de chaves de API (`GOOGLE_API_KEY_1` e `GOOGLE_API_KEY_2`) no ambiente**
  - *Mitigação*: O módulo `assistente_ia.py` valida as variáveis no boot. Se nenhuma estiver definida, a interface Streamlit exibe um card instrutivo e amigável para configuração. Se apenas uma estiver configurada, a cascata opera com os modelos disponíveis daquela chave.
- **[Risk] Rate limits (429) e esgotamento de quota em planos gratuitos do Google Gemini**
  - *Mitigação*: A cascata com 2 chaves distintas e múltiplos modelos (ex: flash, flash-lite) aliada ao cooldown temporário previne paradas abruptas do assistente em momentos de pico operacional.
- **[Risk] Vazamento acidental de chaves de API em logs ou telas**
  - *Mitigação*: Sanitização estrita em todas as camadas. Métricas, logs e o painel "Como calculei" utilizam exclusivamente os identificadores opacos `"Chave 1"` e `"Chave 2"`. Nenhuma string de chave é impressa ou gravada no banco.
- **[Risk] Histórico vazio em bancos recém-iniciados**
  - *Mitigação*: Script utilitário `tools/seed_vendas_demo.py` gera 60 dias de histórico simulado consistente com setores de mesas e turnos para testes do time.
- **[Risk] Ambiguidade de termos não mapeados na ontologia**
  - *Mitigação*: Quando um termo não possui mapeamento ontológico exato, o motor realiza busca difusa (FTS5 / LIKE) no catálogo de produtos e informa na resposta os termos considerados.

---

## Migration Plan

1. **Hotfix de Integridade**: Aplicar e validar a preservação de itens de comandas pagas no `data_manager.py` (já validado por `test_suite.py`).
2. **Novas Tabelas e Índices**: Executar migração automática de schema no `init_db()` para criar `ontologia_conceitos`, `ontologia_sinonimos`, `ontologia_relacoes`, `chat_conversas`, `chat_mensagens` e `llm_fallback_logs`.
3. **Seed Ontológico**: Popular os conceitos, sinônimos e relações padrão do restaurante no primeiro boot.
4. **Dependências**: Adicionar `google-genai` e `pydantic` ao `requirements.txt`.
5. **Implementação de Backend e UI**:
   - Implementar `ontologia.py` com o motor de inferência semântica.
   - Implementar `assistente_ia.py` com o gerenciador de cascata multi-chave/multi-modelo, descoberta dinâmica, cooldown, registro de `llm_fallback_logs` e catálogo de ferramentas determinísticas.
   - Implementar `pages/8_Assistente_IA.py` com o painel "Como calculei" exibindo telemetria de LLM ("Chave 1"|"2", modelo, falhas) e tratamento gracioso de esgotamento.
   - Atualizar navbar em `ui_components.py` com guarda RBAC para `gerente`.
6. **Validação**: Executar suíte de testes `tools/test_suite.py` com testes simulados de fallback em cascata, cooldown, descoberta e asserção de não-vazamento de credenciais.

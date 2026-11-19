# Decisoes de Arquitetura e Design: Correcoes do Assistente IA

**Change ID**: `2026-11-18-correcoes-assistente-ia`  
**Data**: 2026-11-18  

## 1. Classificacao Precisa de Erros e Extracao de Retry
- A inspecao de erros utiliza uma abordagem estrita em tres camadas:
  1. **Atributos Estruturados do SDK**:
     - `getattr(err, "code", None)` ou `getattr(err, "status_code", None)`.
     - `getattr(err, "status", None)` (ex: `"RESOURCE_EXHAUSTED"`, `"INVALID_ARGUMENT"`, `"PERMISSION_DENIED"`, `"UNAUTHENTICATED"`).
  2. **Ordem de Avaliacao**:
     - 429 / Quota / Resource Exhausted e avaliado **SEMPRE ANTES** de 400.
  3. **Reserva Textual com Word Boundaries**:
     - Uso de regex estrito com delimitadores de palavra: `\b401\b`, `\b403\b`, `\b429\b`, `\b400\b`.
     - Impede que strings como "1400", "4010" ou codigos internos aleatorios ativem classificacoes indevidas.
  4. **Deteccao de Cota Diaria**:
     - Expressoes `"perday"`, `"per_day"`, `"daily"` acionam `DEFAULT_COOLDOWN_DAILY_QUOTA` (padrao: 3600s).
  5. **Parser de Retry**:
     - Restrito a `r'(?:retry in|retrydelay|retry-after)\s*[:=]?\s*(\d+)\s*s?'` e ao cabecalho `Retry-After`.

## 2. Filtragem de Modelos e Tratamento de Incompatibilidade
- **Criterio de Aceitacao de Modelos**:
  - O nome deve comecar obrigatoriamente com `"gemini-"`.
  - Deve conter `"generateContent"` em `supported_actions`.
  - Nao pode conter termos da lista de exclusao: `["tts", "image", "live", "audio", "embedding", "gemma", "learnlm", "robotics", "computer-use", "imagen", "veo", "aqa"]`.
- **Tratamento de Incompatibilidade de Ferramentas (Erro 400 de Modelo)**:
  - Se um modelo falhar com 400 com indicios de incompatibilidade com tools ou system instruction (ex: "does not support tools", "does not support system instruction"), ele e marcado como incompativel e a cascata segue para o proximo modelo.
  - A cascata so e interrompida se o mesmo erro 400 ocorrer em 2 modelos distintos.
- **Modelos de Contingencia Verificados**:
  - `["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]`.

## 3. Unificacao de Parametros em Todas as Ferramentas Analiticas
- Todas as 5 ferramentas analiticas de vendas passam a aceitar simultaneamente `turno` e `setor`:
  - `resumo_financeiro(inicio=None, fim=None, turno=None, setor=None)`
  - `ranking_mesas(inicio=None, fim=None, turno=None, setor=None, limite=10)`
  - `ranking_produtos(inicio=None, fim=None, turno=None, setor=None, conceito_ontologico=None, limite=10)`
  - `vendas_por_categoria(inicio=None, fim=None, turno=None, setor=None)`
  - `evolucao_temporal(inicio=None, fim=None, turno=None, setor=None, granularidade="dia")`
- **Validacao Estrita sem Ignorar Filtros**:
  - Se o `turno` nao for reconhecido pela ontologia: retorna dicionario com erro explicito (`"erro": "Turno 'X' nao reconhecido. Opcoes validas: almoco, jantar, happy hour."`).
  - Se o `setor` nao for reconhecido: retorna erro explicito com opcoes validas (`Varanda, Salao Interno, Kids`).
  - Se for passado apenas o `turno` sem datas: a ferramenta adota o periodo padrao declarado em premissa (Hoje para resumo; Ultimos 7 dias para rankings/categorias/evolucao).

## 4. Ocultacao de `ignorar_demo` e Repasse via Thread-Local
- O parametro `ignorar_demo` e completamente removido das assinaturas expostas ao modelo LLM (evitando contaminacao no function calling).
- O valor e mantido no contexto de execucao (`threading.local`) e inicializado por `executar_pergunta_gerente(..., ignorar_demo=True)`.
- As ferramentas analiticas consultam internamente `_obter_ignorar_demo()` a partir do contexto thread-local.

## 5. Regras de Horarios de Turnos sem Sobreposicao e Madrugada
- **Horarios Definidos na Ontologia**:
  - `turno_almoco`: `11:30:00` as `15:30:00`.
  - `happy_hour`: `17:00:00` as `18:29:59` (fim de tarde antes do jantar, sem sobreposicao).
  - `turno_jantar`: `18:30:00` as `23:59:59`.
- **Comandas Abertas na Madrugada (00:00:00 as 05:59:59)**:
  - Pertencem contabilmente ao turno `Jantar` do dia anterior (a operacao de fechamento noturno frequentemente se estende apos a meia-noite).
- **Prompt do Sistema Dinamico**:
  - Os horarios sao lidos dinamicamente da ontologia durante a construcao do prompt do sistema, sem duplicar valores estaticos no texto.

## 6. Discriminacao Contabil de Faturamento e Receita de Itens
- O retorno de `resumo_financeiro` e `vendas_por_categoria` inclui:
  - `faturamento_comandas_com_taxa`: soma de `valor_total` das comandas pagas (incluindo taxa de servico de 10% quando houver).
  - `receita_total_itens`: soma exata de `quantidade * preco_momento` de todos os itens dessas comandas.
  - `total_taxa_servico`: a parcela correspondente a taxa de servico.
  - Nas categorias, a soma de `receita_total` bate exatamente com `receita_total_itens`.

## 7. Mapeamento de Setor 100% via Ontologia
- Funcao `ontologia.obter_setor_da_mesa(mesa_num, conn=conn)`: consulta as relacoes em `ontologia_relacoes` e retorna o `nome_legivel` do setor.
- Se a mesa nao tiver vinculo cadastrado, retorna `"Sem setor"`.
- Nao ha listas ou mapeamentos fixos no codigo Python.

## 8. Sanitizacao Centralizada de Credenciais
- Funcao `sanitizar_texto(texto: str) -> str`:
  - Aplica regex para ocultar chaves de API (`AIza...`, `key=...`, `api_key=...`, `token=...`) substituindo por `[CHAVE_PROTEGIDA]`.
  - Aplicada em todas as chamadas de log e saidas de texto para o Gerente.
  - Em erros 400, o assistente emite mensagem amigavel generica sem exibir o stack trace ou detalhes brutos da API.

## 9. Verificacao de Dono de Conversas e Respostas Vazias
- `renomear_conversa` e `excluir_conversa` recebem opcionalmente `usuario_id` e validam se a conversa pertence ao usuario autenticado.
- Se o modelo retornar texto vazio (`not response.text or not response.text.strip()`), a tentativa e classificada como falha e a cascata avanca imediatamente para o proximo modelo.
- Conexao `get_readonly_connection` trata falha na primeira consulta em modo WAL atraves de fallback seguro com `PRAGMA query_only = ON;`.

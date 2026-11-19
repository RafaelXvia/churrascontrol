# Plano de Tarefas: Melhorias do Assistente IA

**Change ID**: `2026-11-18-melhorias-assistente-ia`  
**Status**: in_progress  

## 1. Camada de Dados, Schema e Isolamento de Demo
- [x] 1.1 Adicionar coluna `is_demo INTEGER DEFAULT 0` na tabela `comandas` em `backend/database/schema.sql` e indice correspondente.
- [x] 1.2 Implementar auto-migracao idempotente em `init_db()` do `backend/database/data_manager.py` para garantir que `is_demo` exista sem quebrar bancos existentes.
- [x] 1.3 Atualizar `tools/seed_vendas_demo.py` para salvar `is_demo = 1` em todas as comandas simuladas.
- [x] 1.4 Reforcar `get_readonly_connection()` em `backend/ai/assistente_ia.py` com normalizacao de barras para SQLite URI e execucao redundante de `PRAGMA query_only = ON;`.
- [x] 1.5 Atualizar ferramentas analiticas deterministas em `backend/ai/assistente_ia.py` para aceitar `ignorar_demo: bool = True` e filtrar `is_demo = 0`.

## 2. Ontologia Relacional e Regras Temporais
- [x] 2.1 Definir formalmente o conceito `happy_hour` com horario `17:00 as 19:30` em `backend/ai/ontologia.py`.
- [x] 2.2 Formalizar axioma de atribuicao de turno pela data/hora de abertura (`data_abertura`) para comandas que cruzam a meia-noite.
- [x] 2.3 Padronizar setores oficiais (Varanda, Salao Interno, Kids) e registrar sinonimos ampliados ("salao principal", "espaco kids", "area kids", etc.) em `backend/ai/ontologia.py`.

## 3. Motor de Cascata, Classificacao de Erros e Contexto
- [x] 3.1 Implementar ordem de preferencia configuravel de modelos via `GEMINI_MODELS_PREFERENCE` com fallback seguro para modelos estaveis.
- [x] 3.2 Implementar classificador de erros na cascata:
  - Erros transientes (429, 5xx, timeout) colocam o modelo em cooldown e tentam o proximo.
  - Chave invalida/sem permissao (401, 403, API_KEY_INVALID) desativa a chave inteira e pula imediatamente para a proxima chave.
  - Requisicao malformada (400) interrompe a cascata e registra o motivo.
- [x] 3.3 Formalizar tempos de cooldown configuraveis e parser de tempo de retry da excecao (`Retry-After`).
- [x] 3.4 Implementar tratamento de perguntas ambiguas com premissa padrao declarada explicitamente no texto e na telemetria.
- [x] 3.5 Implementar tratamento para retorno de zero linhas nas ferramentas sem inventar numeros.
- [x] 3.6 Adicionar manutencao de contexto conversacional com janela deslizante delimitada das ultimas mensagens.

## 4. Redesign Visual da Interface (pages/8_Assistente_IA.py)
- [x] 4.1 Criar cabecalho corporativo limpo com indicador de status discreto da conexao (Chave 1, Chave 2, Indisponivel).
- [x] 4.2 Construir gerenciador lateral de conversas em coluna dedicada: Nova Conversa, Renomear (dialog), Apagar (dialog de confirmacao) e geracao automatica de titulo sintetizado.
- [x] 4.3 Desenhar tela inicial com grade de cartoes tematicos de perguntas sugeridas (Faturamento, Mesas e Setores, Cardapio, Estoque, Auditoria).
- [x] 4.4 Implementar chat legivel com baloes distintos, formatacao monetaria brasileira (R$) e destaque de numeros.
- [x] 4.5 Adicionar suporte a graficos nativos leves (`st.bar_chart`, `st.line_chart`) sem inclusao de novas dependencias pesadas.
- [x] 4.6 Reestruturar painel "Como calculei" em 6 secoes organizadas e recolhido por padrao.
- [x] 4.7 Adicionar controle visual para alternar filtro de vendas de demonstracao (Demo).

## 5. Bateria de Testes Automatizados
- [x] 5.1 Atualizar `tools/test_suite.py` com casos de teste especificos para as novas funcionalidades.
- [x] 5.2 Executar `python tools/run_all.py` e garantir 100% de aprovacao na suite de testes.

## 6. Validacao Final
- [ ] 6.1 Validacao interativa do usuario (revisar interface, fluxos e confirmacao dos parametros padrao).

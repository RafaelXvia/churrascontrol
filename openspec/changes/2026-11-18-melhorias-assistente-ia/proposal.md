# Proposta de Mudanca: Melhorias de Comportamento, Resiliencia e Redesign Visual do Assistente IA

**Change ID**: `2026-11-18-melhorias-assistente-ia`  
**Data**: 2026-11-18  
**Autor**: Antigravity AI & Rafael  
**Status**: in_progress  

## 1. Contexto de Negocio
O Assistente IA do Gerente do ChurrasControl e uma ferramenta estrategica de apoio a tomada de decisao operacional e financeira. Ele permite ao Gerente consultar indicadores de receita, ocupacao de mesas por setor, pratos e cortes mais vendidos, controle de estoque critico e trilhas de auditoria atraves de linguagem natural, com calculos 100% deterministicos sobre o banco SQLite e total higiene de credenciais.

Apos a conclusao da primeira versao funcional, identificou-se a necessidade de elevar o nivel de maturidade, resiliencia e usabilidade executiva do assistente, corrigindo limitacoes na cascata de modelos, lacunas ontologicas de horarios e setores, e modernizando a interface visual para alcancar a mesma excelencia das demais telas do sistema.

## 2. Problemas Identificados

### 2.1 Comportamento da Cascata de Modelos e Classificacao de Erros
- A cascata anterior aplicava uma politica unica de fallback para qualquer excecao: um cooldown generico de 60 segundos era ativado tanto para limites de taxa (HTTP 429), quanto para indisponibilidade temporaria (HTTP 5xx), chave invalida/revogada (HTTP 401/403) ou requisicao malformada (HTTP 400).
- Chaves invalidas forjavam tentativas inuteis em todos os modelos daquela mesma chave, consumindo tempo de resposta do usuario antes de pular para a chave reserva.
- Erros de requisicao malformada (formato incorreto) continuavam tentando modelos subsequentes, quando deveriam interromper a cascata imediatamente e alertar a falha de schema.
- A ordem de preferencia dos modelos estava engessada no codigo-fonte, sem flexibilidade para o administrador priorizar modelos estaveis ou mais rapidos via variavel de ambiente.
- O tempo de retry sugerido pelo provedor (Retry-After) nao era inspecionado nem aproveitado no cooldown.

### 2.2 Lacunas Ontologicas e Tratamento de Dados
- Ausencia de definicao formal do horario de Happy Hour nos axiomas ontologicos.
- Comandas que cruzam a meia-noite (ex: abertas as 23:45 e encerradas na madrugada) nao tinham uma regra contabil explicita sobre qual turno e data pertenciam.
- Divergencia de nomenclatura de setores entre especificacoes, sementes de dados e codigo (ex: Salao Interno vs Salao Principal vs Espaco Kids).
- Perguntas sem especificacao de periodo ou setor geravam analises sem explicitar a hipotese assumida pelo assistente.
- Consultas a periodos vazios demandam tratamento formal de resposta sem dados, sem qualquer risco de inferencia aproximada.
- As conversas nao preservavam historico das interacoes imediatamente anteriores, impedindo perguntas naturais de continuacao (ex: "e no sabado?").
- A massa de vendas de demonstracao gerada por `seed_vendas_demo.py` misturava-se a comandas reais sem uma coluna de segregacao explicita (`is_demo`).

### 2.3 Experiencia do Usuario e Redesign da Interface
- A pagina `pages/8_Assistente_IA.py` apresentava um layout simplificado: sem indicador de status do servico no cabecalho, sem categorizacao das perguntas frequentes e sem gerenciador lateral completo de conversas (com criacao, renomeacao, delecao e titulagem automatica).
- O painel "Como calculei" precisava de divisao estruturada por secoes para facilitar a auditoria executiva.
- Faltava suporte a graficos nativos leves para visualizacao rapida de rankings e series temporais, respeitando o teto de 512 MB de memoria RAM.

## 3. Escopo da Solucao

1. **Cascata Inteligente e Classificacao de Erros**:
   - Prioridade configuravel via variavel `GEMINI_MODELS_PREFERENCE`.
   - Distincao categorica de erros: rate limit/5xx avanca modelo; chave invalida desativa a chave inteira e segue imediatamente para a proxima chave; requisicao malformada interrompe a cascata.
   - Cooldown formalizado com leitura de tempo de retry da excecao (Retry-After).
2. **Aprimoramento Ontologico e Regras de Negocio**:
   - Happy Hour formalizado no intervalo 17:00 as 19:30.
   - Axioma contabil formal: turno atribuido estritamente pela data e hora de abertura da comanda.
   - Padronizacao dos setores: Varanda (1-4), Salao Interno (5-8), Kids (9-10) e inclusao de sinonimos abrangentes.
   - Regra de ambiguidade: premissa temporal/espacial declarada explicitamente no texto e na telemetria.
   - Tratamento explícito de consultas vazias (zero linhas).
   - Manutencao de contexto das ultimas mensagens com janela deslizante delimitada.
   - Segregacao de dados de teste via coluna `is_demo` na tabela `comandas`.
3. **Redesign Visual da Pagina 8**:
   - Cabecalho corporativo com indicador discreto de status da conexao (Chave 1, Chave 2, Indisponivel).
   - Cartoes tematicos de perguntas sugeridas (Faturamento, Mesas e Setores, Cardapio, Estoque, Auditoria).
   - Gerenciador lateral de conversas com criacao, edicao de titulo, exclusao e titulo automatico sintetizado.
   - Graficos analiticos nativos leves (`st.bar_chart`, `st.line_chart`) sem adicao de bibliotecas pesadas.
   - Painel "Como calculei" estruturado em secoes claras de auditoria e recolhido por padrao.
   - Formatacao monetaria brasileira (R$) e valores em destaque.

## 4. Criterios de Sucesso e Nao-Regressao
- 100% de aprovacao na suite de testes consolidada (`tools/test_suite.py` e `tools/run_all.py`).
- Zero emojis em todos os arquivos de codigo, specs, telas e documentacao.
- Nenhuma chave de API registrada em logs, gravada em disco ou exposta na interface.
- Zero gravacoes na tabela `fila_sincronizacao` por modulos de IA.
- Conexao somente-leitura com banco WAL operando com total seguranca e bloqueio de mutacoes.

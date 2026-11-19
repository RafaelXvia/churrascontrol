# Proposta de Mudanca: Correcoes de Robustez, Classificacao de Erros, Ontologia e Sanitizacao do Assistente IA

**Change ID**: `2026-11-18-correcoes-assistente-ia`  
**Data**: 2026-11-18  
**Autor**: Antigravity AI & Rafael  
**Status**: in_progress  

## 1. Contexto de Negocio
Apos a entrega das melhorias iniciais do Assistente IA do Gerente, uma revisao detalhada identificou pontos especificos de robustez operacional, consistencia ontologica e blindagem de seguranca que necessitam de correcoes pontuais para garantir confiabilidade em producao.

## 2. Problemas Identificados e Solucoes

### 2.1 Classificacao de Erros do SDK e Falsos Positivos
- **Problema**: A classificacao de excecoes do Google GenAI dependia de buscas por substrings soltas (ex: encontrar "400" dentro de um numero como "1400" ou "4010"), gerando falsos positivos onde um erro 429 de cota (ex: "Quota limit 1400 exceeded") podia ser erroneamente interpretado como erro 400 e interromper a cascata. Alem disso, cotas diarias ("PerDay", "daily") necessitam de cooldown diferenciado.
- **Solucao**: Priorizar os atributos estruturados do SDK (`err.code`, `err.status`, `status_code`). Usar inspecao textual apenas como contingencia com limites de palavra (`\b401\b`, `\b403\b`, `\b429\b`, `\b400\b`). Avaliar 429/quota antes de 400. Restringir regex de retry a padroes explicitos ("retry in Xs", "retryDelay" ou header `Retry-After`). Detectar cota diaria e aplicar cooldown estendido configuravel (`LLM_COOLDOWN_DAILY_QUOTA_SECONDS`).

### 2.2 Descoberta de Modelos e Incompatibilidade de Ferramentas
- **Problema**: Modelos nao compativeis com texto ou com function calling (ex: modelos de voz, imagem, audio, gemma, learnlm, computer-use) poderiam ser incluidos na cascata se retornados pela listagem da API. Alem disso, se um modelo retornar erro 400 especificamente por nao suportar tools/system instructions, ele deve ser pulado individualmente, interrompendo a cascata apenas se dois modelos distintos falharem com 400.
- **Solucao**: Filtrar estritamente modelos que comecem com `gemini-` e suportem `generateContent`, excluindo prefixos/sufixos de imagem, audio, live, embedding, gemma, learnlm, robotics e computer-use. Ao receber 400 por falta de suporte a ferramentas/system instructions, marcar o modelo como incompativel e seguir para o proximo; parar a cascata por erro de cliente apenas se dois modelos diferentes confirmarem erro 400. Manter na contingencia apenas modelos oficiais e confirmados (`gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-1.5-flash`).

### 2.3 Parametros Setor e Turno em Todas as Ferramentas Analiticas
- **Problema**: Algumas ferramentas aceitavam apenas turno (como `resumo_financeiro`), enquanto outras aceitavam apenas setor (como `ranking_mesas`), impedindo analises cruzadas (ex: "vendas na varanda durante o almoco"). Alem disso, se o usuario informava um turno ou setor inexistente, o filtro era silenciosamente ignorado.
- **Solucao**: Padronizar todas as 5 ferramentas de vendas (`resumo_financeiro`, `ranking_mesas`, `ranking_produtos`, `vendas_por_categoria`, `evolucao_temporal`) para aceitarem simultaneamente `turno` e `setor`. Se o turno ou setor nao for reconhecido pela ontologia, retornar imediatamente um erro claro informando as opcoes validas ao inves de ignorar o filtro. Se apenas o turno for informado, aplicar a premissa de periodo padrao declarada.

### 2.4 Isolamento do Parametro `ignorar_demo`
- **Problema**: O parametro `ignorar_demo` estava exposto na assinatura das ferramentas, confundindo o schema de function calling do modelo LLM.
- **Solucao**: Remover `ignorar_demo` da assinatura exposta ao modelo. Armazenar a opcao no contexto de execucao thread-local e fazer `executar_pergunta_gerente` repassa-lo de forma transparente para todas as ferramentas.

### 2.5 Regras e Horarios de Turnos sem Sobreposicao e Madrugada
- **Problema**: O Happy Hour (17:00 as 19:30) se sobrepunha ao Jantar (18:30 as 23:59), causando ambiguidade nas contagens. Comandas abertas na madrugada (apos a meia-noite) nao tinham turno atribuido. O limite de 23:59 deixava uma lacuna de 59 segundos.
- **Solucao**: Propor regra sem sobreposicao:
  - Almoco: 11:30:00 as 15:30:00.
  - Happy Hour: 17:00:00 as 18:29:59 (fim de tarde antes do jantar).
  - Jantar: 18:30:00 as 23:59:59.
  - Madrugada (00:00:00 as 05:59:59): Comandas abertas na madrugada pertencem contabilmente ao Jantar do dia anterior.
  - Injetar os horarios no prompt do sistema dinamicamente a partir da ontologia, sem duplicacao de texto.

### 2.6 Discriminacao Clara de Valores: Faturamento de Comandas vs Receita de Itens
- **Problema**: O faturamento bruto de comandas (com taxa de servico) e a receita direta de itens (sem taxa) podiam gerar pequenas diferencas visuais se nao rotulados expressamente.
- **Solucao**: Rotular claramente no resumo e categorias: "faturamento da comanda (valor_total)" e "receita de itens", mostrando o valor com e sem taxa de servico, e garantindo que a soma das categorias coincida exatamente com a receita de itens.

### 2.7 Mapeamento de Setores via Ontologia
- **Problema**: O setor de cada mesa era atribuido por listas hardcoded (`if m_num in [1, 2, 3, 4]`).
- **Solucao**: Consultar a ontologia em SQLite (`ontologia_relacoes`) para identificar o setor de cada mesa fisica. Mesas sem setor associado sao rotuladas como "Sem setor".

### 2.8 Sanitizacao Centralizada de Chaves em Logs e UI
- **Problema**: A higienizacao de credenciais precisava ser centralizada e aplicada em todas as saidas.
- **Solucao**: Criar funcao unica `sanitizar_texto(texto: str) -> str` que remove chaves (`AIza...`, `key=...`, `api_key=...`) e aplica-la em todas as chamadas de `logger.*` e respostas devolvidas ao Gerente. Em erros 400, exibir mensagem amigavel sem exibir o payload bruto.

### 2.9 Resposta Vazia, Verificacao de Dono de Conversa e Conexao WAL
- **Problema**: Respostas vazias do modelo devem ser tratadas como falha para tentar o proximo modelo. Renomear e excluir conversas devem verificar a propriedade do usuario logado. A conexao `mode=ro` deve lidar com falhas de primeira consulta em ambientes concorrentes com WAL.
- **Solucao**: Implementar verificacao de resposta vazia, checagem de `usuario_id` nas operacoes de conversa e robustez na conexao `get_readonly_connection`.

## 3. Criterios de Sucesso
- 100% de aprovacao na suite de testes (`tools/run_all.py`).
- Zero emojis em todo o repositorio.
- Nenhuma exposicao de credenciais.

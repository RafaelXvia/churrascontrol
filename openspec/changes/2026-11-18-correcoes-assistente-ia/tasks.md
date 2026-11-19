# Plano de Tarefas: Correcoes do Assistente IA

**Change ID**: `2026-11-18-correcoes-assistente-ia`  
**Status**: in_progress  

## 1. Ontologia, Turnos sem Sobreposicao e Setores Dinamicos
- [ ] 1.1 Atualizar intervalos de turnos em `backend/ai/ontologia.py` sem sobreposicao: Almoco (11:30:00 as 15:30:00), Happy Hour (17:00:00 as 18:29:59) e Jantar (18:30:00 as 23:59:59).
- [ ] 1.2 Formalizar e implementar na ontologia a regra de comandas abertas na madrugada (00:00:00 as 05:59:59) atribuidas contabilmente ao Jantar do dia anterior.
- [ ] 1.3 Implementar funcao `obter_setor_da_mesa(mesa_num, conn=None)` em `backend/ai/ontologia.py` para consultar o setor no SQLite sem listas fixas no codigo.

## 2. Sanitizacao Centralizada de Credenciais
- [ ] 2.1 Criar funcao `sanitizar_texto(texto: str) -> str` em `backend/ai/assistente_ia.py` para ocultar qualquer chave de API (`AIza...`, `key=...`).
- [ ] 2.2 Aplicar `sanitizar_texto` em todas as chamadas de `logger.*` e em todos os textos retornados ao usuario e a interface.
- [ ] 2.3 Em falhas 400, exibir mensagem amigavel generica sem exibir o stack trace ou detalhes brutos da requisicao.

## 3. Classificacao de Erros e Descoberta de Modelos
- [ ] 3.1 Refatorar `classificar_erro` usando atributos estruturados do SDK (`code`, `status_code`, `status`), avaliando 429/quota antes de 400 e regex com word boundaries (`\b401\b`, `\b400\b`).
- [ ] 3.2 Implementar deteccao de cota diaria ("PerDay", "daily") com cooldown maior configuravel (`LLM_COOLDOWN_DAILY_QUOTA_SECONDS`).
- [ ] 3.3 Restringir o regex de retry a expressoes explicitas ("retry in Xs", "retryDelay" ou header `Retry-After`).
- [ ] 3.4 Refatorar `descobrir_modelos_chave` para aceitar exclusivamente modelos iniciados por `gemini-`, excluir modelos de midia/gemma/robotics e utilizar contingencia confirmada (`gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-1.5-flash`).
- [ ] 3.5 Implementar tratamento para modelos que falham com 400 por falta de suporte a ferramentas (pular modelo e interromper a cascata apenas se 2 modelos distintos confirmarem 400).

## 4. Ferramentas Analiticas, Turno + Setor e Ocultacao de `ignorar_demo`
- [ ] 4.1 Remover `ignorar_demo` das assinaturas expostas ao modelo e implementar repasse transparente via contexto `threading.local` em `executar_pergunta_gerente`.
- [ ] 4.2 Padronizar as 5 ferramentas de vendas (`resumo_financeiro`, `ranking_mesas`, `ranking_produtos`, `vendas_por_categoria`, `evolucao_temporal`) para aceitarem simultaneamente `turno` e `setor`.
- [ ] 4.3 Implementar validacao estrita de `turno` e `setor`: retornar erro explicito com opcoes validas caso nao sejam reconhecidos, sem ignorar o filtro.
- [ ] 4.4 Aplicar premissa de periodo padrao caso seja informado apenas o turno sem datas.
- [ ] 4.5 Utilizar `ontologia.obter_setor_da_mesa` em `ranking_mesas`, atribuindo "Sem setor" a mesas nao mapeadas.
- [ ] 4.6 Rotular claramente "faturamento da comanda (valor_total)" e "receita de itens", exibindo ambos e garantindo paridade das categorias com a receita de itens.
- [ ] 4.7 Injetar os horarios dos turnos no prompt do sistema dinamicamente a partir da ontologia.

## 5. Resposta Vazia, Dono de Conversa e Conexao WAL
- [ ] 5.1 Tratar resposta vazia do modelo como falha para tentar o proximo modelo da cascata.
- [ ] 5.2 Implementar verificacao de dono (`usuario_id`) nas operacoes `renomear_conversa` e `excluir_conversa`.
- [ ] 5.3 Atualizar `obter_status_servico` para refletir cascata esgotada ou em cooldown.
- [ ] 5.4 Reforcar `get_readonly_connection` contra falhas de primeira consulta em modo WAL com fallback seguro.

## 6. Bateria de Testes Automatizados
- [ ] 6.1 Atualizar `tools/test_suite.py` com testes para: 429 com numeros contendo "400", 401 real desativando chave, modelo sem ferramentas pulado, setor+turno combinados, turno invalido gerando erro claro, demo ligado/desligado e sanitizacao de chave em logs e respostas.
- [ ] 6.2 Executar `python tools/run_all.py` e garantir 100% de aprovacao na suite de testes.

## 7. Validacao Final
- [ ] 7.1 Validacao interativa do usuario (revisar interface, fluxos e confirmacao dos parametros padrao).

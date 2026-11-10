## Why

O ChurrasControl possui dados transacionais completos de salão, comandas, produtos e auditoria no SQLite local, mas o Gerente só consegue analisá-los por gráficos pré-moldados e relatórios PDF fixos de 1d/7d/15d/30d. Dúvidas gerenciais naturais do dia a dia — como:
- *"Quais mesas mais faturaram este mês e onde os clientes mais gostam de sentar?"*
- *"Vendemos mais carne no almoço ou no jantar de domingo?"*
- *"Como foram as vendas de chopp e cerveja na varanda ontem?"*
- *"Tem produto com estoque crítico ou precisando produzir agora?"*

exigem cruzamentos manuais de tabelas e filtros complexos que o operador não domina.

Ao mesmo tempo, integrar Inteligência Artificial diretamente sobre um banco de dados de restaurante traz riscos sérios se feito de maneira amadora. Para resolver isso com alto padrão técnico e acadêmico, esta mudança implementa a união de dois conceitos fundamentais da computação moderna: **RAG (Geração Aumentada por Recuperação)** e **Ontologia de Domínio**, executados de forma 100% local no SQLite para criar o **Assistente IA do Gerente**.


---

## Guia Didático para o Time: O que é RAG e o que é Ontologia?

Como esses conceitos são novidade para a maioria da equipe e para quem nunca trabalhou com Inteligência Artificial aplicada a sistemas empresariais, preparamos este guia com **analogias do mundo real**, **exemplos práticos de restaurante** e **comparações diretas**.

O objetivo é que qualquer pessoa do time — seja de negócios, desenvolvimento ou operações — compreenda com clareza o que cada tecnologia faz e por que a combinação das duas é a solução ideal para o ChurrasControl.

---

### O Resumo em Uma Frase
> **A Ontologia é o cérebro que entende o negócio do restaurante; o RAG é a mão que busca os números exatos no banco; e a IA generativa (Gemini) é a voz que redige a resposta em português claro.**

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        O FLUXO DE RACIOCÍNIO DO CHURRASCONTROL                         │
│                                                                                        │
│   1. ENTRADA DO USUÁRIO       2. ONTOLOGIA                3. RAG ESTRUTURADO           │
│   (Linguagem Natural)         (Semântica & Negócio)       (Dados & Matemática)         │
│   "Quanto vendemos de     ->  Traduz os termos:       ->  Consulta o SQLite:           │
│   churrasco na varanda        • 'churrasco' = Carnes      • Mesas [1, 2, 3, 4]         │
│   no almoço de ontem?"        • 'varanda' = Mesas 1 a 4   • Data: 2026-10-06           │
│                               • 'almoço' = 11:30 às 15:30 • Horário: 11:30 às 15:30    │
│                               • Axioma: status = 'PAGA'   • Executa: SUM(valor_total)  │
│                                                                                        │
│                               4. IA (GEMINI)              5. RESPOSTA AO GERENTE       │
│                           ->  (Comunicação & Formato) ->  (Executiva e Auditável)      │
│                               Recebe o total exato:       "Ontem no almoço da varanda  │
│                               R$ 1.840,00 e lista         foram vendidos R$ 1.840,00   │
│                               dos pratos. Redige o        em carnes (18 picanhas e     │
│                               texto sem inventar contas!   7 anchos). [Ver detalhes]"  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 1. O que é RAG (Retrieval-Augmented Generation)?

* **Tradução da sigla**: **Geração Aumentada por Recuperação**  
  - **Retrieval** (*Recuperação / Busca*): Buscar os dados reais no banco de dados.  
  - **Augmentation** (*Aumento / Enriquecimento*): Colocar esses dados dentro do contexto da pergunta.  
  - **Generation** (*Geração*): A IA escrever a resposta em linguagem humana.

* **Analogia Simples do Mundo Real (A Prova com Consulta)**:
  Imagine um estudante fazendo uma prova difícil de contabilidade:
  - **Sem RAG (Prova sem consulta)**: O estudante tenta chutar de memória números de um balanço que ele nunca viu. Ele pode inventar valores com extrema confiança, mas os números serão 100% inventados. Isso na IA se chama **Alucinação**.
  - **Com RAG (Prova com livro aberto)**: O estudante tem na sua frente a pasta oficial com o balanço patrimonial da empresa. Ele abre a pasta, confere o valor exato registrado na linha do extrato e redige a resposta com precisão absoluta.

#### Por que a Inteligência Artificial pura não serve para restaurantes?
Modelos de IA modernos (como o Google Gemini, ChatGPT, Claude) são gigantescos e inteligentes, mas foram treinados lendo a internet pública (notícias, enciclopédias, artigos gerais).  
**Eles NÃO conhecem e nunca viram os dados privados do ChurrasControl**:
- Eles não sabem quantas mesas temos abertas agora.
- Eles não sabem que a nossa picanha custa R$ 89,90.
- Eles não sabem quanto entrou no caixa no último domingo.

Se você conectar o Gemini direto no sistema e o gerente perguntar: *"Quanto faturamos ontem?"*, o modelo não tem esse número guardado. Como a IA foi programada para sempre tentar responder e agradar ao usuário, ela vai **inventar um número qualquer** (ex: *"Vocês faturaram R$ 4.350,00"*), que soa muito convincente, mas é uma mentira desastrosa para um gerente que precisa tomar decisões financeiras.

#### O RAG resolve isso em 3 passos cronológicos:
1. **Passo 1: Retrieval (Recuperação)**  
   Quando o gerente digita uma pergunta, o sistema **não** entrega a pergunta de imediato para a IA. Em vez disso, o sistema busca no nosso banco de dados local (`churrascontrol.db`) os registros oficiais que têm a ver com a pergunta.
2. **Passo 2: Augmentation (Aumento)**  
   O sistema monta um "dossiê de evidências" contendo a dúvida do gerente somada aos dados oficiais encontrados no banco de dados.
3. **Passo 3: Generation (Geração)**  
   O modelo de IA recebe esse dossiê com uma ordem estrita:  
   *"Responda ao gerente baseando-se única e exclusivamente nos dados anexados neste dossiê. Não faça cálculos de cabeça e não invente nenhum número."*  
   A IA então redige uma resposta executiva clara, resumida e profissional em português.

#### Os Dois Tipos de RAG: Por que o "RAG Clássico" não serve para restaurante e escolhemos o "RAG Estruturado"?
Este é o ponto técnico mais importante para a equipe de tecnologia:

| Característica | RAG Clássico (Vetorial / Embeddings) | RAG Estruturado (Text-to-Tool / Nossa Escolha) |
|---|---|---|
| **Como funciona?** | Converte textos em números matemáticos (*vetores*) e busca por frases "parecidas" (semelhança semântica). | O modelo entende o objetivo do usuário e aciona ferramentas Python que executam consultas SQL no banco. |
| **Para o que serve?** | Excelente para manuais de instruções, artigos científicos, PDFs de leis e políticas de RH. | Excelente para **dinheiro, contabilidade, estoque, datas e rankings**. |
| **Como lida com contas?** | **Péssimo**: Se perguntar o faturamento do mês, ele puxa 5 ou 10 comprovantes aleatórios e pede para a IA somar. A IA erra a conta e esquece comandas. | **100% Preciso**: O próprio banco de dados SQLite faz a conta através de `SELECT SUM(valor_total)`. O SQLite nunca erra uma soma. |
| **Consumo de Memória (RAM)** | Exige bancos vetoriais pesados (ChromaDB, FAISS, PyTorch), consumindo 800 MB a 1.5 GB de RAM. Derrubaria o nosso container de 512 MB no Discloud! | **Levíssimo**: Roda direto sobre o nosso banco SQLite local existente, consumindo menos de 5 MB de RAM e respondendo em menos de 2 milissegundos. |

---

### 2. O que é uma Ontologia?

* **Origem da palavra**: Em filosofia, ontologia é a ciência que estuda a natureza do ser e da realidade. Na Computação e Inteligência Artificial, uma **Ontologia** é o modelo formal que representa o **conhecimento, as regras de negócio e os significados de um domínio específico**.
* **Analogia Simples do Mundo Real (O Garçom Novato vs O Gerente Experiente)**:
  - **Garçom Novato (O Banco SQLite Puro)**: Sabe apenas o que está impresso no sistema. Se um cliente na mesa pedir *"traz uma gelada lá fora"*, o novato fica travado, porque no cardápio não existe um prato chamado "gelada" e no mapa do salão não tem nenhuma mesa chamada "lá fora". Ele só entende IDs e nomes exatos.
  - **Gerente Experiente (A Ontologia)**: Conhece a casa como a palma da mão. Ele sabe que *"gelada"* ou *"breja"* significa Chopp Brahma ou Heineken; sabe que *"lá fora"* é o setor da Varanda (Mesas 1 a 4); e sabe que o *"almoço de domingo"* vai até as 16h, enquanto na quarta-feira fecha às 15h30.

#### O Problema que a Ontologia resolve:
O banco de dados relacional guarda **dados brutos e frios**: números, textos soltos, chaves primárias e carimbos de data/hora (ex: `2026-10-06T12:45:00`). O banco não possui inteligência sobre o negócio:
- No banco existe uma coluna de data e hora. O banco não sabe se 13:00 é *almoço*, se 19:30 é *jantar* ou se 03:00 é *madrugada*.
- No banco existem as Mesas `1, 2, 3, 4`. O banco não sabe que essas mesas ficam na *Varanda Externa ao ar livre*, enquanto as Mesas `5 a 8` ficam no *Salão Principal Climatizado*.
- No banco existe o prato `"Picanha Parrilla"`. Se o gerente perguntar por *"vendas de churrasco"*, uma busca normal no banco faz `WHERE nome LIKE '%churrasco%'` e retorna **zero**, porque a palavra "churrasco" não está escrita no nome do prato.

#### Os 4 Pilares da nossa Ontologia no ChurrasControl:
1. **Conceitos e Categorias**: Define formally tudo o que existe no restaurante (*Prato, Bebida, Sobremesa, Setor do Salão, Turno de Horário, Forma de Pagamento*).
2. **Sinônimos e Linguagem do Salão**: Dicionário que ensina a IA a traduzir gírias e termos cotidianos:
   - *"cervejinha"*, *"breja"*, *"loira gelada"* $\rightarrow$ Chopp / Cerveja.
   - *"lá fora"*, *"deck"*, *"varandinha"* $\rightarrow$ Setor Varanda.
   - *"churrasco"*, *"cortes nobres"* $\rightarrow$ Picanha, Ancho, Costela, Prime Rib.
3. **Mapeamento Espacial e Temporal**:
   - *Varanda ao Ar Livre*: Mesas 1, 2, 3 e 4.
   - *Salão Principal Climatizado*: Mesas 5, 6, 7 e 8.
   - *Espaço Kids (Famílias)*: Mesas 9 e 10.
   - *Turno de Almoço*: das 11:30 às 15:30.
   - *Turno de Jantar*: das 18:30 às 23:59.
4. **Axiomas (Regras Sagradas do Negócio)**:
   - Regra 1: *Faturamento só considera comandas com status `PAGA`*. Comandas canceladas são estornos contábeis; comandas abertas são consumo em aberto que ainda não virou receita.
   - Regra 2: *Preço de venda é sempre o `preco_momento` gravado no histórico da comanda*, garantindo imutabilidade contábil mesmo se o dono alterar o preço do produto amanhã no cardápio.

---

### 3. A Sinergia: Como RAG e Ontologia se Completam na Prática

Muitas empresas cometem o erro de colocar apenas o RAG. Quando o gerente pergunta algo em linguagem humana comum, o RAG falha porque não entende a intenção de negócio.

A **Ontologia dá o significado da pergunta**, e o **RAG busca os dados e faz a conta**:

| Pergunta Real do Gerente | Cenário 1: IA Pura (Sem RAG nem Ontologia) | Cenário 2: IA com RAG Comum (Sem Ontologia) | Cenário 3: ChurrasControl (Ontologia + RAG Estruturado) |
|---|---|---|---|
| *"Quanto faturamos de carne na varanda no almoço de ontem?"* | Inventa um número qualquer (ex: "R$ 3.500,00"). Não tem acesso ao banco. | Procura a palavra "varanda" no banco (não acha mesa com esse nome), não sabe que horas é o almoço, e tenta somar textos. Responde: *"Dados não encontrados"*. | 1. **Ontologia**: Traduz *varanda* $\rightarrow$ Mesas 1 a 4; *carne* $\rightarrow$ Picanha, Ancho, Costela; *almoço* $\rightarrow$ 11:30-15:30; *ontem* $\rightarrow$ 2026-10-06; aplica filtro `status='PAGA'`.<br>2. **RAG/SQLite**: Roda `SELECT SUM(...)` nas tabelas certas.<br>3. **IA**: Formata a resposta com centavos exatos e exibe a tabela de evidências! |
| *"Quais mesas os clientes mais gostam de sentar?"* | Responde generalidades teóricas sobre psicologia de restaurantes sem olhar sua casa. | Pega as últimas 5 comandas abertas e lista mesas aleatórias, sem ranquear o histórico real. | 1. **Ontologia**: Entende que "gostar de sentar" significa *maior frequência de ocupação e faturamento acumulado por mesa* e mapeia para os setores.<br>2. **RAG/SQLite**: Agrupa todas as comandas pagas por mesa física e calcula o ranking total.<br>3. **IA**: Responde: *"As mesas mais disputadas são a 2 e a 3 da Varanda (faturaram 35% do total do mês), seguidas da mesa 6 no Salão."* |
| *"Tem algum produto que preciso comprar urgente?"* | Diz para o gerente olhar as prateleiras ou inventa produtos fictícios. | Faz uma busca por "urgente" no banco de produtos e não acha nada. | 1. **Ontologia**: Entende que "comprar urgente" aciona o conceito de *Estoque Crítico (`estoque_atual <= estoque_minimo`)*.<br>2. **RAG/SQLite**: Filtra os produtos com estoque abaixo do limite de segurança.<br>3. **IA**: Lista exatamente os produtos em falta com a quantidade restante e a recomendação de reposição. |

---

### 4. Resumo de Benefícios para o Projeto e para a Equipe

1. **Alta Precisão (Zero "Chutes" da IA)**: A diretoria e o gerente podem confiar 100% nos números, porque quem faz a conta é a matemática do banco relacional, e não a imaginação do modelo de linguagem.
2. **Linguagem Natural Descomplicada**: O gerente não precisa saber SQL, nem nomes de colunas do banco, nem códigos técnicos. Ele fala do jeito dele (*"lá fora"*, *"ontem no almoço"*, *"breja"*) e o sistema compreende perfeitamente.
3. **Leve e Sem Custos de Infraestrutura Adicionais**: Não precisamos contratar servidores pesados de grafos (Neo4j) nem bancos de vetores caros na nuvem. A ontologia e o RAG estruturado rodam de forma nativa e relacional dentro do próprio **SQLite** do projeto, gastando menos de 10 MB de RAM.
4. **Privacidade e Auditoria**: Cada resposta do assistente vem acompanhada do painel *"Como calculei"*, mostrando exatamente quais mesas, quais horas e quais registros sustentam aquela resposta, garantindo transparência total.

---

## What Changes

- **Preservação Definitiva de Histórico (Hotfix de Integridade Contábil)**: Eliminação do `DELETE FROM itens_comanda` em comandas não-abertas no `init_db()`, assegurando que itens de comandas `PAGA` permaneçam imutáveis para consultas analíticas de ranking de produtos, faturamento por categoria e consumo por mesa.
- **Isolamento de Banco da Suíte de Testes e Saneamento de Ferramentas**: Suíte de testes unificada em `tools/test_suite.py` e executada por `tools/run_all.py` em banco temporário descartável (`CHURRAS_DB_PATH`), desativando resets automáticos e protegendo o banco real de vendas.
- **Camada Ontológica no SQLite (`ontologia_conceitos`, `ontologia_sinonimos`, `ontologia_relacoes`)**:
  - Resolução de termos informais e sinônimos (*"cervejinha"*, *"drinques"*, *"cortes nobres"*, *"lá fora"*, *"mesa de canto"*).
  - Definição temporal de turnos (*Almoço*: 11:30 às 15:30; *Jantar*: 18:30 às 23:59).
  - Mapeamento espacial de salão (*Varanda*: Mesas 1 a 4; *Salão Principal*: Mesas 5 a 8; *Espaço Kids*: Mesas 9 e 10).
  - Axiomas de negócio: *Faturamento exige status PAGA*; *Preço de venda é sempre preco_momento histórico*.
- **Novo Módulo de Backend Analítico/RAG (`assistente_ia.py` & `ontologia.py`)**: Catálogo de ferramentas determinísticas tipadas via Pydantic (`resumo_financeiro`, `ranking_mesas`, `ranking_produtos`, `vendas_por_categoria`, `evolucao_temporal`, `estoque_critico`, `salao_tempo_real`, `auditoria_operacional`) executadas em conexão estritamente somente-leitura (`mode=ro`).
- **Orquestração com LLM Gemini e Fallback em Cascata Multi-Chave/Multi-Modelo (SDK oficial `google-genai`)**:
  - Leitura de credenciais a partir de duas variáveis de ambiente: `GOOGLE_API_KEY_1` e `GOOGLE_API_KEY_2`. Princípio de segurança estrito: NUNCA gravar chaves no código, na spec, no SQLite ou em logs.
  - Descoberta dinâmica de modelos na inicialização inspecionando quais modelos cada chave tem acesso com suporte conjunto a `generateContent` e chamadas de ferramentas (*function calling*).
  - Montagem de cascata ordenada: execução sequencial de todos os modelos elegíveis da Chave 1; esgotando-se, transição transparente para todos os modelos elegíveis da Chave 2.
  - Recuperação automática em caso de rate limit (429), cota estourada, timeout, erros de servidor 5xx, indisponibilidade ou falhas de chave, saltando para o próximo modelo e aplicando cooldown curto ao modelo com falha.
  - Fail-safe amigável: se toda a cascata falhar, resposta educada ao Gerente explicando a indisponibilidade momentânea, sem alucinação numérica.
  - Roteamento por Function Calling com resolução explícita de datas relativas com timezone de Brasília (`America/Sao_Paulo`) e verificação anti-alucinação.
- **Nova Tela Streamlit (`pages/8_Assistente_IA.py`) e Painel "Como Calculei" com Telemetria de LLM**:
  - Interface de chat conversacional com `st.chat_message`, `st.chat_input`, botões de perguntas sugeridas ("Quais mesas mais vendem?", "Top 5 pratos do almoço", "Estoque baixo").
  - Painel expansível *"Como calculei"* atualizado para exibir parâmetros, períodos, tabelas de evidência (`st.dataframe`), além da telemetria de execução: qual API respondeu ("Chave 1" ou "Chave 2", sem expor o segredo), qual modelo gerou a resposta e quantas tentativas falharam na cascata.
- **Guarda RBAC e Navegação Unificada**: Inclusão da aba *"8. Assistente IA"* na navbar exclusiva para colaboradores com cargo `gerente`. Perfil `caixa` tem acesso expressamente bloqueado por `verificar_permissao_acesso(["gerente"])`.
- **Persistência de Conversas e Isolamento da Nuvem**: Tabelas locais `chat_conversas`, `chat_mensagens` e `llm_fallback_logs` para manter histórico de chat e telemetria de tentativas no SQLite sem despachar dados de conversação ou logs para o Xano (preservando o rate limit de 8 req/20s da nuvem).
- **Massa de Dados de Demonstração (Seed de Vendas)**: Script controlado para semear 60 dias de vendas realistas (mesas 1 a 10, horários de almoço/jantar, categorias carnes/bebidas/acompanhamentos) para validação executiva e testes com o time.

## Capabilities

### New Capabilities
- `assistente-ia-gerente`: Interface e motor de chat conversacional com RAG estruturado e Ontologia Relacional sobre o SQLite, ferramentas determinísticas de análise financeira, ranking de mesas/produtos, controle de estoque e auditoria, restrito ao cargo Gerente, com resiliência via fallback em cascata multi-chave e multi-modelo Google Gemini.

### Modified Capabilities
- `fechamento-conta-e-relatorios-pdf`: Extensão das regras de imutabilidade e agregação analítica para garantir que comandas liquidadas e seus respectivos itens permaneçam consultáveis indefinidamente por múltiplos períodos e dimensões (incluindo número histórico da mesa física).
- `lancamento-itens-e-imutabilidade-consumo`: Reforço formal de que `itens_comanda` vinculados a comandas `PAGA` jamais podem ser expurgados por rotinas de limpeza periódica ou inicialização do sistema.

## Impact

- **Código Modificado**:
  - `data_manager.py`: Remoção do delete acidental no `init_db()`, suporte a `CHURRAS_DB_PATH`, criação das tabelas da ontologia, histórico de chat e telemetria local `llm_fallback_logs` (isolada do Xano).
  - `ui_components.py`: Registro da rota `pages/8_Assistente_IA.py` e badge na navbar para `gerente`.
  - `tools/run_all.py`, `tools/db_diagnostics.py`, `tools/clean_sqlite.py`: Suíte de testes unificada e diagnóstico com novas tabelas ontológicas e telemetria.
- **Novos Arquivos**:
  - `ontologia.py`: Motor de inferência semântica e resolução de termos/conceitos/setores em SQLite.
  - `assistente_ia.py`: Núcleo de orquestração RAG com gerenciador de cascata multi-chave/multi-modelo, cooldown de modelos, validação Pydantic, prompts do sistema e conexão read-only com SQLite.
  - `pages/8_Assistente_IA.py`: Tela Streamlit de chat com histórico, painel "Como calculei" com telemetria (Chave 1/2, modelo, tentativas falhas) e visual executivo.
  - `tools/seed_vendas_demo.py`: Gerador de massa histórica de vendas para demonstração.
  - `specs/assistente-ia-gerente/spec.md`: Especificação comportamental detalhada da nova capacidade.
- **Dependências (`requirements.txt`)**: Adição de `google-genai` (SDK oficial do Gemini) e `pydantic`.
- **Infraestrutura e Nuvem**:
  - Memória Discloud: Zero impacto em RAM local (inferência executada na nuvem via Google GenAI API; ontologia e queries rodam no SQLite em < 2ms).
  - Rate limit Xano: 100% protegido (chat e logs de tentativas do LLM não entram na fila de sincronização do Xano).
  - Variáveis de ambiente: Leitura de `GOOGLE_API_KEY_1` e `GOOGLE_API_KEY_2` com fallback em cascata e degradação graciosa em tela. Chaves de API nunca gravadas em código, banco, spec ou logs.

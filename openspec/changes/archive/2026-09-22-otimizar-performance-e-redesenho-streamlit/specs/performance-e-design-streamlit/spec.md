## Purpose

Garantir resposta instantânea das telas do Streamlit através de persistência local direta no arquivo JSON e fornecer interface gráfica sóbria, elegante e sem emojis.

## ADDED Requirements

### Requirement: Persistência local imediata e sincronização seletiva
O sistema SHALL ler e gravar dados operacionais de salão, comandas e cardápio diretamente no arquivo `churras_data.json`, despachando atualizações para o Xano exclusivamente em eventos de fechamento de conta ou alteração de itens via fila assíncrona com rate limit.

#### Scenario: Operação em mesa sem latência de rede
- **WHEN** o operador abre uma mesa ou adiciona um item
- **THEN** os dados são refletidos instantaneamente na interface sem espera de rede externa ou bloqueios de requisições.

#### Scenario: Sincronização em segundo plano no pagamento
- **WHEN** uma comanda tem seu fechamento/pagamento concluído
- **THEN** a operação é persistida imediatamente no arquivo local e agendada na fila de sincronização com o Xano respeitando o intervalo de segurança de taxa de chamadas.

### Requirement: Identidade visual executiva e ausência de emojis
A interface web do Streamlit SHALL adotar tema escuro executivo e não conter emojis em títulos, menus laterais, botões ou indicadores visuais.

#### Scenario: Carregamento visual da interface
- **WHEN** o usuário acessa qualquer página do sistema
- **THEN** os elementos gráficos apresentam tipografia sóbria, cores padronizadas (Obsidian, Slate e Amber) e ausência de caracteres emoji.

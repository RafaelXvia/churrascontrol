# performance-e-design-streamlit Specification

## Purpose
Garantir resposta instantânea das telas do Streamlit através de persistência local direta no arquivo JSON e fornecer interface gráfica sóbria, elegante e sem emojis.

## Requirements

### Requirement: Persistência local relacional em SQLite e fila persistente
O sistema SHALL ler e gravar dados operacionais de salão, comandas e cardápio diretamente no banco relacional SQLite local (`churrascontrol.db`) com suporte a concorrência WAL, despachando atualizações para o Xano exclusivamente através da tabela persistente em disco `fila_sincronizacao` com worker assíncrono e controle estrito de rate limit.

#### Scenario: Operação em mesa sem latência de rede
- **WHEN** o operador abre uma mesa ou adiciona um item
- **THEN** os dados são refletidos instantaneamente na interface (0-2ms) via transação atômica no SQLite sem espera de rede externa ou bloqueios de requisições.

#### Scenario: Sincronização em segundo plano no pagamento e itens
- **WHEN** uma comanda tem seu fechamento/pagamento concluído ou itens adicionados
- **THEN** a operação é persistida imediatamente no SQLite local e agendada na tabela `fila_sincronizacao`, sendo despachada com segurança e persistência contra falhas de energia/rede.

### Requirement: Identidade visual executiva, sistema de componentes e micro-animações
A interface web do Streamlit SHALL adotar tema escuro executivo moderno (paleta Obsidian, Slate, Amber Flame, Royal Blue e Emerald), com cards em estilo glassmorphism, micro-animações de hover com elevação suave (`translateY`), bordas neon temáticas, navegação integrada em barra superior (sem badges redundantes como "MODO LOCAL") e contenção estrita de dimensões evitando quebra ou transbordamento de texto.

#### Scenario: Carregamento visual e interações da interface
- **WHEN** o usuário acessa qualquer página ou passa o mouse sobre cards interativos
- **THEN** os elementos gráficos apresentam tipografia refinada, transições suaves de hover, cores harmônicas de alto contraste e layout perfeitamente responsivo e alinhado.

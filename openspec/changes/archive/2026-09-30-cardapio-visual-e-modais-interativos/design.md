# Design: Cardápio Visual Unificado & Modais Interativos com Sincronização Xano

## 1. Arquitetura de Componentes

### 1.1 Modais Nativos com `@st.dialog`
Em vez de renderizar formulários longos em cascata ou `st.expander` que aumentam o scroll vertical da página, foram implementados modais isolados:
- **`dialog_novo_produto()`**: Formulário completo solicitando código PDV, nome, categoria, preço unitário, estoque (`qtd_disp`), URL da imagem (Imgur), descrição completa, requer produção (`precisa_produzir`) e disponibilidade (`disponivel`).
- **`dialog_gerenciar_produto(p)`**: Modal amplo dividido em duas abas:
  - Miniatura com foto real, código PDV e preço consolidado no topo.
  - **Aba de Edição**: Permite atualizar qualquer um dos campos do produto com validação de tipos e dados.
  - **Aba de Exclusão**: Caixa de confirmação de segurança com acionamento do método `excluir_produto` e sincronização assíncrona com o Xano.

### 1.2 Clique Reativo nos Cards Sem F5 (Overlay Pattern)
A tentativa inicial de utilizar links HTML (`<a href="?detalhe_id=...">`) causava recarregamento completo da página (navegação GET com efeito de "F5").
A solução arquitetural definitiva adota o **Overlay Pattern Nativo do Streamlit**:
1. O card visual em HTML/CSS é renderizado dentro da coluna (`st.markdown`).
2. Imediatamente a seguir, é instanciado um botão Streamlit nativo com rótulo vazio (`st.button("", key=...)`).
3. O CSS injeta regras na classe do botão:
   ```css
   [data-testid="stColumn"] { position: relative !important; }
   div[class*="st-key-btn_prod_card_"] {
       position: absolute !important;
       inset: 0 !important;
       width: 100% !important;
       height: 100% !important;
       z-index: 20 !important;
   }
   div[class*="st-key-btn_prod_card_"] div.stButton > button {
       width: 100% !important;
       height: 100% !important;
       opacity: 0 !important;
       cursor: pointer !important;
   }
   ```
4. Um script JavaScript delegado intercepta cliques em qualquer subelemento do card e repassa para o botão nativo.
5. O Streamlit recebe o clique via WebSocket persistente e dispara `@st.dialog` instantaneamente, mantendo o estado da página sem reload.

### 1.3 Política de Referrer para Fotos do Imgur
Servidores de CDN de imagem como o Imgur rejeitam requisições vindas de hosts locais quando o cabeçalho `Referer` aponta para `http://localhost:8501`.
A solução aplica:
- `<meta name="referrer" content="no-referrer">` no cabeçalho das páginas.
- Atributo `referrerpolicy="no-referrer"` em todas as tags `<img>`.
- Imagem de fallback caso a URL original esteja temporariamente inacessível.

### 1.4 Sincronização Bidirecional Xano <-> SQLite
A função `sincronizar_produtos_xano()` consulta o endpoint GET `/produto` da API do Xano via HTTPX e atualiza ou insere registros no banco SQLite local (`churrascontrol.db`), assegurando que fotos reais e preços cadastrados no painel web do Xano reflitam instantaneamente na aplicação.

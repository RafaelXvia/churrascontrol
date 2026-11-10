# Proposta: Refinamento UX, Login Moderno, Avatar de Perfil e RBAC Estrito

## 1. Contexto e Motivação
Após os testes de usabilidade realizados pelo usuário, foram identificados pontos cruciais de melhoria estética, funcional e de controle de acesso:
1. **Design da Tela de Login**: A tela de login anterior era muito simplista e básica. É necessário um redesign moderno, com glassmorphism, tipografia refinada e identidade visual de alto padrão.
2. **Acesso Público aos QR Codes das Mesas**: A página `4_Mesas_QRCodes.py` foi indevidamente protegida com login de gerente. Essa tela deve ser de acesso livre/operacional para impressão e consulta de QR Codes sem forçar autenticação.
3. **Cardápio Digital do Cliente**:
   - Remoção completa do botão físico "Pedir" que aparecia abaixo do prato.
   - O clique no próprio card deve adicionar o item instantaneamente à pré-comanda.
   - Eliminação do conflito de diálogos múltiplos no Streamlit (`Only one dialog is allowed to be opened at the same time`), impedindo que dois diálogos concorram no mesmo ciclo.
4. **Ergonomia Operacional no Salão e Mesas**:
   - Aumentar os botões de ajuste de quantidade (`+` e `-`).
   - Substituir o botão de texto "Remover" (que ficava truncado como "Rem...") por um ícone compacto e claro (`✖`).
5. **Avatar de Perfil e Modal de Troca de Senha**:
   - Na barra de navegação, substituir o texto do usuário por um avatar circular exibindo a inicial do nome.
   - Ao clicar no avatar, abrir modal de perfil com dados cadastrais em modo somente leitura (nome, e-mail, telefone, cargo) e formulário seguro para alteração da própria senha.
   - Botão de logout elegante integrado ao modal/navbar.
6. **Edição Completa de Colaboradores pelo Gerente**:
   - Na página `6_Colaboradores.py`, o Gerente agora pode editar todos os dados de qualquer colaborador (nome, e-mail, telefone, cargo, redefinição de senha).
7. **RBAC Estrito para Perfil Caixa**:
   - O perfil Caixa deve ter acesso estritamente ao Salão & Mesas e ao Cardápio.
   - O Caixa não deve ver as abas de Painel Geral, Relatórios ou Colaboradores na navbar.
   - Qualquer tentativa de navegação direta pelo Caixa para `app.py`, `3_Relatorios.py` ou `6_Colaboradores.py` deve ser interceptada e redirecionada para `1_Salao_e_Mesas.py`.

## 2. Escopo
- Redesenhar `ui_components.py` (tela de login, avatar circular, modal de perfil, navbar adaptada ao cargo).
- Ajustar `pages/4_Mesas_QRCodes.py` para acesso desimpedido sem exigir login.
- Corrigir `pages/5_Cardapio_Cliente.py` para clique nativo no card, eliminação do botão "Pedir" e remoção da colisão de modais `@st.dialog`.
- Atualizar `pages/1_Salao_e_Mesas.py` com botões aumentados e ícone `✖`.
- Atualizar `pages/2_Cardapio.py` para permitir acesso de `["gerente", "caixa"]`.
- Adicionar modal de edição completa em `pages/6_Colaboradores.py` e função `editar_colaborador` em `data_manager.py`.
- Adicionar redirecionamento protetivo em `app.py` para o perfil Caixa.

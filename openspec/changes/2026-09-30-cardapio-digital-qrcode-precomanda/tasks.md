# Tarefas de Implementação: Cardápio Digital de Mesa via QR Code com Pré-Comanda do Cliente e Baixa Automática de Estoque

## Fase 1: Regras de Negócio e Gestão de Estoque no `data_manager.py`
- [ ] 1.1 Implementar função atômica de decremento de estoque (`qtd_disp`) e atualização automática de `disponivel = 0` quando o saldo zera.
- [ ] 1.2 Implementar estorno/recomposição de estoque ao remover item de comanda ou cancelar comanda.
- [ ] 1.3 Implementar função `confirmar_precomanda_cliente(numero_mesa: int, itens: list)` no `data_manager.py`:
  - Validar se a mesa existe (ou criar automaticamente se for número válido).
  - Obter comanda aberta ou abrir nova comanda para a mesa.
  - Lançar cada item com preço histórico, observação sanitizada e baixa de estoque.
  - Enfileirar itens na fila de sincronização com o Xano.
  - Retornar ID da comanda e resumo do pedido para o cliente.

## Fase 2: Central Administrativa de QR Codes de Mesa (`pages/4_Mesas_QRCodes.py`)
- [ ] 2.1 Criar a página `pages/4_Mesas_QRCodes.py` listando todas as mesas do restaurante.
- [ ] 2.2 Renderizar cartões com QR Code individual para cada mesa (`?mesa=X`).
- [ ] 2.3 Adicionar botões de ação: "Testar no Navegador", "Copiar Link" e opção de impressão/download.

## Fase 3: Página do Cardápio Digital do Cliente (`pages/5_Cardapio_Cliente.py`)
- [ ] 3.1 Criar interface mobile-first responsiva com leitura automática do parâmetro `?mesa=X`.
- [ ] 3.2 Implementar navegação gastronômica por categorias e busca de pratos.
- [ ] 3.3 Renderizar cards de pratos com imagem, descrição, preço e status de estoque (Disponível ou Esgotado).
- [ ] 3.4 Gerenciar carrinho de Pré-Comanda em `st.session_state` (itens ainda não confirmados).
- [ ] 3.5 Implementar modal/drawer de Pré-Comanda com ajuste de quantidades, observações e botão "🚀 Confirmar Pedido".
- [ ] 3.6 Exibir tela de sucesso após confirmação com resumo dos pratos e atualização em tempo real.

## Fase 4: Atualização da Barra de Navegação e Isolamento de Telas
- [ ] 4.1 Garantir que a barra superior interna (`ui_components.py`) permaneça limpa para o operador do salão, com link discreto para "QR Codes das Mesas".
- [ ] 4.2 Ocultar da visualização do cliente cabeçalhos ou menus administrativos quando na tela de cliente.

## Fase 5: Testes Automatizados e Validação
- [ ] 5.1 Criar `test_cardapio_cliente_qrcode.py` cobrindo:
  - Decremento automático de estoque e status esgotado ao zerar saldo.
  - Confirmação de pré-comanda criando ou anexando à comanda da mesa.
  - Lançamento atômico e enfileiramento Xano.
- [ ] 5.2 Executar suíte completa de testes (`test_app.py`, `test_cardapio_delivery.py`, `test_cardapio_cliente_qrcode.py`).

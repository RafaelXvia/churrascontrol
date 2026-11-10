# Tarefas Granulares de Implementação — Sincronização de Comandas com Xano

## Fase 1: Arquitetura XanoScript & Endpoints
- [x] 1.1 Criar o arquivo `backend/xano/api/churrascontrol/comandas_POST.xs` para receber requisições de criação/abertura de comanda.
- [x] 1.2 Atualizar `backend/xano/api/churrascontrol/comandas_itens_POST.xs` com fallback defensivo para auto-criar a comanda caso ela não exista no Xano antes de gravar o item em `itens_comanda`.

## Fase 2: Backend Python (`backend/database/data_manager.py`)
- [x] 2.1 Em `abrir_mesa()`, adicionar a chamada `_sync_push_imediato_ou_enfileirar("POST", "/comandas", payload)` logo após a persistência da comanda no SQLite.
- [x] 2.2 Em `confirmar_precomanda_cliente()`, adicionar a chamada de sincronização ao abrir nova comanda para pedidos via QR Code.
- [x] 2.3 Implementar rotina de reconciliação de inicialização (`reconciliar_comandas_abertas_xano()`) para enviar comandas ativas do SQLite que ainda não constem no Xano.

## Fase 3: Testes & Validação
- [x] 3.1 Criar teste unitário em `tools/test_suite.py` (`test_sincronizacao_abertura_comanda_xano`) validando o envio da comanda pai ao abrir mesa.
- [x] 3.2 Executar a suíte consolidada `tools/run_all.py` para garantir 100% de aprovação e ausência de regressões (19/19 testes PASS).
- [ ] 3.3 Validação interativa do usuário no painel do Xano antes do arquivamento da change.

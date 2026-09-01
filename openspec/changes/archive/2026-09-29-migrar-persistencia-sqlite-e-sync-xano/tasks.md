## 1. Estruturação do Banco de Dados SQLite e Migração

- [x] 1.1 Implementar utilitário de conexão SQLite em `data_manager.py` com ativação de `PRAGMA journal_mode=WAL` e criação automática das tabelas (`mesas`, `produtos`, `comandas`, `itens_comanda`, `fila_sincronizacao`).
- [x] 1.2 Implementar rotina de migração inicial para importar dados legados de `churras_data.json` para o SQLite caso o banco esteja novo.

## 2. Refatoração das Operações de Dados (Local-First CRUD)

- [x] 2.1 Refatorar funções de mesas e comandas (`listar_mesas`, `abrir_mesa`, `excluir_mesa`, `cancelar_comanda`, `obter_comanda_detalhes`, `fechar_comanda`) para executar transações SQL com resposta imediata.
- [x] 2.2 Refatorar funções de itens da comanda (`adicionar_item_comanda`, `editar_item_comanda`, `remover_item_comanda`) com agregação atômica e enfileiramento na tabela `fila_sincronizacao`.
- [x] 2.3 Refatorar funções do catálogo de produtos (`listar_produtos`, `criar_produto`, `atualizar_produto`, `excluir_produto`) garantindo unicidade do código PDV via restrição UNIQUE do SQLite.
- [x] 2.4 Refatorar agregação de métricas do dashboard e relatórios (`obter_dashboard_dados`, `gerar_pdf_bytes`) para consumir diretamente consultas SQL otimizadas.

## 3. Worker de Sincronização Persistente com Xano

- [x] 3.1 Implementar worker daemon que consome registros com status `PENDENTE` da tabela `fila_sincronizacao`, despacha com `httpx` e aplica rate limit de 2.5s entre chamadas.
- [x] 3.2 Implementar controle de tentativas (`tentativas`, status `ENVIADO` ou `ERRO`) com marcação de timestamp `processado_em`.

## 4. Testes, Validação e Arquivamento

- [x] 4.1 Criar teste automatizado `test_sqlite_sync.py` validando integridade de escrita/leitura no SQLite, imutabilidade contábil e enfileiramento Xano.
- [x] 4.2 Executar testes e verificar compilação e funcionamento do Streamlit.
- [x] 4.3 Atualizar especificações do OpenSpec e arquivar a change.

# Proposta Formal de Mudança — Sincronização e Integridade de Comandas no Xano

## 1. Contexto & Problema Identificado
O **ChurrasControl** possui um modelo híbrido de banco de dados: SQLite local transacional (`churrascontrol.db`) e persistência remota no Xano (`XANO_BASE_URL`).

Durante testes operacionais de atendimento (abertura de mesa pelo garçom e autoatendimento do cliente via QR Code em `5_Cardapio_Cliente.py`), identificou-se uma assimetria no ciclo de vida das comandas:
1. **Ausência de Criação de Comanda no Xano:**
   - As funções `abrir_mesa()` e `confirmar_precomanda_cliente()` geram a comanda com sucesso apenas no SQLite local.
   - Não existia chamada de sincronização ou endpoint dedicado para registrar a abertura da comanda na tabela `comandas` do Xano.
2. **Quebra da Chave Estrangeira Relacional no Xano:**
   - Quando o operador ou cliente lança um prato, `adicionar_item_comanda()` envia `POST /comandas/{comanda_id}/itens`.
   - O Xano insere o registro na tabela `itens_comanda`. Contudo, a coluna `comanda_id` foi modelada como uma **Table Reference** (`{ table = "comandas" }`).
   - Como a comanda correspondente (ex.: Comanda #17) não existe na tabela pai `comandas` do Xano, o Xano não consegue resolver a referência relacional e apresenta o campo **vazio/em branco** no painel administrativo do banco de dados.
3. **Falhas em Cascata no Fechamento e Cancelamento:**
   - Os endpoints `comandas_fechar_POST.xs` e `comandas_cancelar_POST.xs` executam a validação:
     ```xs
     db.get comandas { field_value = $input.comanda_id } as $comanda
     precondition ($comanda != null) { error_type = "notfound" }
     ```
   - Como a comanda nunca foi criada no Xano, qualquer tentativa de fechar ou cancelar a conta retorna HTTP 404 (`ERROR_CODE_NOT_FOUND`), resultando em erros reincidentes marcados na tabela `fila_sincronizacao`.

---

## 2. Objetivos da Mudança
1. **Garantir Integridade Referencial Estrita:** Toda linha inserida em `itens_comanda` no Xano deve possuir uma comanda pai válida na tabela `comandas`.
2. **Sincronização na Abertura:**
   - Ao abrir uma mesa no salão via garçom (`abrir_mesa`), registrar imediatamente a comanda na tabela `comandas` do Xano.
   - Ao receber o primeiro pedido via QR Code do cliente (`confirmar_precomanda_cliente`), registrar a comanda criada no Xano antes do envio dos itens.
3. **Mecanismo de Defesa & Auto-Recuperação no XanoScript:**
   - Alterar `comandas_itens_POST.xs` para que, caso a comanda informada ainda não exista na tabela `comandas` (por exemplo, devido a oscilação de rede temporária), ela seja criada automaticamente em tempo de execução (*upsert/on-demand creation*), garantindo que `itens_comanda.comanda_id` nunca fique órfão.
4. **Reconciliação Retroativa:**
   - Criar rotina de reconciliação para sincronizar todas as comandas existentes no SQLite que ainda não estejam presentes no Xano.

---

## 3. Escopo de Arquivos Afetados
- **XanoScript (APIs do Xano):**
  - `xano/api/churrascontrol/comandas_POST.xs`: Novo endpoint para abertura e cadastro de comanda no Xano.
  - `xano/api/churrascontrol/comandas_itens_POST.xs`: Adição de verificação defensiva com criação automática da comanda se inexistente.
- **Backend Python (`data_manager.py`):**
  - `abrir_mesa()`: Disparar `_sync_push_imediato_ou_enfileirar("POST", "/comandas", payload)`.
  - `confirmar_precomanda_cliente()`: Disparar sincronização da nova comanda antes de lançar os itens.
- **Suíte de Testes (`tools/test_sqlite_sync.py` ou `tools/test_suite.py`):**
  - Teste de integração garantindo que a comanda pai é criada antes de seus itens associados.

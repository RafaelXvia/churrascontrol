## Context

A implementação preliminar transferia o processamento via chamadas HTTP síncronas entre Streamlit e FastAPI, provocando lentidão nas re-execuções das páginas e dependência do status do servidor web. Além disso, a presença de emojis e imagens externas reduzia o caráter profissional da aplicação.

## Goals / Non-Goals

**Goals:**
- Centralizar o acesso a dados no módulo `data_manager.py` com leitura e escrita direta em `churras_data.json`.
- Enviar chamadas ao Xano apenas em operações críticas (pagamento de comanda e alterações estruturais de itens) em thread desacoplada com intervalo seguro de 2.5s.
- Reformular completamente o design de `app.py` e das páginas em `pages/`, removendo qualquer emoji e aplicando layout premium corporativo.
- Atualizar `.streamlit/config.toml` com tema dark executivo.

**Non-Goals:**
- Descartar o backend FastAPI (ele continua disponível e pode consumir a mesma camada `data_manager.py`).
- Alterar o esquema de dados do Xano ou de `churras_data.json`.

## Decisions

- **Decisão 1: Arquitetura de Acesso Direto Local (`data_manager.py`)**:
  - *Motivação*: Elimina 100% da latência de loopback HTTP, elimina dependência de o uvicorn estar ativo para a interface funcionar e garante consistência atômica nos dados salvos em disco.
- **Decisão 2: Thread Daemon de Sincronização Xano**:
  - *Motivação*: Assegura que o usuário nunca sinta travamento na tela ao finalizar uma comanda, despachando as tarefas para o Xano de forma ordenada e segura.

## Risks / Trade-offs

- [Concorrência de Arquivo] Se múltiplos processos tentarem escrever simultaneamente em `churras_data.json` → Mitigação: Uso de `threading.Lock` no `data_manager.py` para sincronizar operações de escrita.

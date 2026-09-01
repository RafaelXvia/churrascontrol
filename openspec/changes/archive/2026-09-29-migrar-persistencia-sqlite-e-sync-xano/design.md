## Context

A arquitetura do ChurrasControl necessita de resposta visual imediata no Streamlit para operações de salão (abertura de mesas, adição de itens, conferência e fechamento de conta), ao mesmo tempo em que precisa manter a nuvem do Xano atualizada sem esgotar o limite estrito de requisições por segundo (Rate Limit do plano gratuito).

A transição de JSON para SQLite resolve a fragilidade de concorrência e corrupção de arquivos, permitindo transações ACID confiáveis e persistência da fila de envio em disco.

## Goals / Non-Goals

**Goals:**
- Implementar persistência local em SQLite com suporte a WAL mode (`PRAGMA journal_mode=WAL`) para alta taxa de leitura simultânea sem bloqueios.
- Manter o tempo de resposta percebido pelo usuário em < 5ms (Local-First / Optimistic Update).
- Armazenar a fila de sincronização Xano na tabela `fila_sincronizacao`, processada por worker em background seguro contra interrupções.
- Migrar automaticamente os dados de `churras_data.json` para o SQLite se o banco estiver vazio.
- Manter 100% de compatibilidade com as assinaturas de funções de `data_manager.py`.

**Non-Goals:**
- Não alterar a interface gráfica nem substituir o Streamlit.
- Não remover a sincronização com o Xano (o Xano permanece como fonte centralizada de auditoria).
- Não exigir instalação de serviços pesados (como servidores PostgreSQL dedicados); o SQLite nativo do Python 3 é suficiente e portátil para Discloud.

## Decisions

- **Decisão 1: SQLite com modo WAL**:
  - *Motivação*: Garante leituras não-bloqueantes mesmo durante escritas, fundamental para a navegação fluida de múltiplas abas no Streamlit.
- **Decisão 2: Tabela `fila_sincronizacao` persistente**:
  - *Motivação*: Em caso de falha de conexão com a internet ou reinício do container na Discloud, as tarefas não processadas continuam no banco e são retomadas assim que o worker reiniciar.
- **Decisão 3: Manter isolamento estrito no `data_manager.py`**:
  - *Motivação*: Preserva a camada de abstração para que `app.py`, `pages/1_Salao_e_Mesas.py`, `pages/2_Cardapio.py` e `pages/3_Relatorios.py` continuem operando sem nenhuma alteração traumática de código.

## Schema do Banco Local (`churrascontrol.db`)

```sql
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_pdv TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL,
    preco_unitario REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS mesas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_mesa INTEGER UNIQUE NOT NULL,
    capacidade INTEGER DEFAULT 1,
    status TEXT DEFAULT 'OCUPADA'
);

CREATE TABLE IF NOT EXISTS comandas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mesa_id INTEGER,
    numero_mesa_historico INTEGER NOT NULL,
    data_abertura TEXT NOT NULL,
    data_fechamento TEXT,
    status TEXT DEFAULT 'ABERTA',
    taxa_servico INTEGER DEFAULT 1,
    qtd_pessoas INTEGER DEFAULT 1,
    valor_total REAL DEFAULT 0.0,
    FOREIGN KEY(mesa_id) REFERENCES mesas(id)
);

CREATE TABLE IF NOT EXISTS itens_comanda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comanda_id INTEGER NOT NULL,
    produto_id INTEGER,
    nome_produto_historico TEXT NOT NULL,
    categoria_historico TEXT,
    quantidade INTEGER NOT NULL DEFAULT 1,
    preco_momento REAL NOT NULL,
    observacao TEXT DEFAULT '',
    FOREIGN KEY(comanda_id) REFERENCES comandas(id)
);

CREATE TABLE IF NOT EXISTS fila_sincronizacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metodo TEXT NOT NULL,
    rota TEXT NOT NULL,
    payload_json TEXT,
    status TEXT DEFAULT 'PENDENTE', -- PENDENTE, ENVIADO, ERRO
    tentativas INTEGER DEFAULT 0,
    criado_em TEXT NOT NULL,
    processado_em TEXT
);
```

## Risks / Trade-offs

- [Concorrência de conexão SQLite] Múltiplas threads do Streamlit compartilhando conexões SQLite → Mitigação: Uso de conexões isoladas por operação com `check_same_thread=False` ou gerenciador de contexto `get_connection()` com fechamento explícito e `timeout=15.0`.

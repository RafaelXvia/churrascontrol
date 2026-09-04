## Context

O sistema opera com um modelo híbrido onde o SQLite embutido atua como autoridade local com latência imediata e o Xano é o backend centralizador de auditoria. Para garantir paridade completa de integridade entre ambas as pontas e mitigar vetores de risco de segurança e lentidão na fila, esta arquitetura eleva o SQLite ao status de autoridade transacional rigorosa (ACID) e adiciona camadas de defesa em profundidade.

## Goals / Non-Goals

**Goals:**
- Implementar regras de cardinalidade e constraints no SQLite idênticas às regras de negócio do Xano:
  - Uma mesa pode ter apenas uma comanda aberta simultaneamente (`idx_comanda_unica_aberta`).
  - Preços e quantidades devem ser estritamente positivos (`CHECK`).
  - Integridade referencial real com chaves estrangeiras (`ON DELETE RESTRICT` onde aplicável).
- Otimizar o tempo de envio da fila com controle adaptativo de tempo: se o worker estiver ocioso, o envio para o Xano ocorre sem atraso artificial desnecessário; se estiver em sequência, aplica o intervalo de segurança de 2.0s a 2.5s.
- Adicionar cabeçalho de autorização no Xano (`Authorization: Bearer ...`).
- Sanitizar saídas HTML no Streamlit contra ataques XSS utilizando `html.escape`.
- Adicionar coluna `ultimo_erro` e log estruturado na tabela `fila_sincronizacao`.

**Non-Goals:**
- Não criar um sistema complexo de login com OAuth; utilizar modelo operacional baseado em credenciais/PIN de autorização simples e eficaz para o salão.
- Não remover o worker desacoplado; a experiência do garçom deve continuar instantânea.

## Schema Refinado do SQLite

```sql
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_pdv TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL,
    preco_unitario REAL NOT NULL CHECK(preco_unitario > 0)
);

CREATE TABLE IF NOT EXISTS mesas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_mesa INTEGER UNIQUE NOT NULL,
    capacidade INTEGER NOT NULL DEFAULT 1 CHECK(capacidade >= 1),
    status TEXT NOT NULL DEFAULT 'OCUPADA' CHECK(status IN ('LIVRE', 'OCUPADA'))
);

CREATE TABLE IF NOT EXISTS comandas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mesa_id INTEGER,
    numero_mesa_historico INTEGER NOT NULL,
    data_abertura TEXT NOT NULL,
    data_fechamento TEXT,
    status TEXT NOT NULL DEFAULT 'ABERTA' CHECK(status IN ('ABERTA', 'PAGA', 'CANCELADA')),
    taxa_servico INTEGER NOT NULL DEFAULT 1 CHECK(taxa_servico IN (0, 1)),
    qtd_pessoas INTEGER NOT NULL DEFAULT 1 CHECK(qtd_pessoas >= 1),
    valor_total REAL NOT NULL DEFAULT 0.0 CHECK(valor_total >= 0.0),
    FOREIGN KEY(mesa_id) REFERENCES mesas(id) ON DELETE SET NULL
);

-- Garantia de no máximo uma comanda aberta por mesa
CREATE UNIQUE INDEX IF NOT EXISTS idx_comanda_unica_aberta 
ON comandas(mesa_id) WHERE status = 'ABERTA';

CREATE TABLE IF NOT EXISTS itens_comanda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comanda_id INTEGER NOT NULL,
    produto_id INTEGER,
    nome_produto_historico TEXT NOT NULL,
    categoria_historico TEXT,
    quantidade INTEGER NOT NULL DEFAULT 1 CHECK(quantidade >= 1),
    preco_momento REAL NOT NULL CHECK(preco_momento >= 0.0),
    observacao TEXT DEFAULT '',
    FOREIGN KEY(comanda_id) REFERENCES comandas(id) ON DELETE CASCADE,
    FOREIGN KEY(produto_id) REFERENCES produtos(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS fila_sincronizacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metodo TEXT NOT NULL,
    rota TEXT NOT NULL,
    payload_json TEXT,
    status TEXT NOT NULL DEFAULT 'PENDENTE' CHECK(status IN ('PENDENTE', 'ENVIADO', 'ERRO')),
    tentativas INTEGER NOT NULL DEFAULT 0,
    ultimo_erro TEXT,
    criado_em TEXT NOT NULL,
    processado_em TEXT
);

-- Índices de Performance
CREATE INDEX IF NOT EXISTS idx_produtos_codigo ON produtos(codigo_pdv);
CREATE INDEX IF NOT EXISTS idx_itens_comanda_cid ON itens_comanda(comanda_id);
CREATE INDEX IF NOT EXISTS idx_comandas_status ON comandas(status);
CREATE INDEX IF NOT EXISTS idx_fila_status ON fila_sincronizacao(status);
```

## Decisions

- **Decisão 1: Validação de Cardinalidade Nativa no SQLite (`idx_comanda_unica_aberta`)**:
  - *Motivação*: Impede que mesmo em caso de erro de clique duplo na interface duas comandas fiquem abertas para a mesma mesa física.
- **Decisão 2: Cooldown Adaptativo na Sincronização Xano**:
  - *Motivação*: Reduz o lag do Xano de minutos para milissegundos quando o salão está com ritmo moderado, e aplica o espaçador estrito apenas quando há rajadas de comandos.
- **Decisão 3: Sanitização Sistemática no Frontend**:
  - *Motivação*: Neutraliza o vetor de ataque XSS em todos os pontos com `unsafe_allow_html=True`.

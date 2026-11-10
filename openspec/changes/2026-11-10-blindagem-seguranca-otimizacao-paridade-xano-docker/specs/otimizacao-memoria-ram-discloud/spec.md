# Especificação Delta: Otimização de Memória RAM, SQLite WAL, Eliminação de $N+1$ e Execução Docker (512MB RAM / 0.50 CPU)

## Requisitos Modificados e Adicionados

### Requisito 1: Conformidade Total Zero-Pandas em Todo o Repositório
Nenhum arquivo do projeto (incluindo `pages/7_Auditoria.py`) DEVE importar `pandas`, `numpy` ou `pyarrow`.

#### Cenário: Exportação CSV e Tabela de Auditoria sem Pandas
- **DADO** que o Gerente acessa `pages/7_Auditoria.py`
- **QUANDO** visualizar a tabela de auditoria ou exportar o relatório CSV
- **ENTÃO** o sistema DEVE renderizar os dados usando estruturas nativas do Python (`list[dict]`) e gerar o CSV via `csv.DictWriter` + `io.StringIO`, economizando ~45 MB de RAM.

### Requisito 2: Modo `WAL` Persistente e Consultas Agregadas $O(1)$ (Sem Loops $N+1$)
O banco SQLite `churrascontrol.db` DEVE operar em `journal_mode = WAL`, e as listagens de salão, QR Codes e dashboard DEVEM utilizar `LEFT JOIN` + `GROUP BY` em consulta única.

#### Cenário: Carregamento do Salão e Dashboard em Consulta Única
- **DADO** um salão com múltiplas mesas e comandas abertas/fechadas
- **QUANDO** `listar_mesas()`, `listar_mesas_qrcodes()` ou `obter_dashboard_dados()` forem invocados
- **ENTÃO** o cálculo de totais e contagem de itens DEVE ocorrer no motor SQLite via `JOIN` sem executar queries dentro de loops Python.

### Requisito 3: Operação Estável em Container Docker com 512MB RAM e 0.50 CPU
O sistema DEVE rodar em container Docker local (`http://localhost:8080`) com limites rígidos de hardware (`mem_limit: 512m`, `cpus: 0.50`) e suportar carga concorrente E2E de todas as operações sem sofrer `OOMKilled` ou `database is locked`.


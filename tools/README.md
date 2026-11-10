# Ferramentas e Testes de Qualidade — ChurrasControl (`tools/`)

Este diretório centraliza todas as ferramentas de verificação, baterias de testes automatizados e utilitários de diagnóstico do banco de dados e sincronização.

---

## 🛠️ Ferramentas Disponíveis

### Utilitários Operacionais e de Sincronização
| Arquivo | Descrição | Como Executar |
| :--- | :--- | :--- |
| **`db_diagnostics.py`** | **Diagnóstico do Banco**: Inspeciona a integridade física do SQLite, modo de journal, chaves estrangeiras, contagem de todas as tabelas (produtos, comandas, colaboradores, sessões, auditoria), detalhamento de faturamento por status e erros na fila Xano. | `python tools/db_diagnostics.py` |
| **`seed_clean_xano.py`** | **Carga Inicial Xano**: Envia o catálogo de produtos e o colaborador gerente do SQLite para o Xano respeitando o rate limit de 2.5s por requisição. | `python tools/seed_clean_xano.py` |
| **`clean_sqlite.py`** | **Reset de Banco (Manual/Controlado)**: Limpeza profunda que preserva catálogo e gerente. Exige confirmação explícita (`--confirmar`) e **não roda automaticamente** para proteger o histórico de vendas. | `python tools/clean_sqlite.py --confirmar` |

### Bateria de Testes Automatizados (Consolidada)
| Arquivo | Descrição | Como Executar |
| :--- | :--- | :--- |
| **`run_all.py`** | **Orquestrador Central**: Executa a suíte completa de testes em um banco temporário isolado (sem tocar no banco real) e emite relatório executivo. | `python tools/run_all.py` |
| **`test_suite.py`** | **Suíte Unificada de Testes**: Reúne em 6 módulos integrados todas as validações de: sintaxe de telas, catálogo/delivery, salão/mesas/QR Code, segurança/XSS/regras SQLite, autenticação/RBAC e imutabilidade de vendas pós-restart. | `python tools/test_suite.py` |

---

## 🚀 Como Executar

A partir da raiz do projeto (`crudfaculdade/`):

```bash
# Executa todos os testes de uma vez só:
python tools/run_all.py

# Executa diagnóstico da saúde do SQLite e fila Xano:
python tools/db_diagnostics.py
```

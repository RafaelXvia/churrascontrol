# Ferramentas e Testes de Qualidade — ChurrasControl (`tools/`)

Este diretório centraliza todas as ferramentas de verificação, baterias de testes automatizados e utilitários de diagnóstico do banco de dados e sincronização.

---

## 🛠️ Ferramentas Disponíveis

| Arquivo | Descrição | Como Executar |
| :--- | :--- | :--- |
| **`run_all.py`** | **Orquestrador Central**: Executa todas as suítes de testes em sequência e gera um relatório com status e tempos de execução. | `python tools/run_all.py` |
| **`db_diagnostics.py`** | **Diagnóstico do Banco**: Inspeciona a integridade física do SQLite, modo WAL, chaves estrangeiras, contagem de tabelas e status da fila de sincronização com o Xano. | `python tools/db_diagnostics.py` |
| **`test_app.py`** | Valida a sintaxe e compilação de todas as páginas (`app.py`, `pages/*.py`) e operações do [data_manager.py](../data_manager.py). | `python tools/test_app.py` |
| **`test_sqlite_sync.py`** | Testa o ciclo de vida completo de mesa, abertura de comanda, agregação atômica de produtos, fechamento e gravação na fila SQLite. | `python tools/test_sqlite_sync.py` |
| **`test_security_performance.py`** | Valida restrições de domínio (preço negativo/zero), sanitização XSS, cardinalidade 1:1 de comanda por mesa e índices de performance. | `python tools/test_security_performance.py` |
| **`test_cardapio_delivery.py`** | Valida o schema completo de produtos (fotos Unsplash, descrição, estoque `qtd_disp`, flag `precisa_produzir` e disponibilidade). | `python tools/test_cardapio_delivery.py` |
| **`test_cardapio_cliente_qrcode.py`** | Testa a geração de tokens de QR Code para mesas, baixa automática de estoque na venda e confirmação de pré-comanda de cliente. | `python tools/test_cardapio_cliente_qrcode.py` |

---

## 🚀 Como Executar

A partir da raiz do projeto (`crudfaculdade/`):

```bash
# Executa todos os testes de uma vez só:
python tools/run_all.py

# Executa diagnóstico da saúde do SQLite e fila Xano:
python tools/db_diagnostics.py
```

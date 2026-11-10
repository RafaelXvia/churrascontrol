# Design Técnico — Criptografia de Colaboradores e Arquitetura Limpa Xano

## 1. Arquitetura de Criptografia Simétrica em `data_manager.py`

### 1.1 Algoritmo e Chave de Criptografia
Utiliza o padrão `cryptography.fernet.Fernet`:
- **Cifra**: AES-128 em modo CBC com padding PKCS7.
- **Autenticação de Integridade**: HMAC-SHA256 para evitar ataques de adulteração ou bit-flipping.
- **Formato de Armazenamento**: Token binário codificado em URL-safe Base64 com prefixo identificador `ENC:`.
- **Chave Mestra**: Derivada determinística através de `hashlib.sha256(b"CHURRASCONTROL_FERNET_MASTER_KEY_2026_INNOVATION_LAB").digest()`, permitindo também sobreposição via variável de ambiente `CHURRAS_ENCRYPTION_KEY`.

### 1.2 Funções Criptográficas
```python
def criptografar_dado(texto: str) -> str:
    # Retorna token Fernet seguro com prefixo "ENC:"

def descriptografar_dado(token: str) -> str:
    # Decodifica e valida assinatura HMAC, retornando texto plano original
```

### 1.3 Mapeamento de Campos
| Campo | No SQLite (`colaboradores`) | No Xano (`/colaborador`) | Em Memória/UI |
| :--- | :--- | :--- | :--- |
| `nome` | `ENC:gAAAAAB...` | `ENC:gAAAAAB...` | Ex.: "Rafael Gerente" |
| `numero` | `ENC:gAAAAAB...` | `ENC:gAAAAAB...` | Ex.: "(11) 98765-4321" |
| `cargo` | `ENC:gAAAAAB...` | `ENC:gAAAAAB...` | Ex.: "caixa" ou "gerente" |
| `senha_hash` | SHA-256 (Salted) | SHA-256 (Salted) | Oculto (nunca exibido) |
| `email` | Texto plano (chave de busca) | Texto plano | Ex.: `gerente@churrascontrol.com` |

## 2. Reestruturação do Diretório `crudfaculdade/xano/`

### 2.1 Esquema Alvo (Clean Architecture)
Apenas as tabelas do ecossistema do restaurante serão mantidas:
- `xano/table/mesas.xs`
- `xano/table/comandas.xs`
- `xano/table/itens_comanda.xs`
- `xano/table/produto.xs`
- `xano/table/colaborador.xs`
- `xano/api/churrascontrol/churrascontrol.xs` (e rotas oficiais)
- `xano/workspace/rafaels_workspace.xs`

Todos os arquivos de templates obsoletos (`cartaotoknzd`, `oe`, `op`, `solcancelamento`, `status_*`, `ttokenizacao`, `faq`, `cep`, `endereco`, etc.) são arquivados em backup prévio e eliminados da pasta ativa.

## 3. Script de Restauração para Nova Instância
Será fornecido `tools/restore_to_xano.py` que:
1. Lê o backup gerado (`backups/xano_full_backup.json` e tabelas SQLite).
2. Se conecta à URL base da nova instância fornecida pelo usuário.
3. Faz o seed automático de produtos, mesas e colaboradores criptografados via API.

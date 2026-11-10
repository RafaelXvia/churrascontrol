# Decisões Técnicas de Design — Saneamento e Reestruturação Modular

## 1. Diagnóstico Detalhado do Workspace Atual

### A. Inventário de Arquivos e Avaliação de Status
| Item | Tamanho Atual | Papel / Função | Ação Recomendada |
| :--- | :--- | :--- | :--- |
| `churrascontrol_teste.db` | ~258 KB | Banco gerado durante execução de testes automatizados | **Excluir da raiz.** Modificar testes para usar banco efêmero em pasta de testes/temp. |
| `churrascontrol.db` | ~237 KB | Banco SQLite de produção/operação local (WAL mode) | **Preservar intacto.** É a fonte da verdade local de dados. |
| `pages/__pycache__/*.cpython-315.pyc` | Vários | Bytecode compilado de versão legada/distinta de Python | **Remover com segurança.** |
| `tools/__pycache__/` | Vários | Caches de testes de módulos já saneados | **Remover com segurança.** |
| `backups/` | ~98 KB | Dumps SQL e JSON de contingência | **Preservar e isolar no backend.** |
| `.discloudignore` / `.gitignore` | Pequeno | Regras de exclusão de versionamento e deploy | **Atualizar e fortalecer.** |

---

## 2. Restrições e Compatibilidade de Plataforma

Ao reorganizar o projeto em Frontend e Backend, **três restrições rígidas** devem ser respeitadas:

### Restrição 1: Descoberta Nativa de Páginas no Streamlit
- O Streamlit possui uma convenção estrutural: quando executado via `streamlit run <script>`, ele busca automaticamente submódulos de navegação na pasta `pages/` localizada **no mesmo diretório do script de entrada**.
- Se movermos `pages/` para uma subpasta arbitrária sem configurar `st.navigation`, a barra de navegação e as rotas nativas podem falhar.
- **Decisão:** Manter a raiz com um ponto de entrada canônico e leve (`app.py`), permitindo que a camada de apresentação (`ui_components` e views) seja consumida de forma limpa, enquanto todo o motor de persistência e serviços vai para `backend/`.

### Restrição 2: Contêiner de Deploy na Discloud
- O arquivo `discloud.config` aponta explicitamente para:
  ```ini
  NAME=ChurrasControl
  TYPE=bot
  MAIN=run.py
  RAM=100
  VERSION=latest
  AUTORESTART=false
  ```
- O script `run.py` invoca o Streamlit via CLI:
  ```python
  sys.argv = ["streamlit", "run", "app.py", "--server.port=8080", ...]
  ```
- **Decisão:** O comando `python run.py` na raiz **deve continuar funcionando sem nenhuma alteração no arquivo `discloud.config`**.

### Restrição 3: Xano Developer MCP e Arquivos XanoScript (`.xs`)
- O servidor `@xano/developer-mcp` (configurado em `.vscode/mcp.json` e `.gemini/settings.json`) espera encontrar as pastas `xano/api/` e `xano/table/` relativas à raiz do workspace.
- **Decisão:** Agrupar `xano/` dentro de `backend/xano/`, mantendo um atalho/link simbólico ou definindo a raiz de trabalho para que o MCP e o Xano CLI continuem operacionais.

---

## 3. Arquitetura Modular Proposta

```
crudfaculdade/
├── app.py                      # Ponto de entrada leve da aplicação Streamlit
├── run.py                      # Script de orquestração para Discloud (porta 8080)
├── requirements.txt            # Dependências unificadas do ecossistema
├── README.md                   # Documentação profissional e universal de onboarding
├── .env.example                # Template de variáveis de ambiente
├── .gitignore                  # Regras reforçadas (ignora bancos de teste, .env e pycache)
├── .discloudignore             # Otimização do bundle de deploy
│
├── backend/                    # ══════ NÚCLEO DE DADOS, REGRAS & INTEGRAÇÃO ══════
│   ├── __init__.py             # Pacote Python com exports diretos
│   ├── database/               # Persistência relacional
│   │   ├── __init__.py
│   │   ├── data_manager.py     # CRUD transacional SQLite, WAL mode e fila de sincronização
│   │   └── schema.sql          # DDL declarativo e idempotente do banco
│   ├── ai/                     # Inteligência Artificial e RAG
│   │   ├── __init__.py
│   │   ├── ontologia.py        # Triple Store de domínio e axiomas contábeis
│   │   └── assistente_ia.py    # Motor RAG com Google Gemini e fallback em cascata
│   ├── xano/                   # Schemas e endpoints XanoScript (.xs)
│   │   ├── api/                # Endpoints REST de negócio
│   │   └── table/              # Estruturas de tabelas relacionais
│   └── backups/                # Backups estruturados (SQL e JSON)
│
├── frontend/                   # ══════ CAMADA VISUAL E APRESENTAÇÃO ══════
│   ├── __init__.py
│   ├── components/             # Componentes modulares
│   │   ├── __init__.py
│   │   └── ui_components.py    # Navbar, autenticação RBAC, cards e modais
│   └── styles/                 # Estilos CSS injetáveis e temas
│
├── pages/                      # ══════ TELAS MULTI-PAGE DO STREAMLIT ══════
│   ├── 1_Salao_e_Mesas.py
│   ├── 2_Cardapio.py
│   ├── 3_Relatorios.py
│   ├── 4_Mesas_QRCodes.py
│   ├── 5_Cardapio_Cliente.py
│   ├── 6_Colaboradores.py
│   ├── 7_Auditoria.py
│   └── 8_Assistente_IA.py
│
├── docs/                       # ══════ ESPECIFICAÇÕES E DOCUMENTAÇÃO TÉCNICA ══════
│   ├── project-overview.md
│   ├── domain-model.md
│   └── mcp-xano.md
│
├── openspec/                   # ══════ ESPECIFICAÇÃO DIRIGIDA (OPENSPEC) ══════
│   ├── changes/
│   └── specs/
│
└── tools/                      # ══════ SUÍTE DE TESTES E DIAGNÓSTICO ══════
    ├── run_all.py              # Orquestrador de testes com relatório executivo
    ├── test_suite.py           # Bateria de testes automatizados
    ├── db_diagnostics.py       # Auditoria de integridade do SQLite e fila Xano
    ├── seed_clean_xano.py      # Carga de catálogo com rate limit
    └── seed_vendas_demo.py     # Gerador de histórico realista para RAG
```

---

## 4. Estratégia de Transição e Retrocompatibilidade (Zero Breaking Changes)

Para garantir que nenhum import quebre durante a transição:
1. **Fachadas na Raiz (Root Facades):**
   - Na raiz do projeto, `data_manager.py`, `ontologia.py`, `assistente_ia.py` e `ui_components.py` serão mantidos como módulos de redirecionamento transparente:
     ```python
     # data_manager.py (raiz)
     from backend.database.data_manager import *
     ```
   - Isso permite que `import data_manager` continue funcionando perfeitamente em `tools/test_suite.py`, em `pages/` e em scripts legados sem nenhuma alteração imediata.
2. **Isolamento de Banco de Testes:**
   - O orquestrador `tools/run_all.py` e a classe base em `tools/test_suite.py` definirão a variável de ambiente:
     ```python
     os.environ["CHURRAS_DB_PATH"] = os.path.join(tempfile.gettempdir(), f"churras_test_{uuid.uuid4().hex[:8]}.db")
     ```
   - Ao término da execução dos testes, o arquivo temporário será automaticamente excluído pelo `tearDownClass`, impedindo que bancos temporários voltem a ser gerados na raiz do projeto.

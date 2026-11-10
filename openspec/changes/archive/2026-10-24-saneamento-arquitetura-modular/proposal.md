# Proposta Formal de Mudança — Saneamento de Arquivos Órfãos e Reestruturação Modular

## 1. Contexto & Problema
O repositório do **ChurrasControl** evoluiu organicamente ao longo de mais de 18 mudanças OpenSpec, agregando funcionalidades completas de gestão de salão, comandas, produtos, autenticação RBAC com criptografia, relatórios analíticos em PDF e o Assistente IA do Gerente com RAG e ontologia de domínio.

Contudo, com o crescimento acelerado, surgiram dois pontos de atenção na organização do projeto:
1. **Acúmulo de Arquivos Transitórios e Órfãos na Raiz:**
   - O banco de dados SQLite de teste `churrascontrol_teste.db` (258 KB) permanece salvo na raiz do projeto após baterias de testes manuais/automatizados.
   - Caches de compilação `.pyc` residuais de versões legadas do interpretador (ex: `.cpython-315.pyc` na pasta `pages/__pycache__/`) poluem o histórico e o disco.
   - Regras de exclusão no `.gitignore` e `.discloudignore` ainda não cobrem preventivamente bancos temporários com o sufixo `*_teste.db` ou arquivos de sessão transitórios.
2. **Falta de Segregação de Camadas (Frontend vs Backend vs Xano):**
   - Atualmente, módulos de backend com alta complexidade de regras de negócio (`data_manager.py`, `ontologia.py`, `assistente_ia.py`), componentes visuais (`ui_components.py`), o ponto de entrada da aplicação (`app.py`), páginas do Streamlit (`pages/`), esquemas Xano (`xano/`), scripts de deploy (`run.py`, `discloud.config`) e testes (`tools/`) residem todos "planos" na raiz.
   - Para um novo desenvolvedor que clonar o projeto ou for avaliá-lo academicamente, essa sobreposição de arquivos na raiz mascara a separação conceitual entre lógica de negócios/persistência e camada de apresentação.

---

## 2. Objetivos da Mudança
1. **Higiene e Saneamento Estrito:**
   - Auditar e remover arquivos não utilizados, caches legados de compilação e artefatos de teste gerados localmente.
   - Ajustar a suíte de testes (`tools/run_all.py` e `tools/test_suite.py`) para utilizar banco temporário isolado via `tempfile` ou diretório dedicado `tmp/` devidamente ignorado pelo git.
   - Fortalecer `.gitignore` e `.discloudignore` contra o commit acidental de arquivos de teste e dados transitórios.
2. **Reestruturação Arquitetural Modular (Frontend / Backend / Xano):**
   - Desenhar e implementar uma estrutura de diretórios limpa e elegante, segregando explicitamente:
     - **Backend / Core:** Persistência relacional (`data_manager`), ontologia (`ontologia`), motor analítico RAG (`assistente_ia`) e esquemas de dados Xano (`xano/`).
     - **Frontend / UI:** Componentes visuais estilizados (`ui_components`), páginas do salão e atendimento (`pages/`).
     - **Raiz Limpa:** Apenas os pontos de entrada canônicos (`app.py`, `run.py`, `requirements.txt`, `README.md`, `.env.example`).
3. **Garantia de Não-Regressão e Retrocompatibilidade:**
   - Manter fachadas (*facades*) de importação para que referências legadas não quebrem a execução local, a suíte de testes em `tools/` ou o deploy na Discloud.
   - Garantir compatibilidade com as regras de descoberta de páginas nativas do Streamlit.
   - Preservar o funcionamento do **Xano Developer MCP** configurado no VS Code e Gemini.

---

## 3. Escopo de Arquivos Afetados
- **Arquivos a serem removidos/ignorados:** `churrascontrol_teste.db`, arquivos `.pyc` residuais em `pages/__pycache__/` e `tools/__pycache__/`.
- **Arquivos de Configuração de Ignore:** `.gitignore`, `.discloudignore`.
- **Módulos do Backend:** `data_manager.py`, `ontologia.py`, `assistente_ia.py`, diretório `xano/`.
- **Módulos do Frontend:** `ui_components.py`, `app.py`, diretório `pages/`.
- **Suíte de Testes:** `tools/test_suite.py`, `tools/run_all.py`.

---

## 4. Benefícios Esperados
- Redução de ruído e poluição visual no workspace.
- Facilidade de manutenção: separação evidente de responsabilidades (SoC — Separation of Concerns).
- Zero risco de banco de teste subir para o GitHub ou ser enviado para o contêiner da Discloud.
- 100% de conformidade com os testes automatizados e regras de qualidade do projeto.

# Decisões Técnicas de Design — Documentação Universal e Onboarding

## 1. Estrutura Estratégica do `README.md` Principal

O arquivo `README.md` da raiz do repositório será projetado como o cartão de visitas executivo e técnico do **ChurrasControl**. Ele seguirá o padrão de documentação de projetos de código aberto de alto impacto, estruturado nas seguintes seções:

```
README.md
├── 1. Header & Badges (Python 3.10+, Streamlit, SQLite WAL, Gemini, Xano, ReportLab, Discloud)
├── 2. Visão Geral do Sistema (O que é o ChurrasControl, dor que resolve e público-alvo)
├── 3. Principais Módulos & Recursos (Salão, Cardápio, QR Code, Relatórios PDF, RBAC, RAG IA)
├── 4. Arquitetura da Solução (Diagrama conceitual de dados, segurança e integrações)
├── 5. Pré-requisitos do Ambiente (Python 3.10 ou superior, Git)
├── 6. Guia Passo a Passo de Instalação Universal (git clone -> venv -> pip install)
├── 7. Configuração de Variáveis de Ambiente (.env e Chaves de API)
├── 8. Execução Local e Acesso (Portas 8080 / 8501 e URLs)
├── 9. Credenciais de Teste & Recuperação de Acesso (Gerente, Caixa, Chave Mestra)
├── 10. Qualidade e Testes Automatizados (tools/run_all.py e db_diagnostics.py)
├── 11. Guia de Deploy na Discloud (Hospedagem em nuvem)
└── 12. Metodologia OpenSpec & Diretrizes de Desenvolvimento
```

---

## 2. Princípios de Universalidade e Portabilidade

Para assegurar que qualquer desenvolvedor tenha uma experiência sem atritos após o `git clone`:

### A. Neutralidade de Sistema Operacional (Cross-Platform)
- Fornecer os comandos tanto para **Windows (PowerShell/CMD)** quanto para **Linux / macOS (Bash/Zsh)**:
  - Criação de venv:
    - Windows: `python -m venv venv`
    - Unix: `python3 -m venv venv`
  - Ativação de venv:
    - Windows: `.\venv\Scripts\Activate.ps1` (ou `venv\Scripts\activate.bat`)
    - Unix: `source venv/bin/activate`

### B. Neutralidade de Caminhos de Arquivo
- **Proibido** o uso de caminhos absolutos (ex: `C:\Users\...` ou `/home/usuario/...`).
- Todos os links no markdown devem ser **relativos à raiz do repositório** (ex: `docs/project-overview.md`, `tools/run_all.py`).
- Não assumir que a pasta clonada terá um nome fixo; todas as instruções se referem ao "diretório raiz do projeto clonado".

### C. Isolamento de Segredos e Chaves de API
- O arquivo `.env` real **nunca** deve ser versionado no Git.
- O `README.md` e o `.env.example` devem explicar claramente como obter a chave gratuita no **Google AI Studio** (`https://aistudio.google.com/`) e como preencher:
  ```env
  GOOGLE_API_KEY_1=AIzaSy...
  GOOGLE_API_KEY_2=AIzaSy...
  XANO_BASE_URL=https://x8ki-letl-twmt.n7.xano.io/api:churrascontrol
  ```
- O assistente foi desenhado com **fallback determinístico offline**: mesmo se a pessoa não tiver uma chave do Gemini no momento do clone, o sistema inicia e funciona perfeitamente, informando de modo elegante no chat que as chaves podem ser adicionadas posteriormente.

---

## 3. Revisão e Saneamento de Arquivos em `docs/` e `AGENTS.md`

| Arquivo | Problema Atual | Ajuste Projetado |
| :--- | :--- | :--- |
| `docs/project-overview.md` | Menção fixa à pasta `crudfaculdade/` no item de diretrizes | Atualizar para referenciar a raiz do projeto de forma agnóstica. |
| `docs/mcp-xano.md` | Passo 4 instrui abrir a pasta `crudfaculdade` | Generalizar para "abra a pasta raiz do projeto clonado". |
| `AGENTS.md` | Menção a diretórios externos específicos de backup do usuário | Manter a regra de preservação, mas deixar a nomenclatura limpa e universal. |

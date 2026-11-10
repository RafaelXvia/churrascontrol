# 🍖 ChurrasControl — Ponto de Venda & Gestão de Mesas

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-WAL%20Mode-003B57.svg?logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-RAG%20IA-8E75C4.svg?logo=google&logoColor=white)](https://aistudio.google.com/)
[![Xano](https://img.shields.io/badge/Xano-Cloud%20Sync-FF5722.svg?logo=xano&logoColor=white)](https://www.xano.com/)
[![Discloud](https://img.shields.io/badge/Deploy-Discloud-5865F2.svg)](https://discloudbot.com/)
[![License](https://img.shields.io/badge/Licen%C3%A7a-Acad%C3%AAmica-green.svg)](#)

O **ChurrasControl** é uma plataforma moderna e completa de automação comercial e Ponto de Venda (PDV) voltada para o setor de alimentação (restaurantes, churrascarias, bares e cafeterias). Desenvolvido com foco em **alta disponibilidade**, **experiência do usuário (UX)** e **resiliência operacional**, o sistema combina interface reativa em **Streamlit**, persistência transacional local em **SQLite (WAL)** com sincronização em nuvem via **Xano** e um motor de inteligência analítica com **Google Gemini RAG**.

---

## 📌 Sumário
- [1. Visão Geral e Dores Resolvidas](#1-visão-geral-e-dores-resolvidas)
- [2. Módulos do Sistema](#2-módulos-do-sistema)
- [3. Arquitetura da Solução](#3-arquitetura-da-solução)
- [4. Pré-requisitos](#4-pré-requisitos)
- [5. Guia Rápido de Instalação (Zero ao Deploy)](#5-guia-rápido-de-instalação-zero-ao-deploy)
- [6. Configuração de Ambiente (.env)](#6-configuração-de-ambiente-env)
- [7. Execução Local](#7-execução-local)
- [8. Credenciais de Acesso e Perfis Operacionais](#8-credenciais-de-acesso-e-perfis-operacionais)
- [9. Qualidade e Testes Automatizados](#9-qualidade-e-testes-automatizados)
- [10. Deploy em Produção (Discloud)](#10-deploy-em-produção-discloud)
- [11. Metodologia OpenSpec e Governança](#11-metodologia-openspec-e-governança)

---

## 1. Visão Geral e Dores Resolvidas
Restaurantes de pequeno e médio porte frequentemente sofrem com:
- **Perda de comandas em oscilações de rede:** O ChurrasControl opera no modelo *Offline-First* — transações gravam localmente no SQLite WAL e são sincronizadas de forma resiliente na nuvem Xano.
- **Dificuldade de controle de mesas e autoatendimento:** O sistema gera QR Codes únicos por mesa para autoatendimento do cliente sem necessidade de app externo.
- **Divisão de contas complexa:** Cálculo automático com ou sem taxa de serviço (10%) e divisão exata por pagantes.
- **Tomada de decisão sem inteligência:** Assistente de IA RAG com ontologia do negócio para diagnóstico de vendas, pratos mais lucrativos e gargalos de atendimento.

---

## 2. Módulos do Sistema

| Módulo / Tela | Arquivo | Perfil Mínimo | Descrição |
| :--- | :--- | :--- | :--- |
| **Visão Geral** | `app.py` | Livre / Autenticado | Dashboard de boas-vindas, status do sistema e login |
| **Salão & Mesas** | `pages/1_Salao_e_Mesas.py` | Caixa / Gerente | Grid em tempo real das mesas, abertura de comanda, lançamento de itens e fechamento |
| **Cardápio** | `pages/2_Cardapio.py` | Caixa / Gerente | Catálogo interativo, cadastro/edição de produtos, código PDV e filtros |
| **Métricas** | `pages/3_Metricas.py` | Gerente | Dashboards analíticos com Chart.js e exportação executiva em PDF via ReportLab |
| **QR Codes de Mesas** | `pages/4_Mesas_QRCodes.py` | Caixa / Gerente | Geração e impressão de tokens QR Code para cardápio digital |
| **Cardápio do Cliente** | `pages/5_Cardapio_Cliente.py` | Cliente (Mesa) | Autoatendimento mobile com carrinho e envio de pedidos direto à cozinha |
| **Colaboradores** | `pages/6_Colaboradores.py` | Gerente | Gestão de equipe com RBAC e senhas com hash PBKDF2-SHA256 |
| **Auditoria** | `pages/7_Auditoria.py` | Gerente | Trilha de auditoria operacional e eventos de segurança |
| **Assistente IA** | `pages/8_Assistente_IA.py` | Gerente | Consultor de negócios com RAG semântico e Google Gemini |

---

## 3. Arquitetura da Solução

```text
       ┌────────────────────────────────────────────────────────┐
       │                   FRONTEND (Streamlit)                 │
       │   Navbar Unificada • Design System • Modais • CSS      │
       └───────────────────────────┬────────────────────────────┘
                                   │ Python APIs
       ┌───────────────────────────▼────────────────────────────┐
       │               BACKEND (Camada de Serviços)              │
       │   backend/database/          backend/ai/               │
       │   • data_manager.py          • ontologia.py            │
       │   • SQLite WAL               • assistente_ia.py        │
       └──────────────┬────────────────────────────┬────────────┘
                      │                            │
                      ▼                            ▼
       ┌──────────────────────────┐   ┌─────────────────────────┐
       │   NUVEM XANO (REST API)  │   │     GOOGLE GEMINI IA    │
       │   Fila Assíncrona SQLite │   │  RAG Somente-Leitura    │
       │   Rate Limit Protegido   │   │  Fallback Multi-Chave   │
       └──────────────────────────┘   └─────────────────────────┘
```

---

## 4. Pré-requisitos
- **Python 3.10** ou superior instalado ([python.org](https://www.python.org/))
- **Git** ([git-scm.com](https://git-scm.com/))
- Conexão com a Internet para a primeira instalação de pacotes e sincronização em nuvem

---

## 5. Guia Rápido de Instalação (Zero ao Deploy)

### Passo 1: Clone do Repositório
```bash
git clone https://github.com/seu-usuario/churrascontrol.git
cd churrascontrol
```

### Passo 2: Criação e Ativação do Ambiente Virtual

**No Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(Caso o PowerShell bloqueie scripts, execute antes: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`)*

**No Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**No Linux / macOS (Bash / Zsh):**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Passo 3: Instalação das Dependências
```bash
pip install -r requirements.txt
```

### Passo 4: Configuração do `.env`
Copie o template de exemplo:
```bash
cp .env.example .env
```
*(No Windows PowerShell: `Copy-Item .env.example .env`)*

---

## 6. Configuração de Ambiente (.env)

Abra o arquivo `.env` e configure as credenciais:

```env
# URL Base da API REST no Xano
XANO_BASE_URL=https://x8ki-letl-twmt.n7.xano.io/api:churrascontrol
XANO_API_KEY=

# Chaves de API do Google Gemini (obtenha gratuitamente em https://aistudio.google.com/)
GOOGLE_API_KEY_1=sua_chave_primaria_aqui
GOOGLE_API_KEY_2=sua_chave_secundaria_de_fallback_opcional

# Porta de execução local (padrão: 8080)
PORT=8080
```

> **Nota:** Caso não configure uma chave do Gemini, o sistema continua funcionando 100% de forma local e offline; o módulo do assistente apresentará resposta elegante informando que aguarda as chaves.

---

## 7. Execução Local

Você pode iniciar o ChurrasControl por dois métodos:

### Método 1: Execução Padrão Streamlit (Recomendado para Desenvolvimento)
```bash
streamlit run app.py
```
O navegador abrirá automaticamente em `http://localhost:8501` (ou na porta configurada).

### Método 2: Execução com Orquestrador de Nuvem (Porta 8080)
```bash
python run.py
```
Acesse no navegador: `http://localhost:8080`.

---

## 8. Credenciais de Acesso e Perfis Operacionais

O sistema já vem inicializado com colaboradores de teste para avaliação imediata:

| Papel / Perfil | E-mail de Acesso | Senha | Acesso Permitido |
| :--- | :--- | :--- | :--- |
| **Gerente** | `gerente@churrascontrol.com` | `1q2w` | Acesso Irrestrito (Salão, Cardápio, Métricas, Colaboradores, Auditoria, IA) |
| **Caixa** | `joao@churrascontrol.com` | `1q2w` | Operação (Salão, Mesas, Lançamentos, Fechamento de Comandas e QR Codes) |
| **Contingência** | Chave Mestra | `CHURRAS-REC-2026` / `ADMIN123` | Recuperação e redefinição emergencial de credenciais |

---

## 9. Qualidade e Testes Automatizados

O ChurrasControl possui uma suíte consolidada de testes automatizados que valida integridade estrutural, compilação de telas, ciclo de comandas, segurança, imutabilidade histórica e fallback de IA.

### Executar Toda a Bateria de Testes
```bash
python tools/run_all.py
```
*Os testes são executados em um banco de dados SQLite efêmero e isolado em memória temporária, garantindo 0% de risco ao histórico real.*

### Executar Diagnóstico de Saúde do Banco de Dados
```bash
python tools/db_diagnostics.py
```
*Verifica integridade do SQLite, contagem de registros, status das comandas e fila de sincronização com o Xano.*

---

## 10. Deploy em Produção (Discloud)

O projeto está 100% preparado para deploy contínuo em contêiner na plataforma **Discloud**:

1. Arquivo de configuração: `discloud.config`:
   ```ini
   NAME=ChurrasControl
   TYPE=bot
   MAIN=run.py
   RAM=100
   VERSION=latest
   AUTORESTART=false
   ```
2. Arquivo de otimização de bundle: `.discloudignore` ignora caches, testes, banco efêmero e documentações internas, reduzindo o tempo de upload e o consumo de memória.
3. Para publicar, compacte os arquivos do projeto (respeitando o `.discloudignore`) em um arquivo `.zip` e faça o upload no painel ou via CLI da Discloud.

---

## 11. Metodologia OpenSpec e Governança

Todas as mudanças arquiteturais e novas funcionalidades do ChurrasControl seguem estritamente a metodologia **OpenSpec (Spec-Driven Development)**:

- `openspec/changes/`: Propostas formais de mudança em andamento (`proposal.md`, `design.md`, `tasks.md`).
- `openspec/specs/`: Especificações normativas e requisitos de negócio por domínio.
- `docs/project-overview.md`: Visão técnica e de negócio aprofundada.
- `docs/domain-model.md`: Modelo relacional de domínio e regras de imutabilidade.
- `docs/mcp-xano.md`: Integração com o Xano Developer MCP.

---
**ChurrasControl** — *Desenvolvido com excelência técnica para o ecossistema de alimentação e gastronomia.*

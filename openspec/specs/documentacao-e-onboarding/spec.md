# documentacao-e-onboarding Specification

## Purpose
Garantir que novos desenvolvedores, avaliadores e agentes de IA consigam clonar, instalar dependências, configurar ambiente e executar o ChurrasControl em qualquer sistema operacional (Windows, Linux, macOS) sem atritos ou dependências de caminhos locais específicos.

## Requirements

### Requirement: Documentação Universal e README Executivo
O sistema SHALL disponibilizar `README.md` completo e profissional na raiz do repositório, cobrindo:
1. Resumo executivo, dores de mercado resolvidas e público-alvo.
2. Badges de tecnologias e arquitetura conceitual em diagrama ASCII.
3. Guia de instalação passo a passo multiplataforma (Windows PowerShell/CMD e Linux/macOS).
4. Tabela de perfis operacionais e credenciais de teste para avaliação imediata.
5. Instruções claras de execução local (`streamlit run app.py` e `python run.py`).
6. Comandos para execução de bateria de testes (`tools/run_all.py`) e diagnóstico (`tools/db_diagnostics.py`).
7. Instruções para deploy em nuvem na Discloud.

#### Scenario: Onboarding por novo desenvolvedor após git clone
- **WHEN** um usuário ou avaliador clona o repositório
- **THEN** o `README.md` SHALL conter todos os comandos necessários para criar ambiente virtual, instalar dependências e executar o sistema sem erros de configuração.

### Requirement: Neutralidade e Universalidade de Documentação
Todos os arquivos de documentação em `docs/` e `AGENTS.md` SHALL utilizar referências relativas à raiz do repositório, sem apontamentos para caminhos absolutos com letras de unidade de disco local.

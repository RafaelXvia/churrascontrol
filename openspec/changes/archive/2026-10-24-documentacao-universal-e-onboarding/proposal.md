# Proposta Formal de Mudança — Documentação Universal, Onboarding para `git clone` e README Executivo

## 1. Contexto & Problema
O **ChurrasControl** é uma aplicação completa com alta sofisticação técnica (arquitetura transacional SQLite WAL, sincronização com Xano, criptografia AES-256/Fernet, RBAC, ontologia relacional e RAG assistido por Google Gemini). 

No entanto, atualmente:
1. **Ausência de README.md na Raiz:**
   - O projeto possui `tools/README.md` (focado exclusivamente na suíte de testes), mas **não possui um `README.md` principal na raiz**.
   - Qualquer pessoa, avaliador acadêmico ou colega de time que fizer um `git clone` do repositório fica sem instruções imediatas de como criar o ambiente virtual, instalar os pacotes, configurar o `.env`, iniciar a aplicação ou rodar os testes.
2. **Presença de Referências a Caminhos e Pastas Específicas do PC:**
   - Documentos e comentários continham referências a diretórios específicos do ambiente local (ex: referências a pastas de downloads, caminhos absolutos com letras de disco do Windows ou nomes fixos de pastas como `crudfaculdade/` vs `crudfaculdade_22-10_assistente/`).
   - Se o projeto for clonado em outra máquina (Linux, Mac ou Windows em outro caminho de usuário), instruções que dependem de caminhos rígidos geram confusão.
3. **Credenciais e Portas Não Documentadas Centralizadamente:**
   - As credenciais iniciais de teste (`gerente@churrascontrol.com`, senha `1q2w`), a chave mestre de recuperação (`CHURRAS-REC-2026`) e a porta padrão (`8080` / `8501`) não estão consolidadas em um local público de rápida consulta.

---

## 2. Objetivos da Mudança
1. **Criar um `README.md` Profissional na Raiz:**
   - Apresentar o projeto com clareza executiva e acadêmica (visão geral, telas, problema resolvido e valor de negócio).
   - Diagrama de arquitetura em ASCII/Mermaid (Frontend Streamlit, SQLite WAL, Fila Xano, Ontologia, Google Gemini RAG).
   - Guia de Início Rápido Universal em 4 comandos (`git clone`, `venv`, `pip install`, `streamlit run app.py`).
   - Tabela explicativa de credenciais de acesso padrão para testes.
   - Instruções de configuração de APIs (`.env` com `GOOGLE_API_KEY_1`, `GOOGLE_API_KEY_2`, `XANO_BASE_URL`).
   - Guia de execução da bateria de testes e diagnóstico do banco.
   - Instruções de deploy na nuvem Discloud.
2. **Universalizar a Documentação Existente (`docs/` e `AGENTS.md`):**
   - Garantir que todos os arquivos de documentação (`docs/project-overview.md`, `docs/domain-model.md`, `docs/mcp-xano.md`, `AGENTS.md`) utilizem referências relativas, comandos multiplataforma (Windows PowerShell / CMD / Linux bash / macOS zsh) e nenhuma referência a caminhos locais de computador.
   - Especificar claramente o isolamento de pastas e o fluxo do OpenSpec.

---

## 3. Benefícios Esperados
- **Onboarding em Menos de 3 Minutos:** Qualquer pessoa consegue clonar o projeto e colocá-lo para rodar em seu próprio computador sem depender de ajuda manual.
- **Portabilidade Total:** O repositório torna-se 100% agnóstico a sistema operacional e estrutura de diretórios do desenvolvedor.
- **Apresentação de Alto Nível:** Visual executivo e profissional no GitHub / repositório de entrega.

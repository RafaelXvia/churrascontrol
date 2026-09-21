# Diretrizes para Agentes de IA — ChurrasControl

## 1. Princípio Fundamental & Isolamento Estrito de Diretórios
- **ESCOPO EXCLUSIVO DE MODIFICAÇÃO**: Todo o código, configurações, migrações e testes do projeto residem **EXCLUSIVAMENTE** dentro da pasta `crudfaculdade/`.
- **PROIBIDO ALTERAR PASTAS EXTERNAS**:
  - `material do professor/`: Diretório de **apenas leitura e consulta técnica**. Nunca criar, modificar, mover ou apagar nenhum arquivo nele.
  - `discloud/` (na raiz do workspace): Diretório **reservado para backups manuais do usuário**. Jamais mexer, alterar ou apagar.
- Nenhuma alteração significativa de funcionalidade ou arquitetura deve ser executada sem prévio planejamento via OpenSpec (`spec-driven`).
- Consulte sempre `docs/project-overview.md` e `docs/domain-model.md` antes de implementar novas features.

## 2. Padrões de Arquitetura e Código
- **Backend**: Python 3.10+ utilizando FastAPI com tipagem estrita via Pydantic.
- **Frontend**: O frontend do projeto deve ser implementado exclusivamente com **Streamlit**. Não introduza React, Vue, Angular, Next.js, Jinja2 ou outra tecnologia de frontend para substituir ou complementar o Streamlit, salvo quando houver uma alteração arquitetural explicitamente aprovada para o projeto.
- **Persistência**: Persistência relacional transacional em SQLite embutido (`churrascontrol.db` em modo WAL) com fila persistente de sincronização para o Xano (`fila_sincronizacao`).
- **Imutabilidade Histórica**: Preços de itens lançados em comanda nunca devem depender de lookup dinâmico do produto em tempo de fechamento. Salve sempre `preco_momento` e `nome_produto_historico`.

## 3. Segurança e Robustez
- Todas as regras de negócio e validações (ex: validação de mesas ativas, unicidade de código PDV, fechamento de comandas) devem ser validadas no backend, tratando o frontend apenas como camada visual.
- Rate limits para integrações de terceiros (como o Xano Free Tier) devem ser respeitados via worker desacoplado.

## 4. Integração com Xano Developer MCP
- O projeto possui o **Xano Developer MCP** configurado em `.vscode/mcp.json` e `.gemini/settings.json`.
- Os agentes de IA devem utilizar este MCP para validar arquivos XanoScript (`.xs`), consultar documentação da Meta API / Run API e garantir paridade estrita com o backend Xano antes de sugerir comandos de `xano workspace push`.
- Consulte `docs/mcp-xano.md` para instruções detalhadas.

## 5. Ciclo de Trabalho OpenSpec Obrigatório (Spec-Driven Development)
**REGRA MANDATÓRIA**: Sempre que o usuário solicitar uma **nova funcionalidade**, reformulação de tela, adição de tabelas ou alteração significativa (como feito na modernização do cardápio visual e modais), o agente **DEVE SEGUIR O CICLO COMPLETO DO OPENSPEC**:

1. **Explore (Investigação e Diagnóstico)**:
   - Identificar impactos em banco de dados SQLite (`churrascontrol.db`), tabelas e colunas necessárias.
   - Analisar reflexos na fila de sincronização com o Xano (`fila_sincronizacao`).
   - Mapear componentes de UI e fluxo de interação em Streamlit.
   - Avaliar riscos de regressão e compatibilidade.

2. **Propose (Proposta Formal de Mudança)**:
   - Criar a pasta de change em `openspec/changes/<YYYY-MM-DD-nome-da-funcionalidade>/`.
   - Gerar os quatro arquivos essenciais da proposta:
     - `.openspec.yaml`: Metadados da change (ID, título, data, status).
     - `proposal.md`: Contexto de negócio, problema resolvido, escopo e benefícios.
     - `design.md`: Decisões técnicas de arquitetura, componentes UI, persistência e estratégia de fallback.
     - `tasks.md`: Lista granular de tarefas com critérios de aceite explícitos.
   - Registrar as especificações delta ou novos requisitos no diretório `specs/`.

3. **Review (Alinhamento e Validação)**:
   - Apresentar a proposta estruturada para revisão e validação do usuário antes de codificar grandes refatorações.

4. **Apply (Implementação Guiada por Tarefas)**:
   - Executar estritamente o plano detalhado em `tasks.md`.
   - Escrever testes automatizados unitários/integração para cada novo comportamento.
   - Garantir 100% de aprovação na suíte de testes.

5. **Archive (Consolidação e Arquivamento)**:
   - Atualizar a especificação principal em `openspec/specs/<dominio>/spec.md` incorporando os novos requisitos definitivos.
   - Mover a pasta da change para `openspec/changes/archive/<YYYY-MM-DD-nome-da-funcionalidade>/`.
   - Atualizar o status para `archived` no `.openspec.yaml`.

## 6. Boas Práticas de Versionamento Git
- Antes de iniciar modificações complexas, preservar a branch funcional estável (`funcional`).
- Desenvolver e testar em branches de feature (`feature/<nome-da-funcionalidade>`).
- Ao concluir e validar os testes e a documentação OpenSpec, realizar o merge na linha original principal do projeto (`main` / `master`), garantindo que o branch padrão permaneça 100% operacional.
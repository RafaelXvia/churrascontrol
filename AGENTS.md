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

## 5. Ciclo de Trabalho OpenSpec
1. **Explore**: Investigue impactos, riscos e dependências.
2. **Propose**: Crie artefatos (`proposal.md`, `specs/`, `design.md`, `tasks.md`).
3. **Review**: Valide escopo e viabilidade técnica antes de gerar código.
4. **Apply**: Implemente estritamente as tarefas mapeadas em `tasks.md`.
5. **Archive**: Atualize a especificação principal e arquive a change.
# Diretrizes para Agentes de IA — ChurrasControl

## 1. Princípio Fundamental
- Nenhuma alteração significativa de funcionalidade ou arquitetura deve ser executada sem prévio planejamento via OpenSpec (`spec-driven`).
- Consulte sempre `docs/project-overview.md` e `docs/domain-model.md` antes de implementar novas features.

## 2. Padrões de Arquitetura e Código
- **Backend**: Python 3.10+ utilizando FastAPI com tipagem estrita via Pydantic.
- **Frontend**: O frontend do projeto deve ser implementado exclusivamente com **Streamlit**. Não introduza React, Vue, Angular, Next.js, Jinja2 ou outra tecnologia de frontend para substituir ou complementar o Streamlit, salvo quando houver uma alteração arquitetural explicitamente aprovada para o projeto.
- **Persistência**: Manter compatibilidade entre o cache estruturado em `churras_data.json`, banco relacional PostgreSQL (`init.sql`) e chamadas assíncronas do Xano via fila background (`xano_background_worker`).
- **Imutabilidade Histórica**: Preços de itens lançados em comanda nunca devem depender de lookup dinâmico do produto em tempo de fechamento. Salve sempre `preco_momento` e `nome_produto_historico`.

## 3. Segurança e Robustez
- Todas as regras de negócio e validações (ex: validação de mesas ativas, unicidade de código PDV, fechamento de comandas) devem ser validadas no backend, tratando o frontend apenas como camada visual.
- Rate limits para integrações de terceiros (como o Xano Free Tier) devem ser respeitados via worker desacoplado.

## 4. Ciclo de Trabalho OpenSpec
1. **Explore**: Investigue impactos, riscos e dependências.
2. **Propose**: Crie artefatos (`proposal.md`, `specs/`, `design.md`, `tasks.md`).
3. **Review**: Valide escopo e viabilidade técnica antes de gerar código.
4. **Apply**: Implemente estritamente as tarefas mapeadas em `tasks.md`.
5. **Archive**: Atualize a especificação principal e arquive a change.
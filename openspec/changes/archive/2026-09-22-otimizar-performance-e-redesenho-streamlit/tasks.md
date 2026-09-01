## 1. Módulo de Dados e Sincronização Xano

- [x] 1.1 Criar `data_manager.py` com persistência direta em `churras_data.json`, métodos atômicos de CRUD e thread em background com rate-limit para sincronizar eventos críticos (pagamento e itens) com o Xano.

## 2. Configuração de Tema e Identidade Visual

- [x] 2.1 Configurar `.streamlit/config.toml` com tema dark executivo (Obsidian / Slate / Amber) e supressão de alertas de telemetria.

## 3. Redesenho Completo das Interfaces (Sem Emojis)

- [x] 3.1 Reescrever `app.py` com visual executivo sóbrio, status de integridade dos dados e navegação clara sem imagens lentas ou emojis.
- [x] 3.2 Criar `pages/1_Salao_e_Mesas.py` com novo design corporativo, cards minimalistas de mesas, painel de comanda ágil e fechamento de conta com cálculo de taxa.
- [x] 3.3 Criar `pages/2_Cardapio.py` com busca rápida, tabela estilizada, formulário de cadastro e ações de edição/exclusão.
- [x] 3.4 Criar `pages/3_Relatorios.py` com métricas executivas, gráficos de alta legibilidade e download do relatório PDF.

## 4. Testes e Validação da Change

- [x] 4.1 Criar e executar teste automatizado `test_redesign.py` validando integridade do `data_manager` e compilação de todas as páginas.
- [x] 4.2 Validar e arquivar a change via `openspec validate` e `openspec archive`.

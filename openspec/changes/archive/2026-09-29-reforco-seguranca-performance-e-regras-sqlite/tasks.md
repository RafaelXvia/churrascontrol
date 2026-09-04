## 1. Integridade Relacional e Restrições de Domínio no SQLite

- [x] 1.1 Atualizar schema do SQLite em `data_manager.py` com constraints `CHECK`, integridade referencial ativa (`PRAGMA foreign_keys = ON`), índices de performance e índice condicional único para comandas ativas por mesa.
- [x] 1.2 Implementar validações atômicas de domínio (rejeitar preços <= 0, quantidades <= 0, duplicidade de código PDV).

## 2. Reforço de Segurança e Tratamento de Erros

- [x] 2.1 Adicionar suporte a cabeçalho de autenticação Bearer e API Key no cliente HTTP do Xano via variável `XANO_API_KEY` / `XANO_AUTH_TOKEN`.
- [x] 2.2 Substituir supressões silenciosas de erro por logging estruturado e persistência de detalhes do erro na coluna `ultimo_erro` da `fila_sincronizacao`.
- [x] 2.3 Implementar sanitização preventiva contra injeção de HTML/XSS (`html.escape`) nos componentes visuais e tabelas de exibição.
- [x] 2.4 Adicionar controle operacional por confirmação de segurança para ações destrutivas (excluir produto, cancelar comanda).

## 3. Otimização de Performance e Fila Adaptativa

- [x] 3.1 Implementar controle adaptativo de taxa de envio (*Cooldown Adaptativo*): disparo imediato quando não há chamadas recentes, e espera controlada apenas em caso de rajadas sucessivas.
- [x] 3.2 Otimizar consultas SQL com índices direcionados em `comandas`, `itens_comanda` e `produtos`.

## 4. Testes, Validação e Arquivamento

- [x] 4.1 Criar teste automatizado `test_security_performance.py` validando as constraints relacionais, bloqueio de inputs inválidos, sanitização XSS e fila adaptativa.
- [x] 4.2 Executar suíte de testes de regressão e compilação de todas as páginas.
- [x] 4.3 Atualizar especificações do OpenSpec e arquivar a change.

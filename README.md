# ChurrasControl — Manual de Uso do Aplicativo Web

## 1. Apresentação

O **ChurrasControl** é uma aplicação web de automação comercial, Ponto de Venda (PDV) e gestão de mesas desenvolvida para o setor de alimentação (churrascarias, restaurantes, bares e cafeterias).

### Problema que Resolve
Estabelecimentos de pequeno e médio porte frequentemente enfrentam:
- Perda de histórico de lançamentos e comandas durante oscilações de internet.
- Lentidão no fechamento de contas e erros na divisão de valores por pessoa ou aplicação de taxa de serviço.
- Falta de visibilidade sobre o faturamento, ticket médio e produtos com maior saída.
- Dependência de atendimento presencial constante para pedidos simples, sem opção de autoatendimento na mesa.

### Público-Alvo
- **Operadores de Caixa e Garçons:** Profissionais que operam o salão, abrem comandas, lançam itens e realizam o fechamento de contas.
- **Gerentes e Administradores:** Gestores responsáveis pelo cardápio, equipe, auditoria, análise de métricas e tomada de decisão.
- **Clientes no Salão:** Consumidores que utilizam o cardápio digital via QR Code para consultar itens e enviar pedidos diretamente da mesa.

---

## 2. Acesso ao Aplicativo

### Execução Local
1. Clone o repositório:
   ```bash
   git clone https://github.com/RafaelXvia/churrascontrol.git
   cd churrascontrol
   ```
2. Crie e ative um ambiente virtual Python (3.10+):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure o arquivo `.env` a partir do `.env.example` (opcional para uso offline; necessário apenas se quiser ativar a sincronização com o Xano ou o Assistente IA com Google Gemini).
5. Inicie a aplicação:
   ```bash
   streamlit run app.py
   ```
   O sistema abrirá automaticamente em `http://localhost:8501` (ou via `python run.py` na porta `8080`).

### Deploy em Nuvem (Discloud)
O projeto conta com configuração pronta para hospedagem na plataforma Discloud (`discloud.config` e `.discloudignore`).

### Credenciais de Demonstração
O banco de dados inicial já possui contas pré-cadastradas para testes:

| Perfil | E-mail | Senha |
| :--- | :--- | :--- |
| **Gerente** | `gerente@churrascontrol.com` | `1q2w` |
| **Caixa** | `joao@churrascontrol.com` | `1q2w` |

---

## 3. Perfis de Usuários

O sistema utiliza controle de acesso baseado em papéis (RBAC):

1. **Gerente (`Gerente`)**
   - **Responsabilidades:** Administração completa do negócio, gestão de cardápio, controle de equipe, auditoria e análise financeira.
   - **Permissões:** Acesso irrestrito a todas as telas (`Salão e Mesas`, `Cardápio`, `Métricas`, `QR Codes de Mesas`, `Colaboradores`, `Auditoria` e `Assistente IA`).

2. **Caixa (`Caixa`)**
   - **Responsabilidades:** Operação diária do salão, atendimento às mesas, lançamento de pedidos e recebimento de contas.
   - **Permissões:** Acesso a `Salão e Mesas`, `Cardápio` (consulta/operação) e `QR Codes de Mesas`. Não possui acesso a `Métricas`, `Colaboradores`, `Auditoria` ou `Assistente IA`.

3. **Cliente na Mesa (Acesso via QR Code)**
   - **Responsabilidades:** Consulta ao cardápio digital e envio de pedidos de autoatendimento.
   - **Permissões:** Acesso exclusivo à tela `Cardápio do Cliente` (`pages/5_Cardapio_Cliente.py`) vinculada ao token da mesa, sem necessidade de login.

---

## 4. Funcionalidades

- **Salão e Mesas (`pages/1_Salao_e_Mesas.py`):** Painel visual em tempo real com status das mesas (livre/ocupada), abertura de comandas, lançamento de itens com observações, remoção de itens e fechamento de conta com taxa de serviço opcional (10%) e divisão por número de pagantes.
- **Cardápio (`pages/2_Cardapio.py`):** Cadastro, edição, ativação/inativação e filtragem de produtos, com validação de unicidade de código PDV e precificação.
- **Métricas e Relatórios (`pages/3_Metricas.py`):** Gráficos analíticos de faturamento e desempenho por período (`1d`, `7d`, `15d`, `30d`), cálculo de ticket médio e exportação de relatório executivo em PDF.
- **QR Codes de Mesas (`pages/4_Mesas_QRCodes.py`):** Geração de links e QR Codes exclusivos por mesa para autoatendimento.
- **Cardápio do Cliente (`pages/5_Cardapio_Cliente.py`):** Interface mobile para o cliente montar o carrinho e enviar pedidos direto para a comanda da mesa.
- **Colaboradores (`pages/6_Colaboradores.py`):** Cadastro e gerenciamento de usuários e perfis de acesso.
- **Auditoria (`pages/7_Auditoria.py`):** Registro de eventos operacionais e de segurança do sistema.
- **Assistente IA (`pages/8_Assistente_IA.py`):** Consultor analítico baseado em RAG (Google Gemini) para responder perguntas sobre vendas, produtos e operação.
- **Persistência Offline-First:** Gravação local em SQLite (modo WAL) com fila assíncrona (`fila_sincronizacao`) para envio ao backend Xano.

---

## 5. Manual de Utilização

### Jornada 1: Operação de Salão e Fechamento de Conta (Perfil: Caixa ou Gerente)
1. **Login:** Na tela inicial (`app.py`), informe o e-mail e a senha do perfil `Caixa` ou `Gerente` e clique em entrar.
   - *Resultado esperado:* O menu lateral libera os módulos correspondentes ao perfil autenticado.
2. **Abrir Mesa:** Acesse **Salão e Mesas**, selecione uma mesa com status livre e clique para abrir uma nova comanda.
   - *Resultado esperado:* A mesa muda para o status ocupada e passa a exibir a comanda ativa.
3. **Lançar Itens:** Selecione produtos do cardápio, informe a quantidade e observações (ex.: ponto da carne) e confirme o lançamento.
   - *Resultado esperado:* Os itens aparecem na lista da comanda com preço congelado no momento do lançamento (`preco_momento`) e o subtotal é atualizado.
4. **Fechar Conta:** Clique em fechar comanda, escolha se deseja aplicar a taxa de serviço de 10% e informe a quantidade de pessoas para divisão. Confirme o pagamento.
   - *Resultado esperado:* O sistema calcula o valor total e o valor por pessoa, encerra a comanda, registra a venda no histórico e libera a mesa.

### Jornada 2: Autoatendimento do Cliente via QR Code (Perfil: Cliente + Caixa/Gerente)
1. **Gerar QR Code (Caixa/Gerente):** Acesse **QR Codes de Mesas**, selecione a mesa desejada e gere o QR Code ou copie o link de acesso.
   - *Resultado esperado:* Um token único é exibido para aquela mesa.
2. **Realizar Pedido (Cliente):** Ao acessar o link do QR Code no celular, o cliente visualiza o **Cardápio do Cliente**, adiciona itens ao carrinho e confirma o envio.
   - *Resultado esperado:* O pedido é vinculado automaticamente à comanda da mesa correspondente.

### Jornada 3: Gestão Administrativa e Análise (Perfil: Gerente)
1. **Gerenciar Cardápio:** Acesse **Cardápio** para cadastrar novos produtos (informando nome, categoria, código PDV único e preço) ou editar itens existentes.
   - *Resultado esperado:* O novo produto fica imediatamente disponível para lançamento no salão e no cardápio digital.
2. **Consultar Métricas e Exportar PDF:** Acesse **Métricas**, selecione o período desejado (`1d`, `7d`, `15d` ou `30d`), analise os gráficos e clique para gerar o relatório em PDF.
   - *Resultado esperado:* Os indicadores são atualizados na tela e o arquivo PDF é disponibilizado para download.
3. **Gerenciar Equipe e Auditoria:** Utilize **Colaboradores** para criar novos acessos e **Auditoria** para acompanhar o histórico de ações críticas.
4. **Consultar o Assistente IA:** Acesse **Assistente IA**, digite uma pergunta sobre o desempenho do restaurante e envie.
   - *Resultado esperado:* O assistente analisa os dados do banco e retorna uma resposta contextualizada.

---

## 6. Exemplos de Utilização

- **Cenário 1 — Horário de Pico com Oscilação de Internet:** O garçom/caixa lança 5 rodadas de bebidas e cortes na Mesa 04 mesmo com a internet instável. O sistema grava tudo localmente no SQLite e enfileira a sincronização com o Xano para quando a conexão estabilizar, sem perda de dados.
- **Cenário 2 — Divisão de Conta em Grupo:** Uma mesa com 4 clientes consome R$ 240,00. No fechamento, o caixa ativa a taxa de serviço de 10% (total R$ 264,00) e informa 4 pagantes. O sistema exibe imediatamente o valor de R$ 66,00 por pessoa.
- **Cenário 3 — Atualização de Preço sem Afetar Comandas Abertas:** O gerente reajusta o preço de um corte no Cardápio. Itens já lançados anteriormente em comandas abertas mantêm o preço histórico do momento do pedido.

---

## 7. Limitações Conhecidas

- **Assistente IA:** Requer a configuração de pelo menos uma chave válida da API do Google Gemini (`GOOGLE_API_KEY_1`) no arquivo `.env`. Sem a chave, o restante do sistema funciona normalmente, mas o módulo de IA informa que aguarda configuração.
- **Sincronização em Nuvem (Xano Free Tier):** A integração com o Xano respeita limites de requisições da camada gratuita; em ambientes locais sem configuração de `XANO_BASE_URL`, a operação ocorre 100% em modo local.
- **Pagamentos e Emissão Fiscal:** O fechamento de comanda realiza o controle financeiro interno e cálculo de divisão, não possuindo integração direta com maquininhas de cartão (TEF/PIX) ou emissão de nota fiscal eletrônica (NFC-e).

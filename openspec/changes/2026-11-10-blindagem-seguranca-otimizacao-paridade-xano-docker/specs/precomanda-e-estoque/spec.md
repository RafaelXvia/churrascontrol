# Especificação Delta: Pré-Comanda, Cardápio Digital Cliente e Segurança de Token QR Code

## Requisitos Modificados e Adicionados

### Requisito 1: Validação Criptográfica Obrigatória do `token` QR Code no Cardápio do Cliente
O acesso de clientes não autenticados à página `pages/5_Cardapio_Cliente.py` DEVE validar tanto `mesa_id` quanto o parâmetro `token` da query string contra `mesas.qr_code_token` utilizando comparação em tempo constante (`hmac.compare_digest`).

#### Cenário: Tentativa de acesso ao Cardápio Digital apenas com `mesa_id` ou com `token` inválido
- **DADO** um usuário não autenticado que acessa `/?mesa_id=1` sem `token` ou com `token=invalido`
- **QUANDO** a página `pages/5_Cardapio_Cliente.py` for carregada
- **ENTÃO** o sistema DEVE recusar o carregamento do cardápio de autoatendimento e exibir aviso solicitando a leitura do QR Code físico oficial da mesa.

#### Cenário: Acesso legítimo via QR Code da mesa
- **DADO** um cliente que escaneia o QR Code contendo `?mesa_id=1&token=<qr_code_token_valido>`
- **QUANDO** a página `pages/5_Cardapio_Cliente.py` validar o token
- **ENTÃO** o cardápio digital da Mesa 1 DEVE ser liberado normalmente para visualização.


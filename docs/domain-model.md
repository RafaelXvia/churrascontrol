# Modelo de Domínio — ChurrasControl

Este documento estabelece as entidades essenciais do negócio, suas responsabilidades e as regras estruturais que regem o ciclo de vida dos pedidos.

---

## 1. Mesa (`Mesa`)
Representa o espaço físico de acomodação dos clientes no salão.
- **Atributos principais**: `id`, `numero_mesa`, `capacidade`, `status` (`LIVRE`, `OCUPADA`, `CONTA`).
- **Regras estruturais**:
  - Uma mesa só pode ter no máximo uma comanda com status `ABERTA` em determinado momento.
  - O número da mesa deve ser único no salão ativo.

---

## 2. Produto (`Produto`)
Representa um item comercializável constante no cardápio.
- **Atributos principais**: `id`, `codigo_pdv`, `nome`, `categoria`, `preco_unitario`.
- **Regras estruturais**:
  - O `codigo_pdv` é a chave natural de identificação rápida pelo operador de caixa e não pode se repetir.
  - O preço unitário deve ser obrigatoriamente numérico positivo.

---

## 3. Comanda (`Comanda`)
Representa o atendimento em andamento ou histórico financeiro de consumo de uma mesa.
- **Atributos principais**: `id`, `mesa_id`, `numero_mesa_historico`, `data_abertura`, `data_fechamento`, `status` (`ABERTA`, `PAGA`, `CANCELADA`), `taxa_servico`, `qtd_pessoas`, `valor_total`.
- **Regras estruturais**:
  - Ao ser finalizada com status `PAGA`, o vínculo `mesa_id` é desassociado (`null`), e a mesa é liberada.
  - Seus dados consolidados alimentam os relatórios gerenciais e dashboards de faturamento.
  - Comandas canceladas não entram na soma de faturamento e ticket médio.

---

## 4. Item da Comanda (`ItemComanda`)
Instância de consumo adicionada à comanda do cliente.
- **Atributos principais**: `id`, `comanda_id`, `produto_id`, `nome_produto_historico`, `categoria_historico`, `quantidade`, `preco_momento`, `observacao`.
- **Regras estruturais de Imutabilidade**:
  - O item guarda cópia em texto do nome, categoria e valor no momento do lançamento (`preco_momento`). Reajustes cadastrais no cardápio não alteram comandas já lançadas.
  - Itens idênticos adicionados na mesma comanda devem acumular quantidade em vez de duplicar linhas desnecessariamente.
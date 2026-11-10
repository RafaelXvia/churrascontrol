"""
Script de Geração de Massa de Vendas Históricas Realistas — ChurrasControl
Localização: tools/seed_vendas_demo.py

Gera histórico consistente de vendas dos últimos 60 dias para demonstração
e testes executivos do Assistente IA:
- Mesas 1 a 10 (Varanda 1-4, Salão Interno 5-8, Kids 9-10)
- Turnos de Almoço (11:30-15:30) e Jantar (18:30-23:30)
- Comandas com status 'PAGA', imutabilidade histórica de itens e cálculo determinístico
"""
import sys
import os
import random
import sqlite3
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from backend.database import data_manager
from backend.ai import ontologia

def gerar_vendas_demo(dias: int = 60, comandas_por_dia: int = 2, db_path: str = None) -> int:
    """Gera histórico de vendas realistas distribuídas nos últimos N dias."""
    if db_path is None:
        db_path = data_manager.DB_PATH

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        # Garante que as tabelas e ontologia existam
        data_manager.init_db()
        ontologia.seed_ontologia(conn)

        # Busca catálogo de produtos
        cur.execute("SELECT id, nome, categoria, preco_unitario FROM produtos WHERE preco_unitario > 0")
        produtos = [dict(r) for r in cur.fetchall()]
        if not produtos:
            print("[ALERTA] Nenhum produto cadastrado para gerar histórico de vendas.")
            return 0

        total_comandas_criadas = 0
        hoje = datetime.now()

        # Garante registro das mesas 1 a 10
        for m_num in range(1, 11):
            cur.execute("SELECT id FROM mesas WHERE numero_mesa = ?", (m_num,))
            if not cur.fetchone():
                cur.execute("INSERT INTO mesas (numero_mesa, capacidade, status) VALUES (?, 4, 'LIVRE')", (m_num,))

        cur.execute("SELECT id, numero_mesa FROM mesas ORDER BY numero_mesa")
        mesas_dict = {r["numero_mesa"]: r["id"] for r in cur.fetchall()}

        for dia_offset in range(dias, 0, -1):
            data_base = hoje - timedelta(days=dia_offset)
            # Gera 2 a 4 comandas por dia
            qtd_comandas_hoje = random.randint(1, comandas_por_dia + 1)

            for _ in range(qtd_comandas_hoje):
                mesa_num = random.randint(1, 10)
                mesa_id = mesas_dict.get(mesa_num)

                # Escolhe turno: 60% almoço, 40% jantar
                is_almoco = random.random() < 0.6
                if is_almoco:
                    hora = random.randint(12, 14)
                    minuto = random.randint(0, 59)
                else:
                    hora = random.randint(19, 22)
                    minuto = random.randint(0, 59)

                abertura = data_base.replace(hour=hora, minute=minuto, second=random.randint(0, 59))
                duracao_min = random.randint(45, 110)
                fechamento = abertura + timedelta(minutes=duracao_min)

                qtd_pessoas = random.randint(2, 6)
                taxa_servico = 1

                # Cria comanda PAGA
                cur.execute("""
                INSERT INTO comandas (
                    mesa_id, numero_mesa_historico, data_abertura, data_fechamento,
                    status, taxa_servico, qtd_pessoas, valor_total
                ) VALUES (?, ?, ?, ?, 'PAGA', ?, ?, 0.0)
                """, (
                    mesa_id, mesa_num, abertura.isoformat(), fechamento.isoformat(),
                    taxa_servico, qtd_pessoas
                ))
                comanda_id = cur.lastrowid
                total_comandas_criadas += 1

                # Adiciona de 2 a 5 itens variados
                subtotal = 0.0
                itens_sorteados = random.sample(produtos, min(len(produtos), random.randint(2, 5)))
                for prod in itens_sorteados:
                    qtd_item = random.randint(1, 3)
                    preco_unit = float(prod["preco_unitario"])
                    subtotal += qtd_item * preco_unit

                    cur.execute("""
                    INSERT INTO itens_comanda (
                        comanda_id, produto_id, nome_produto_historico, categoria_historico,
                        quantidade, preco_momento, observacao
                    ) VALUES (?, ?, ?, ?, ?, ?, '')
                    """, (
                        comanda_id, prod["id"], prod["nome"], prod["categoria"],
                        qtd_item, preco_unit
                    ))

                # Atualiza total com taxa de serviço se aplicável
                valor_final = round(subtotal * 1.10 if taxa_servico else subtotal, 2)
                cur.execute("UPDATE comandas SET valor_total = ? WHERE id = ?", (valor_final, comanda_id))

        conn.commit()
        print(f"[SUCESSO] Geradas {total_comandas_criadas} comandas históricas pagas com itens nos últimos {dias} dias.")
        return total_comandas_criadas
    finally:
        conn.close()

if __name__ == "__main__":
    dias_input = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    gerar_vendas_demo(dias=dias_input)

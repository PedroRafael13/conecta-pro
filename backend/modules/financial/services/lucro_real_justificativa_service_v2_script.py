"""
Classifica automaticamente as saídas bancárias por categoria de Lucro Real.
Schema real bank_transactions: id, description, amount, transaction_date,
transaction_type, justificativa_categoria, reconciliation_status

Categorias Lucro Real Conecta Mais:
- FOLHA_PAGAMENTO: salários, FGTS, INSS, férias, 13º
- FORNECEDORES: equipamentos, materiais, manutenção
- IMPOSTOS: IRPJ, CSLL, ISS, PIS, COFINS, DAS, DARF
- OPERACIONAL: aluguel, energia, internet, telefone, combustível
- CLIENTE_REEMBOLSO: reembolsos a clientes
- FINANCEIRO: tarifas bancárias, IOF, juros
- INVESTIMENTO: compra de equipamentos, veículos, infraestrutura
- OUTROS: não classificado automaticamente
"""

import json
import os
import re
import sys

sys.path.insert(0, "/opt/conecta-pro/backend")
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/conecta_pro")
engine = create_engine(DATABASE_URL)

# Regras de classificação por padrão de descrição (calibradas para banco real)
REGRAS = [
    (
        "FOLHA_PAGAMENTO",
        r"salario|salário|folha|pagto func|funcionario|fgts|inss|rescisao|rescisão|ferias|férias|13 sal|colaborador|cp\s*:\d{8}-(?!solides|cef|uber|one port|cruz|econdos|jordana)",
    ),
    (
        "IMPOSTOS",
        r"darf|das |irpj|csll|cofins|\bpis\b|simples|receita federal|pgdas|dctf|gps |grf |cef matriz|00360305",
    ),
    ("FORNECEDORES", r"solides|fornec|equip|material|manutenc|manutenç|instalac|instalação|nota fiscal"),
    (
        "OPERACIONAL",
        r"aluguel|energia|luz |agua |internet|telefon|combustiv|frete|transporte|limpeza|seguro|uber|banco24h|saque banco",
    ),
    ("FINANCEIRO", r"tarifa|iof |juros|multa banco|taxa saque|taxa pix|anuidade"),
    ("INVESTIMENTO", r"aquisic|aquisição|compra ativo|veiculo|veículo|computador|servidor|camera|câmera|cftv"),
    ("CLIENTE_REEMBOLSO", r"reembolso|devolucao|devolução|estorno cliente"),
]

# CNPJs conhecidos por categoria
CNPJ_CAT = {
    "00360305": "IMPOSTOS",  # CEF — FGTS
    "31680151": "FORNECEDORES",  # SOLIDES
    "14796606": "CLIENTE_REEMBOLSO",  # Uber
    "02282709": "FORNECEDORES",  # Advogados
    "60701190": "FOLHA_PAGAMENTO",  # Jordan (pró-labore)
}


def classificar(descricao: str) -> str:
    desc_lower = (descricao or "").lower()
    # Primeiro: CNPJ match
    m = re.search(r"cp\s*:(\d{8})", desc_lower)
    if m:
        cnpj = m.group(1)
        if cnpj in CNPJ_CAT:
            return CNPJ_CAT[cnpj]
    # Depois: regex
    for categoria, padrao in REGRAS:
        if re.search(padrao, desc_lower):
            return categoria
    return "OUTROS"


with engine.connect() as conn:
    # Query adaptada ao schema real
    pendentes = conn.execute(
        text("""
        SELECT id, description, amount, transaction_date, justificativa_categoria
        FROM bank_transactions
        WHERE transaction_type = 'debit'
        ORDER BY ABS(amount) DESC
        LIMIT 616
    """)
    ).fetchall()

    print(f"Pendentes para classificar: {len(pendentes)}")

    classificacoes = {}
    valor_por_cat = {}
    for p in pendentes:
        desc = str(p.description or "")
        cat = classificar(desc)
        classificacoes[cat] = classificacoes.get(cat, 0) + 1
        valor_por_cat[cat] = valor_por_cat.get(cat, 0.0) + float(abs(p.amount or 0))

    print("\nDistribuição automática:")
    total_auto = sum(v for k, v in classificacoes.items() if k != "OUTROS")
    for cat, qtd in sorted(classificacoes.items(), key=lambda x: -x[1]):
        pct = (qtd / len(pendentes)) * 100 if pendentes else 0
        print(f"  {cat:25s}: {qtd:4d} ({pct:.1f}%) — R$ {valor_por_cat.get(cat, 0):,.2f}")

    print(f"\nClassificados automaticamente: {total_auto}/{len(pendentes)} ({total_auto / len(pendentes) * 100:.1f}%)")
    print(f"Requerem revisão manual (OUTROS): {classificacoes.get('OUTROS', 0)}")

    resultado = {
        "total_pendentes": len(pendentes),
        "classificados_auto": total_auto,
        "distribuicao": classificacoes,
        "valor_por_categoria": {k: round(v, 2) for k, v in valor_por_cat.items()},
        "pendentes_revisao": classificacoes.get("OUTROS", 0),
        "percentual_auto": round(total_auto / len(pendentes) * 100, 1) if pendentes else 0,
    }
    with open("/tmp/classificacao_resultado.json", "w") as f:  # nosec B108
        json.dump(resultado, f, indent=2, default=str)
    print("\nResultado salvo em /tmp/classificacao_resultado.json")

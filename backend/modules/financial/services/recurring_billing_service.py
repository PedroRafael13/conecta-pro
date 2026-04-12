"""
Recurring Billing Service — Cobrança Mensal Automática PIX
Gera PIX com vencimento (cobv) para os clientes da Conecta Mais.
MRR: R$270.586,96 distribuídos entre 10 clientes ativos com contrato.

Schema real:
  clients: id, name, document_number, email, mrr, pix_key, billing_day, status='active'
  receivable_accounts: condominio_id (NOT NULL), customer_id, reference_month,
                       is_recurring, metadata, pix_txid, pix_copy_paste, due_date
"""

import asyncio
import logging
import os
from datetime import date

import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "").replace("+asyncpg", "")
INTER_CLIENT_ID = os.getenv("INTER_CLIENT_ID", "")
INTER_CLIENT_SECRET = os.getenv("INTER_CLIENT_SECRET", "")
INTER_CERT_PATH = os.getenv("INTER_CERT_PATH", "")
INTER_KEY_PATH = os.getenv("INTER_KEY_PATH", "")
INTER_ENV = os.getenv("INTER_ENVIRONMENT", "production")
INTER_PIX_KEY = os.getenv("INTER_PIX_KEY", "35710481000103")

# condominio_id padrão usado por receivable_accounts existentes
CONDOMINIO_ID_DEFAULT = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"


def _get_conn():
    return psycopg2.connect(DATABASE_URL)


def _build_inter_adapter():
    from modules.integrations.banking.adapters.base import BankCredentials
    from modules.integrations.banking.adapters.inter import InterAdapter

    creds = BankCredentials(
        client_id=INTER_CLIENT_ID,
        client_secret=INTER_CLIENT_SECRET,
        certificate_path=INTER_CERT_PATH if os.path.exists(INTER_CERT_PATH) else None,
        private_key_path=INTER_KEY_PATH if os.path.exists(INTER_KEY_PATH) else None,
        environment=INTER_ENV,
    )
    return InterAdapter(creds)


def _chamar_pix_cobv(txid: str, valor: float, cnpj: str, nome: str, descricao: str, vencimento: str) -> dict:
    """Chama InterAdapter.create_pix_cobv via asyncio.run (adapter é async)."""
    try:
        adapter = _build_inter_adapter()

        async def _run():
            try:
                resultado = await adapter.create_pix_cobv(
                    txid=txid,
                    valor=valor,
                    cpf_cnpj=cnpj,
                    nome=nome,
                    descricao=descricao,
                    vencimento=vencimento,
                    chave_pix=INTER_PIX_KEY,
                )
                return resultado
            finally:
                await adapter.close()

        return asyncio.run(_run())
    except Exception as exc:
        logger.warning("PIX cobv erro (%s): %s", txid, exc)
        return {"success": False, "error": str(exc)}


def gerar_cobrancas_mensais(mes: int, ano: int, apenas_preview: bool = False) -> dict:
    """
    Gera cobranças PIX com vencimento para todos os clientes com MRR.
    Cria registro em receivable_accounts + chama Inter API (cobv).
    """
    conn = _get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # Buscar clientes ativos com MRR configurado
        cur.execute("""
            SELECT id, name, document_number, email, mrr, pix_key, billing_day
            FROM clients
            WHERE status = 'active'
              AND mrr IS NOT NULL
              AND mrr > 0
            ORDER BY name
        """)
        clientes = [dict(r) for r in cur.fetchall()]

        if apenas_preview:
            return {
                "modo": "preview",
                "mes": mes,
                "ano": ano,
                "total_clientes": len(clientes),
                "total_mrr": float(sum(float(c["mrr"]) for c in clientes)),
                "sem_pix_key": [c["name"] for c in clientes if not c.get("pix_key")],
                "clientes": [
                    {
                        "nome": c["name"],
                        "cnpj": c["document_number"],
                        "mrr": float(c["mrr"]),
                        "pix_key": c.get("pix_key") or "não configurada",
                        "vencimento": date(ano, mes, min(c.get("billing_day") or 10, 28)).isoformat(),
                    }
                    for c in clientes
                ],
            }

        resultados = []
        total_cobrado = 0.0
        erros = 0

        for cliente in clientes:
            valor = float(cliente["mrr"])
            dia_venc = cliente.get("billing_day") or 10
            vencimento = date(ano, mes, min(dia_venc, 28)).isoformat()
            txid = f"MRR{ano}{mes:02d}{str(cliente['id'])[:8].upper().replace('-', '')}"
            descricao = f"Servicos Seguranca {mes:02d}/{ano} - Conecta Mais"
            ref_month = f"{mes:02d}/{ano}"

            # Idempotência: verificar se já existe cobrança para este cliente/mês/ano
            cur_plain = conn.cursor()
            cur_plain.execute(
                """
                SELECT id FROM receivable_accounts
                WHERE (metadata->>'client_id') = %s
                  AND reference_month = %s
                  AND is_recurring = TRUE
                  AND (metadata->>'origem') = 'cobranca_automatica'
                LIMIT 1
                """,
                (str(cliente["id"]), ref_month),
            )
            if cur_plain.fetchone():
                resultados.append({"cliente": cliente["name"], "status": "ja_cobrado", "valor": valor})
                continue

            # Gerar PIX cobv via Inter (se tiver pix_key)
            resultado_pix: dict = {}
            if cliente.get("pix_key"):
                resultado_pix = _chamar_pix_cobv(
                    txid=txid,
                    valor=valor,
                    cnpj=cliente.get("document_number", ""),
                    nome=cliente["name"],
                    descricao=descricao,
                    vencimento=vencimento,
                )

            # Inserir receivable_account
            try:
                cur_plain.execute(
                    """
                    INSERT INTO receivable_accounts (
                        id, condominio_id, customer_id, description,
                        gross_value, net_value, issue_date, due_date,
                        reference_month, status, is_recurring, recurring_day,
                        pix_txid, pix_copy_paste,
                        pix_generated, pix_generated_at,
                        metadata, created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), %s, %s, %s,
                        %s, %s, NOW(), %s,
                        %s, 'pendente', TRUE, %s,
                        %s, %s,
                        %s, CASE WHEN %s THEN NOW() ELSE NULL END,
                        %s::jsonb, NOW(), NOW()
                    )
                    """,
                    (
                        CONDOMINIO_ID_DEFAULT,
                        None,  # customer_id FK aponta para customers, não clients; usar NULL
                        descricao,
                        valor,
                        valor,
                        vencimento,
                        ref_month,
                        dia_venc,
                        resultado_pix.get("txid", txid),
                        (resultado_pix.get("pix_copy_paste", "") or "")[:500],
                        resultado_pix.get("success", False),
                        resultado_pix.get("success", False),
                        (
                            f'{{"origem":"cobranca_automatica","client_id":"{cliente["id"]}",'
                            f'"pix_success":{str(resultado_pix.get("success", False)).lower()}}}'
                        ),
                    ),
                )
                conn.commit()
                total_cobrado += valor
                resultados.append(
                    {
                        "cliente": cliente["name"],
                        "status": "cobrado",
                        "valor": valor,
                        "vencimento": vencimento,
                        "pix_gerado": resultado_pix.get("success", False),
                        "pix_copy_paste": (resultado_pix.get("pix_copy_paste") or "")[:80],
                    }
                )
            except Exception as exc:
                conn.rollback()
                erros += 1
                logger.error("Erro ao inserir receivable para %s: %s", cliente["name"], exc)
                resultados.append({"cliente": cliente["name"], "status": "erro", "erro": str(exc)})

        cobrados = len([r for r in resultados if r["status"] == "cobrado"])
        return {
            "mes": mes,
            "ano": ano,
            "total_clientes": len(clientes),
            "cobrados": cobrados,
            "ja_cobrados": len([r for r in resultados if r["status"] == "ja_cobrado"]),
            "erros": erros,
            "total_cobrado": round(total_cobrado, 2),
            "resultados": resultados,
        }

    finally:
        cur.close()
        conn.close()

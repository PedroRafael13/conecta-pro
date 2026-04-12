"""
Webhook Controller — Receptor de notificações do Banco Inter
Processa eventos: PIX recebido, boleto pago, devolução
Concilia automaticamente com receivable/payable_accounts
"""

import json
import logging
import os
import uuid

from fastapi import APIRouter, Header, HTTPException, Request

router = APIRouter(prefix="/webhooks", tags=["Webhooks — Inter"])
logger = logging.getLogger(__name__)
INTER_WEBHOOK_SECRET = os.getenv("INTER_WEBHOOK_SECRET", "")  # pragma: allowlist secret


def _get_conn():
    import psycopg2

    database_url = os.getenv("DATABASE_URL", "").replace("+asyncpg", "")
    return psycopg2.connect(database_url)


def _log_webhook(payload: dict, event_type: str, path: str) -> None:
    """Persiste recebimento do webhook em integration_logs."""
    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO integration_logs (
                id, log_type, level, status,
                retry_count, is_retry, timestamp,
                method, path, request_body, created_at
            ) VALUES (
                %s, 'webhook_delivery', 'info', 'success',
                0, false, NOW(),
                'POST', %s, %s, NOW()
            )
            """,
            (str(uuid.uuid4()), path, json.dumps(payload)[:4000]),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as exc:
        logger.warning("Falha ao gravar integration_logs: %s", exc)


async def _processar_pix_recebido(pix_data: dict) -> dict:
    """Processa PIX recebido e atualiza receivable_account."""
    conn = _get_conn()
    cur = conn.cursor()

    try:
        e2e_id = pix_data.get("endToEndId", "")
        txid = pix_data.get("txid", "")
        valor = float(pix_data.get("valor", 0))
        pagador = pix_data.get("pagador", {})
        pagador_cnpj = pagador.get("cnpj", pagador.get("cpf", ""))
        pagador_nome = pagador.get("nome", "")

        # Buscar bank_account_id do Inter
        cur.execute("SELECT id FROM bank_accounts WHERE bank_code = '077' LIMIT 1")
        ba_row = cur.fetchone()
        bank_account_id = str(ba_row[0]) if ba_row else None

        # Salvar na tabela de transações
        cur.execute(
            """
            INSERT INTO bank_transactions (
                id, bank_account_id, transaction_type, category,
                amount, description, transaction_date,
                counterparty_name, counterparty_document,
                reconciliation_status, external_id,
                created_at, updated_at
            ) VALUES (
                gen_random_uuid(), %s::uuid, 'credito', 'pix_recebido',
                %s, %s, NOW(),
                %s, %s, 'pendente', %s,
                NOW(), NOW()
            )
            ON CONFLICT (external_id) WHERE external_id IS NOT NULL
            DO UPDATE SET updated_at = NOW()
            RETURNING id
            """,
            (
                bank_account_id,
                valor,
                f"PIX recebido - {pagador_nome} - {txid}",
                pagador_nome,
                pagador_cnpj,
                e2e_id or None,
            ),
        )
        tx_row = cur.fetchone()
        tx_id = str(tx_row[0]) if tx_row else None

        # Tentar conciliar por txid
        if txid:
            cur.execute(
                """
                UPDATE receivable_accounts SET
                    status = 'recebido',
                    data_recebimento = CURRENT_DATE,
                    transacao_bancaria_id = %s,
                    updated_at = NOW()
                WHERE pix_txid = %s
                  AND status = 'pendente'
                RETURNING id
                """,
                (tx_id, txid),
            )
            rec = cur.fetchone()
            if rec:
                conn.commit()
                return {
                    "conciliado": True,
                    "receivable_id": str(rec[0]),
                    "e2e_id": e2e_id,
                    "valor": valor,
                    "metodo": "txid",
                }

        # Fallback: conciliar por valor + janela de 7 dias
        cur.execute(
            """
            UPDATE receivable_accounts SET
                status = 'recebido',
                data_recebimento = CURRENT_DATE,
                transacao_bancaria_id = %s,
                updated_at = NOW()
            WHERE id = (
                SELECT id FROM receivable_accounts
                WHERE ABS(net_value - %s) <= 0.01
                  AND status = 'pendente'
                  AND due_date >= CURRENT_DATE - INTERVAL '7 days'
                  AND ativo IS NOT FALSE
                  AND deleted_at IS NULL
                ORDER BY due_date ASC
                LIMIT 1
            )
            RETURNING id
            """,
            (tx_id, valor),
        )
        rec = cur.fetchone()
        conn.commit()
        return {
            "conciliado": rec is not None,
            "receivable_id": str(rec[0]) if rec else None,
            "e2e_id": e2e_id,
            "valor": valor,
            "tx_salva": tx_id is not None,
            "metodo": "valor" if rec else "nenhum",
        }

    except Exception as e:
        conn.rollback()
        logger.error("Erro processar PIX: %s", e)
        return {"erro": str(e)}
    finally:
        cur.close()
        conn.close()


async def _processar_boleto_pago(boleto_data: dict) -> dict:
    """Processa notificação de boleto pago."""
    conn = _get_conn()
    cur = conn.cursor()

    try:
        boleto_id = boleto_data.get("codigoSolicitacao", "")
        valor = float(boleto_data.get("valorTotal", 0))

        cur.execute(
            """
            UPDATE receivable_accounts SET
                status = 'recebido',
                data_recebimento = CURRENT_DATE,
                updated_at = NOW()
            WHERE (boleto_number ILIKE %s OR pix_txid = %s)
              AND status = 'pendente'
            RETURNING id
            """,
            (f"%{boleto_id}%", boleto_id),
        )
        rec = cur.fetchone()
        conn.commit()
        return {
            "boleto_id": boleto_id,
            "conciliado": rec is not None,
            "receivable_id": str(rec[0]) if rec else None,
            "valor": valor,
        }
    except Exception as e:
        conn.rollback()
        logger.error("Erro processar boleto: %s", e)
        return {"erro": str(e)}
    finally:
        cur.close()
        conn.close()


@router.post(
    "/inter/pix",
    summary="Webhook PIX — notificações Inter",
    include_in_schema=False,
)
async def webhook_pix(
    request: Request,
    x_inter_webhook_signature: str | None = Header(None),
):
    """
    Receptor de webhooks PIX do Banco Inter.
    Processa: PIX recebidos, devoluções, confirmações.
    Concilia automaticamente com receivable_accounts.
    """
    try:
        body = await request.body()
        payload = json.loads(body)
        logger.info("Webhook PIX Inter: %s", str(payload)[:200])
        _log_webhook(payload, "pix", "/webhooks/inter/pix")

        pix_list = payload.get("pix", [payload])
        resultados = []
        for pix in pix_list:
            resultado = await _processar_pix_recebido(pix)
            resultados.append(resultado)

        return {"status": "ok", "processados": resultados}

    except Exception as e:
        logger.error("Webhook PIX erro: %s", e)
        return {"status": "erro", "detalhe": str(e)}


@router.post(
    "/inter/boleto",
    summary="Webhook Boleto — notificações Inter",
    include_in_schema=False,
)
async def webhook_boleto(request: Request):
    """Receptor de webhooks de boleto pago do Banco Inter."""
    try:
        body = await request.body()
        payload = json.loads(body)
        logger.info("Webhook Boleto Inter: %s", str(payload)[:200])
        _log_webhook(payload, "boleto", "/webhooks/inter/boleto")
        resultado = await _processar_boleto_pago(payload)
        return {"status": "ok", "resultado": resultado}
    except Exception as e:
        logger.error("Webhook Boleto erro: %s", e)
        return {"status": "erro", "detalhe": str(e)}


@router.post("/inter/configurar", summary="Configurar webhooks no painel Inter")
async def configurar_webhooks_inter():
    """
    Registra os webhooks no Banco Inter apontando para
    os endpoints do Conecta PRO.
    """
    from modules.integrations.banking.adapters import BankCredentials
    from modules.integrations.banking.adapters.inter import InterAdapter

    inter_client_id = os.getenv("INTER_CLIENT_ID")
    inter_secret = os.getenv("INTER_CLIENT_SECRET")
    inter_cert = os.getenv("INTER_CERT_PATH")
    inter_key = os.getenv("INTER_KEY_PATH")

    if not all([inter_client_id, inter_secret, inter_cert, inter_key]):
        raise HTTPException(
            status_code=503,
            detail="Credenciais Inter não configuradas (INTER_CLIENT_ID, INTER_CLIENT_SECRET, INTER_CERT_PATH, INTER_KEY_PATH)",
        )

    base_url = os.getenv("APP_BASE_URL", "https://erp.conectamais.pro")
    creds = BankCredentials(
        client_id=inter_client_id,
        client_secret=inter_secret,
        certificate_path=inter_cert,
        private_key_path=inter_key,
        environment=os.getenv("INTER_ENVIRONMENT", "production"),
    )
    adapter = InterAdapter(creds)

    try:
        pix_result = await adapter.register_pix_webhook(f"{base_url}/api/v1/webhooks/inter/pix")
        boleto_result = await adapter.register_boleto_webhook(f"{base_url}/api/v1/webhooks/inter/boleto")
        return {
            "pix_webhook": pix_result,
            "boleto_webhook": boleto_result,
            "urls_registradas": {
                "pix": f"{base_url}/api/v1/webhooks/inter/pix",
                "boleto": f"{base_url}/api/v1/webhooks/inter/boleto",
            },
        }
    finally:
        await adapter.close()


@router.get("/inter/status", summary="Status dos webhooks configurados")
async def status_webhooks():
    """Consulta webhooks configurados no Inter."""
    from modules.integrations.banking.adapters import BankCredentials
    from modules.integrations.banking.adapters.inter import InterAdapter

    inter_client_id = os.getenv("INTER_CLIENT_ID")
    inter_secret = os.getenv("INTER_CLIENT_SECRET")
    inter_cert = os.getenv("INTER_CERT_PATH")
    inter_key = os.getenv("INTER_KEY_PATH")

    if not all([inter_client_id, inter_secret, inter_cert, inter_key]):
        return {
            "configurado": False,
            "motivo": "Credenciais Inter não encontradas nas variáveis de ambiente",
        }

    creds = BankCredentials(
        client_id=inter_client_id,
        client_secret=inter_secret,
        certificate_path=inter_cert,
        private_key_path=inter_key,
        environment=os.getenv("INTER_ENVIRONMENT", "production"),
    )
    adapter = InterAdapter(creds)
    try:
        pix = await adapter.get_pix_webhook()
        return {"pix": pix, "configurado": pix.get("success", False)}
    finally:
        await adapter.close()

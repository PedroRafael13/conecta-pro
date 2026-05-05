"""Tasks Celery para gestao automatica de afastamentos SST.

Roda diariamente via Celery Beat:
- Encerra afastamentos com data_fim_prevista vencida
- Alerta afastamentos > 15 dias sem encaminhamento INSS
"""

import logging
from datetime import date

from sqlalchemy import text

from celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="sst.verificar_afastamentos_vencidos")
def verificar_afastamentos_vencidos():
    """Encerra afastamentos com data_fim_prevista anterior a hoje."""
    from core.database.session import get_sync_db

    hoje = date.today()
    try:
        with get_sync_db() as db:
            result = db.execute(
                text(
                    "UPDATE sst_afastamentos "
                    "SET status = 'encerrado', "
                    "    data_retorno = data_fim_prevista, "
                    "    updated_at = NOW() "
                    "WHERE status = 'ativo' "
                    "AND data_fim_prevista IS NOT NULL "
                    "AND data_fim_prevista < :hoje "
                    "RETURNING employee_nome, data_fim_prevista"
                ),
                {"hoje": hoje},
            )
            encerrados = result.fetchall()
            db.commit()

            for nome, data_fim in encerrados:
                logger.info(
                    "Afastamento encerrado automaticamente: %s (fim: %s)",
                    nome,
                    data_fim,
                )

            return f"{len(encerrados)} afastamentos encerrados"
    except Exception as exc:
        logger.error("Erro ao verificar afastamentos: %s", exc)
        return f"Erro: {exc}"


@app.task(name="sst.verificar_inss_pendente")
def verificar_inss_pendente():
    """Alerta afastamentos > 15 dias sem encaminhamento INSS."""
    from core.database.session import get_sync_db

    hoje = date.today()
    try:
        with get_sync_db() as db:
            result = db.execute(
                text(
                    "SELECT employee_nome, data_inicio, "
                    "  :hoje - data_inicio AS dias "
                    "FROM sst_afastamentos "
                    "WHERE status = 'ativo' "
                    "AND encaminhado_inss = FALSE "
                    "AND (:hoje - data_inicio) > 15"
                ),
                {"hoje": hoje},
            )
            pendentes = result.fetchall()

            for nome, inicio, dias in pendentes:
                logger.warning(
                    "ALERTA INSS: %s afastado ha %s dias sem encaminhamento INSS (inicio: %s)",
                    nome,
                    dias,
                    inicio,
                )

            return f"{len(pendentes)} alertas INSS"
    except Exception as exc:
        logger.error("Erro ao verificar INSS: %s", exc)
        return f"Erro: {exc}"

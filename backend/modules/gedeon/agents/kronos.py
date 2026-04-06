"""
KRONOS — Agente de Vencimentos do GEDEON
"Nenhuma certidão vence sem aviso"

Responsabilidades:
- Monitorar vencimentos de certidões (ged_certidoes)
- Monitorar ASOs dos funcionários (gp_asos + employees)
- Alertas escalonados: 60d → 30d → 15d → 7d → CRÍTICO
- Prever data ideal de renovação por tipo
- Publicar eventos no ConectaEventBus para GEDEON processar

Colunas reais:
  ged_certidoes: id, name, document_type, expiry_date
  gp_asos:       employee_id, data_validade, tipo, apto, medico, status
  employees:     id, nome, cargo
"""

import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

# Janelas de alerta em dias
ALERTAS_DIAS = [60, 30, 15, 7, 0]

# Tempo médio de renovação por tipo (dias)
TEMPO_RENOVACAO: dict[str, int] = {
    "certidao_negativa_federal": 5,
    "certidao_negativa_debito": 5,
    "cnd": 5,
    "regularidade_fgts": 3,
    "crf_fgts": 3,
    "certidao_trabalhista": 5,
    "certidao_estadual": 7,
    "certidao_municipal": 7,
    "alvara_funcionamento": 30,
    "certificado_digital_a1": 15,
    "aso": 5,
    "nr_20": 10,
    "nr_34": 10,
}


def calcular_nivel_alerta(
    data_vencimento: date,
    hoje: date | None = None,
) -> dict:
    """
    Calcular nível de alerta para uma data de vencimento.
    Retorna: dias_restantes, nivel, cor, label.
    """
    hoje = hoje or date.today()
    dias = (data_vencimento - hoje).days

    if dias < 0:
        return {
            "dias_restantes": dias,
            "nivel": "critico",
            "cor": "vermelho",
            "label": f"VENCIDA há {abs(dias)} dias",
        }
    if dias == 0:
        return {
            "dias_restantes": 0,
            "nivel": "critico",
            "cor": "vermelho",
            "label": "VENCE HOJE",
        }
    if dias <= 7:
        return {
            "dias_restantes": dias,
            "nivel": "critico",
            "cor": "vermelho",
            "label": f"Vence em {dias} dias",
        }
    if dias <= 15:
        return {
            "dias_restantes": dias,
            "nivel": "alto",
            "cor": "laranja",
            "label": f"Vence em {dias} dias",
        }
    if dias <= 30:
        return {
            "dias_restantes": dias,
            "nivel": "medio",
            "cor": "amarelo",
            "label": f"Vence em {dias} dias",
        }
    if dias <= 60:
        return {
            "dias_restantes": dias,
            "nivel": "baixo",
            "cor": "azul",
            "label": f"Vence em {dias} dias",
        }
    return {
        "dias_restantes": dias,
        "nivel": "ok",
        "cor": "verde",
        "label": f"Válida por {dias} dias",
    }


def data_ideal_renovacao(tipo: str, data_vencimento: date) -> date:
    """
    Calcular data ideal para iniciar a renovação,
    usando 2× o tempo médio de processamento como margem.
    """
    tipo_lower = tipo.lower()
    tempo = next(
        (v for k, v in TEMPO_RENOVACAO.items() if k in tipo_lower),
        10,
    )
    return data_vencimento - timedelta(days=tempo * 2)


class Kronos:
    """
    Agente de Vencimentos — monitora tudo que tem data de validade.
    Usa a sessão assíncrona do banco quando disponível,
    com fallback para psql via subprocess (modo background/Celery).
    """

    def verificar_certidoes_sync(self) -> list[dict]:
        """
        Verificar certidões via psql (modo background / Celery).
        Usa colunas reais: name, document_type, expiry_date.
        """
        import subprocess

        r = subprocess.run(  # noqa: S602 S603
            "docker ps --filter name=conecta-pro-postgres "  # noqa: S607
            "--format '{{.Names}}' | head -1",
            shell=True,  # nosec B602 B607
            capture_output=True,
            text=True,
        )
        pg = r.stdout.strip()
        if not pg:
            return []

        hoje = date.today()
        limite = hoje + timedelta(days=60)

        resultado = subprocess.run(  # noqa: S602 S603
            f"docker exec {pg} psql -U postgres -d conecta_pro "  # noqa: S607
            f'-t -A -c "'
            f"SELECT name, document_type, expiry_date::text "
            f"FROM ged_certidoes "
            f"WHERE expiry_date IS NOT NULL "
            f"AND expiry_date <= '{limite}' "
            f'ORDER BY expiry_date"',
            shell=True,  # nosec B602 B607
            capture_output=True,
            text=True,
        )

        alertas = []
        for linha in resultado.stdout.strip().splitlines():
            partes = linha.strip().split("|")
            if len(partes) < 3:
                continue
            nome, tipo, venc_str = partes[0], partes[1], partes[2]
            try:
                venc_date = date.fromisoformat(venc_str)
                alerta = calcular_nivel_alerta(venc_date)
                alertas.append(
                    {
                        "nome": nome,
                        "tipo": tipo,
                        "data_vencimento": venc_str,
                        "data_renovacao": str(data_ideal_renovacao(tipo, venc_date)),
                        **alerta,
                    }
                )
            except ValueError:
                continue

        return alertas

    def verificar_asos_sync(self) -> list[dict]:
        """
        Verificar ASOs dos funcionários ativos via psql.
        Usa gp_asos.data_validade e JOIN com employees.nome.
        """
        import subprocess

        r = subprocess.run(  # noqa: S602 S603
            "docker ps --filter name=conecta-pro-postgres "  # noqa: S607
            "--format '{{.Names}}' | head -1",
            shell=True,  # nosec B602 B607
            capture_output=True,
            text=True,
        )
        pg = r.stdout.strip()
        if not pg:
            return []

        hoje = date.today()
        limite = hoje + timedelta(days=60)

        resultado = subprocess.run(  # noqa: S602 S603
            f"docker exec {pg} psql -U postgres -d conecta_pro "  # noqa: S607
            f'-t -A -c "'
            f"SELECT e.nome, e.cargo, "
            f"a.data_validade::text, a.tipo "
            f"FROM gp_asos a "
            f"JOIN employees e ON e.id = a.employee_id "
            f"WHERE a.data_validade IS NOT NULL "
            f"AND a.data_validade <= '{limite}' "
            f"AND a.status != 'cancelado' "
            f'ORDER BY a.data_validade"',
            shell=True,  # nosec B602 B607
            capture_output=True,
            text=True,
        )

        alertas = []
        for linha in resultado.stdout.strip().splitlines():
            partes = linha.strip().split("|")
            if len(partes) < 3:
                continue
            nome = partes[0]
            cargo = partes[1]
            venc_str = partes[2]
            tipo = partes[3] if len(partes) > 3 else "periodico"
            try:
                venc_date = date.fromisoformat(venc_str)
                alerta = calcular_nivel_alerta(venc_date)
                alertas.append(
                    {
                        "funcionario": nome,
                        "cargo": cargo,
                        "tipo_aso": tipo,
                        "data_validade": venc_str,
                        **alerta,
                    }
                )
            except ValueError:
                continue

        return alertas

    # ── versões async para uso nos endpoints FastAPI ──────────────────────────

    async def verificar_certidoes(self, db=None) -> list[dict]:
        """
        Verificar certidões — versão async.
        Aceita sessão SQLAlchemy (AsyncSession) ou usa fallback sync.
        """
        if db is not None:
            from sqlalchemy import text

            hoje = date.today()
            limite = hoje + timedelta(days=60)
            rows = await db.execute(
                text(
                    "SELECT name, document_type, expiry_date "
                    "FROM ged_certidoes "
                    "WHERE expiry_date IS NOT NULL "
                    "AND expiry_date <= :limite "
                    "ORDER BY expiry_date"
                ),
                {"limite": limite},
            )
            alertas = []
            for row in rows.fetchall():
                nome, tipo, venc_date = row
                alerta = calcular_nivel_alerta(venc_date)
                alertas.append(
                    {
                        "nome": nome,
                        "tipo": tipo,
                        "data_vencimento": str(venc_date),
                        "data_renovacao": str(data_ideal_renovacao(str(tipo), venc_date)),
                        **alerta,
                    }
                )
            return alertas

        # Fallback: subprocess (background tasks)
        return self.verificar_certidoes_sync()

    async def verificar_asos_funcionarios(self, db=None) -> list[dict]:
        """
        Verificar ASOs — versão async.
        Aceita sessão SQLAlchemy (AsyncSession) ou usa fallback sync.
        """
        if db is not None:
            from sqlalchemy import text

            hoje = date.today()
            limite = hoje + timedelta(days=60)
            rows = await db.execute(
                text(
                    "SELECT e.nome, e.cargo, "
                    "a.data_validade, a.tipo "
                    "FROM gp_asos a "
                    "JOIN employees e ON e.id = a.employee_id "
                    "WHERE a.data_validade IS NOT NULL "
                    "AND a.data_validade <= :limite "
                    "AND a.status != 'cancelado' "
                    "ORDER BY a.data_validade"
                ),
                {"limite": limite},
            )
            alertas = []
            for row in rows.fetchall():
                nome, cargo, venc_date, tipo = row
                alerta = calcular_nivel_alerta(venc_date)
                alertas.append(
                    {
                        "funcionario": nome,
                        "cargo": cargo,
                        "tipo_aso": tipo or "periodico",
                        "data_validade": str(venc_date),
                        **alerta,
                    }
                )
            return alertas

        return self.verificar_asos_sync()

    async def executar_verificacao_diaria(self) -> dict:
        """
        Job diário — verificar tudo e publicar eventos
        para o GEDEON processar via ConectaEventBus.
        """
        try:
            from infrastructure.event_bus import (
                ConectaEvent,
                EventTypes,
                event_bus,
            )
        except ImportError:
            logger.warning("KRONOS: event_bus indisponível")
            event_bus = None

        logger.info("KRONOS: iniciando verificação diária")

        certidoes = self.verificar_certidoes_sync()
        asos = self.verificar_asos_sync()

        if event_bus:
            for cert in certidoes:
                if cert["nivel"] in ("critico", "alto"):
                    await event_bus.publish(
                        ConectaEvent(
                            event_type=(
                                EventTypes.FISCAL_CERTIDAO_VENCIDA
                                if cert["dias_restantes"] <= 0
                                else "fiscal.certidao.vencendo"
                            ),
                            payload={
                                "nome": cert["nome"],
                                "tipo": cert["tipo"],
                                "data_vencimento": cert["data_vencimento"],
                                "dias_restantes": cert["dias_restantes"],
                                "nivel": cert["nivel"],
                                "data_renovacao": cert["data_renovacao"],
                            },
                            source_module="kronos",
                        )
                    )
                    logger.warning(
                        "KRONOS: certidão %s — %s",
                        cert["nome"],
                        cert["label"],
                    )

            for aso in asos:
                if aso["nivel"] in ("critico", "alto"):
                    await event_bus.publish(
                        ConectaEvent(
                            event_type=EventTypes.SAUDE_ASO_VENCENDO,
                            payload={
                                "funcionario_nome": aso["funcionario"],
                                "cargo": aso["cargo"],
                                "data_validade": aso["data_validade"],
                                "dias_restantes": aso["dias_restantes"],
                                "nivel": aso["nivel"],
                            },
                            source_module="kronos",
                        )
                    )

        logger.info(
            "KRONOS: verificação concluída — %d certidões, %d ASOs com alerta",
            len(certidoes),
            len(asos),
        )

        return {
            "certidoes_alerta": len(certidoes),
            "asos_alerta": len(asos),
        }


# Singleton global
kronos = Kronos()

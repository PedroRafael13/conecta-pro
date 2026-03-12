"""
Servico de Notificacoes do Modulo de Licitacoes.

Gera alertas para eventos importantes do ciclo de licitacoes:
- Certidoes vencendo/vencidas
- Novas oportunidades relevantes
- Pipeline GO/NO-GO concluido
- Abertura de editais se aproximando
- Sincronizacoes concluidas

Integra-se com o sistema de notificacoes operacional existente
(modules.operacional.communication) quando disponivel, ou opera
de forma standalone registrando notificacoes internamente.

Author: Conecta PRO Team
Date: 2026-03-12
"""

from __future__ import annotations

import logging
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────


class NotificationChannel(StrEnum):
    """Canais de envio de notificacao do modulo de licitacoes."""

    EMAIL = "email"
    PUSH = "push"
    WHATSAPP = "whatsapp"
    INTERNAL = "internal"  # Notificacao interna no sistema


class BiddingNotificationType(StrEnum):
    """Tipos de notificacao especificos do modulo de licitacoes."""

    CERTIDAO_VENCENDO = "certidao_vencendo"
    CERTIDAO_VENCIDA = "certidao_vencida"
    NOVA_OPORTUNIDADE = "nova_oportunidade"
    PIPELINE_CONCLUIDO = "pipeline_concluido"
    EDITAL_ABERTURA = "edital_abertura"
    SYNC_COMPLETA = "sync_completa"


class NotificationPriority(StrEnum):
    """Prioridade da notificacao."""

    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


# ──────────────────────────────────────────────
# DTOs
# ──────────────────────────────────────────────


class BiddingNotification(BaseModel):
    """Estrutura de uma notificacao do modulo de licitacoes."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    tipo: BiddingNotificationType
    titulo: str
    mensagem: str
    prioridade: NotificationPriority = NotificationPriority.MEDIA
    canal: NotificationChannel = NotificationChannel.INTERNAL
    criado_em: datetime = Field(default_factory=datetime.utcnow)
    enviado: bool = False
    enviado_em: datetime | None = None
    lido: bool = False
    lido_em: datetime | None = None

    # Referencia ao objeto relacionado
    referencia_tipo: str | None = None  # "certidao", "oportunidade", "pipeline", "edital", "sync"
    referencia_id: str | None = None

    # Dados adicionais para contexto
    dados_extras: dict[str, Any] = Field(default_factory=dict)

    # URL de acao no frontend
    action_url: str | None = None


# ──────────────────────────────────────────────
# Service
# ──────────────────────────────────────────────


class BiddingNotificationService:
    """
    Servico de notificacoes para o modulo de licitacoes.

    Gera e registra alertas para eventos criticos do fluxo de licitacoes.
    Por enquanto, as notificacoes sao registradas internamente e logadas.
    A integracao com canais externos (email, WhatsApp, push) sera feita
    em uma etapa futura.

    Pode operar de forma standalone ou integrada com o NotificationService
    do modulo operacional (communication).

    Attributes:
        _notifications: Buffer interno de notificacoes geradas.
        _operacional_service: Referencia opcional ao NotificationService
                              do modulo operacional para integracao.

    Example:
        >>> service = BiddingNotificationService()
        >>> notif = service.notify_certidao_vencendo("cnd_federal", 10, "35.710.481/0001-03")
        >>> print(notif.titulo)
        'Certidao Vencendo: CND Federal'
    """

    def __init__(self, operacional_service: Any | None = None) -> None:
        """
        Inicializa o servico de notificacoes de licitacoes.

        Args:
            operacional_service: Instancia opcional do NotificationService
                                 do modulo operacional para integracao.
                                 Se None, opera de forma standalone.
        """
        self._notifications: list[BiddingNotification] = []
        self._operacional_service = operacional_service

    # ──────────────────────────────────────────
    # Metodos publicos de notificacao
    # ──────────────────────────────────────────

    def notify_certidao_vencendo(
        self,
        tipo: str,
        dias_restantes: int,
        cnpj: str,
        channel: NotificationChannel = NotificationChannel.INTERNAL,
    ) -> BiddingNotification:
        """
        Notifica sobre certidao proxima do vencimento.

        Determina automaticamente a prioridade com base nos dias restantes:
        - <= 0 dias: CRITICA (ja vencida)
        - <= 15 dias: ALTA
        - <= 30 dias: MEDIA
        - > 30 dias: BAIXA

        Args:
            tipo: Tipo da certidao (ex: "cnd_federal", "crf_fgts").
            dias_restantes: Dias ate o vencimento. Negativo = ja vencida.
            cnpj: CNPJ da empresa.
            channel: Canal de envio da notificacao.

        Returns:
            BiddingNotification com dados do alerta.
        """
        tipo_display = tipo.upper().replace("_", " ")

        # Determinar prioridade e tipo com base nos dias
        if dias_restantes <= 0:
            prioridade = NotificationPriority.CRITICA
            notif_tipo = BiddingNotificationType.CERTIDAO_VENCIDA
            titulo = f"Certidao VENCIDA: {tipo_display}"
            mensagem = (
                f"A certidao {tipo_display} do CNPJ {cnpj} esta VENCIDA "
                f"ha {abs(dias_restantes)} dia(s). Renovacao imediata necessaria "
                f"para manter aptidao em licitacoes."
            )
        elif dias_restantes <= 15:
            prioridade = NotificationPriority.ALTA
            notif_tipo = BiddingNotificationType.CERTIDAO_VENCENDO
            titulo = f"URGENTE - Certidao Vencendo: {tipo_display}"
            mensagem = (
                f"A certidao {tipo_display} do CNPJ {cnpj} vence em "
                f"{dias_restantes} dia(s). Providenciar renovacao urgente."
            )
        elif dias_restantes <= 30:
            prioridade = NotificationPriority.MEDIA
            notif_tipo = BiddingNotificationType.CERTIDAO_VENCENDO
            titulo = f"Certidao Vencendo: {tipo_display}"
            mensagem = f"A certidao {tipo_display} do CNPJ {cnpj} vence em {dias_restantes} dia(s). Agendar renovacao."
        else:
            prioridade = NotificationPriority.BAIXA
            notif_tipo = BiddingNotificationType.CERTIDAO_VENCENDO
            titulo = f"Certidao Vencendo: {tipo_display}"
            mensagem = f"A certidao {tipo_display} do CNPJ {cnpj} vence em {dias_restantes} dia(s). Acompanhar."

        notification = self._create_notification(
            tipo=notif_tipo,
            titulo=titulo,
            mensagem=mensagem,
            prioridade=prioridade,
            canal=channel,
            referencia_tipo="certidao",
            dados_extras={
                "tipo_certidao": tipo,
                "dias_restantes": dias_restantes,
                "cnpj": cnpj,
            },
            action_url=f"/licitacoes/certidoes?tipo={tipo}&cnpj={cnpj}",
        )

        logger.warning(
            "[BIDDING_NOTIF] Certidao %s | CNPJ %s | %d dias restantes | Prioridade: %s",
            tipo,
            cnpj,
            dias_restantes,
            prioridade.value,
        )

        return notification

    def notify_nova_oportunidade(
        self,
        oportunidade_data: dict[str, Any],
        channel: NotificationChannel = NotificationChannel.INTERNAL,
    ) -> BiddingNotification:
        """
        Notifica sobre nova oportunidade de licitacao encontrada.

        Args:
            oportunidade_data: Dados da oportunidade. Campos esperados:
                - id (str): Identificador da oportunidade.
                - numero (str): Numero do edital/processo.
                - orgao (str): Orgao licitante.
                - objeto (str): Objeto resumido da licitacao.
                - valor_estimado (float, optional): Valor estimado.
                - data_abertura (str, optional): Data de abertura (ISO).
                - modalidade (str, optional): Modalidade (pregao, concorrencia, etc).
                - relevancia_score (float, optional): Score de relevancia 0-100.
                - fonte (str, optional): Portal de origem (PNCP, ComprasNet, etc).
            channel: Canal de envio da notificacao.

        Returns:
            BiddingNotification com dados do alerta.
        """
        numero = oportunidade_data.get("numero", "N/A")
        orgao = oportunidade_data.get("orgao", "Orgao nao informado")
        objeto = oportunidade_data.get("objeto", "Objeto nao informado")
        valor = oportunidade_data.get("valor_estimado")
        data_abertura = oportunidade_data.get("data_abertura", "")
        modalidade = oportunidade_data.get("modalidade", "")
        relevancia = oportunidade_data.get("relevancia_score", 0)
        oportunidade_id = oportunidade_data.get("id", "")

        # Prioridade baseada na relevancia
        if relevancia >= 80:
            prioridade = NotificationPriority.ALTA
        elif relevancia >= 50:
            prioridade = NotificationPriority.MEDIA
        else:
            prioridade = NotificationPriority.BAIXA

        valor_fmt = f"R$ {valor:,.2f}" if valor else "Nao informado"
        modalidade_fmt = f" ({modalidade})" if modalidade else ""
        abertura_fmt = f" | Abertura: {data_abertura}" if data_abertura else ""

        titulo = f"Nova Oportunidade: {numero}{modalidade_fmt}"
        mensagem = (
            f"Orgao: {orgao}\n"
            f"Objeto: {objeto[:200]}\n"
            f"Valor estimado: {valor_fmt}{abertura_fmt}\n"
            f"Relevancia: {relevancia:.0f}%"
        )

        notification = self._create_notification(
            tipo=BiddingNotificationType.NOVA_OPORTUNIDADE,
            titulo=titulo,
            mensagem=mensagem,
            prioridade=prioridade,
            canal=channel,
            referencia_tipo="oportunidade",
            referencia_id=oportunidade_id,
            dados_extras=oportunidade_data,
            action_url=f"/licitacoes/oportunidades/{oportunidade_id}" if oportunidade_id else None,
        )

        logger.info(
            "[BIDDING_NOTIF] Nova oportunidade: %s | Orgao: %s | Valor: %s | Relevancia: %.0f%%",
            numero,
            orgao,
            valor_fmt,
            relevancia,
        )

        return notification

    def notify_pipeline_concluido(
        self,
        pipeline_result: dict[str, Any],
        channel: NotificationChannel = NotificationChannel.INTERNAL,
    ) -> BiddingNotification:
        """
        Notifica sobre conclusao da analise de pipeline GO/NO-GO.

        Args:
            pipeline_result: Resultado do pipeline. Campos esperados:
                - tender_id (str): ID da licitacao analisada.
                - numero (str): Numero do edital.
                - decisao (str): "GO" ou "NO_GO".
                - score_final (float): Score final da analise 0-100.
                - motivos (list[str]): Motivos da decisao.
                - agentes_resultados (dict, optional): Resultados por agente.
                - tempo_analise_segundos (float, optional): Tempo total.
            channel: Canal de envio da notificacao.

        Returns:
            BiddingNotification com dados do alerta.
        """
        tender_id = pipeline_result.get("tender_id", "")
        numero = pipeline_result.get("numero", "N/A")
        decisao = pipeline_result.get("decisao", "INDEFINIDO")
        score = pipeline_result.get("score_final", 0)
        motivos = pipeline_result.get("motivos", [])
        tempo = pipeline_result.get("tempo_analise_segundos")

        is_go = decisao.upper() == "GO"
        prioridade = NotificationPriority.ALTA if is_go else NotificationPriority.MEDIA

        decisao_label = "GO - Participar" if is_go else "NO-GO - Nao participar"
        tempo_fmt = f" em {tempo:.1f}s" if tempo else ""

        titulo = f"Pipeline Concluido: {numero} - {decisao_label}"

        motivos_fmt = "\n".join(f"  - {m}" for m in motivos[:5]) if motivos else "  Nenhum motivo registrado"
        mensagem = (
            f"Licitacao: {numero}\nDecisao: {decisao_label}\nScore: {score:.1f}/100{tempo_fmt}\nMotivos:\n{motivos_fmt}"
        )

        notification = self._create_notification(
            tipo=BiddingNotificationType.PIPELINE_CONCLUIDO,
            titulo=titulo,
            mensagem=mensagem,
            prioridade=prioridade,
            canal=channel,
            referencia_tipo="pipeline",
            referencia_id=tender_id,
            dados_extras=pipeline_result,
            action_url=f"/licitacoes/pipeline/{tender_id}" if tender_id else None,
        )

        logger.info(
            "[BIDDING_NOTIF] Pipeline concluido: %s | Decisao: %s | Score: %.1f",
            numero,
            decisao,
            score,
        )

        return notification

    def notify_edital_abertura(
        self,
        tender_data: dict[str, Any],
        channel: NotificationChannel = NotificationChannel.INTERNAL,
    ) -> BiddingNotification:
        """
        Notifica sobre data de abertura de edital se aproximando.

        A prioridade e calculada automaticamente:
        - Hoje ou amanha: CRITICA
        - 2-3 dias: ALTA
        - 4-7 dias: MEDIA
        - > 7 dias: BAIXA

        Args:
            tender_data: Dados do edital. Campos esperados:
                - id (str): ID da licitacao.
                - numero (str): Numero do edital.
                - orgao (str): Orgao licitante.
                - objeto (str): Objeto resumido.
                - data_abertura (str): Data de abertura (ISO format).
                - dias_para_abertura (int): Dias ate a abertura.
                - modalidade (str, optional): Modalidade da licitacao.
                - local (str, optional): Local da sessao.
                - documentos_pendentes (list[str], optional): Docs pendentes.
            channel: Canal de envio da notificacao.

        Returns:
            BiddingNotification com dados do alerta.
        """
        tender_id = tender_data.get("id", "")
        numero = tender_data.get("numero", "N/A")
        orgao = tender_data.get("orgao", "")
        data_abertura = tender_data.get("data_abertura", "")
        dias = tender_data.get("dias_para_abertura", 0)
        docs_pendentes = tender_data.get("documentos_pendentes", [])

        # Prioridade baseada em proximidade
        if dias <= 1:
            prioridade = NotificationPriority.CRITICA
            urgencia = "HOJE/AMANHA"
        elif dias <= 3:
            prioridade = NotificationPriority.ALTA
            urgencia = f"em {dias} dias"
        elif dias <= 7:
            prioridade = NotificationPriority.MEDIA
            urgencia = f"em {dias} dias"
        else:
            prioridade = NotificationPriority.BAIXA
            urgencia = f"em {dias} dias"

        titulo = f"Abertura de Edital {urgencia}: {numero}"

        docs_fmt = ""
        if docs_pendentes:
            docs_list = "\n".join(f"  - {d}" for d in docs_pendentes[:5])
            docs_fmt = f"\nDocumentos pendentes:\n{docs_list}"

        mensagem = f"Edital: {numero}\nOrgao: {orgao}\nAbertura: {data_abertura} ({urgencia}){docs_fmt}"

        notification = self._create_notification(
            tipo=BiddingNotificationType.EDITAL_ABERTURA,
            titulo=titulo,
            mensagem=mensagem,
            prioridade=prioridade,
            canal=channel,
            referencia_tipo="edital",
            referencia_id=tender_id,
            dados_extras=tender_data,
            action_url=f"/licitacoes/editais/{tender_id}" if tender_id else None,
        )

        logger.info(
            "[BIDDING_NOTIF] Edital abertura: %s | %s | Prioridade: %s",
            numero,
            urgencia,
            prioridade.value,
        )

        return notification

    def notify_sync_completa(
        self,
        sync_job_data: dict[str, Any],
        channel: NotificationChannel = NotificationChannel.INTERNAL,
    ) -> BiddingNotification:
        """
        Notifica sobre conclusao de sincronizacao com portal de licitacoes.

        Args:
            sync_job_data: Dados do job de sincronizacao. Campos esperados:
                - job_id (str): ID do job de sync.
                - portal (str): Portal sincronizado (PNCP, ComprasNet, etc).
                - total_encontradas (int): Total de licitacoes encontradas.
                - novas (int): Licitacoes novas adicionadas.
                - atualizadas (int): Licitacoes atualizadas.
                - erros (int): Quantidade de erros.
                - tempo_segundos (float): Tempo total da sincronizacao.
                - filtros_aplicados (dict, optional): Filtros usados.
                - proxima_sync (str, optional): Proxima sync agendada.
            channel: Canal de envio da notificacao.

        Returns:
            BiddingNotification com dados do alerta.
        """
        job_id = sync_job_data.get("job_id", "")
        portal = sync_job_data.get("portal", "Portal")
        total = sync_job_data.get("total_encontradas", 0)
        novas = sync_job_data.get("novas", 0)
        atualizadas = sync_job_data.get("atualizadas", 0)
        erros = sync_job_data.get("erros", 0)
        tempo = sync_job_data.get("tempo_segundos", 0)
        proxima = sync_job_data.get("proxima_sync", "")

        # Prioridade: alta se houve novas oportunidades, media se apenas atualizacoes
        if erros > 0:
            prioridade = NotificationPriority.ALTA
        elif novas > 0:
            prioridade = NotificationPriority.MEDIA
        else:
            prioridade = NotificationPriority.BAIXA

        titulo = f"Sync {portal} Concluida: {novas} novas, {atualizadas} atualizadas"

        proxima_fmt = f"\nProxima sync: {proxima}" if proxima else ""
        erros_fmt = f"\nERROS: {erros}" if erros > 0 else ""

        mensagem = (
            f"Portal: {portal}\n"
            f"Total encontradas: {total}\n"
            f"Novas: {novas} | Atualizadas: {atualizadas}\n"
            f"Tempo: {tempo:.1f}s{erros_fmt}{proxima_fmt}"
        )

        notification = self._create_notification(
            tipo=BiddingNotificationType.SYNC_COMPLETA,
            titulo=titulo,
            mensagem=mensagem,
            prioridade=prioridade,
            canal=channel,
            referencia_tipo="sync",
            referencia_id=job_id,
            dados_extras=sync_job_data,
            action_url="/licitacoes/sync/historico",
        )

        logger.info(
            "[BIDDING_NOTIF] Sync %s concluida: %d encontradas, %d novas, %d erros (%.1fs)",
            portal,
            total,
            novas,
            erros,
            tempo,
        )

        return notification

    # ──────────────────────────────────────────
    # Metodos de consulta
    # ──────────────────────────────────────────

    def get_notifications(
        self,
        tipo: BiddingNotificationType | None = None,
        prioridade: NotificationPriority | None = None,
        apenas_nao_lidas: bool = False,
        limit: int = 50,
    ) -> list[BiddingNotification]:
        """
        Retorna notificacoes do buffer interno, com filtros opcionais.

        Args:
            tipo: Filtrar por tipo de notificacao.
            prioridade: Filtrar por prioridade.
            apenas_nao_lidas: Se True, retorna apenas nao lidas.
            limit: Maximo de resultados.

        Returns:
            Lista de notificacoes filtradas, ordenadas por criacao (mais recente primeiro).
        """
        result = self._notifications

        if tipo is not None:
            result = [n for n in result if n.tipo == tipo]
        if prioridade is not None:
            result = [n for n in result if n.prioridade == prioridade]
        if apenas_nao_lidas:
            result = [n for n in result if not n.lido]

        # Mais recente primeiro
        result = sorted(result, key=lambda n: n.criado_em, reverse=True)
        return result[:limit]

    def get_summary(self) -> dict[str, Any]:
        """
        Retorna resumo das notificacoes pendentes.

        Returns:
            Dict com contadores por tipo e prioridade.
        """
        total = len(self._notifications)
        nao_lidas = sum(1 for n in self._notifications if not n.lido)

        por_tipo: dict[str, int] = {}
        for n in self._notifications:
            por_tipo[n.tipo.value] = por_tipo.get(n.tipo.value, 0) + 1

        por_prioridade: dict[str, int] = {}
        for n in self._notifications:
            if not n.lido:
                por_prioridade[n.prioridade.value] = por_prioridade.get(n.prioridade.value, 0) + 1

        return {
            "total": total,
            "nao_lidas": nao_lidas,
            "por_tipo": por_tipo,
            "por_prioridade": por_prioridade,
        }

    def mark_as_read(self, notification_id: str) -> bool:
        """
        Marca uma notificacao como lida.

        Args:
            notification_id: ID da notificacao.

        Returns:
            True se encontrada e marcada, False se nao encontrada.
        """
        for n in self._notifications:
            if n.id == notification_id:
                n.lido = True
                n.lido_em = datetime.utcnow()
                return True
        return False

    def clear(self) -> int:
        """
        Limpa todas as notificacoes do buffer interno.

        Returns:
            Quantidade de notificacoes removidas.
        """
        count = len(self._notifications)
        self._notifications.clear()
        return count

    # ──────────────────────────────────────────
    # Metodos internos
    # ──────────────────────────────────────────

    def _create_notification(
        self,
        tipo: BiddingNotificationType,
        titulo: str,
        mensagem: str,
        prioridade: NotificationPriority,
        canal: NotificationChannel,
        referencia_tipo: str | None = None,
        referencia_id: str | None = None,
        dados_extras: dict[str, Any] | None = None,
        action_url: str | None = None,
    ) -> BiddingNotification:
        """
        Cria uma notificacao, registra no buffer e despacha para o canal.

        Args:
            tipo: Tipo da notificacao.
            titulo: Titulo da notificacao.
            mensagem: Corpo da mensagem.
            prioridade: Prioridade do alerta.
            canal: Canal de envio.
            referencia_tipo: Tipo do objeto referenciado.
            referencia_id: ID do objeto referenciado.
            dados_extras: Dados adicionais de contexto.
            action_url: URL de acao no frontend.

        Returns:
            BiddingNotification criada e registrada.
        """
        notification = BiddingNotification(
            tipo=tipo,
            titulo=titulo,
            mensagem=mensagem,
            prioridade=prioridade,
            canal=canal,
            referencia_tipo=referencia_tipo,
            referencia_id=referencia_id,
            dados_extras=dados_extras or {},
            action_url=action_url,
        )

        # Registrar no buffer interno
        self._notifications.append(notification)

        # Despachar para o canal
        self._dispatch(notification)

        return notification

    def _dispatch(self, notification: BiddingNotification) -> None:
        """
        Despacha a notificacao para o canal configurado.

        Por enquanto, todos os canais apenas logam a notificacao.
        Em producao, cada canal sera integrado com seu respectivo
        provedor (SMTP, Firebase, WhatsApp Business API).

        Args:
            notification: Notificacao a ser despachada.
        """
        canal = notification.canal

        if canal == NotificationChannel.INTERNAL:
            logger.info(
                "[BIDDING_NOTIF][INTERNAL] %s | %s",
                notification.titulo,
                notification.prioridade.value,
            )

        elif canal == NotificationChannel.EMAIL:
            # TODO: Integrar com servico de email (SMTP / SES)
            logger.info(
                "[BIDDING_NOTIF][EMAIL] Pendente envio: %s",
                notification.titulo,
            )

        elif canal == NotificationChannel.PUSH:
            # TODO: Integrar com Firebase Cloud Messaging
            logger.info(
                "[BIDDING_NOTIF][PUSH] Pendente envio: %s",
                notification.titulo,
            )

        elif canal == NotificationChannel.WHATSAPP:
            # TODO: Integrar com WhatsApp Business API
            logger.info(
                "[BIDDING_NOTIF][WHATSAPP] Pendente envio: %s",
                notification.titulo,
            )

        # Marcar como "enviado" (internamente registrado)
        notification.enviado = True
        notification.enviado_em = datetime.utcnow()

    # ──────────────────────────────────────────
    # Integracao com modulo operacional
    # ──────────────────────────────────────────

    async def forward_to_operacional(
        self,
        notification: BiddingNotification,
        tenant_id: str,
        user_ids: list[str],
    ) -> None:
        """
        Encaminha notificacao para o sistema de notificacoes operacional.

        Converte a BiddingNotification para o formato do
        NotificationService do modulo operacional e envia para
        os usuarios especificados. Requer que o servico operacional
        tenha sido injetado na inicializacao.

        Args:
            notification: Notificacao de licitacao a encaminhar.
            tenant_id: ID do tenant.
            user_ids: Lista de IDs dos usuarios destinatarios.

        Note:
            Se o servico operacional nao estiver disponivel,
            a notificacao e apenas logada com um aviso.
        """
        if self._operacional_service is None:
            logger.warning(
                "[BIDDING_NOTIF] Servico operacional nao configurado. "
                "Notificacao '%s' nao encaminhada para %d usuario(s).",
                notification.titulo,
                len(user_ids),
            )
            return

        try:
            # Importar schemas do modulo operacional apenas quando necessario
            from modules.operacional.communication.models.notification import (
                NotificationChannel as OpNotifChannel,
            )
            from modules.operacional.communication.models.notification import (
                NotificationType as OpNotifType,
            )
            from modules.operacional.communication.schemas.communication_schemas import (
                NotificationCreate,
            )

            # Mapear canal do bidding para canal operacional
            channel_map = {
                NotificationChannel.EMAIL: OpNotifChannel.EMAIL,
                NotificationChannel.PUSH: OpNotifChannel.PUSH,
                NotificationChannel.WHATSAPP: OpNotifChannel.WHATSAPP,
                NotificationChannel.INTERNAL: OpNotifChannel.IN_APP,
            }
            op_channel = channel_map.get(notification.canal, OpNotifChannel.IN_APP)

            for user_id in user_ids:
                data = NotificationCreate(
                    user_id=user_id,
                    title=notification.titulo[:100],
                    body=notification.mensagem[:500],
                    type=OpNotifType.ALERTA,
                    channels=[op_channel],
                    reference_type=notification.referencia_tipo,
                    reference_id=notification.referencia_id,
                    action_url=notification.action_url,
                    extra_data={
                        "bidding_notification_id": notification.id,
                        "bidding_tipo": notification.tipo.value,
                        "bidding_prioridade": notification.prioridade.value,
                        **notification.dados_extras,
                    },
                )
                await self._operacional_service.send(data, tenant_id)

            logger.info(
                "[BIDDING_NOTIF] Encaminhada para operacional: '%s' -> %d usuario(s)",
                notification.titulo,
                len(user_ids),
            )

        except ImportError:
            logger.warning(
                "[BIDDING_NOTIF] Modulo operacional de comunicacao nao disponivel. "
                "Notificacao '%s' mantida apenas no buffer interno.",
                notification.titulo,
            )
        except Exception as e:
            logger.error(
                "[BIDDING_NOTIF] Erro ao encaminhar para operacional: %s",
                str(e),
            )

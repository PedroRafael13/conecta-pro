"""
Servico de Notificacoes do Modulo de Licitacoes.

Gera alertas para eventos importantes do ciclo de licitacoes:
- Novo edital compativel encontrado
- Edital vencendo (prazo se aproximando)
- Certidoes vencendo/vencidas
- Proposta mudou de status
- Disputa de pregao iniciando
- Convocacao no pregao
- Resultado do pregao
- Novas oportunidades relevantes
- Pipeline GO/NO-GO concluido
- Sincronizacoes concluidas

Integra-se com o sistema de notificacoes operacional existente
(modules.operacional.communication) quando disponivel, ou opera
de forma standalone registrando notificacoes internamente.

Canais suportados: EMAIL (SMTP), PUSH (buffer interno), INTERNAL (log).

Author: Conecta PRO Team
Date: 2026-03-12
"""

from __future__ import annotations

import logging
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
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
    INTERNAL = "internal"  # Notificacao interna no sistema


class BiddingNotificationType(StrEnum):
    """Tipos de notificacao especificos do modulo de licitacoes."""

    # Tipos primarios (7 eventos obrigatorios)
    EDITAL_NOVO = "edital_novo"  # Novo edital compativel encontrado
    EDITAL_VENCENDO = "edital_vencendo"  # Edital vence em {dias} dias
    CERTIDAO_VENCENDO = "certidao_vencendo"  # Certidao {tipo} vence em {dias} dias
    PROPOSTA_STATUS = "proposta_status"  # Proposta mudou de status
    DISPUTA_INICIANDO = "disputa_iniciando"  # Disputa do pregao inicia em {min} min
    CONVOCACAO = "convocacao"  # Convocacao no pregao
    RESULTADO = "resultado"  # Resultado do pregao

    # Tipos complementares
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
    referencia_tipo: str | None = None  # "certidao", "oportunidade", "pipeline", "edital", "sync", "proposta", "pregao"
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
    Suporta envio via EMAIL (SMTP), PUSH (buffer consultavel via API) e
    INTERNAL (log apenas).

    Canais de despacho:
    - EMAIL: envia via SMTP usando variaveis de ambiente SMTP_HOST, SMTP_PORT,
      SMTP_USER, SMTP_PASS. Se nao configurado, faz fallback para log.
    - PUSH: armazena no buffer interno _push_buffer, consultavel via
      get_push_notifications().
    - INTERNAL: apenas loga e armazena no buffer geral.

    Attributes:
        _notifications: Buffer interno de notificacoes geradas.
        _push_buffer: Buffer de notificacoes push pendentes.
        _operacional_service: Referencia opcional ao NotificationService
                              do modulo operacional para integracao.

    Example:
        >>> service = BiddingNotificationService()
        >>> notif = service.notify_certidao_vencendo("cnd_federal", 10)
        >>> print(notif.titulo)
        'URGENTE - Certidao Vencendo: CND FEDERAL'
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
        self._push_buffer: list[BiddingNotification] = []
        self._operacional_service = operacional_service

        # SMTP config from env
        self._smtp_host = os.environ.get("SMTP_HOST", "")
        self._smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self._smtp_user = os.environ.get("SMTP_USER", "")
        self._smtp_pass = os.environ.get("SMTP_PASS", "")

    # ──────────────────────────────────────────
    # 7 Convenience methods (required event types)
    # ──────────────────────────────────────────

    def notify_edital_novo(
        self,
        edital_numero: str,
        orgao: str,
        objeto: str,
        edital_id: str | None = None,
        valor_estimado: float | None = None,
        channel: NotificationChannel = NotificationChannel.INTERNAL,
    ) -> BiddingNotification:
        """
        Notifica sobre novo edital compativel encontrado.

        Args:
            edital_numero: Numero do edital.
            orgao: Orgao licitante.
            objeto: Objeto resumido da licitacao.
            edital_id: ID do edital (para action_url).
            valor_estimado: Valor estimado (opcional).
            channel: Canal de envio.

        Returns:
            BiddingNotification criada.
        """
        valor_fmt = f" | Valor: R$ {valor_estimado:,.2f}" if valor_estimado else ""
        titulo = f"Novo Edital: {edital_numero}"
        mensagem = f"Orgao: {orgao}\nObjeto: {objeto[:300]}{valor_fmt}\nEdital compativel com perfil da empresa."

        notification = self._create_notification(
            tipo=BiddingNotificationType.EDITAL_NOVO,
            titulo=titulo,
            mensagem=mensagem,
            prioridade=NotificationPriority.ALTA,
            canal=channel,
            referencia_tipo="edital",
            referencia_id=edital_id,
            dados_extras={
                "edital_numero": edital_numero,
                "orgao": orgao,
                "objeto": objeto[:500],
                "valor_estimado": valor_estimado,
            },
            action_url=f"/licitacoes/editais/{edital_id}" if edital_id else None,
        )

        logger.info(
            "[BIDDING_NOTIF] Novo edital: %s | Orgao: %s",
            edital_numero,
            orgao,
        )

        return notification

    def notify_edital_vencendo(
        self,
        edital_numero: str,
        dias: int,
        edital_id: str | None = None,
        channel: NotificationChannel = NotificationChannel.INTERNAL,
    ) -> BiddingNotification:
        """
        Notifica que edital vence em {dias} dias.

        Args:
            edital_numero: Numero do edital.
            dias: Dias restantes ate vencimento/abertura.
            edital_id: ID do edital.
            channel: Canal de envio.

        Returns:
            BiddingNotification criada.
        """
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

        titulo = f"Edital Vencendo {urgencia}: {edital_numero}"
        mensagem = f"O edital {edital_numero} vence {urgencia}. Verifique documentacao e proposta."

        notification = self._create_notification(
            tipo=BiddingNotificationType.EDITAL_VENCENDO,
            titulo=titulo,
            mensagem=mensagem,
            prioridade=prioridade,
            canal=channel,
            referencia_tipo="edital",
            referencia_id=edital_id,
            dados_extras={
                "edital_numero": edital_numero,
                "dias_restantes": dias,
            },
            action_url=f"/licitacoes/editais/{edital_id}" if edital_id else None,
        )

        logger.info(
            "[BIDDING_NOTIF] Edital vencendo: %s | %s | Prioridade: %s",
            edital_numero,
            urgencia,
            prioridade.value,
        )

        return notification

    def notify_certidao_vencendo(
        self,
        tipo: str,
        dias: int,
        cnpj: str = "35.710.481/0001-03",
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
            dias: Dias ate o vencimento. Negativo = ja vencida.
            cnpj: CNPJ da empresa.
            channel: Canal de envio da notificacao.

        Returns:
            BiddingNotification com dados do alerta.
        """
        tipo_display = tipo.upper().replace("_", " ")

        # Determinar prioridade e tipo com base nos dias
        if dias <= 0:
            prioridade = NotificationPriority.CRITICA
            notif_tipo = BiddingNotificationType.CERTIDAO_VENCIDA
            titulo = f"Certidao VENCIDA: {tipo_display}"
            mensagem = (
                f"A certidao {tipo_display} do CNPJ {cnpj} esta VENCIDA "
                f"ha {abs(dias)} dia(s). Renovacao imediata necessaria "
                f"para manter aptidao em licitacoes."
            )
        elif dias <= 15:
            prioridade = NotificationPriority.ALTA
            notif_tipo = BiddingNotificationType.CERTIDAO_VENCENDO
            titulo = f"URGENTE - Certidao Vencendo: {tipo_display}"
            mensagem = (
                f"A certidao {tipo_display} do CNPJ {cnpj} vence em {dias} dia(s). Providenciar renovacao urgente."
            )
        elif dias <= 30:
            prioridade = NotificationPriority.MEDIA
            notif_tipo = BiddingNotificationType.CERTIDAO_VENCENDO
            titulo = f"Certidao Vencendo: {tipo_display}"
            mensagem = f"A certidao {tipo_display} do CNPJ {cnpj} vence em {dias} dia(s). Agendar renovacao."
        else:
            prioridade = NotificationPriority.BAIXA
            notif_tipo = BiddingNotificationType.CERTIDAO_VENCENDO
            titulo = f"Certidao Vencendo: {tipo_display}"
            mensagem = f"A certidao {tipo_display} do CNPJ {cnpj} vence em {dias} dia(s). Acompanhar."

        notification = self._create_notification(
            tipo=notif_tipo,
            titulo=titulo,
            mensagem=mensagem,
            prioridade=prioridade,
            canal=channel,
            referencia_tipo="certidao",
            dados_extras={
                "tipo_certidao": tipo,
                "dias_restantes": dias,
                "cnpj": cnpj,
            },
            action_url=f"/licitacoes/certidoes?tipo={tipo}&cnpj={cnpj}",
        )

        logger.warning(
            "[BIDDING_NOTIF] Certidao %s | CNPJ %s | %d dias restantes | Prioridade: %s",
            tipo,
            cnpj,
            dias,
            prioridade.value,
        )

        return notification

    def notify_proposta_status(
        self,
        proposta_numero: str,
        novo_status: str,
        proposta_id: str | None = None,
        tender_id: str | None = None,
        channel: NotificationChannel = NotificationChannel.INTERNAL,
    ) -> BiddingNotification:
        """
        Notifica que uma proposta mudou de status.

        Args:
            proposta_numero: Numero/identificador da proposta.
            novo_status: Novo status da proposta.
            proposta_id: ID da proposta.
            tender_id: ID do edital relacionado.
            channel: Canal de envio.

        Returns:
            BiddingNotification criada.
        """
        # Prioridade baseada no status
        status_prioridade = {
            "winner": NotificationPriority.ALTA,
            "vencedora": NotificationPriority.ALTA,
            "submitted": NotificationPriority.MEDIA,
            "enviada": NotificationPriority.MEDIA,
            "classified": NotificationPriority.MEDIA,
            "disqualified": NotificationPriority.ALTA,
            "desclassificada": NotificationPriority.ALTA,
        }
        prioridade = status_prioridade.get(novo_status.lower(), NotificationPriority.MEDIA)

        titulo = f"Proposta {proposta_numero}: Status -> {novo_status.upper()}"
        mensagem = f"A proposta {proposta_numero} teve seu status alterado para: {novo_status}."

        notification = self._create_notification(
            tipo=BiddingNotificationType.PROPOSTA_STATUS,
            titulo=titulo,
            mensagem=mensagem,
            prioridade=prioridade,
            canal=channel,
            referencia_tipo="proposta",
            referencia_id=proposta_id,
            dados_extras={
                "proposta_numero": proposta_numero,
                "novo_status": novo_status,
                "tender_id": tender_id,
            },
            action_url=f"/licitacoes/propostas/{proposta_id}" if proposta_id else None,
        )

        logger.info(
            "[BIDDING_NOTIF] Proposta status: %s -> %s | Prioridade: %s",
            proposta_numero,
            novo_status,
            prioridade.value,
        )

        return notification

    def notify_disputa_iniciando(
        self,
        pregao_numero: str,
        minutos: int,
        pregao_id: str | None = None,
        channel: NotificationChannel = NotificationChannel.INTERNAL,
    ) -> BiddingNotification:
        """
        Notifica que disputa de pregao inicia em {minutos} minutos.

        Args:
            pregao_numero: Numero do pregao.
            minutos: Minutos ate o inicio da disputa.
            pregao_id: ID do pregao/tender.
            channel: Canal de envio.

        Returns:
            BiddingNotification criada.
        """
        if minutos <= 5:
            prioridade = NotificationPriority.CRITICA
        elif minutos <= 15:
            prioridade = NotificationPriority.ALTA
        elif minutos <= 30:
            prioridade = NotificationPriority.MEDIA
        else:
            prioridade = NotificationPriority.BAIXA

        titulo = f"Disputa Iniciando em {minutos}min: Pregao {pregao_numero}"
        mensagem = (
            f"A fase de disputa do Pregao {pregao_numero} inicia em {minutos} minuto(s). "
            f"Certifique-se de estar conectado ao portal."
        )

        notification = self._create_notification(
            tipo=BiddingNotificationType.DISPUTA_INICIANDO,
            titulo=titulo,
            mensagem=mensagem,
            prioridade=prioridade,
            canal=channel,
            referencia_tipo="pregao",
            referencia_id=pregao_id,
            dados_extras={
                "pregao_numero": pregao_numero,
                "minutos_para_inicio": minutos,
            },
            action_url=f"/licitacoes/pregao/{pregao_id}/disputa" if pregao_id else None,
        )

        logger.info(
            "[BIDDING_NOTIF] Disputa iniciando: Pregao %s em %d min | Prioridade: %s",
            pregao_numero,
            minutos,
            prioridade.value,
        )

        return notification

    def notify_convocacao(
        self,
        pregao_numero: str,
        pregao_id: str | None = None,
        mensagem_portal: str | None = None,
        channel: NotificationChannel = NotificationChannel.INTERNAL,
    ) -> BiddingNotification:
        """
        Notifica sobre convocacao no pregao.

        Args:
            pregao_numero: Numero do pregao.
            pregao_id: ID do pregao/tender.
            mensagem_portal: Mensagem do portal (se disponivel).
            channel: Canal de envio.

        Returns:
            BiddingNotification criada.
        """
        titulo = f"CONVOCACAO - Pregao {pregao_numero}"
        mensagem = f"Voce foi convocado no Pregao {pregao_numero}."
        if mensagem_portal:
            mensagem += f"\nMensagem do portal: {mensagem_portal[:500]}"

        notification = self._create_notification(
            tipo=BiddingNotificationType.CONVOCACAO,
            titulo=titulo,
            mensagem=mensagem,
            prioridade=NotificationPriority.CRITICA,
            canal=channel,
            referencia_tipo="pregao",
            referencia_id=pregao_id,
            dados_extras={
                "pregao_numero": pregao_numero,
                "mensagem_portal": mensagem_portal,
            },
            action_url=f"/licitacoes/pregao/{pregao_id}/disputa" if pregao_id else None,
        )

        logger.warning(
            "[BIDDING_NOTIF] CONVOCACAO: Pregao %s",
            pregao_numero,
        )

        return notification

    def notify_resultado(
        self,
        pregao_numero: str,
        resultado: str,
        pregao_id: str | None = None,
        valor_final: float | None = None,
        posicao: int | None = None,
        channel: NotificationChannel = NotificationChannel.INTERNAL,
    ) -> BiddingNotification:
        """
        Notifica sobre resultado do pregao.

        Args:
            pregao_numero: Numero do pregao.
            resultado: Resultado ("vencedor", "segundo_lugar", "desclassificado", "desistiu").
            pregao_id: ID do pregao/tender.
            valor_final: Valor final (se aplicavel).
            posicao: Posicao na classificacao.
            channel: Canal de envio.

        Returns:
            BiddingNotification criada.
        """
        resultado_upper = resultado.upper().replace("_", " ")
        prioridade = NotificationPriority.ALTA

        valor_fmt = f" | Valor final: R$ {valor_final:,.2f}" if valor_final else ""
        posicao_fmt = f" | Posicao: {posicao}o" if posicao else ""

        titulo = f"Resultado Pregao {pregao_numero}: {resultado_upper}"
        mensagem = f"Pregao {pregao_numero} encerrado.\nResultado: {resultado_upper}{valor_fmt}{posicao_fmt}"

        notification = self._create_notification(
            tipo=BiddingNotificationType.RESULTADO,
            titulo=titulo,
            mensagem=mensagem,
            prioridade=prioridade,
            canal=channel,
            referencia_tipo="pregao",
            referencia_id=pregao_id,
            dados_extras={
                "pregao_numero": pregao_numero,
                "resultado": resultado,
                "valor_final": valor_final,
                "posicao": posicao,
            },
            action_url=f"/licitacoes/pregao/{pregao_id}" if pregao_id else None,
        )

        logger.info(
            "[BIDDING_NOTIF] Resultado pregao: %s -> %s",
            pregao_numero,
            resultado,
        )

        return notification

    # ──────────────────────────────────────────
    # Metodos de notificacao complementares (existentes)
    # ──────────────────────────────────────────

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

        # Prioridade: alta se houve erros, media se novas oportunidades
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

    def get_push_notifications(
        self,
        apenas_nao_lidas: bool = True,
        limit: int = 50,
    ) -> list[BiddingNotification]:
        """
        Retorna notificacoes push pendentes do buffer.

        Args:
            apenas_nao_lidas: Se True, retorna apenas nao lidas.
            limit: Maximo de resultados.

        Returns:
            Lista de notificacoes push, mais recente primeiro.
        """
        result = self._push_buffer
        if apenas_nao_lidas:
            result = [n for n in result if not n.lido]
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
        # Also check push buffer
        for n in self._push_buffer:
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
        count = len(self._notifications) + len(self._push_buffer)
        self._notifications.clear()
        self._push_buffer.clear()
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

        Canais implementados:
        - INTERNAL: apenas loga.
        - EMAIL: envia via SMTP (fallback para log se nao configurado).
        - PUSH: armazena em _push_buffer para consulta via API.

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
            self._dispatch_email(notification)

        elif canal == NotificationChannel.PUSH:
            self._push_buffer.append(notification)
            logger.info(
                "[BIDDING_NOTIF][PUSH] Armazenado no buffer: %s",
                notification.titulo,
            )

        # Marcar como "enviado" (internamente registrado)
        notification.enviado = True
        notification.enviado_em = datetime.utcnow()

    def _dispatch_email(self, notification: BiddingNotification) -> None:
        """
        Envia notificacao por email via SMTP.

        Le configuracao de SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
        das variaveis de ambiente. Se nao configurado, faz fallback para log.

        Args:
            notification: Notificacao a ser enviada por email.
        """
        if not self._smtp_host or not self._smtp_user:
            logger.info(
                "[BIDDING_NOTIF][EMAIL] SMTP nao configurado (fallback log): %s",
                notification.titulo,
            )
            return

        try:
            msg = EmailMessage()
            msg["Subject"] = f"[Conecta PRO - Licitacoes] {notification.titulo}"
            msg["From"] = self._smtp_user
            msg["To"] = self._smtp_user  # Default: envia para o proprio usuario SMTP
            msg.set_content(
                f"{notification.titulo}\n"
                f"{'=' * 50}\n\n"
                f"Prioridade: {notification.prioridade.value.upper()}\n"
                f"Tipo: {notification.tipo.value}\n\n"
                f"{notification.mensagem}\n\n"
                f"---\n"
                f"Referencia: {notification.referencia_tipo or 'N/A'} "
                f"(ID: {notification.referencia_id or 'N/A'})\n"
                f"URL: {notification.action_url or 'N/A'}\n"
                f"Gerado em: {notification.criado_em.isoformat()}\n"
            )

            with smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=10) as server:
                server.ehlo()
                if self._smtp_port != 25:
                    server.starttls()
                    server.ehlo()
                if self._smtp_user and self._smtp_pass:
                    server.login(self._smtp_user, self._smtp_pass)
                server.send_message(msg)

            logger.info(
                "[BIDDING_NOTIF][EMAIL] Enviado com sucesso: %s",
                notification.titulo,
            )

        except Exception as e:
            logger.warning(
                "[BIDDING_NOTIF][EMAIL] Falha ao enviar email: %s | Erro: %s",
                notification.titulo,
                str(e),
            )

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


# ──────────────────────────────────────────────
# Singleton accessor (must be after class definition)
# ──────────────────────────────────────────────

_notification_service: BiddingNotificationService | None = None


def get_notification_service() -> BiddingNotificationService:
    """Retorna instancia singleton do BiddingNotificationService."""
    global _notification_service
    if _notification_service is None:
        _notification_service = BiddingNotificationService()
    return _notification_service

"""
Serviço de Notificações para Diaristas.

Fornece funcionalidades para:
- Envio de SMS/WhatsApp
- Confirmação de agendamento
- Lembretes 24h antes
- Alertas de falta/atraso
- Notificação de pagamento
"""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
import logging
import json

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TipoNotificacao(str, Enum):
    """Tipos de notificação."""
    CONFIRMACAO_AGENDAMENTO = "confirmacao_agendamento"
    LEMBRETE_24H = "lembrete_24h"
    LEMBRETE_1H = "lembrete_1h"
    ALERTA_ATRASO = "alerta_atraso"
    ALERTA_FALTA = "alerta_falta"
    PAGAMENTO_APROVADO = "pagamento_aprovado"
    PAGAMENTO_REALIZADO = "pagamento_realizado"
    AVALIACAO_RECEBIDA = "avaliacao_recebida"
    NOVO_AGENDAMENTO = "novo_agendamento"
    CANCELAMENTO = "cancelamento"
    REAGENDAMENTO = "reagendamento"
    BOAS_VINDAS = "boas_vindas"
    DOCUMENTOS_PENDENTES = "documentos_pendentes"
    CUSTOM = "custom"


class CanalNotificacao(str, Enum):
    """Canais de notificação."""
    SMS = "sms"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    PUSH = "push"
    INTERNO = "interno"


class StatusNotificacao(str, Enum):
    """Status da notificação."""
    PENDENTE = "pendente"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    LIDO = "lido"
    FALHA = "falha"
    CANCELADO = "cancelado"


class NotificacaoRequest(BaseModel):
    """Request para criar notificação."""
    diarist_id: UUID
    tipo: TipoNotificacao
    canal: CanalNotificacao = CanalNotificacao.WHATSAPP
    titulo: Optional[str] = None
    mensagem: Optional[str] = None
    dados_extras: Optional[Dict[str, Any]] = None
    agendar_para: Optional[datetime] = None


class NotificacaoResponse(BaseModel):
    """Response de notificação."""
    id: str
    tipo: str
    canal: str
    status: str
    mensagem: str
    enviado_em: Optional[datetime]
    entregue_em: Optional[datetime]


# =============================================================================
# TEMPLATES DE MENSAGENS
# =============================================================================

TEMPLATES_MENSAGENS = {
    TipoNotificacao.BOAS_VINDAS: {
        "titulo": "Bem-vindo(a) ao Conecta PRO!",
        "mensagem": """Olá {nome}! 👋

Seja bem-vindo(a) ao Conecta PRO!

Seu cadastro foi aprovado e você já pode receber agendamentos.

Dicas importantes:
✅ Mantenha seu perfil atualizado
✅ Confirme agendamentos rapidamente
✅ Faça check-in ao chegar no local
✅ Mantenha boa avaliação dos clientes

Dúvidas? Entre em contato pelo suporte.

Boa sorte! 🍀""",
    },

    TipoNotificacao.CONFIRMACAO_AGENDAMENTO: {
        "titulo": "Confirme seu agendamento",
        "mensagem": """Olá {nome}! 📋

Você tem um novo agendamento:

📍 Local: {local}
📅 Data: {data}
⏰ Horário: {horario_inicio} às {horario_fim}
💰 Valor: R$ {valor}

Por favor, confirme sua presença respondendo:
✅ SIM - para confirmar
❌ NAO - para recusar

Obs: {observacoes}""",
    },

    TipoNotificacao.LEMBRETE_24H: {
        "titulo": "Lembrete: Serviço amanhã",
        "mensagem": """Olá {nome}! ⏰

Lembrando que você tem serviço AMANHÃ:

📍 Local: {local}
📅 Data: {data}
⏰ Horário: {horario_inicio}
🏢 Cliente: {cliente}

Endereço: {endereco}

Não esqueça de:
✓ Levar documento com foto
✓ Chegar 10 min antes
✓ Fazer check-in no app

Até amanhã! 👍""",
    },

    TipoNotificacao.LEMBRETE_1H: {
        "titulo": "Lembrete: Serviço em 1 hora",
        "mensagem": """🚨 {nome}, seu serviço começa em 1 HORA!

📍 {local}
⏰ {horario_inicio}

Não esqueça do check-in ao chegar!""",
    },

    TipoNotificacao.ALERTA_ATRASO: {
        "titulo": "⚠️ Alerta de Atraso",
        "mensagem": """⚠️ {nome}, você está ATRASADO(A)!

Seu serviço começou às {horario_inicio} em {local}.

Por favor:
1. Entre em contato com o cliente
2. Faça o check-in assim que chegar
3. Informe a previsão de chegada

Se não puder comparecer, avise URGENTE!

Contato do cliente: {telefone_cliente}""",
    },

    TipoNotificacao.ALERTA_FALTA: {
        "titulo": "❌ Falta Registrada",
        "mensagem": """❌ {nome}, foi registrada FALTA no serviço:

📍 {local}
📅 {data}
⏰ {horario_inicio}

Motivo registrado: {motivo}

Essa ocorrência pode afetar sua avaliação e disponibilidade para novos serviços.

Se houve algum engano, entre em contato com o suporte.""",
    },

    TipoNotificacao.PAGAMENTO_APROVADO: {
        "titulo": "💰 Pagamento Aprovado",
        "mensagem": """✅ {nome}, seu pagamento foi APROVADO!

📅 Período: {periodo}
💰 Valor: R$ {valor}
🏦 Forma: {forma_pagamento}

O pagamento será processado em até 3 dias úteis.

Detalhes:
- Serviços realizados: {qtd_servicos}
- Horas trabalhadas: {horas}
- Descontos: R$ {descontos}

Obrigado pelo seu trabalho! 🙏""",
    },

    TipoNotificacao.PAGAMENTO_REALIZADO: {
        "titulo": "💵 Pagamento Realizado",
        "mensagem": """💵 {nome}, PAGAMENTO REALIZADO!

💰 Valor: R$ {valor}
📅 Data: {data_pagamento}
🏦 {detalhes_bancarios}

Comprovante disponível no app.

Obrigado! 🎉""",
    },

    TipoNotificacao.AVALIACAO_RECEBIDA: {
        "titulo": "⭐ Nova Avaliação",
        "mensagem": """⭐ {nome}, você recebeu uma nova avaliação!

Nota: {'⭐' * int(nota)} ({nota}/5)

Cliente: {cliente}
Serviço: {data} - {local}

Comentário: "{comentario}"

Sua média atual: {media_atual}/5

Continue assim! 💪""",
    },

    TipoNotificacao.NOVO_AGENDAMENTO: {
        "titulo": "🆕 Novo Serviço Disponível",
        "mensagem": """🆕 {nome}, há um novo serviço para você!

📍 Local: {local}
📅 Data: {data}
⏰ {horario_inicio} às {horario_fim}
💰 Valor: R$ {valor}

Interessado(a)? Acesse o app para aceitar!

Vagas limitadas, garanta a sua! ⚡""",
    },

    TipoNotificacao.CANCELAMENTO: {
        "titulo": "❌ Serviço Cancelado",
        "mensagem": """❌ {nome}, seu serviço foi CANCELADO.

📍 {local}
📅 {data}
⏰ {horario_inicio}

Motivo: {motivo}

{compensacao}

Sentimos muito pelo inconveniente. Novos serviços em breve!""",
    },

    TipoNotificacao.REAGENDAMENTO: {
        "titulo": "🔄 Serviço Reagendado",
        "mensagem": """🔄 {nome}, seu serviço foi REAGENDADO.

❌ Data anterior: {data_anterior} às {horario_anterior}

✅ Nova data: {nova_data} às {novo_horario}
📍 Local: {local}

Por favor, confirme o reagendamento:
✅ SIM - Confirmo
❌ NAO - Não posso

Aguardamos sua confirmação!""",
    },

    TipoNotificacao.DOCUMENTOS_PENDENTES: {
        "titulo": "📄 Documentos Pendentes",
        "mensagem": """📄 {nome}, você tem DOCUMENTOS PENDENTES!

Para continuar recebendo serviços, envie:
{lista_documentos}

Acesse o app e envie os documentos pela área "Meu Perfil".

Prazo: {prazo}

Dúvidas? Fale com o suporte.""",
    },
}


class NotificacaoService:
    """Serviço de notificações para diaristas."""

    def __init__(self, db: Session):
        self.db = db
        self._notificacoes_enviadas: List[Dict] = []  # Cache em memória

    # =========================================================================
    # CRIAÇÃO E ENVIO DE NOTIFICAÇÕES
    # =========================================================================

    def criar_notificacao(
        self,
        diarist_id: UUID,
        tipo: TipoNotificacao,
        canal: CanalNotificacao = CanalNotificacao.WHATSAPP,
        dados: Optional[Dict[str, Any]] = None,
        mensagem_custom: Optional[str] = None,
        titulo_custom: Optional[str] = None,
        agendar_para: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Cria e envia uma notificação.

        Args:
            diarist_id: ID do diarista
            tipo: Tipo de notificação
            canal: Canal de envio
            dados: Dados para preencher o template
            mensagem_custom: Mensagem customizada (ignora template)
            titulo_custom: Título customizado
            agendar_para: Data/hora para envio agendado

        Returns:
            Dict com resultado do envio
        """
        # Buscar diarista
        from modules.operacional.diaristas.models import Diarist

        diarista = self.db.query(Diarist).filter(
            Diarist.id == diarist_id
        ).first()

        if not diarista:
            raise ValueError(f"Diarista {diarist_id} não encontrado")

        # Preparar dados base
        dados = dados or {}
        dados["nome"] = diarista.full_name or diarista.first_name
        dados["telefone"] = diarista.phone

        # Obter template ou usar mensagem custom
        if mensagem_custom:
            titulo = titulo_custom or "Notificação"
            mensagem = mensagem_custom
        else:
            template = TEMPLATES_MENSAGENS.get(tipo, {})
            titulo = template.get("titulo", "Notificação")
            mensagem = template.get("mensagem", "")

        # Substituir variáveis no template
        try:
            mensagem = mensagem.format(**dados)
            titulo = titulo.format(**dados) if "{" in titulo else titulo
        except KeyError as e:
            logger.warning(f"Variável não encontrada no template: {e}")

        # Se agendado, armazenar para envio posterior
        if agendar_para and agendar_para > datetime.now():
            return self._agendar_notificacao(
                diarista, tipo, canal, titulo, mensagem, agendar_para, dados
            )

        # Enviar notificação
        resultado = self._enviar_notificacao(
            diarista, tipo, canal, titulo, mensagem, dados
        )

        return resultado

    def _enviar_notificacao(
        self,
        diarista: Any,
        tipo: TipoNotificacao,
        canal: CanalNotificacao,
        titulo: str,
        mensagem: str,
        dados: Dict,
    ) -> Dict[str, Any]:
        """Envia notificação através do canal especificado."""
        resultado = {
            "id": str(UUID(int=len(self._notificacoes_enviadas) + 1)),
            "diarist_id": str(diarista.id),
            "tipo": tipo.value,
            "canal": canal.value,
            "titulo": titulo,
            "mensagem": mensagem,
            "status": StatusNotificacao.PENDENTE.value,
            "criado_em": datetime.now().isoformat(),
            "enviado_em": None,
            "entregue_em": None,
            "erro": None,
        }

        try:
            if canal == CanalNotificacao.WHATSAPP:
                self._enviar_whatsapp(diarista.phone, mensagem)
            elif canal == CanalNotificacao.SMS:
                self._enviar_sms(diarista.phone, mensagem)
            elif canal == CanalNotificacao.EMAIL:
                self._enviar_email(diarista.email, titulo, mensagem)
            elif canal == CanalNotificacao.PUSH:
                self._enviar_push(diarista.id, titulo, mensagem)
            elif canal == CanalNotificacao.INTERNO:
                pass  # Apenas registro interno

            resultado["status"] = StatusNotificacao.ENVIADO.value
            resultado["enviado_em"] = datetime.now().isoformat()

            logger.info(
                f"Notificação {tipo.value} enviada para diarista {diarista.id} via {canal.value}"
            )

        except Exception as e:
            resultado["status"] = StatusNotificacao.FALHA.value
            resultado["erro"] = str(e)
            logger.error(f"Erro ao enviar notificação: {e}")

        # Armazenar no cache
        self._notificacoes_enviadas.append(resultado)

        return resultado

    def _agendar_notificacao(
        self,
        diarista: Any,
        tipo: TipoNotificacao,
        canal: CanalNotificacao,
        titulo: str,
        mensagem: str,
        agendar_para: datetime,
        dados: Dict,
    ) -> Dict[str, Any]:
        """Agenda notificação para envio posterior."""
        resultado = {
            "id": str(UUID(int=len(self._notificacoes_enviadas) + 1000)),
            "diarist_id": str(diarista.id),
            "tipo": tipo.value,
            "canal": canal.value,
            "titulo": titulo,
            "mensagem": mensagem,
            "status": "agendado",
            "criado_em": datetime.now().isoformat(),
            "agendado_para": agendar_para.isoformat(),
            "enviado_em": None,
        }

        # Aqui integraria com sistema de filas (Celery, Redis, etc.)
        # Por ora, apenas registra
        self._notificacoes_enviadas.append(resultado)

        logger.info(
            f"Notificação {tipo.value} agendada para {agendar_para} - diarista {diarista.id}"
        )

        return resultado

    # =========================================================================
    # MÉTODOS DE ENVIO POR CANAL
    # =========================================================================

    def _enviar_whatsapp(self, telefone: str, mensagem: str) -> bool:
        """
        Envia mensagem via WhatsApp.

        Integração com APIs:
        - Twilio
        - WhatsApp Business API
        - Evolution API
        - Z-API
        """
        # TODO: Implementar integração real com WhatsApp API
        # Exemplo de integração com Evolution API:
        #
        # import httpx
        # url = f"{settings.EVOLUTION_API_URL}/message/sendText/{settings.EVOLUTION_INSTANCE}"
        # payload = {
        #     "number": telefone,
        #     "text": mensagem
        # }
        # headers = {"apikey": settings.EVOLUTION_API_KEY}
        # response = httpx.post(url, json=payload, headers=headers)
        # return response.status_code == 200

        logger.info(f"[WHATSAPP] Enviando para {telefone}: {mensagem[:50]}...")
        return True

    def _enviar_sms(self, telefone: str, mensagem: str) -> bool:
        """
        Envia SMS.

        Integração com APIs:
        - Twilio
        - Zenvia
        - AWS SNS
        """
        # TODO: Implementar integração real com SMS API
        # Exemplo com Twilio:
        #
        # from twilio.rest import Client
        # client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
        # message = client.messages.create(
        #     body=mensagem,
        #     from_=settings.TWILIO_PHONE,
        #     to=telefone
        # )
        # return message.sid is not None

        logger.info(f"[SMS] Enviando para {telefone}: {mensagem[:50]}...")
        return True

    def _enviar_email(self, email: str, titulo: str, mensagem: str) -> bool:
        """
        Envia email.

        Integração com:
        - SendGrid
        - AWS SES
        - SMTP
        """
        # TODO: Implementar integração real com Email API
        logger.info(f"[EMAIL] Enviando para {email}: {titulo}")
        return True

    def _enviar_push(self, diarist_id: UUID, titulo: str, mensagem: str) -> bool:
        """
        Envia push notification.

        Integração com:
        - Firebase Cloud Messaging
        - OneSignal
        """
        # TODO: Implementar integração real com Push API
        logger.info(f"[PUSH] Enviando para diarista {diarist_id}: {titulo}")
        return True

    # =========================================================================
    # NOTIFICAÇÕES AUTOMÁTICAS
    # =========================================================================

    def enviar_confirmacao_agendamento(
        self,
        diarist_id: UUID,
        schedule_id: UUID,
    ) -> Dict[str, Any]:
        """Envia confirmação de novo agendamento."""
        from modules.operacional.diaristas.models import DiaristSchedule

        schedule = self.db.query(DiaristSchedule).filter(
            DiaristSchedule.id == schedule_id
        ).first()

        if not schedule:
            raise ValueError(f"Schedule {schedule_id} não encontrado")

        dados = {
            "local": schedule.location or "A confirmar",
            "data": schedule.date.strftime("%d/%m/%Y"),
            "horario_inicio": schedule.scheduled_start.strftime("%H:%M") if schedule.scheduled_start else "A confirmar",
            "horario_fim": schedule.scheduled_end.strftime("%H:%M") if schedule.scheduled_end else "A confirmar",
            "valor": f"{schedule.agreed_rate or 0:.2f}",
            "observacoes": schedule.notes or "Nenhuma observação",
        }

        return self.criar_notificacao(
            diarist_id=diarist_id,
            tipo=TipoNotificacao.CONFIRMACAO_AGENDAMENTO,
            dados=dados,
        )

    def enviar_lembrete_24h(self, diarist_id: UUID, schedule_id: UUID) -> Dict[str, Any]:
        """Envia lembrete 24h antes do serviço."""
        from modules.operacional.diaristas.models import DiaristSchedule, DiaristAssignment

        schedule = self.db.query(DiaristSchedule).filter(
            DiaristSchedule.id == schedule_id
        ).first()

        if not schedule:
            raise ValueError(f"Schedule {schedule_id} não encontrado")

        # Buscar assignment para obter dados do cliente
        assignment = self.db.query(DiaristAssignment).filter(
            DiaristAssignment.id == schedule.assignment_id
        ).first() if schedule.assignment_id else None

        dados = {
            "local": schedule.location or "A confirmar",
            "data": schedule.date.strftime("%d/%m/%Y"),
            "horario_inicio": schedule.scheduled_start.strftime("%H:%M") if schedule.scheduled_start else "A confirmar",
            "cliente": assignment.client_name if assignment else "Cliente",
            "endereco": assignment.location if assignment else schedule.location or "A confirmar",
        }

        return self.criar_notificacao(
            diarist_id=diarist_id,
            tipo=TipoNotificacao.LEMBRETE_24H,
            dados=dados,
        )

    def enviar_alerta_atraso(
        self,
        diarist_id: UUID,
        schedule_id: UUID,
        telefone_cliente: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Envia alerta quando diarista está atrasado."""
        from modules.operacional.diaristas.models import DiaristSchedule

        schedule = self.db.query(DiaristSchedule).filter(
            DiaristSchedule.id == schedule_id
        ).first()

        if not schedule:
            raise ValueError(f"Schedule {schedule_id} não encontrado")

        dados = {
            "local": schedule.location or "Local do serviço",
            "horario_inicio": schedule.scheduled_start.strftime("%H:%M") if schedule.scheduled_start else "Horário",
            "telefone_cliente": telefone_cliente or "Não informado",
        }

        return self.criar_notificacao(
            diarist_id=diarist_id,
            tipo=TipoNotificacao.ALERTA_ATRASO,
            dados=dados,
        )

    def enviar_notificacao_pagamento(
        self,
        diarist_id: UUID,
        payment_id: UUID,
        tipo: TipoNotificacao = TipoNotificacao.PAGAMENTO_APROVADO,
    ) -> Dict[str, Any]:
        """Envia notificação de pagamento."""
        from modules.operacional.diaristas.models import DiaristPayment

        payment = self.db.query(DiaristPayment).filter(
            DiaristPayment.id == payment_id
        ).first()

        if not payment:
            raise ValueError(f"Payment {payment_id} não encontrado")

        if tipo == TipoNotificacao.PAGAMENTO_APROVADO:
            dados = {
                "periodo": f"{payment.period_start.strftime('%d/%m')} a {payment.period_end.strftime('%d/%m/%Y')}",
                "valor": f"{payment.gross_amount:.2f}",
                "forma_pagamento": payment.payment_method or "Transferência",
                "qtd_servicos": payment.schedules_count or 0,
                "horas": f"{payment.total_hours:.1f}h" if payment.total_hours else "0h",
                "descontos": f"{payment.deductions:.2f}" if payment.deductions else "0.00",
            }
        else:  # PAGAMENTO_REALIZADO
            dados = {
                "valor": f"{payment.net_amount:.2f}",
                "data_pagamento": payment.paid_at.strftime("%d/%m/%Y") if payment.paid_at else date.today().strftime("%d/%m/%Y"),
                "detalhes_bancarios": f"PIX: {payment.pix_key}" if hasattr(payment, 'pix_key') and payment.pix_key else "Via banco cadastrado",
            }

        return self.criar_notificacao(
            diarist_id=diarist_id,
            tipo=tipo,
            dados=dados,
        )

    # =========================================================================
    # PROCESSAMENTO EM LOTE
    # =========================================================================

    def processar_lembretes_24h(self) -> List[Dict[str, Any]]:
        """
        Processa lembretes 24h para todos os agendamentos de amanhã.

        Deve ser chamado por um job/cron diário.
        """
        from modules.operacional.diaristas.models import DiaristSchedule

        amanha = date.today() + timedelta(days=1)

        schedules = self.db.query(DiaristSchedule).filter(
            DiaristSchedule.date == amanha,
            DiaristSchedule.status.in_(["scheduled", "confirmed"]),
        ).all()

        resultados = []
        for schedule in schedules:
            try:
                resultado = self.enviar_lembrete_24h(
                    diarist_id=schedule.diarist_id,
                    schedule_id=schedule.id,
                )
                resultados.append(resultado)
            except Exception as e:
                logger.error(f"Erro ao enviar lembrete para schedule {schedule.id}: {e}")
                resultados.append({
                    "schedule_id": str(schedule.id),
                    "status": "falha",
                    "erro": str(e),
                })

        logger.info(f"Processados {len(resultados)} lembretes 24h para {amanha}")
        return resultados

    def verificar_atrasos(self, tolerancia_minutos: int = 15) -> List[Dict[str, Any]]:
        """
        Verifica diaristas atrasados e envia alertas.

        Deve ser chamado periodicamente (ex: a cada 5 minutos).
        """
        from modules.operacional.diaristas.models import DiaristSchedule

        agora = datetime.now()
        hoje = agora.date()
        hora_atual = agora.time()

        # Buscar schedules de hoje sem check-in e com horário já passado
        schedules = self.db.query(DiaristSchedule).filter(
            DiaristSchedule.date == hoje,
            DiaristSchedule.status == "confirmed",
            DiaristSchedule.actual_check_in.is_(None),
            DiaristSchedule.scheduled_start <= hora_atual,
        ).all()

        resultados = []
        for schedule in schedules:
            # Calcular atraso
            horario_inicio = datetime.combine(hoje, schedule.scheduled_start)
            atraso_minutos = (agora - horario_inicio).total_seconds() / 60

            if atraso_minutos >= tolerancia_minutos:
                try:
                    resultado = self.enviar_alerta_atraso(
                        diarist_id=schedule.diarist_id,
                        schedule_id=schedule.id,
                    )
                    resultado["atraso_minutos"] = round(atraso_minutos)
                    resultados.append(resultado)
                except Exception as e:
                    logger.error(f"Erro ao enviar alerta de atraso: {e}")

        if resultados:
            logger.warning(f"Detectados {len(resultados)} atrasos")

        return resultados

    # =========================================================================
    # CONSULTAS
    # =========================================================================

    def listar_notificacoes(
        self,
        diarist_id: Optional[UUID] = None,
        tipo: Optional[TipoNotificacao] = None,
        status: Optional[StatusNotificacao] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Lista notificações com filtros."""
        resultado = self._notificacoes_enviadas.copy()

        if diarist_id:
            resultado = [n for n in resultado if n.get("diarist_id") == str(diarist_id)]

        if tipo:
            resultado = [n for n in resultado if n.get("tipo") == tipo.value]

        if status:
            resultado = [n for n in resultado if n.get("status") == status.value]

        # Ordenar por data mais recente
        resultado.sort(key=lambda x: x.get("criado_em", ""), reverse=True)

        return resultado[:limit]

    def get_estatisticas(
        self,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Retorna estatísticas de notificações."""
        notificacoes = self._notificacoes_enviadas

        total = len(notificacoes)
        enviados = len([n for n in notificacoes if n.get("status") == "enviado"])
        falhas = len([n for n in notificacoes if n.get("status") == "falha"])
        agendados = len([n for n in notificacoes if n.get("status") == "agendado"])

        por_tipo = {}
        for n in notificacoes:
            tipo = n.get("tipo", "outro")
            por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

        por_canal = {}
        for n in notificacoes:
            canal = n.get("canal", "outro")
            por_canal[canal] = por_canal.get(canal, 0) + 1

        return {
            "total": total,
            "enviados": enviados,
            "falhas": falhas,
            "agendados": agendados,
            "taxa_sucesso": round(enviados / total * 100, 2) if total > 0 else 0,
            "por_tipo": por_tipo,
            "por_canal": por_canal,
        }


# Singleton
def get_notificacao_service(db: Session) -> NotificacaoService:
    """Factory function para obter instância do serviço."""
    return NotificacaoService(db)

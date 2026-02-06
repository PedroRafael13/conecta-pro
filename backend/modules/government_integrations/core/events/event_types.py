"""
Tipos de Eventos do Sistema de Integrações.

Define eventos específicos para comunicação entre módulos.
"""

from datetime import datetime
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4

from .event_bus import Event


class TipoEvento(str, Enum):
    """Tipos de evento do sistema."""
    # Documentos Fiscais
    NFE_EMITIDA = "nfe.emitida"
    NFE_AUTORIZADA = "nfe.autorizada"
    NFE_REJEITADA = "nfe.rejeitada"
    NFE_CANCELADA = "nfe.cancelada"
    NFE_INUTILIZADA = "nfe.inutilizada"

    CTE_EMITIDO = "cte.emitido"
    CTE_AUTORIZADO = "cte.autorizado"
    CTE_REJEITADO = "cte.rejeitado"
    CTE_CANCELADO = "cte.cancelado"

    MDFE_EMITIDO = "mdfe.emitido"
    MDFE_AUTORIZADO = "mdfe.autorizado"
    MDFE_ENCERRADO = "mdfe.encerrado"

    NFSE_EMITIDA = "nfse.emitida"
    NFSE_CANCELADA = "nfse.cancelada"

    # eSocial
    ESOCIAL_EVENTO_ENVIADO = "esocial.evento_enviado"
    ESOCIAL_EVENTO_PROCESSADO = "esocial.evento_processado"
    ESOCIAL_EVENTO_REJEITADO = "esocial.evento_rejeitado"
    ESOCIAL_FECHAMENTO_PERIODO = "esocial.fechamento_periodo"

    # FGTS Digital
    FGTS_GUIA_GERADA = "fgts.guia_gerada"
    FGTS_PAGAMENTO_CONFIRMADO = "fgts.pagamento_confirmado"

    # Folha de Pagamento
    FOLHA_CALCULADA = "folha.calculada"
    FOLHA_FECHADA = "folha.fechada"
    FOLHA_REABERTURA = "folha.reabertura"

    # Sincronização
    SYNC_INICIADA = "sync.iniciada"
    SYNC_CONCLUIDA = "sync.concluida"
    SYNC_FALHA = "sync.falha"

    # Sistema
    CERTIFICADO_EXPIRANDO = "sistema.certificado_expirando"
    ENDPOINT_INDISPONIVEL = "sistema.endpoint_indisponivel"
    ENDPOINT_RESTAURADO = "sistema.endpoint_restaurado"
    CONTINGENCIA_ATIVADA = "sistema.contingencia_ativada"
    CONTINGENCIA_DESATIVADA = "sistema.contingencia_desativada"

    # Erros
    ERRO_INTEGRACAO = "erro.integracao"
    ERRO_VALIDACAO = "erro.validacao"
    ERRO_PROCESSAMENTO = "erro.processamento"


@dataclass
class EventoDocumentoFiscal(Event):
    """Evento relacionado a documento fiscal."""

    def __init__(
        self,
        tipo_evento: TipoEvento,
        tenant_id: UUID,
        tipo_documento: str,  # nfe, cte, mdfe, nfse
        documento_id: UUID,
        chave_acesso: Optional[str] = None,
        numero: Optional[int] = None,
        serie: Optional[str] = None,
        valor_total: Optional[float] = None,
        destinatario_cnpj_cpf: Optional[str] = None,
        protocolo: Optional[str] = None,
        status_sefaz: Optional[str] = None,
        motivo: Optional[str] = None,
        xml_proc: Optional[str] = None,
        **kwargs
    ):
        dados = {
            "tipo_documento": tipo_documento,
            "documento_id": str(documento_id),
            "chave_acesso": chave_acesso,
            "numero": numero,
            "serie": serie,
            "valor_total": valor_total,
            "destinatario": destinatario_cnpj_cpf,
            "protocolo": protocolo,
            "status_sefaz": status_sefaz,
            "motivo": motivo,
        }

        # Não incluir XML no evento (muito grande)
        metadata = {
            "tem_xml": xml_proc is not None,
        }

        super().__init__(
            tipo=tipo_evento.value,
            tenant_id=tenant_id,
            origem="government_integrations",
            dados=dados,
            metadata=metadata,
            **kwargs
        )


@dataclass
class EventoFolhaPagamento(Event):
    """Evento relacionado a folha de pagamento."""

    def __init__(
        self,
        tipo_evento: TipoEvento,
        tenant_id: UUID,
        competencia: str,  # AAAAMM
        total_funcionarios: int = 0,
        total_bruto: float = 0,
        total_descontos: float = 0,
        total_liquido: float = 0,
        total_encargos: float = 0,
        **kwargs
    ):
        dados = {
            "competencia": competencia,
            "total_funcionarios": total_funcionarios,
            "total_bruto": total_bruto,
            "total_descontos": total_descontos,
            "total_liquido": total_liquido,
            "total_encargos": total_encargos,
        }

        super().__init__(
            tipo=tipo_evento.value,
            tenant_id=tenant_id,
            origem="folha_pagamento",
            dados=dados,
            **kwargs
        )


@dataclass
class EventoeSocial(Event):
    """Evento relacionado ao eSocial."""

    def __init__(
        self,
        tipo_evento: TipoEvento,
        tenant_id: UUID,
        evento_esocial: str,  # S-1000, S-2200, etc
        id_evento: str,
        numero_recibo: Optional[str] = None,
        funcionario_id: Optional[UUID] = None,
        cpf_funcionario: Optional[str] = None,
        competencia: Optional[str] = None,
        status: str = "enviado",
        erros: Optional[List[str]] = None,
        **kwargs
    ):
        dados = {
            "evento_esocial": evento_esocial,
            "id_evento": id_evento,
            "numero_recibo": numero_recibo,
            "funcionario_id": str(funcionario_id) if funcionario_id else None,
            "cpf_funcionario": cpf_funcionario,
            "competencia": competencia,
            "status": status,
            "erros": erros or [],
        }

        super().__init__(
            tipo=tipo_evento.value,
            tenant_id=tenant_id,
            origem="esocial",
            dados=dados,
            **kwargs
        )


@dataclass
class EventoFGTS(Event):
    """Evento relacionado ao FGTS Digital."""

    def __init__(
        self,
        tipo_evento: TipoEvento,
        tenant_id: UUID,
        competencia: str,
        tipo_guia: str = "mensal",  # mensal, rescisorio
        valor_total: float = 0,
        codigo_barras: Optional[str] = None,
        data_vencimento: Optional[datetime] = None,
        data_pagamento: Optional[datetime] = None,
        **kwargs
    ):
        dados = {
            "competencia": competencia,
            "tipo_guia": tipo_guia,
            "valor_total": valor_total,
            "codigo_barras": codigo_barras,
            "data_vencimento": data_vencimento.isoformat() if data_vencimento else None,
            "data_pagamento": data_pagamento.isoformat() if data_pagamento else None,
        }

        super().__init__(
            tipo=tipo_evento.value,
            tenant_id=tenant_id,
            origem="fgts_digital",
            dados=dados,
            **kwargs
        )


@dataclass
class EventoSincronizacao(Event):
    """Evento de sincronização de dados."""

    def __init__(
        self,
        tipo_evento: TipoEvento,
        tenant_id: UUID,
        servico: str,  # sefaz_nfe, esocial, etc
        tipo_sync: str = "incremental",  # full, incremental
        registros_processados: int = 0,
        registros_novos: int = 0,
        registros_atualizados: int = 0,
        registros_erro: int = 0,
        duracao_segundos: float = 0,
        periodo_inicio: Optional[datetime] = None,
        periodo_fim: Optional[datetime] = None,
        erro: Optional[str] = None,
        **kwargs
    ):
        dados = {
            "servico": servico,
            "tipo_sync": tipo_sync,
            "registros_processados": registros_processados,
            "registros_novos": registros_novos,
            "registros_atualizados": registros_atualizados,
            "registros_erro": registros_erro,
            "duracao_segundos": duracao_segundos,
            "periodo_inicio": periodo_inicio.isoformat() if periodo_inicio else None,
            "periodo_fim": periodo_fim.isoformat() if periodo_fim else None,
            "erro": erro,
        }

        super().__init__(
            tipo=tipo_evento.value,
            tenant_id=tenant_id,
            origem="sync_service",
            dados=dados,
            **kwargs
        )


@dataclass
class EventoSistema(Event):
    """Evento de sistema/infraestrutura."""

    def __init__(
        self,
        tipo_evento: TipoEvento,
        tenant_id: Optional[UUID] = None,
        servico: str = "",
        uf: Optional[str] = None,
        descricao: str = "",
        detalhes: Optional[Dict] = None,
        severidade: str = "info",  # info, warning, error, critical
        **kwargs
    ):
        dados = {
            "servico": servico,
            "uf": uf,
            "descricao": descricao,
            "detalhes": detalhes or {},
            "severidade": severidade,
        }

        super().__init__(
            tipo=tipo_evento.value,
            tenant_id=tenant_id,
            origem="sistema",
            dados=dados,
            **kwargs
        )


@dataclass
class EventoErro(Event):
    """Evento de erro no sistema."""

    def __init__(
        self,
        tipo_evento: TipoEvento,
        tenant_id: UUID,
        servico: str,
        operacao: str,
        erro_tipo: str,  # timeout, validacao, autenticacao, etc
        erro_mensagem: str,
        erro_codigo: Optional[str] = None,
        stack_trace: Optional[str] = None,
        documento_id: Optional[UUID] = None,
        recuperavel: bool = True,
        tentativas: int = 0,
        **kwargs
    ):
        dados = {
            "servico": servico,
            "operacao": operacao,
            "erro_tipo": erro_tipo,
            "erro_mensagem": erro_mensagem,
            "erro_codigo": erro_codigo,
            "documento_id": str(documento_id) if documento_id else None,
            "recuperavel": recuperavel,
            "tentativas": tentativas,
        }

        metadata = {
            "stack_trace": stack_trace[:1000] if stack_trace else None,
        }

        super().__init__(
            tipo=tipo_evento.value,
            tenant_id=tenant_id,
            origem="error_handler",
            dados=dados,
            metadata=metadata,
            **kwargs
        )


# Funções auxiliares para criar eventos comuns

def criar_evento_nfe_autorizada(
    tenant_id: UUID,
    documento_id: UUID,
    chave_acesso: str,
    numero: int,
    serie: str,
    valor_total: float,
    protocolo: str,
    **kwargs
) -> EventoDocumentoFiscal:
    """Cria evento de NF-e autorizada."""
    return EventoDocumentoFiscal(
        tipo_evento=TipoEvento.NFE_AUTORIZADA,
        tenant_id=tenant_id,
        tipo_documento="nfe",
        documento_id=documento_id,
        chave_acesso=chave_acesso,
        numero=numero,
        serie=serie,
        valor_total=valor_total,
        protocolo=protocolo,
        status_sefaz="100",
        **kwargs
    )


def criar_evento_folha_fechada(
    tenant_id: UUID,
    competencia: str,
    total_funcionarios: int,
    total_liquido: float,
    **kwargs
) -> EventoFolhaPagamento:
    """Cria evento de folha de pagamento fechada."""
    return EventoFolhaPagamento(
        tipo_evento=TipoEvento.FOLHA_FECHADA,
        tenant_id=tenant_id,
        competencia=competencia,
        total_funcionarios=total_funcionarios,
        total_liquido=total_liquido,
        **kwargs
    )


def criar_evento_sync_concluida(
    tenant_id: UUID,
    servico: str,
    registros_processados: int,
    duracao_segundos: float,
    **kwargs
) -> EventoSincronizacao:
    """Cria evento de sincronização concluída."""
    return EventoSincronizacao(
        tipo_evento=TipoEvento.SYNC_CONCLUIDA,
        tenant_id=tenant_id,
        servico=servico,
        registros_processados=registros_processados,
        duracao_segundos=duracao_segundos,
        **kwargs
    )


def criar_evento_erro_integracao(
    tenant_id: UUID,
    servico: str,
    operacao: str,
    erro_tipo: str,
    erro_mensagem: str,
    **kwargs
) -> EventoErro:
    """Cria evento de erro de integração."""
    return EventoErro(
        tipo_evento=TipoEvento.ERRO_INTEGRACAO,
        tenant_id=tenant_id,
        servico=servico,
        operacao=operacao,
        erro_tipo=erro_tipo,
        erro_mensagem=erro_mensagem,
        **kwargs
    )

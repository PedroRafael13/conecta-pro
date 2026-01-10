"""
modules/fase5/email_intelligence/enums.py - Email Intelligence Enums
====================================================================
Enumeracoes para analise de emails
"""

from enum import Enum


class EmailCategory(str, Enum):
    """Categorias de email."""
    PROPOSTA_COMERCIAL = "proposta_comercial"
    SOLICITACAO_ORCAMENTO = "solicitacao_orcamento"
    RECLAMACAO = "reclamacao"
    DUVIDA = "duvida"
    SUPORTE = "suporte"
    ADMINISTRATIVO = "administrativo"
    RH = "recursos_humanos"
    FINANCEIRO = "financeiro"
    LICITACAO = "licitacao"
    MARKETING = "marketing"
    SPAM = "spam"
    OUTROS = "outros"


class EmailPriority(str, Enum):
    """Prioridade do email."""
    URGENTE = "urgente"
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


class EmailIntent(str, Enum):
    """Intencao identificada no email."""
    SOLICITAR_PROPOSTA = "solicitar_proposta"
    SOLICITAR_INFORMACAO = "solicitar_informacao"
    FAZER_RECLAMACAO = "fazer_reclamacao"
    CANCELAR_SERVICO = "cancelar_servico"
    RENOVAR_CONTRATO = "renovar_contrato"
    RENEGOCIAR_VALORES = "renegociar_valores"
    AGENDAR_REUNIAO = "agendar_reuniao"
    ENVIAR_DOCUMENTOS = "enviar_documentos"
    CONFIRMAR_RECEBIMENTO = "confirmar_recebimento"
    SOLICITAR_SUPORTE = "solicitar_suporte"
    FEEDBACK = "feedback"
    OUTRO = "outro"


class SentimentType(str, Enum):
    """Tipo de sentimento identificado."""
    POSITIVO = "positivo"
    NEUTRO = "neutro"
    NEGATIVO = "negativo"
    URGENTE = "urgente"
    FRUSTRADO = "frustrado"


class EmailStatus(str, Enum):
    """Status do email."""
    NAO_LIDO = "nao_lido"
    LIDO = "lido"
    RESPONDIDO = "respondido"
    ARQUIVADO = "arquivado"
    EXCLUIDO = "excluido"
    SPAM = "spam"


class ActionType(str, Enum):
    """Tipo de acao sugerida."""
    RESPONDER = "responder"
    ENCAMINHAR = "encaminhar"
    AGENDAR = "agendar"
    CRIAR_TAREFA = "criar_tarefa"
    CRIAR_PROPOSTA = "criar_proposta"
    NOTIFICAR_EQUIPE = "notificar_equipe"
    ARQUIVAR = "arquivar"
    IGNORAR = "ignorar"

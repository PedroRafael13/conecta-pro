"""GEDEON Fase 3 — Onvio Sync Models (fonte canônica — migrado de modules.ged T7 STEP 1.4)"""

import enum as pyenum
import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from core.database import Base


class OnvioSyncStatus(str, pyenum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"


class OnvioDocCategory(str, pyenum.Enum):
    FOLHA_PAGAMENTO = "folha_pagamento"
    CONTRACHEQUE = "contracheque"
    FGTS_GUIA = "fgts_guia"
    FGTS_RELATORIO = "fgts_relatorio"
    FGTS_CONSIGNADO = "fgts_consignado"
    INSS_GUIA = "inss_guia"
    DCTFWEB_DECLARACAO = "dctfweb_declaracao"
    DCTFWEB_RECIBO = "dctfweb_recibo"
    DCTFWEB_EXTRATO = "dctfweb_extrato"
    DCTFWEB_DEBITOS = "dctfweb_debitos"
    DCTFWEB_CREDITOS = "dctfweb_creditos"
    DCTFWEB_SITUACAO = "dctfweb_situacao"
    ADMISSAO = "admissao"
    RESCISAO = "rescisao"
    FERIAS = "ferias"
    DECIMO_TERCEIRO = "decimo_terceiro"
    EMPRESA_DOCS = "empresa_docs"
    OUTROS = "outros"


class OnvioSyncLog(Base):
    __tablename__ = "onvio_sync_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mes_ref = Column(String(7))  # "03.2026"
    status = Column(String(20), default="pending")
    docs_baixados = Column(Integer, default=0)
    docs_novos = Column(Integer, default=0)
    docs_erro = Column(Integer, default=0)
    duracao_s = Column(Float)
    detalhes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OnvioDocument(Base):
    __tablename__ = "onvio_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    onvio_id = Column(String(64), unique=True, nullable=False)
    onvio_folder_id = Column(String(64), nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    categoria = Column(String(50), nullable=False)
    mes_ref = Column(String(7))  # "03.2026"
    caminho_local = Column(String(512))
    tamanho_bytes = Column(Integer)
    data_onvio = Column(DateTime(timezone=True))
    data_importado = Column(DateTime(timezone=True), server_default=func.now())
    processado = Column(Boolean, default=False)
    metadata_json = Column(Text)


class FgtsGuia(Base):
    __tablename__ = "fgts_guias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mes_ref = Column(String(7), nullable=False)
    tipo = Column(String(50))  # "GFD", "CONSIGNADO", "RELATORIO"
    valor = Column(Float)
    vencimento = Column(DateTime(timezone=True))
    status = Column(String(20), default="pendente")
    arquivo_pdf = Column(String(512))
    onvio_doc_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InssGuia(Base):
    __tablename__ = "inss_guias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mes_ref = Column(String(7), nullable=False)
    valor = Column(Float)
    vencimento = Column(DateTime(timezone=True))
    competencia = Column(String(7))
    status = Column(String(20), default="pendente")
    arquivo_pdf = Column(String(512))
    onvio_doc_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

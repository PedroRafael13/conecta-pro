"""
KitBuilderService — FASE 4 BLOCO 3 T1 (§26 CONTRACTS_GEDEON.md v1.21).
Serviço read-only: calcula completude de kit documental por condomínio/mês.
ZERO endpoints, ZERO UI, ZERO ZIP. Apenas build_completude + build_lote_condominios.
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import text

from core.database.session import SyncSessionLocal

logger = logging.getLogger(__name__)

# §26.3 — Mapeamento imutável categoria Onvio → tipo_documento do kit
CATEGORIA_TO_TIPO_DOCUMENTO: dict[str, str] = {
    "folha_pagamento": "folha_pagamento",
    "recibo_folha": "contracheque",
    "folha_ponto": "folhas_ponto",
    "fgts_guia": "gfd_fgts_mensal",
    "fgts_relatorio": "relatorio_gfd_fgts",
    "dctfweb_declaracao": "dctfweb_declaracao",
    "dctfweb_recibo": "dctfweb_recibo",
    "dctfweb_extrato": "dctfweb_extrato",
    "dctfweb_resumo_creditos": "dctfweb_extrato",
    "dctfweb_resumo_debitos": "dctfweb_extrato",
    "dctfweb_creditos": "dctfweb_extrato",
    "dctfweb_debitos": "dctfweb_extrato",
    "dctfweb_situacao": "dctfweb_extrato",
    "contrato_trabalho": "contrato_trabalho",
    "ficha_registro": "ficha_empregado",
    "rescisao": "rescisao_contrato",
    "aso": "aso",
    "aviso_previo": "aviso_previo_ferias",
    "ferias": "recibo_ferias",
    "declaracao_vt": "comp_vt_individual",
}

# §26.4 — CNDs: geradas pela FASE 1, nunca em onvio_documents
_CND_TIPOS: frozenset[str] = frozenset({"cnd_caixa", "cnd_prefeitura", "cnd_rfb", "cnd_sefaz", "cnd_trabalhista"})

# §26.5 — comp_pagamentos: gerados pela FASE 2, nunca em onvio_documents
_COMP_PAGAMENTOS_TIPOS: frozenset[str] = frozenset({"comp_pag_fgts", "comp_salario_individual", "comp_va_solides"})

_MES_REF_RE = re.compile(r"^\d{2}\.\d{4}$")


# ---------------------------------------------------------------------------
# DTOs (§26.6)
# ---------------------------------------------------------------------------


class DocumentoPresente(BaseModel):
    tipo_documento: str
    escopo: str
    onvio_id: str
    nome_arquivo: str
    condominio_id: UUID | None
    employee_id: UUID | None
    mes_ref: str


class DocumentoFaltante(BaseModel):
    tipo_documento: str
    escopo: str
    obrigatorio: bool
    motivo: str  # "nao_encontrado" | "aguarda_fase_1_cnd" | "aguarda_fase_2_banco"


class MetricasKit(BaseModel):
    total_esperados: int
    total_presentes: int
    total_faltantes: int
    percentual_completude: float
    obrigatorios_faltantes: int


class CompletudeKit(BaseModel):
    condominio_id: UUID
    condominio_nome: str
    tipo_servico: str
    mes_ref: str
    docs_presentes: list[DocumentoPresente]
    docs_faltantes: list[DocumentoFaltante]
    metricas: MetricasKit


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class KitBuilderService:
    """
    Calcula completude de kit documental para um condomínio + mês.
    Leitura pura — sem escrita no banco, sem efeitos colaterais.
    """

    def build_completude(self, condominio_id: UUID, mes_ref: str) -> CompletudeKit:
        """
        Retorna CompletudeKit para (condominio_id, mes_ref).

        Raises:
            ValueError: mes_ref fora do formato MM.YYYY ou condomínio inexistente.
        """
        # §26.7 — validar mes_ref
        if not _MES_REF_RE.match(mes_ref):
            raise ValueError(f"mes_ref inválido: '{mes_ref}'. Formato esperado: 'MM.YYYY' (ex: '03.2026')")

        with SyncSessionLocal() as session:
            # 1. Buscar condomínio
            cond = (
                session.execute(
                    text("SELECT id, nome, tipo_servico FROM condominios WHERE id = :id AND ativo = true"),
                    {"id": str(condominio_id)},
                )
                .mappings()
                .first()
            )

            if not cond:
                raise ValueError(f"Condomínio {condominio_id} não encontrado ou inativo")

            # 2. Buscar templates para o tipo_servico deste condomínio
            templates = (
                session.execute(
                    text(
                        "SELECT tipo_documento, escopo, obrigatorio "
                        "FROM kit_documental_templates WHERE tipo_servico = :ts"
                    ),
                    {"ts": cond["tipo_servico"]},
                )
                .mappings()
                .all()
            )

            # 3. Buscar onvio_documents deste condomínio no mês
            onvio_docs = (
                session.execute(
                    text(
                        "SELECT onvio_id, nome_arquivo, categoria, "
                        "condominio_id, referente_a_employee_id, doc_scope "
                        "FROM onvio_documents "
                        "WHERE condominio_id = :cid AND mes_ref = :mr"
                    ),
                    {"cid": str(condominio_id), "mr": mes_ref},
                )
                .mappings()
                .all()
            )

        # 4. Indexar onvio_docs por tipo_documento derivado
        tipo_to_docs: dict[str, list] = defaultdict(list)
        for doc in onvio_docs:
            tipo = CATEGORIA_TO_TIPO_DOCUMENTO.get(doc["categoria"])
            if tipo:
                tipo_to_docs[tipo].append(doc)

        # 5. Processar cada template
        docs_presentes: list[DocumentoPresente] = []
        docs_faltantes: list[DocumentoFaltante] = []
        tipos_com_doc: set[str] = set()

        for t in templates:
            tipo = t["tipo_documento"]
            escopo = t["escopo"]
            obrigatorio = bool(t["obrigatorio"])

            # §26.4 — CND → sempre faltante (gerado por FASE 1)
            if tipo in _CND_TIPOS:
                docs_faltantes.append(
                    DocumentoFaltante(
                        tipo_documento=tipo,
                        escopo=escopo,
                        obrigatorio=obrigatorio,
                        motivo="aguarda_fase_1_cnd",
                    )
                )
                continue

            # §26.5 — comp_pagamentos → sempre faltante (gerado por FASE 2)
            if tipo in _COMP_PAGAMENTOS_TIPOS:
                docs_faltantes.append(
                    DocumentoFaltante(
                        tipo_documento=tipo,
                        escopo=escopo,
                        obrigatorio=obrigatorio,
                        motivo="aguarda_fase_2_banco",
                    )
                )
                continue

            # Demais tipos: cruzar com onvio_documents
            matching = tipo_to_docs.get(tipo, [])
            if matching:
                tipos_com_doc.add(tipo)
                for doc in matching:
                    docs_presentes.append(
                        DocumentoPresente(
                            tipo_documento=tipo,
                            escopo=escopo,
                            onvio_id=doc["onvio_id"] or "",
                            nome_arquivo=doc["nome_arquivo"] or "",
                            condominio_id=(UUID(str(doc["condominio_id"])) if doc["condominio_id"] else None),
                            employee_id=(
                                UUID(str(doc["referente_a_employee_id"])) if doc["referente_a_employee_id"] else None
                            ),
                            mes_ref=mes_ref,
                        )
                    )
            else:
                docs_faltantes.append(
                    DocumentoFaltante(
                        tipo_documento=tipo,
                        escopo=escopo,
                        obrigatorio=obrigatorio,
                        motivo="nao_encontrado",
                    )
                )

        # 6. Calcular métricas
        total_esperados = len(templates)
        # presentes = tipos distintos que têm ao menos 1 doc; faltantes = restantes
        total_presentes = len(tipos_com_doc)
        total_faltantes = total_esperados - total_presentes
        percentual = round(total_presentes / total_esperados * 100, 2) if total_esperados else 0.0
        obrig_faltantes = sum(1 for d in docs_faltantes if d.obrigatorio)

        return CompletudeKit(
            condominio_id=condominio_id,
            condominio_nome=str(cond["nome"]),
            tipo_servico=str(cond["tipo_servico"]),
            mes_ref=mes_ref,
            docs_presentes=docs_presentes,
            docs_faltantes=docs_faltantes,
            metricas=MetricasKit(
                total_esperados=total_esperados,
                total_presentes=total_presentes,
                total_faltantes=total_faltantes,
                percentual_completude=percentual,
                obrigatorios_faltantes=obrig_faltantes,
            ),
        )

    def build_lote_condominios(self, mes_ref: str) -> list[CompletudeKit]:
        """
        Retorna CompletudeKit para todos os condomínios ativos no mês.
        Erros individuais são logados e pulados (não aborta o lote).
        """
        if not _MES_REF_RE.match(mes_ref):
            raise ValueError(f"mes_ref inválido: '{mes_ref}'. Formato esperado: 'MM.YYYY'")

        with SyncSessionLocal() as session:
            conds = (
                session.execute(text("SELECT id FROM condominios WHERE ativo = true ORDER BY nome")).mappings().all()
            )

        resultados: list[CompletudeKit] = []
        for row in conds:
            try:
                kit = self.build_completude(UUID(str(row["id"])), mes_ref)
                resultados.append(kit)
            except Exception as exc:
                logger.warning("build_lote: falha no condomínio %s — %s", row["id"], exc)

        return resultados

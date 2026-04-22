"""KitBuilderService — FASE 4 BLOCO 3 / BLOCO A (modelo canônico)

Dada (condominio_id, mes_ref), retorna CompletudeKit com docs presentes
e faltantes, separando confirmados vs pendentes revisão.

§26 / §27 / §35 do CONTRACTS_GEDEON.md v1.33.

BLOCO A: total_esperado agora é dinâmico por condomínio:
  - empresa_matriz: COUNT templates presença='obrigatorio' e escopo='empresa_matriz'
  - condominio:     COUNT templates presença='obrigatorio' e escopo='condominio'
  - funcionario:    COUNT templates presença='obrigatorio' e escopo='funcionario' × N_func_ativos
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

# ============================================================================
# MAPPING categoria (onvio) → slug (kit_documental_templates)
# Exportado como constante pública (T2 importa se necessário)
# ============================================================================
CategoriaToTipoDocumento: dict[str, str] = {
    # M2 Contábil
    "folha_pagamento": "folha_pagamento",
    "recibo_folha": "contracheque",
    "folha_ponto": "folhas_ponto",
    # M3 FGTS
    "fgts_guia": "gfd_fgts_mensal",
    "fgts_relatorio": "relatorio_gfd_fgts",
    # M4 DCTFWeb
    "dctfweb_declaracao": "dctfweb_declaracao",
    "dctfweb_recibo": "dctfweb_recibo",
    "dctfweb_extrato": "dctfweb_extrato",
    "dctfweb_resumo_creditos": "dctfweb_extrato",
    "dctfweb_resumo_debitos": "dctfweb_extrato",
    "dctfweb_creditos": "dctfweb_extrato",
    "dctfweb_debitos": "dctfweb_extrato",
    "dctfweb_situacao": "dctfweb_extrato",
    # M7 RH
    "contrato_trabalho": "contrato_trabalho",
    "ficha_registro": "ficha_empregado",
    "rescisao": "rescisao_contrato",
    "aso": "aso",
    "aviso_previo": "aviso_previo_ferias",
    "ferias": "recibo_ferias",
    # M6 VT/VA
    "declaracao_vt": "comp_vt_individual",
}

# tipo_documento que AGUARDA FASE 1 (CNDs — Claude in Chrome)
TIPOS_DOCUMENTO_AGUARDA_FASE_1_CND: frozenset[str] = frozenset(
    {"cnd_rfb", "cnd_caixa", "cnd_prefeitura", "cnd_sefaz", "cnd_trabalhista"}
)

# tipo_documento que AGUARDA FASE 2 (comprovantes bancários / NFS-e / Boleto)
TIPOS_DOCUMENTO_AGUARDA_FASE_2_BANCO: frozenset[str] = frozenset(
    {
        "comp_pag_fgts",
        "comp_fgts_rescisao",
        "comp_salario_individual",
        "comp_rescisao",
        "nfse",
        "boleto",
    }
)

# slug sem categoria Onvio correspondente (não sincronizado)
TIPOS_DOCUMENTO_SEM_SINCRONIZACAO: frozenset[str] = frozenset(
    {"comp_vt_va_combinado", "recibo_vt_va", "comp_va_solides", "relatorio_pedido_va"}
)

# Regex com validação de mês 01-12 (§26.7)
MES_REF_PATTERN = re.compile(r"^(0[1-9]|1[0-2])\.\d{4}$")


# ============================================================================
# DTOs (§26.6 / §27.3)
# ============================================================================


@dataclass
class DocumentoPresente:
    tipo_documento: str
    escopo: str
    onvio_document_id: UUID
    nome_arquivo: str
    revisao_pendente: bool


@dataclass
class DocumentoFaltante:
    tipo_documento: str
    escopo: str
    obrigatorio: bool
    periodicidade: str
    motivo: str


@dataclass
class MetricasKit:
    total_esperado: int
    total_presente_confirmado: int
    total_presente_pendente_revisao: int
    total_faltante: int
    pct_completude_confirmada: float
    pct_completude_total: float


@dataclass
class CompletudeKit:
    condominio_id: UUID
    condominio_nome: str
    tipo_servico: str
    mes_ref: str
    docs_presentes: list[DocumentoPresente] = field(default_factory=list)
    docs_faltantes: list[DocumentoFaltante] = field(default_factory=list)
    metricas: MetricasKit | None = None
    gerado_em: datetime = field(default_factory=datetime.utcnow)


# ============================================================================
# Helpers públicos
# ============================================================================


def _validate_mes_ref(mes_ref: str) -> None:
    if not isinstance(mes_ref, str) or not MES_REF_PATTERN.match(mes_ref):
        raise ValueError(f"mes_ref inválido: '{mes_ref}'. Formato esperado: 'MM.YYYY' (ex: '03.2026').")


def _determinar_motivo_faltante(tipo_documento: str) -> str:
    if tipo_documento in TIPOS_DOCUMENTO_AGUARDA_FASE_1_CND:
        return "aguarda_fase_1_cnd"
    if tipo_documento in TIPOS_DOCUMENTO_AGUARDA_FASE_2_BANCO:
        return "aguarda_fase_2_banco"
    if tipo_documento in TIPOS_DOCUMENTO_SEM_SINCRONIZACAO:
        return "nao_sincronizado"
    return "nao_encontrado_onvio"


# ============================================================================
# KitBuilderService
# ============================================================================


class KitBuilderService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _count_funcionarios_ativos(self, condominio_id: UUID, mes_ref: str) -> int:
        """Conta funcionários com alocação ativa para o condomínio no mês de referência."""
        row = self.db.execute(
            text(
                "SELECT COUNT(DISTINCT employee_id) "
                "FROM employee_alocacoes "
                "WHERE condominio_id = CAST(:cid AS uuid) AND ativo = true"
            ),
            {"cid": str(condominio_id)},
        ).fetchone()
        return int(row[0]) if row else 0

    def _calc_total_esperado(self, condominio_id: UUID, mes_ref: str) -> int:
        """
        Fórmula canônica §35.4:
          empresa_matriz obrig → ×1
          condominio obrig → ×1
          funcionario obrig → ×N_funcionarios_ativos
        Apenas presença='obrigatorio' conta (⚠️='eventual' e -='na' excluídos).
        """
        n_func = self._count_funcionarios_ativos(condominio_id, mes_ref)

        row = self.db.execute(
            text(
                """
                SELECT
                  COUNT(*) FILTER (WHERE t.escopo = 'empresa_matriz') AS cnt_matriz,
                  COUNT(*) FILTER (WHERE t.escopo = 'condominio')     AS cnt_cond,
                  COUNT(*) FILTER (WHERE t.escopo = 'funcionario')    AS cnt_func
                FROM kit_documental_templates t
                JOIN kit_template_presenca p ON t.id = p.template_id
                WHERE p.condominio_id = CAST(:cid AS uuid)
                  AND p.presenca = 'obrigatorio'
                """
            ),
            {"cid": str(condominio_id)},
        ).fetchone()

        cnt_matriz = int(row[0]) if row else 0
        cnt_cond = int(row[1]) if row else 0
        cnt_func = int(row[2]) if row else 0

        return cnt_matriz + cnt_cond + (cnt_func * n_func)

    def build_completude(self, condominio_id: UUID, mes_ref: str) -> CompletudeKit:
        """Monta completude do kit para 1 condomínio × 1 mes_ref. (§27 signature preservada)"""
        _validate_mes_ref(mes_ref)

        # 1. Buscar condomínio
        row = self.db.execute(
            text("SELECT id, nome, tipo_servico FROM condominios WHERE id = CAST(:cid AS uuid) AND ativo = true"),
            {"cid": str(condominio_id)},
        ).fetchone()

        if not row:
            raise ValueError(f"Condomínio não encontrado ou inativo: {condominio_id}")

        cond_id = row[0]
        cond_nome = row[1]
        tipo_servico = row[2]

        # 2. Administrativo → kit vazio
        if tipo_servico == "administrativo":
            return CompletudeKit(
                condominio_id=UUID(str(cond_id)),
                condominio_nome=cond_nome,
                tipo_servico=tipo_servico,
                mes_ref=mes_ref,
                docs_presentes=[],
                docs_faltantes=[],
                metricas=MetricasKit(
                    total_esperado=0,
                    total_presente_confirmado=0,
                    total_presente_pendente_revisao=0,
                    total_faltante=0,
                    pct_completude_confirmada=0.0,
                    pct_completude_total=0.0,
                ),
            )

        # 3. Buscar templates com presença para este condomínio (apenas 'obrigatorio' e 'eventual')
        templates = self.db.execute(
            text(
                """
                SELECT t.slug AS tipo_documento, t.escopo, t.obrigatorio,
                       t.periodicidade, p.presenca
                FROM kit_documental_templates t
                JOIN kit_template_presenca p ON t.id = p.template_id
                WHERE p.condominio_id = CAST(:cid AS uuid)
                  AND p.presenca IN ('obrigatorio', 'eventual')
                ORDER BY t.num
                """
            ),
            {"cid": str(condominio_id)},
        ).fetchall()

        # 4. Buscar docs Onvio: condomínio + empresa_matriz + funcionários alocados
        onvio_rows = self.db.execute(
            text(
                """
                SELECT od.id, od.categoria, od.doc_scope, od.nome_arquivo, od.revisao_manual
                FROM onvio_documents od
                WHERE od.mes_ref = :mes
                  AND (
                    (od.doc_scope = 'condominio' AND od.condominio_id = CAST(:cid AS uuid))
                    OR (od.doc_scope = 'empresa_matriz')
                    OR (od.doc_scope = 'funcionario' AND od.referente_a_employee_id IN (
                        SELECT employee_id FROM employee_alocacoes
                        WHERE condominio_id = CAST(:cid AS uuid) AND ativo = true
                    ))
                  )
                """
            ),
            {"mes": mes_ref, "cid": str(condominio_id)},
        ).fetchall()

        # 5. Mapear onvio_docs por slug (via CategoriaToTipoDocumento)
        docs_por_tipo: dict[str, list] = {}
        for od in onvio_rows:
            od_id, categoria, scope, nome_arq, revisao = od[0], od[1], od[2], od[3], od[4]
            slug = CategoriaToTipoDocumento.get(categoria)
            if not slug:
                continue
            docs_por_tipo.setdefault(slug, []).append(
                {
                    "onvio_id": od_id,
                    "escopo": scope,
                    "nome_arquivo": nome_arq,
                    "revisao_pendente": bool(revisao),
                }
            )

        # 6. Para cada template, verificar se tem doc correspondente
        presentes: list[DocumentoPresente] = []
        faltantes: list[DocumentoFaltante] = []

        for t in templates:
            tipo_doc, escopo, obrig, period, _ = t[0], t[1], t[2], t[3], t[4]
            docs_encontrados = docs_por_tipo.get(tipo_doc, [])

            if docs_encontrados:
                for doc in docs_encontrados:
                    presentes.append(
                        DocumentoPresente(
                            tipo_documento=tipo_doc,
                            escopo=doc["escopo"],
                            onvio_document_id=UUID(str(doc["onvio_id"])),
                            nome_arquivo=doc["nome_arquivo"],
                            revisao_pendente=doc["revisao_pendente"],
                        )
                    )
            else:
                faltantes.append(
                    DocumentoFaltante(
                        tipo_documento=tipo_doc,
                        escopo=escopo,
                        obrigatorio=bool(obrig),
                        periodicidade=period or "mensal",
                        motivo=_determinar_motivo_faltante(tipo_doc),
                    )
                )

        # 7. Calcular métricas com fórmula canônica §35.4
        total_esperado = self._calc_total_esperado(UUID(str(cond_id)), mes_ref)
        total_confirmado = sum(1 for p in presentes if not p.revisao_pendente)
        total_pendente = sum(1 for p in presentes if p.revisao_pendente)
        total_faltante = len(faltantes)

        pct_conf = (total_confirmado / total_esperado * 100) if total_esperado else 0.0
        pct_total = ((total_confirmado + total_pendente) / total_esperado * 100) if total_esperado else 0.0

        return CompletudeKit(
            condominio_id=UUID(str(cond_id)),
            condominio_nome=cond_nome,
            tipo_servico=tipo_servico,
            mes_ref=mes_ref,
            docs_presentes=presentes,
            docs_faltantes=faltantes,
            metricas=MetricasKit(
                total_esperado=total_esperado,
                total_presente_confirmado=total_confirmado,
                total_presente_pendente_revisao=total_pendente,
                total_faltante=total_faltante,
                pct_completude_confirmada=round(pct_conf, 2),
                pct_completude_total=round(pct_total, 2),
            ),
        )

    def build_lote_condominios(self, mes_ref: str) -> list[CompletudeKit]:
        """Monta completude do kit para TODOS os condomínios ativos em 1 mes_ref."""
        _validate_mes_ref(mes_ref)

        rows = self.db.execute(text("SELECT id FROM condominios WHERE ativo = true ORDER BY nome")).fetchall()

        return [self.build_completude(UUID(str(r[0])), mes_ref) for r in rows]

"""Schemas para modulo Folha de Pagamento."""

from typing import Any

from pydantic import BaseModel, Field


class RubricaCalculo(BaseModel):
    """Uma rubrica calculada no holerite."""

    codigo: str
    descricao: str
    tipo: str  # provento | desconto
    referencia: str = ""
    valor: float = 0.0


class HoleriteResponse(BaseModel):
    """Holerite calculado de um colaborador."""

    employee_id: str
    employee_nome: str
    cargo: str
    escala: str
    mes: int
    ano: int
    salario_base: float
    proventos: list[RubricaCalculo] = Field(default_factory=list)
    descontos: list[RubricaCalculo] = Field(default_factory=list)
    total_proventos: float = 0.0
    total_descontos: float = 0.0
    liquido: float = 0.0
    base_inss: float = 0.0
    base_irrf: float = 0.0
    base_fgts: float = 0.0
    fgts_empresa: float = 0.0


class FolhaBatchResponse(BaseModel):
    """Resultado do calculo batch da folha."""

    mes: int
    ano: int
    total_colaboradores: int
    total_calculados: int
    total_erros: int
    total_proventos: float = 0.0
    total_descontos: float = 0.0
    total_liquido: float = 0.0
    total_fgts: float = 0.0
    erros: list[dict[str, Any]] = Field(default_factory=list)
    holerites: list[HoleriteResponse] = Field(default_factory=list)


class DashboardFolhaResponse(BaseModel):
    """Dashboard gerencial da folha."""

    mes: int
    ano: int
    total_colaboradores: int
    total_proventos: float = 0.0
    total_descontos: float = 0.0
    total_liquido: float = 0.0
    total_fgts: float = 0.0
    total_inss: float = 0.0
    total_irrf: float = 0.0
    por_cargo: dict[str, dict[str, Any]] = Field(default_factory=dict)
    rubricas_count: int = 0
    status: str = "aberta"


class ResumoFolhaResponse(BaseModel):
    """Resumo totalizador da folha do mes."""

    mes: int
    ano: int
    total_colaboradores: int
    total_proventos: float
    total_descontos: float
    total_liquido: float
    total_fgts: float
    total_inss: float
    total_irrf: float
    custo_total_empresa: float


class AjusteRequest(BaseModel):
    """Ajuste manual em rubrica do holerite."""

    rubrica_codigo: str
    valor: float
    motivo: str = Field(..., min_length=5)
    ajustado_por: str


class RubricaResponse(BaseModel):
    """Rubrica cadastrada."""

    id: int
    codigo: str
    descricao: str
    tipo: str
    natureza: str
    base_calculo: str | None = None
    percentual: float | None = None
    valor_fixo: float | None = None
    incide_inss: bool = False
    incide_irrf: bool = False
    incide_fgts: bool = False
    ativo: bool = True


class FechamentoResponse(BaseModel):
    """Resposta do fechamento mensal."""

    mes: int
    ano: int
    total_colaboradores: int
    total_liquido: float
    total_fgts: float
    fechado_por: str
    fechado_em: str
    status: str = "fechada"
    message: str = ""


class ConferenciaResponse(BaseModel):
    """Confronto Conecta PRO vs Alterdata."""

    mes: int
    ano: int
    total_colaboradores: int
    total_liquido_conecta: float
    total_liquido_alterdata: float | None = None
    divergencias_count: int = 0
    status: str = "aguardando_importacao"
    colaboradores: list[dict[str, Any]] = Field(default_factory=list)
    message: str = ""

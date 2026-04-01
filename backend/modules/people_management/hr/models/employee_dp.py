"""
Modelo EmployeeDP — Dados Trabalhistas Completos (50+ campos CLT).

Estende os dados básicos do Employee (operacional) com todos os campos
necessários para gestão trabalhista: CTPS, PIS, dependentes, adicionais,
jornada, sindicato, eSocial, etc.
"""

from datetime import date, datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class JornadaType(StrEnum):
    """Tipo de jornada de trabalho."""

    PADRAO_44H = "44h_semanais"
    ESCALA_12X36 = "12x36"
    ESCALA_24X48 = "24x48"
    ESCALA_5X1 = "5x1"
    ESCALA_5X2 = "5x2"
    ESCALA_6X1 = "6x1"
    PARCIAL = "parcial"


class GrauInsalubridade(StrEnum):
    """Grau de insalubridade."""

    NENHUM = "nenhum"
    MINIMO = "minimo"
    MEDIO = "medio"
    MAXIMO = "maximo"


class EmployeeDP(Base):
    """Dados trabalhistas estendidos do colaborador — 50+ campos CLT.

    Complementa Employee (operacional) com informações de:
    - Documentação trabalhista (CTPS, PIS/PASEP, NIT)
    - Regime de trabalho (jornada, escala, sindicato)
    - Adicionais legais (periculosidade, insalubridade, noturno)
    - Benefícios e dependentes
    - Dados bancários para pagamento
    - Histórico eSocial
    """

    __tablename__ = "employee_dp"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    employee_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False, unique=True, index=True)

    # === DOCUMENTACAO TRABALHISTA ===
    ctps_numero: Mapped[str | None] = mapped_column(String(20))
    ctps_serie: Mapped[str | None] = mapped_column(String(10))
    ctps_uf: Mapped[str | None] = mapped_column(String(2))
    ctps_data_emissao: Mapped[date | None] = mapped_column(Date)
    pis_pasep: Mapped[str | None] = mapped_column(String(15), unique=True)
    nit: Mapped[str | None] = mapped_column(String(15))
    titulo_eleitor: Mapped[str | None] = mapped_column(String(15))
    titulo_zona: Mapped[str | None] = mapped_column(String(5))
    titulo_secao: Mapped[str | None] = mapped_column(String(5))
    certificado_reservista: Mapped[str | None] = mapped_column(String(15))
    cnh_numero: Mapped[str | None] = mapped_column(String(15))
    cnh_categoria: Mapped[str | None] = mapped_column(String(3))
    cnh_validade: Mapped[date | None] = mapped_column(Date)

    # === DADOS PESSOAIS COMPLEMENTARES ===
    nome_mae: Mapped[str | None] = mapped_column(String(200))
    nome_pai: Mapped[str | None] = mapped_column(String(200))
    estado_civil: Mapped[str | None] = mapped_column(String(20))
    grau_instrucao: Mapped[str | None] = mapped_column(String(50))
    nacionalidade: Mapped[str | None] = mapped_column(String(50), default="Brasileira")
    naturalidade_cidade: Mapped[str | None] = mapped_column(String(100))
    naturalidade_uf: Mapped[str | None] = mapped_column(String(2))
    raca_cor: Mapped[str | None] = mapped_column(String(20))
    deficiencia: Mapped[bool] = mapped_column(Boolean, default=False)
    tipo_deficiencia: Mapped[str | None] = mapped_column(String(100))

    # === CONTRATO / JORNADA ===
    data_admissao: Mapped[date | None] = mapped_column(Date)
    data_demissao: Mapped[date | None] = mapped_column(Date)
    tipo_contrato: Mapped[str | None] = mapped_column(String(30), default="indeterminado")
    jornada_tipo: Mapped[str | None] = mapped_column(String(30), default=JornadaType.PADRAO_44H)
    carga_horaria_semanal: Mapped[int] = mapped_column(Integer, default=44)
    carga_horaria_mensal: Mapped[int] = mapped_column(Integer, default=220)
    horario_entrada: Mapped[str | None] = mapped_column(String(5))
    horario_saida: Mapped[str | None] = mapped_column(String(5))
    horario_intervalo_inicio: Mapped[str | None] = mapped_column(String(5))
    horario_intervalo_fim: Mapped[str | None] = mapped_column(String(5))

    # === REMUNERACAO ===
    salario_base: Mapped[float | None] = mapped_column(Numeric(12, 2))
    salario_familia: Mapped[bool] = mapped_column(Boolean, default=False)
    quantidade_dependentes_sf: Mapped[int] = mapped_column(Integer, default=0)

    # === ADICIONAIS LEGAIS ===
    adicional_periculosidade: Mapped[bool] = mapped_column(Boolean, default=False)
    percentual_periculosidade: Mapped[float | None] = mapped_column(Numeric(5, 2), default=30)
    grau_insalubridade: Mapped[str] = mapped_column(String(10), default=GrauInsalubridade.NENHUM)
    adicional_noturno: Mapped[bool] = mapped_column(Boolean, default=False)
    percentual_noturno: Mapped[float | None] = mapped_column(Numeric(5, 2), default=20)
    adicional_transferencia: Mapped[bool] = mapped_column(Boolean, default=False)

    # === BENEFICIOS ===
    vale_transporte: Mapped[bool] = mapped_column(Boolean, default=True)
    vale_refeicao: Mapped[bool] = mapped_column(Boolean, default=False)
    valor_vale_refeicao: Mapped[float | None] = mapped_column(Numeric(10, 2))
    vale_alimentacao: Mapped[bool] = mapped_column(Boolean, default=False)
    valor_vale_alimentacao: Mapped[float | None] = mapped_column(Numeric(10, 2))
    plano_saude: Mapped[bool] = mapped_column(Boolean, default=False)
    plano_odontologico: Mapped[bool] = mapped_column(Boolean, default=False)
    seguro_vida: Mapped[bool] = mapped_column(Boolean, default=False)

    # === SINDICATO ===
    sindicato_nome: Mapped[str | None] = mapped_column(String(200))
    sindicato_cnpj: Mapped[str | None] = mapped_column(String(18))
    contribuicao_sindical: Mapped[bool] = mapped_column(Boolean, default=False)
    data_base_categoria: Mapped[str | None] = mapped_column(String(5))

    # === DADOS BANCARIOS ===
    banco_codigo: Mapped[str | None] = mapped_column(String(5))
    banco_nome: Mapped[str | None] = mapped_column(String(100))
    agencia: Mapped[str | None] = mapped_column(String(10))
    agencia_digito: Mapped[str | None] = mapped_column(String(2))
    conta: Mapped[str | None] = mapped_column(String(15))
    conta_digito: Mapped[str | None] = mapped_column(String(2))
    tipo_conta: Mapped[str | None] = mapped_column(String(20), default="corrente")
    chave_pix: Mapped[str | None] = mapped_column(String(100))

    # === DEPENDENTES (JSON) ===
    dependentes: Mapped[dict | None] = mapped_column(JSONB, default=list)

    # === eSocial ===
    matricula_esocial: Mapped[str | None] = mapped_column(String(30), unique=True)
    categoria_trabalhador: Mapped[str | None] = mapped_column(String(5), default="101")
    cod_cbo: Mapped[str | None] = mapped_column(String(10))

    # === FERIAS / AFASTAMENTO ===
    periodo_aquisitivo_inicio: Mapped[date | None] = mapped_column(Date)
    ferias_vencidas: Mapped[bool] = mapped_column(Boolean, default=False)
    afastamento_atual: Mapped[str | None] = mapped_column(String(50))
    data_retorno_previsto: Mapped[date | None] = mapped_column(Date)

    # === FGTS ===
    optante_fgts: Mapped[bool] = mapped_column(Boolean, default=True)
    data_opcao_fgts: Mapped[date | None] = mapped_column(Date)
    conta_fgts: Mapped[str | None] = mapped_column(String(30))
    saldo_fgts_estimado: Mapped[float | None] = mapped_column(Numeric(14, 2))

    # === METADATA ===
    observacoes: Mapped[str | None] = mapped_column(Text)
    dados_extras: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<EmployeeDP employee_id={self.employee_id} pis={self.pis_pasep}>"

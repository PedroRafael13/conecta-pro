"""Schemas Pydantic para modulo Fiscal - NF-e, NFS-e, SPED, Retencoes."""
# pylint: disable=too-few-public-methods,no-self-argument,missing-class-docstring

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

# ============================================================
# Enums para Schemas
# ============================================================


class TaxRegimeEnum(str, Enum):
    """Regime tributario."""

    SIMPLES_NACIONAL = "simples_nacional"
    LUCRO_PRESUMIDO = "lucro_presumido"
    LUCRO_REAL = "lucro_real"
    MEI = "mei"
    ISENTO = "isento"


class NFeTipoEnum(str, Enum):
    """Tipo de NF-e."""

    ENTRADA = "entrada"
    SAIDA = "saida"


class NFeStatusEnum(str, Enum):
    """Status da NF-e."""

    RASCUNHO = "rascunho"
    VALIDANDO = "validando"
    ASSINADA = "assinada"
    ENVIADA = "enviada"
    AUTORIZADA = "autorizada"
    DENEGADA = "denegada"
    REJEITADA = "rejeitada"
    CANCELADA = "cancelada"
    INUTILIZADA = "inutilizada"


class NFSeStatusEnum(str, Enum):
    """Status da NFS-e."""

    RASCUNHO = "rascunho"
    VALIDANDO = "validando"
    ENVIANDO = "enviando"
    PROCESSANDO = "processando"
    AUTORIZADA = "autorizada"
    REJEITADA = "rejeitada"
    CANCELADA = "cancelada"
    SUBSTITUIDA = "substituida"


class SPEDTipoEnum(str, Enum):
    """Tipo de arquivo SPED."""

    EFD_ICMS_IPI = "efd_icms_ipi"
    EFD_CONTRIBUICOES = "efd_contribuicoes"
    ECD = "ecd"
    ECF = "ecf"
    REINF = "reinf"
    ESOCIAL = "esocial"


class SPEDStatusEnum(str, Enum):
    """Status do arquivo SPED."""

    GERANDO = "gerando"
    GERADO = "gerado"
    VALIDANDO = "validando"
    VALIDADO = "validado"
    ERRO_VALIDACAO = "erro_validacao"
    ASSINANDO = "assinando"
    ASSINADO = "assinado"
    TRANSMITINDO = "transmitindo"
    TRANSMITIDO = "transmitido"
    ERRO_TRANSMISSAO = "erro_transmissao"
    ACEITO = "aceito"
    RECUSADO = "recusado"


class ObrigacaoStatusEnum(str, Enum):
    """Status de obrigacao fiscal."""

    PENDENTE = "pendente"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    ATRASADA = "atrasada"
    CANCELADA = "cancelada"


# ============================================================
# CFOP Schemas
# ============================================================


class CFOPBase(BaseModel):
    """Base para CFOP."""

    codigo: str = Field(..., min_length=4, max_length=4, description="Codigo CFOP")
    descricao: str = Field(..., min_length=5, max_length=500)
    descricao_resumida: Optional[str] = Field(None, max_length=100)
    tipo: str = Field(..., description="entrada ou saida")
    grupo: str = Field(..., min_length=1, max_length=1, description="1,2,3,5,6,7")
    natureza: Optional[str] = Field(None, max_length=30)

    # Tributacao
    gera_credito_icms: bool = False
    gera_debito_icms: bool = False
    gera_credito_ipi: bool = False
    gera_debito_ipi: bool = False
    gera_pis_cofins: bool = True

    # Movimentacao
    movimenta_estoque: bool = True
    movimenta_financeiro: bool = True
    movimenta_contabilidade: bool = True

    # Zona Franca
    zfm_aplicavel: bool = False
    zfm_isenta_icms: bool = False
    zfm_isenta_ipi: bool = False
    zfm_suspende_pis_cofins: bool = False

    # CFOP correspondente
    cfop_correspondente: Optional[str] = Field(None, max_length=4)

    # Contas contabeis
    conta_contabil_debito: Optional[str] = Field(None, max_length=20)
    conta_contabil_credito: Optional[str] = Field(None, max_length=20)


class CFOPCreate(CFOPBase):
    """Schema para criar CFOP."""


class CFOPUpdate(BaseModel):
    """Schema para atualizar CFOP."""

    descricao: Optional[str] = Field(None, max_length=500)
    descricao_resumida: Optional[str] = Field(None, max_length=100)
    natureza: Optional[str] = Field(None, max_length=30)
    gera_credito_icms: Optional[bool] = None
    gera_debito_icms: Optional[bool] = None
    gera_credito_ipi: Optional[bool] = None
    gera_debito_ipi: Optional[bool] = None
    gera_pis_cofins: Optional[bool] = None
    movimenta_estoque: Optional[bool] = None
    movimenta_financeiro: Optional[bool] = None
    movimenta_contabilidade: Optional[bool] = None
    zfm_aplicavel: Optional[bool] = None
    zfm_isenta_icms: Optional[bool] = None
    zfm_isenta_ipi: Optional[bool] = None
    zfm_suspende_pis_cofins: Optional[bool] = None
    cfop_correspondente: Optional[str] = Field(None, max_length=4)
    conta_contabil_debito: Optional[str] = Field(None, max_length=20)
    conta_contabil_credito: Optional[str] = Field(None, max_length=20)
    active: Optional[bool] = None


class CFOPResponse(CFOPBase):
    """Response de CFOP."""

    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    active: bool
    is_entrada: bool
    is_saida: bool
    is_interestadual: bool
    is_exterior: bool

    class Config:
        from_attributes = True


class CFOPListResponse(BaseModel):
    """Lista de CFOPs."""

    items: List[CFOPResponse]
    total: int
    page: int
    page_size: int


class CFOPFilter(BaseModel):
    """Filtro para busca de CFOPs."""

    tipo: Optional[str] = None
    grupo: Optional[str] = None
    natureza: Optional[str] = None
    zfm_aplicavel: Optional[bool] = None
    movimenta_estoque: Optional[bool] = None
    active: Optional[bool] = True
    search: Optional[str] = None


# ============================================================
# NCM Schemas
# ============================================================


class NCMBase(BaseModel):
    """Base para NCM."""

    codigo: str = Field(..., min_length=8, max_length=8, description="Codigo NCM")
    descricao: str = Field(..., min_length=5, max_length=2000)
    descricao_resumida: Optional[str] = Field(None, max_length=200)

    # Classificacao
    capitulo: Optional[str] = Field(None, max_length=2)
    posicao: Optional[str] = Field(None, max_length=4)
    subposicao: Optional[str] = Field(None, max_length=6)

    # IPI
    ipi_aliquota: Optional[Decimal] = Field(None, ge=0, le=100)
    ipi_codigo_enquadramento: Optional[str] = Field(None, max_length=5)
    ipi_unidade_tributavel: Optional[str] = Field(None, max_length=6)

    # PIS/COFINS
    pis_aliquota: Optional[Decimal] = Field(Decimal("1.65"), ge=0, le=100)
    cofins_aliquota: Optional[Decimal] = Field(Decimal("7.6"), ge=0, le=100)
    pis_cofins_cst_entrada: Optional[str] = Field("50", max_length=2)
    pis_cofins_cst_saida: Optional[str] = Field("01", max_length=2)

    # ICMS
    icms_cest: Optional[str] = Field(None, max_length=7)
    icms_st_mva: Optional[Decimal] = Field(None, ge=0, le=500)

    # II
    ii_aliquota: Optional[Decimal] = Field(None, ge=0, le=100)

    # Tributacao Monofasica
    tributacao_monofasica: bool = False
    aliquota_monofasica: Optional[Decimal] = Field(None, ge=0, le=100)

    # Zona Franca
    zfm_isento_ipi: bool = False
    zfm_reduz_ii: bool = False
    zfm_percentual_reducao_ii: Optional[Decimal] = Field(None, ge=0, le=100)

    # TIPI
    tipi_unidade: Optional[str] = Field(None, max_length=10)
    tipi_nota: Optional[str] = Field(None, max_length=500)

    # Vigencia
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None


class NCMCreate(NCMBase):
    """Schema para criar NCM."""

    @validator("capitulo", always=True)
    def extract_capitulo(cls, v, values):
        """Extrai capitulo do codigo NCM."""
        if not v and "codigo" in values:
            return values["codigo"][:2]
        return v

    @validator("posicao", always=True)
    def extract_posicao(cls, v, values):
        """Extrai posicao do codigo NCM."""
        if not v and "codigo" in values:
            return values["codigo"][:4]
        return v

    @validator("subposicao", always=True)
    def extract_subposicao(cls, v, values):
        """Extrai subposicao do codigo NCM."""
        if not v and "codigo" in values:
            return values["codigo"][:6]
        return v


class NCMUpdate(BaseModel):
    """Schema para atualizar NCM."""

    descricao: Optional[str] = Field(None, max_length=2000)
    descricao_resumida: Optional[str] = Field(None, max_length=200)
    ipi_aliquota: Optional[Decimal] = None
    ipi_codigo_enquadramento: Optional[str] = None
    pis_aliquota: Optional[Decimal] = None
    cofins_aliquota: Optional[Decimal] = None
    icms_cest: Optional[str] = None
    icms_st_mva: Optional[Decimal] = None
    ii_aliquota: Optional[Decimal] = None
    tributacao_monofasica: Optional[bool] = None
    aliquota_monofasica: Optional[Decimal] = None
    zfm_isento_ipi: Optional[bool] = None
    zfm_reduz_ii: Optional[bool] = None
    zfm_percentual_reducao_ii: Optional[Decimal] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    active: Optional[bool] = None


class NCMResponse(NCMBase):
    """Response de NCM."""

    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    active: bool
    is_vigente: bool

    class Config:
        from_attributes = True


class NCMListResponse(BaseModel):
    """Lista de NCMs."""

    items: List[NCMResponse]
    total: int
    page: int
    page_size: int


class NCMFilter(BaseModel):
    """Filtro para busca de NCMs."""

    capitulo: Optional[str] = None
    posicao: Optional[str] = None
    tributacao_monofasica: Optional[bool] = None
    zfm_isento_ipi: Optional[bool] = None
    active: Optional[bool] = True
    vigente: Optional[bool] = True
    search: Optional[str] = None


# ============================================================
# Retencao Federal Schemas
# ============================================================


class RetencaoFederalBase(BaseModel):
    """Base para configuracao de retencao federal."""

    nome: str = Field(..., min_length=3, max_length=100)
    codigo_servico: Optional[str] = Field(None, max_length=20)
    descricao: Optional[str] = Field(None, max_length=500)

    # Tipo de servico
    servico_vigilancia: bool = False
    servico_limpeza: bool = False
    servico_locacao_mao_obra: bool = False
    servico_construcao_civil: bool = False

    # INSS (11%)
    inss_retido: bool = True
    inss_aliquota: Decimal = Field(Decimal("11.00"), ge=0, le=100)
    inss_base_minima: Optional[Decimal] = Field(None, ge=0)

    # Liminar INSS
    inss_liminar_ativa: bool = False
    inss_liminar_numero: Optional[str] = Field(None, max_length=50)
    inss_liminar_vara: Optional[str] = Field(None, max_length=100)
    inss_liminar_data: Optional[date] = None
    inss_liminar_validade: Optional[date] = None
    inss_liminar_texto: Optional[str] = Field(None, max_length=1000)

    # IR (1.5%)
    ir_retido: bool = True
    ir_aliquota: Decimal = Field(Decimal("1.50"), ge=0, le=100)
    ir_base_minima: Decimal = Field(Decimal("666.66"), ge=0)

    # CSLL (1%)
    csll_retido: bool = True
    csll_aliquota: Decimal = Field(Decimal("1.00"), ge=0, le=100)

    # PIS (0.65%)
    pis_retido: bool = True
    pis_aliquota: Decimal = Field(Decimal("0.65"), ge=0, le=100)

    # COFINS (3%)
    cofins_retido: bool = True
    cofins_aliquota: Decimal = Field(Decimal("3.00"), ge=0, le=100)

    # PCC base minima
    pcc_base_minima: Decimal = Field(Decimal("215.05"), ge=0)

    # ISS
    iss_retido: bool = False
    iss_aliquota: Optional[Decimal] = Field(None, ge=0, le=5)

    # Cliente especifico
    cliente_id: Optional[UUID] = None
    cliente_aceita_liminar: Optional[bool] = None

    # Vigencia
    valid_from: date = Field(default_factory=date.today)
    valid_until: Optional[date] = None


class RetencaoFederalCreate(RetencaoFederalBase):
    """Schema para criar configuracao de retencao."""

    condominio_id: UUID


class RetencaoFederalUpdate(BaseModel):
    """Schema para atualizar configuracao de retencao."""

    nome: Optional[str] = Field(None, max_length=100)
    descricao: Optional[str] = Field(None, max_length=500)
    servico_vigilancia: Optional[bool] = None
    servico_limpeza: Optional[bool] = None
    servico_locacao_mao_obra: Optional[bool] = None
    servico_construcao_civil: Optional[bool] = None
    inss_retido: Optional[bool] = None
    inss_aliquota: Optional[Decimal] = None
    inss_base_minima: Optional[Decimal] = None
    inss_liminar_ativa: Optional[bool] = None
    inss_liminar_numero: Optional[str] = None
    inss_liminar_vara: Optional[str] = None
    inss_liminar_data: Optional[date] = None
    inss_liminar_validade: Optional[date] = None
    inss_liminar_texto: Optional[str] = None
    ir_retido: Optional[bool] = None
    ir_aliquota: Optional[Decimal] = None
    ir_base_minima: Optional[Decimal] = None
    csll_retido: Optional[bool] = None
    csll_aliquota: Optional[Decimal] = None
    pis_retido: Optional[bool] = None
    pis_aliquota: Optional[Decimal] = None
    cofins_retido: Optional[bool] = None
    cofins_aliquota: Optional[Decimal] = None
    pcc_base_minima: Optional[Decimal] = None
    iss_retido: Optional[bool] = None
    iss_aliquota: Optional[Decimal] = None
    cliente_id: Optional[UUID] = None
    cliente_aceita_liminar: Optional[bool] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    active: Optional[bool] = None


class RetencaoFederalResponse(RetencaoFederalBase):
    """Response de configuracao de retencao."""

    id: UUID
    condominio_id: UUID
    aliquota_pcc: Decimal
    created_at: datetime
    updated_at: Optional[datetime]
    active: bool

    class Config:
        from_attributes = True


class RetencaoFederalListResponse(BaseModel):
    """Lista de configuracoes de retencao."""

    items: List[RetencaoFederalResponse]
    total: int


class CalculoRetencaoRequest(BaseModel):
    """Request para calculo de retencoes."""

    valor_servico: Decimal = Field(..., gt=0)
    retencao_id: Optional[UUID] = None
    cliente_aceita_liminar: bool = False
    tipo_servico: Optional[str] = None


class CalculoRetencaoResponse(BaseModel):
    """Response do calculo de retencoes."""

    valor_servico: Decimal
    inss: Decimal
    ir: Decimal
    csll: Decimal
    pis: Decimal
    cofins: Decimal
    iss: Decimal
    total: Decimal
    valor_liquido: Decimal
    liminar_aplicada: bool
    liminar_numero: Optional[str] = None
    detalhamento: Dict[str, Any]


# ============================================================
# NF-e Schemas
# ============================================================


class NFeItemBase(BaseModel):
    """Base para item de NF-e."""

    numero_item: int = Field(..., ge=1)
    produto_id: Optional[UUID] = None
    codigo_produto: str = Field(..., max_length=60)
    descricao: str = Field(..., max_length=120)
    ncm: str = Field(..., min_length=8, max_length=8)
    cfop: str = Field(..., min_length=4, max_length=4)

    unidade: str = Field(..., max_length=6)
    quantidade: Decimal = Field(..., gt=0)
    valor_unitario: Decimal = Field(..., gt=0)
    valor_total: Optional[Decimal] = None

    # Descontos/Acrescimos
    valor_desconto: Decimal = Field(Decimal("0"), ge=0)
    valor_frete: Decimal = Field(Decimal("0"), ge=0)
    valor_seguro: Decimal = Field(Decimal("0"), ge=0)
    valor_outros: Decimal = Field(Decimal("0"), ge=0)

    # ICMS
    icms_origem: str = Field("0", max_length=1)
    icms_cst: Optional[str] = Field(None, max_length=3)
    icms_csosn: Optional[str] = Field(None, max_length=3)
    icms_base_calculo: Decimal = Field(Decimal("0"), ge=0)
    icms_aliquota: Decimal = Field(Decimal("0"), ge=0, le=100)
    icms_valor: Decimal = Field(Decimal("0"), ge=0)

    # IPI
    ipi_cst: Optional[str] = Field(None, max_length=2)
    ipi_base_calculo: Decimal = Field(Decimal("0"), ge=0)
    ipi_aliquota: Decimal = Field(Decimal("0"), ge=0, le=100)
    ipi_valor: Decimal = Field(Decimal("0"), ge=0)

    # PIS
    pis_cst: Optional[str] = Field(None, max_length=2)
    pis_base_calculo: Decimal = Field(Decimal("0"), ge=0)
    pis_aliquota: Decimal = Field(Decimal("0"), ge=0, le=100)
    pis_valor: Decimal = Field(Decimal("0"), ge=0)

    # COFINS
    cofins_cst: Optional[str] = Field(None, max_length=2)
    cofins_base_calculo: Decimal = Field(Decimal("0"), ge=0)
    cofins_aliquota: Decimal = Field(Decimal("0"), ge=0, le=100)
    cofins_valor: Decimal = Field(Decimal("0"), ge=0)

    @validator("valor_total", always=True)
    def calculate_total(cls, v, values):
        """Calcula valor total do item se nao informado."""
        if v is None:
            qtd = values.get("quantidade", Decimal("0"))
            unit = values.get("valor_unitario", Decimal("0"))
            desc = values.get("valor_desconto", Decimal("0"))
            return (qtd * unit) - desc
        return v


class NFeItemCreate(NFeItemBase):
    """Schema para criar item de NF-e."""


class NFeItemResponse(NFeItemBase):
    """Response de item de NF-e."""

    id: UUID
    nfe_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class NFeBase(BaseModel):
    """Base para NF-e."""

    tipo: NFeTipoEnum = NFeTipoEnum.SAIDA
    finalidade: str = Field("1", max_length=1)  # 1-Normal, 2-Complementar, etc

    # Identificacao
    serie: int = Field(1, ge=1, le=999)
    numero: Optional[int] = Field(None, ge=1)
    natureza_operacao: str = Field(..., max_length=60)
    data_emissao: datetime = Field(default_factory=datetime.now)
    data_saida_entrada: Optional[datetime] = None

    # Emitente (pre-configurado ou informado)
    emitente_cnpj: str = Field(..., min_length=14, max_length=14)
    emitente_razao_social: str = Field(..., max_length=60)
    emitente_ie: Optional[str] = Field(None, max_length=14)
    emitente_uf: str = Field(..., min_length=2, max_length=2)
    emitente_crt: str = Field("1", max_length=1)  # 1-Simples, 2-SN Exc, 3-Normal

    # Destinatario
    destinatario_cpf_cnpj: str = Field(..., max_length=14)
    destinatario_razao_social: str = Field(..., max_length=60)
    destinatario_ie: Optional[str] = Field(None, max_length=14)
    destinatario_email: Optional[str] = Field(None, max_length=60)
    destinatario_uf: str = Field(..., min_length=2, max_length=2)
    destinatario_logradouro: str = Field(..., max_length=60)
    destinatario_numero: str = Field(..., max_length=60)
    destinatario_bairro: str = Field(..., max_length=60)
    destinatario_municipio: str = Field(..., max_length=60)
    destinatario_cep: str = Field(..., min_length=8, max_length=8)
    destinatario_telefone: Optional[str] = Field(None, max_length=14)

    # Frete
    modalidade_frete: str = Field("9", max_length=1)  # 0-Emit, 1-Dest, 9-SemFrete
    transportadora_cnpj: Optional[str] = Field(None, max_length=14)
    transportadora_razao_social: Optional[str] = Field(None, max_length=60)

    # Pagamento
    forma_pagamento: str = Field("0", max_length=2)  # 0-AVista, 1-APrazo
    meio_pagamento: str = Field("99", max_length=2)  # 01-Dinheiro, 99-Outros
    valor_pagamento: Optional[Decimal] = Field(None, ge=0)

    # Informacoes adicionais
    informacoes_complementares: Optional[str] = Field(None, max_length=5000)
    informacoes_fisco: Optional[str] = Field(None, max_length=2000)

    # Zona Franca
    is_zfm: bool = False
    suframa_destinatario: Optional[str] = Field(None, max_length=9)


class NFeCreate(NFeBase):
    """Schema para criar NF-e."""

    condominio_id: UUID
    itens: List[NFeItemCreate] = Field(..., min_items=1)


class NFeUpdate(BaseModel):
    """Schema para atualizar NF-e (apenas rascunho)."""

    natureza_operacao: Optional[str] = Field(None, max_length=60)
    data_saida_entrada: Optional[datetime] = None
    destinatario_email: Optional[str] = Field(None, max_length=60)
    modalidade_frete: Optional[str] = None
    informacoes_complementares: Optional[str] = None
    informacoes_fisco: Optional[str] = None


class NFeResponse(NFeBase):
    """Response de NF-e."""

    id: UUID
    condominio_id: UUID
    chave_acesso: Optional[str]
    status: NFeStatusEnum
    protocolo_autorizacao: Optional[str]
    data_autorizacao: Optional[datetime]
    motivo_rejeicao: Optional[str]

    # Totais
    valor_total_produtos: Decimal
    valor_total_icms: Decimal
    valor_total_ipi: Decimal
    valor_total_pis: Decimal
    valor_total_cofins: Decimal
    valor_total_frete: Decimal
    valor_total_seguro: Decimal
    valor_total_desconto: Decimal
    valor_total_outros: Decimal
    valor_total_nota: Decimal

    itens: List[NFeItemResponse]

    created_at: datetime
    updated_at: Optional[datetime]
    active: bool

    class Config:
        from_attributes = True


class NFeListResponse(BaseModel):
    """Lista de NF-e."""

    items: List[NFeResponse]
    total: int
    page: int
    page_size: int


class NFeFilter(BaseModel):
    """Filtro para busca de NF-e."""

    tipo: Optional[NFeTipoEnum] = None
    status: Optional[NFeStatusEnum] = None
    serie: Optional[int] = None
    numero_inicial: Optional[int] = None
    numero_final: Optional[int] = None
    data_emissao_inicial: Optional[date] = None
    data_emissao_final: Optional[date] = None
    destinatario_cpf_cnpj: Optional[str] = None
    chave_acesso: Optional[str] = None
    search: Optional[str] = None


class NFeEmitirRequest(BaseModel):
    """Request para emitir NF-e."""

    nfe_id: UUID
    ambiente: str = Field("2", description="1-Producao, 2-Homologacao")


class NFeEmitirResponse(BaseModel):
    """Response da emissao de NF-e."""

    nfe_id: UUID
    status: NFeStatusEnum
    chave_acesso: Optional[str]
    protocolo: Optional[str]
    mensagem: str
    xml_autorizado: Optional[str]
    pdf_danfe: Optional[str]


class NFeCancelarRequest(BaseModel):
    """Request para cancelar NF-e."""

    nfe_id: UUID
    justificativa: str = Field(..., min_length=15, max_length=255)


class NFeInutilizarRequest(BaseModel):
    """Request para inutilizar numeracao."""

    serie: int
    numero_inicial: int
    numero_final: int
    justificativa: str = Field(..., min_length=15, max_length=255)


# ============================================================
# NFS-e Schemas
# ============================================================


class NFSeBase(BaseModel):
    """Base para NFS-e."""

    # Identificacao
    numero_rps: Optional[int] = None
    serie_rps: str = Field("A", max_length=5)
    tipo_rps: str = Field("1", max_length=1)  # 1-RPS, 2-Cupom
    natureza_operacao: str = Field("1", max_length=1)  # 1-Tributada, 2-Isenta, etc
    regime_especial: Optional[str] = Field(None, max_length=1)

    data_emissao: datetime = Field(default_factory=datetime.now)
    data_competencia: date = Field(default_factory=date.today)

    # Prestador
    prestador_cnpj: str = Field(..., min_length=14, max_length=14)
    prestador_inscricao_municipal: Optional[str] = Field(None, max_length=15)
    prestador_razao_social: str = Field(..., max_length=150)

    # Tomador
    tomador_cpf_cnpj: str = Field(..., max_length=14)
    tomador_razao_social: str = Field(..., max_length=150)
    tomador_email: Optional[str] = Field(None, max_length=80)
    tomador_inscricao_municipal: Optional[str] = Field(None, max_length=15)
    tomador_logradouro: str = Field(..., max_length=125)
    tomador_numero: str = Field(..., max_length=10)
    tomador_complemento: Optional[str] = Field(None, max_length=60)
    tomador_bairro: str = Field(..., max_length=60)
    tomador_municipio: str = Field(..., max_length=60)
    tomador_uf: str = Field(..., min_length=2, max_length=2)
    tomador_cep: str = Field(..., min_length=8, max_length=8)
    tomador_telefone: Optional[str] = Field(None, max_length=20)

    # Servico
    codigo_servico: str = Field(..., max_length=20)  # LC 116
    descricao_servico: str = Field(..., max_length=2000)
    codigo_cnae: Optional[str] = Field(None, max_length=7)
    codigo_tributacao_municipio: Optional[str] = Field(None, max_length=20)

    # Valores
    valor_servicos: Decimal = Field(..., gt=0)
    valor_deducoes: Decimal = Field(Decimal("0"), ge=0)
    valor_desconto_condicionado: Decimal = Field(Decimal("0"), ge=0)
    valor_desconto_incondicionado: Decimal = Field(Decimal("0"), ge=0)

    # ISS
    iss_aliquota: Decimal = Field(..., ge=0, le=5)
    iss_valor: Optional[Decimal] = Field(None, ge=0)
    iss_retido: bool = False

    # Retencoes federais
    pis_valor: Decimal = Field(Decimal("0"), ge=0)
    cofins_valor: Decimal = Field(Decimal("0"), ge=0)
    inss_valor: Decimal = Field(Decimal("0"), ge=0)
    ir_valor: Decimal = Field(Decimal("0"), ge=0)
    csll_valor: Decimal = Field(Decimal("0"), ge=0)
    outras_retencoes: Decimal = Field(Decimal("0"), ge=0)

    # Liminar INSS
    inss_liminar_aplicada: bool = False
    inss_liminar_numero: Optional[str] = Field(None, max_length=50)
    inss_liminar_texto: Optional[str] = Field(None, max_length=500)

    # Informacoes adicionais
    discriminacao: Optional[str] = Field(None, max_length=2000)
    observacao: Optional[str] = Field(None, max_length=1000)


class NFSeCreate(NFSeBase):
    """Schema para criar NFS-e."""

    condominio_id: UUID


class NFSeUpdate(BaseModel):
    """Schema para atualizar NFS-e (apenas rascunho)."""

    tomador_email: Optional[str] = Field(None, max_length=80)
    descricao_servico: Optional[str] = Field(None, max_length=2000)
    discriminacao: Optional[str] = None
    observacao: Optional[str] = None


class NFSeResponse(NFSeBase):
    """Response de NFS-e."""

    id: UUID
    condominio_id: UUID
    status: NFSeStatusEnum
    numero_nfse: Optional[str]
    codigo_verificacao: Optional[str]
    link_nfse: Optional[str]
    protocolo: Optional[str]
    data_processamento: Optional[datetime]
    mensagem_retorno: Optional[str]

    # Valores calculados
    valor_liquido: Decimal
    total_retencoes: Decimal

    created_at: datetime
    updated_at: Optional[datetime]
    active: bool

    class Config:
        from_attributes = True


class NFSeListResponse(BaseModel):
    """Lista de NFS-e."""

    items: List[NFSeResponse]
    total: int
    page: int
    page_size: int


class NFSeFilter(BaseModel):
    """Filtro para busca de NFS-e."""

    status: Optional[NFSeStatusEnum] = None
    data_emissao_inicial: Optional[date] = None
    data_emissao_final: Optional[date] = None
    competencia_mes: Optional[int] = None
    competencia_ano: Optional[int] = None
    tomador_cpf_cnpj: Optional[str] = None
    codigo_servico: Optional[str] = None
    numero_nfse: Optional[str] = None
    search: Optional[str] = None


class NFSeEmitirRequest(BaseModel):
    """Request para emitir NFS-e."""

    nfse_id: UUID
    ambiente: str = Field("2", description="1-Producao, 2-Homologacao")


class NFSeEmitirResponse(BaseModel):
    """Response da emissao de NFS-e."""

    nfse_id: UUID
    status: NFSeStatusEnum
    numero_nfse: Optional[str]
    codigo_verificacao: Optional[str]
    link_nfse: Optional[str]
    protocolo: Optional[str]
    mensagem: str
    xml: Optional[str]
    pdf: Optional[str]


class NFSeCancelarRequest(BaseModel):
    """Request para cancelar NFS-e."""

    nfse_id: UUID
    codigo_cancelamento: str = Field(..., max_length=4)
    motivo_cancelamento: Optional[str] = Field(None, max_length=255)


# ============================================================
# SPED Schemas
# ============================================================


class SPEDFileBase(BaseModel):
    """Base para arquivo SPED."""

    tipo: SPEDTipoEnum
    ano: int = Field(..., ge=2000, le=2100)
    mes: Optional[int] = Field(None, ge=1, le=12)
    finalidade: str = Field("0", max_length=1)  # 0-Original, 1-Retificadora
    perfil: Optional[str] = Field(None, max_length=1)  # A, B, C


class SPEDFileCreate(SPEDFileBase):
    """Schema para criar arquivo SPED."""

    condominio_id: UUID


class SPEDFileResponse(SPEDFileBase):
    """Response de arquivo SPED."""

    id: UUID
    condominio_id: UUID
    status: SPEDStatusEnum
    nome_arquivo: Optional[str]
    hash_arquivo: Optional[str]
    tamanho_bytes: Optional[int]

    # Transmissao
    recibo_transmissao: Optional[str]
    data_transmissao: Optional[datetime]
    protocolo_entrega: Optional[str]
    data_processamento: Optional[datetime]

    # Erros
    total_erros: int
    total_avisos: int
    erros: Optional[List[Dict[str, Any]]]
    avisos: Optional[List[Dict[str, Any]]]

    # Resumo
    resumo: Optional[Dict[str, Any]]

    created_at: datetime
    updated_at: Optional[datetime]
    active: bool

    class Config:
        from_attributes = True


class SPEDFileListResponse(BaseModel):
    """Lista de arquivos SPED."""

    items: List[SPEDFileResponse]
    total: int
    page: int
    page_size: int


class SPEDFilter(BaseModel):
    """Filtro para busca de arquivos SPED."""

    tipo: Optional[SPEDTipoEnum] = None
    status: Optional[SPEDStatusEnum] = None
    ano: Optional[int] = None
    mes: Optional[int] = None


class SPEDGerarRequest(BaseModel):
    """Request para gerar arquivo SPED."""

    tipo: SPEDTipoEnum
    ano: int
    mes: Optional[int] = None
    finalidade: str = Field("0", description="0-Original, 1-Retificadora")


class SPEDValidarRequest(BaseModel):
    """Request para validar arquivo SPED."""

    sped_id: UUID


class SPEDTransmitirRequest(BaseModel):
    """Request para transmitir arquivo SPED."""

    sped_id: UUID
    ambiente: str = Field("2", description="1-Producao, 2-Homologacao")


# ============================================================
# Obrigacao Fiscal Schemas
# ============================================================


class ObrigacaoFiscalBase(BaseModel):
    """Base para obrigacao fiscal."""

    tipo: str = Field(..., max_length=30)  # DAS, DCTF, DIRF, EFD, etc
    nome: str = Field(..., max_length=100)
    descricao: Optional[str] = Field(None, max_length=500)
    competencia_mes: Optional[int] = Field(None, ge=1, le=12)
    competencia_ano: int = Field(..., ge=2000, le=2100)
    data_vencimento: date
    valor_devido: Optional[Decimal] = Field(None, ge=0)


class ObrigacaoFiscalCreate(ObrigacaoFiscalBase):
    """Schema para criar obrigacao fiscal."""

    condominio_id: UUID


class ObrigacaoFiscalUpdate(BaseModel):
    """Schema para atualizar obrigacao fiscal."""

    data_vencimento: Optional[date] = None
    valor_devido: Optional[Decimal] = None
    valor_pago: Optional[Decimal] = None
    data_pagamento: Optional[date] = None
    numero_recibo: Optional[str] = None
    observacoes: Optional[str] = None
    status: Optional[ObrigacaoStatusEnum] = None


class ObrigacaoFiscalResponse(ObrigacaoFiscalBase):
    """Response de obrigacao fiscal."""

    id: UUID
    condominio_id: UUID
    status: ObrigacaoStatusEnum
    valor_pago: Optional[Decimal]
    data_pagamento: Optional[date]
    numero_recibo: Optional[str]
    observacoes: Optional[str]
    dias_para_vencimento: int
    is_atrasada: bool

    created_at: datetime
    updated_at: Optional[datetime]
    active: bool

    class Config:
        from_attributes = True


class ObrigacaoFiscalListResponse(BaseModel):
    """Lista de obrigacoes fiscais."""

    items: List[ObrigacaoFiscalResponse]
    total: int
    proximas_a_vencer: int
    atrasadas: int


class ObrigacaoFilter(BaseModel):
    """Filtro para busca de obrigacoes."""

    tipo: Optional[str] = None
    status: Optional[ObrigacaoStatusEnum] = None
    mes: Optional[int] = None
    ano: Optional[int] = None
    vencimento_inicio: Optional[date] = None
    vencimento_fim: Optional[date] = None


# ============================================================
# Simples Nacional / DAS Schemas
# ============================================================


class SimplesNacionalDASBase(BaseModel):
    """Base para DAS do Simples Nacional."""

    competencia_mes: int = Field(..., ge=1, le=12)
    competencia_ano: int = Field(..., ge=2000, le=2100)
    data_vencimento: date

    # Receita
    receita_bruta_mes: Decimal = Field(..., ge=0)
    receita_bruta_12_meses: Decimal = Field(..., ge=0)

    # Faixa e aliquota
    anexo: str = Field("III", max_length=5)  # III para vigilancia
    faixa: int = Field(..., ge=1, le=6)
    aliquota_nominal: Decimal = Field(..., ge=0, le=100)
    aliquota_efetiva: Decimal = Field(..., ge=0, le=100)
    parcela_deduzir: Decimal = Field(..., ge=0)

    # Valor
    valor_devido: Decimal = Field(..., ge=0)


class SimplesNacionalDASCreate(SimplesNacionalDASBase):
    """Schema para criar DAS."""

    condominio_id: UUID


class SimplesNacionalDASResponse(SimplesNacionalDASBase):
    """Response de DAS."""

    id: UUID
    condominio_id: UUID
    status: ObrigacaoStatusEnum
    numero_documento: Optional[str]
    codigo_barras: Optional[str]
    valor_pago: Optional[Decimal]
    data_pagamento: Optional[date]
    numero_recibo: Optional[str]

    # Reparticao tributos
    reparticao_irpj: Optional[Decimal]
    reparticao_csll: Optional[Decimal]
    reparticao_cofins: Optional[Decimal]
    reparticao_pis: Optional[Decimal]
    reparticao_cpp: Optional[Decimal]
    reparticao_iss: Optional[Decimal]

    created_at: datetime
    updated_at: Optional[datetime]
    active: bool

    class Config:
        from_attributes = True


class DASCalcularRequest(BaseModel):
    """Request para calcular DAS."""

    receita_bruta_mes: Decimal
    receita_bruta_12_meses: Decimal
    anexo: str = Field("III", description="III, IV ou V")
    competencia_mes: int
    competencia_ano: int


class DASCalcularResponse(BaseModel):
    """Response do calculo do DAS."""

    faixa: int
    aliquota_nominal: Decimal
    parcela_deduzir: Decimal
    aliquota_efetiva: Decimal
    valor_devido: Decimal
    reparticao: Dict[str, Decimal]
    data_vencimento: date


# ============================================================
# SUFRAMA / Zona Franca Schemas
# ============================================================


class SUFRAMAConfigBase(BaseModel):
    """Base para configuracao SUFRAMA."""

    inscricao_suframa: str = Field(..., max_length=9)
    data_validade: date
    tipo_incentivo: str = Field(..., max_length=20)

    # Beneficios
    isento_ipi: bool = True
    reducao_icms: bool = True
    percentual_reducao_icms: Decimal = Field(Decimal("100"), ge=0, le=100)
    suspensao_pis_cofins: bool = True

    # Produtos incentivados
    ncms_incentivados: Optional[List[str]] = None


class SUFRAMAConfigCreate(SUFRAMAConfigBase):
    """Schema para criar config SUFRAMA."""

    condominio_id: UUID


class SUFRAMAConfigResponse(SUFRAMAConfigBase):
    """Response de config SUFRAMA."""

    id: UUID
    condominio_id: UUID
    is_vigente: bool
    dias_para_vencimento: int

    created_at: datetime
    updated_at: Optional[datetime]
    active: bool

    class Config:
        from_attributes = True


class SUFRAMAOperacaoBase(BaseModel):
    """Base para operacao com beneficio SUFRAMA."""

    nfe_id: Optional[UUID] = None
    data_operacao: date
    valor_operacao: Decimal = Field(..., gt=0)
    valor_ipi_desonerado: Decimal = Field(Decimal("0"), ge=0)
    valor_icms_desonerado: Decimal = Field(Decimal("0"), ge=0)
    valor_pis_suspenso: Decimal = Field(Decimal("0"), ge=0)
    valor_cofins_suspenso: Decimal = Field(Decimal("0"), ge=0)

    # PIN (Protocolo de Ingresso)
    numero_pin: Optional[str] = Field(None, max_length=20)
    data_pin: Optional[date] = None
    status_pin: Optional[str] = Field(None, max_length=20)


class SUFRAMAOperacaoCreate(SUFRAMAOperacaoBase):
    """Schema para criar operacao SUFRAMA."""

    condominio_id: UUID


class SUFRAMAOperacaoResponse(SUFRAMAOperacaoBase):
    """Response de operacao SUFRAMA."""

    id: UUID
    condominio_id: UUID
    total_economia: Decimal

    created_at: datetime
    active: bool

    class Config:
        from_attributes = True


class SUFRAMAOperacaoListResponse(BaseModel):
    """Lista de operacoes SUFRAMA."""

    items: List[SUFRAMAOperacaoResponse]
    total: int
    total_economia_ipi: Decimal
    total_economia_icms: Decimal
    total_economia_pis_cofins: Decimal


# ============================================================
# AI Service Schemas
# ============================================================


class FiscalAIAnalyseRequest(BaseModel):
    """Request para analise fiscal por IA."""

    periodo_inicio: date
    periodo_fim: date
    incluir_nfe: bool = True
    incluir_nfse: bool = True
    incluir_retencoes: bool = True
    incluir_obrigacoes: bool = True


class FiscalAIAnalyseResponse(BaseModel):
    """Response da analise fiscal por IA."""

    resumo_periodo: Dict[str, Any]
    alertas: List[Dict[str, Any]]
    oportunidades: List[Dict[str, Any]]
    pendencias: List[Dict[str, Any]]
    recomendacoes: List[str]
    score_compliance: int  # 0-100
    projecao_impostos: Dict[str, Decimal]


class FiscalAIOptimizeRequest(BaseModel):
    """Request para otimizacao tributaria por IA."""

    receita_mensal_media: Decimal
    tipo_servico: str
    uf_operacao: str
    simula_regimes: bool = True


class FiscalAIOptimizeResponse(BaseModel):
    """Response da otimizacao tributaria."""

    regime_atual: str
    carga_tributaria_atual: Decimal
    regimes_simulados: List[Dict[str, Any]]
    melhor_regime: str
    economia_potencial: Decimal
    acoes_recomendadas: List[str]


class FiscalAIPredictRequest(BaseModel):
    """Request para previsao de obrigacoes."""

    meses_projecao: int = Field(6, ge=1, le=12)


class FiscalAIPredictResponse(BaseModel):
    """Response da previsao de obrigacoes."""

    projecao_mensal: List[Dict[str, Any]]
    total_previsto: Decimal
    obrigacoes_futuras: List[Dict[str, Any]]
    alertas_vencimento: List[Dict[str, Any]]


# ============================================================
# Stats e Dashboard
# ============================================================


class FiscalStats(BaseModel):
    """Estatisticas fiscais."""

    # NF-e
    total_nfe_emitidas: int
    total_nfe_mes: int
    valor_total_nfe_mes: Decimal

    # NFS-e
    total_nfse_emitidas: int
    total_nfse_mes: int
    valor_total_nfse_mes: Decimal

    # Retencoes
    total_retencoes_mes: Decimal
    economia_liminar_inss: Decimal

    # Obrigacoes
    obrigacoes_pendentes: int
    obrigacoes_atrasadas: int
    proxima_obrigacao: Optional[Dict[str, Any]]

    # Simples Nacional
    das_mes_atual: Optional[Decimal]
    faixa_atual: Optional[int]
    receita_12_meses: Optional[Decimal]

    # SUFRAMA
    economia_zfm_mes: Optional[Decimal]
    economia_zfm_ano: Optional[Decimal]


class FiscalDashboard(BaseModel):
    """Dashboard fiscal completo."""

    stats: FiscalStats
    notas_recentes: List[Dict[str, Any]]
    obrigacoes_proximas: List[Dict[str, Any]]
    alertas: List[Dict[str, Any]]
    grafico_impostos: List[Dict[str, Any]]
    grafico_notas: List[Dict[str, Any]]

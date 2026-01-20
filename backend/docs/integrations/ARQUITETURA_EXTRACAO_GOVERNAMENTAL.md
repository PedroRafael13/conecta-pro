# ARQUITETURA DE EXTRAÇÃO DE DADOS GOVERNAMENTAIS
## Conecta PRO - Documento Operacional v1.0

**Data:** 2026-01-16
**Versão:** 1.0.0
**Status:** Operacional
**Responsável:** Equipe de Integração Governamental

---

## SUMÁRIO EXECUTIVO

Este documento define a arquitetura completa para extração, transformação e carga (ETL) de dados de órgãos governamentais no Conecta PRO. Estabelece diretrizes claras sobre:

- **O que é automatizável** vs **O que requer ação manual**
- **Processos ETL** e normalização de dados
- **Gestão de erros** e estratégias de fallback
- **Escalabilidade** e controle de concorrência
- **Governança de credenciais** e segurança
- **Auditoria** e compliance (LGPD/fiscal)
- **Integração** com módulos internos do ERP

---

## 1. MAPEAMENTO DE DISPONIBILIDADE DE APIs

### 1.1 Matriz de Disponibilidade - Serviços Federais

| Serviço | API Disponível | Tipo de Acesso | Automatizável | Observações |
|---------|---------------|----------------|---------------|-------------|
| **eSocial** | ✅ Sim | WebService SOAP + Certificado | ✅ Total | Eventos S-1000 a S-5013 |
| **EFD-Reinf** | ✅ Sim | WebService SOAP + Certificado | ✅ Total | R-1000 a R-9000 |
| **DCTFWeb** | ✅ Sim | WebService REST + Gov.br | ✅ Total | Consolidação automática |
| **FGTS Digital** | ✅ Sim | WebService REST + Certificado | ✅ Total | Substituiu SEFIP |
| **Simples Nacional (PGDAS-D)** | ✅ Sim | WebService + Certificado | ✅ Total | Cálculo e DAS |
| **SPED Fiscal (EFD ICMS/IPI)** | ⚠️ Parcial | Arquivo TXT + Validador | ⚠️ Geração | Upload manual no PVA |
| **SPED Contábil (ECD)** | ⚠️ Parcial | Arquivo TXT + Validador | ⚠️ Geração | Upload manual no PVA |
| **e-CAC (Situação Fiscal)** | ✅ Sim | Scraping + Gov.br | ⚠️ Parcial | Sem API oficial para guias |
| **NFS-e Nacional** | ✅ Sim | WebService REST + Certificado | ✅ Total | Padrão nacional 2024 |

### 1.2 Matriz de Disponibilidade - SEFAZ por UF (NF-e/NFC-e)

| UF | SEFAZ Própria | Contingência | NF-e API | NFC-e API | CT-e | MDF-e |
|----|---------------|--------------|----------|-----------|------|-------|
| **AM** | ✅ sefaz.am.gov.br | SVC-AN | ✅ | ✅ | SVRS | SVRS |
| **BA** | ✅ sefaz.ba.gov.br | SVC-AN | ✅ | ✅ | ✅ | ✅ |
| **GO** | ✅ sefaz.go.gov.br | SVC-RS | ✅ | ✅ | SVRS | SVRS |
| **MG** | ✅ fazenda.mg.gov.br | SVC-AN | ✅ | ✅ | ✅ | SVRS |
| **MS** | ✅ sefaz.ms.gov.br | SVC-RS | ✅ | ✅ | SVRS | SVRS |
| **MT** | ✅ sefaz.mt.gov.br | SVC-RS | ✅ | ✅ | SVRS | SVRS |
| **PE** | ✅ sefaz.pe.gov.br | SVC-AN | ✅ | ✅ | SVRS | SVRS |
| **PR** | ✅ sefa.pr.gov.br | SVC-RS | ✅ | ✅ | ✅ | SVRS |
| **RS** | ✅ sefaz.rs.gov.br | SVC-AN | ✅ | ✅ | ✅ | ✅ |
| **SP** | ✅ fazenda.sp.gov.br | SVC-AN | ✅ | ✅ | ✅ | SVRS |
| **Demais UFs** | SVRS/SVAN | - | ✅ | ✅ | SVRS | SVRS |

**Legenda:**
- **SVRS**: SEFAZ Virtual Rio Grande do Sul (CT-e/MDF-e)
- **SVAN**: SEFAZ Virtual Ambiente Nacional
- **SVC-AN**: Contingência Ambiente Nacional
- **SVC-RS**: Contingência Rio Grande do Sul

### 1.3 Matriz de Disponibilidade - Serviços Municipais

| Município | Padrão NFS-e | API Disponível | Automatizável |
|-----------|--------------|----------------|---------------|
| **Manaus/AM** | ABRASF 2.04 | ✅ WebService SOAP | ✅ Total |
| **São Paulo/SP** | Próprio | ✅ WebService SOAP | ✅ Total |
| **Rio de Janeiro/RJ** | NOTA CARIOCA | ✅ WebService SOAP | ✅ Total |
| **Belo Horizonte/MG** | ABRASF | ✅ WebService SOAP | ✅ Total |
| **Outros (até 2026)** | Nacional | ✅ WebService REST | ✅ Total |

### 1.4 Serviços SEM API - Ação Manual Obrigatória

```yaml
SERVICOS_SEM_API:
  - nome: "DARFs via e-CAC"
    motivo: "Não há API pública para download de guias geradas"
    workaround: "Usuário deve baixar manualmente e fazer upload no sistema"

  - nome: "SPED PVA Upload"
    motivo: "Validador PVA não aceita transmissão programática"
    workaround: "Sistema gera arquivo TXT; usuário faz upload manual"

  - nome: "Parcelamentos PGFN"
    motivo: "Requer interação humana para negociação"
    workaround: "Sistema alerta sobre débitos; ação manual no portal"

  - nome: "Certidões com Pendências"
    motivo: "Regularização requer análise humana"
    workaround: "Sistema monitora e alerta; regularização manual"
```

### 1.5 Mecanismo de Alerta para APIs Indisponíveis

```python
# Implementação em modules/government_integrations/core/availability.py

from enum import Enum
from typing import Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class DisponibilidadeAPI(Enum):
    DISPONIVEL = "disponivel"
    PARCIAL = "parcial"
    INDISPONIVEL = "indisponivel"
    MANUAL = "manual"

@dataclass
class StatusAPI:
    servico: str
    disponibilidade: DisponibilidadeAPI
    mensagem: str
    acao_necessaria: Optional[str] = None

# Registro de serviços
REGISTRO_DISPONIBILIDADE = {
    "darf_ecac": StatusAPI(
        servico="DARF via e-CAC",
        disponibilidade=DisponibilidadeAPI.MANUAL,
        mensagem="API não disponível - ação manual necessária",
        acao_necessaria="Acesse o e-CAC para baixar as guias manualmente"
    ),
    "sped_upload": StatusAPI(
        servico="SPED PVA Upload",
        disponibilidade=DisponibilidadeAPI.MANUAL,
        mensagem="Upload automatizado não suportado pelo PVA",
        acao_necessaria="Faça upload do arquivo gerado no Validador PVA"
    ),
}

def verificar_disponibilidade(servico: str) -> StatusAPI:
    """Verifica disponibilidade de API e retorna status."""
    if servico in REGISTRO_DISPONIBILIDADE:
        status = REGISTRO_DISPONIBILIDADE[servico]
        if status.disponibilidade == DisponibilidadeAPI.MANUAL:
            logger.warning(
                f"[API INDISPONÍVEL] {status.servico}: {status.mensagem}. "
                f"Ação: {status.acao_necessaria}"
            )
        return status
    return StatusAPI(
        servico=servico,
        disponibilidade=DisponibilidadeAPI.DISPONIVEL,
        mensagem="API disponível para automação"
    )
```

---

## 2. ETL - EXTRAÇÃO, TRANSFORMAÇÃO E CARGA

### 2.1 Arquitetura ETL

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FONTES DE DADOS                               │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────┤
│   SEFAZ     │   eSocial   │  FGTS Dig.  │   NFS-e     │   SPED      │
│  (XML/SOAP) │ (XML/SOAP)  │   (REST)    │   (SOAP)    │   (TXT)     │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┘
       │             │             │             │             │
       ▼             ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CAMADA DE EXTRAÇÃO                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │ XML Parser  │  │ REST Client │  │ TXT Parser  │                  │
│  │ + XSD Valid │  │ + OAuth 2.0 │  │ + Validador │                  │
│  └─────────────┘  └─────────────┘  └─────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   CAMADA DE TRANSFORMAÇÃO                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  • Normalização de campos (CNPJ, CPF, datas, valores)       │    │
│  │  • Validação de schema (XSD)                                │    │
│  │  • De-duplicação (chave única por tipo de documento)        │    │
│  │  • Versionamento (documentos retificados)                   │    │
│  │  • Enriquecimento (lookup de participantes)                 │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CAMADA DE CARGA                                 │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  PostgreSQL: Dados estruturados + JSONB para metadados      │    │
│  │  Redis: Cache de consultas frequentes + Rate limit          │    │
│  │  S3/MinIO: XMLs originais + PDFs de guias                   │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Mapeamento de Campos por Tipo de Documento

#### 2.2.1 NF-e / NFC-e

```python
# Mapeamento XML SEFAZ → Modelo Interno
MAPEAMENTO_NFE = {
    # Identificação
    "ide/cUF": "uf_codigo",
    "ide/cNF": "codigo_numerico",
    "ide/natOp": "natureza_operacao",
    "ide/mod": "modelo",  # 55=NF-e, 65=NFC-e
    "ide/serie": "serie",
    "ide/nNF": "numero",
    "ide/dhEmi": "data_emissao",
    "ide/tpNF": "tipo",  # 0=Entrada, 1=Saída

    # Emitente
    "emit/CNPJ": "emitente_cnpj",
    "emit/xNome": "emitente_razao_social",
    "emit/IE": "emitente_ie",

    # Destinatário
    "dest/CNPJ": "destinatario_cnpj",
    "dest/CPF": "destinatario_cpf",
    "dest/xNome": "destinatario_nome",

    # Totais
    "total/ICMSTot/vNF": "valor_total",
    "total/ICMSTot/vProd": "valor_produtos",
    "total/ICMSTot/vDesc": "valor_desconto",
    "total/ICMSTot/vFrete": "valor_frete",
    "total/ICMSTot/vICMS": "valor_icms",
    "total/ICMSTot/vIPI": "valor_ipi",
    "total/ICMSTot/vPIS": "valor_pis",
    "total/ICMSTot/vCOFINS": "valor_cofins",

    # Protocolo
    "protNFe/infProt/nProt": "protocolo",
    "protNFe/infProt/dhRecbto": "data_autorizacao",
    "protNFe/infProt/cStat": "codigo_status",

    # Chave de acesso (identificador único)
    "@chave_acesso": "chave_acesso",  # 44 dígitos
}

# Chave única para de-duplicação
CHAVE_UNICA_NFE = ["chave_acesso"]
```

#### 2.2.2 eSocial

```python
MAPEAMENTO_ESOCIAL = {
    # Identificação do evento
    "evtInfoEmpregador/ideEvento/tpAmb": "ambiente",
    "evtInfoEmpregador/ideEvento/procEmi": "processo_emissao",
    "evtInfoEmpregador/ideEmpregador/tpInsc": "tipo_inscricao",
    "evtInfoEmpregador/ideEmpregador/nrInsc": "cnpj_empregador",

    # Recibo (identificador único)
    "recibo/nrRecibo": "numero_recibo",
    "recibo/dhRecepcao": "data_recepcao",

    # Tipo de evento
    "@tipoEvento": "tipo_evento",  # S-1000, S-1200, etc.
    "@idEvento": "id_evento",
}

# Chave única para de-duplicação
CHAVE_UNICA_ESOCIAL = ["id_evento", "numero_recibo"]
```

#### 2.2.3 FGTS Digital

```python
MAPEAMENTO_FGTS = {
    # Identificação
    "trabalhador/cpf": "trabalhador_cpf",
    "trabalhador/pis": "trabalhador_pis",
    "trabalhador/nome": "trabalhador_nome",

    # Competência
    "competencia/anoMes": "competencia",  # AAAAMM

    # Valores
    "remuneracao/valor": "remuneracao_bruta",
    "fgts/baseCalculo": "base_calculo_fgts",
    "fgts/valorDeposito": "valor_fgts",
    "fgts/valorMulta": "valor_multa_rescisoria",

    # Guia
    "guia/codigoBarras": "codigo_barras",
    "guia/dataVencimento": "data_vencimento",
    "guia/valorTotal": "valor_guia",
}

CHAVE_UNICA_FGTS = ["trabalhador_cpf", "competencia"]
```

### 2.3 Regras de De-duplicação

```python
from sqlalchemy import select, and_
from sqlalchemy.dialects.postgresql import insert

class DeduplicadorDocumentos:
    """Gerencia de-duplicação de documentos fiscais."""

    REGRAS_DEDUP = {
        "nfe": {
            "campos_chave": ["chave_acesso"],
            "tabela": "documentos_fiscais_nfe",
        },
        "nfse": {
            "campos_chave": ["numero_nfse", "cnpj_prestador", "codigo_municipio"],
            "tabela": "documentos_fiscais_nfse",
        },
        "esocial": {
            "campos_chave": ["id_evento", "numero_recibo"],
            "tabela": "eventos_esocial",
        },
        "cte": {
            "campos_chave": ["chave_acesso"],
            "tabela": "documentos_fiscais_cte",
        },
        "mdfe": {
            "campos_chave": ["chave_acesso"],
            "tabela": "documentos_fiscais_mdfe",
        },
    }

    async def inserir_ou_atualizar(
        self,
        tipo_documento: str,
        dados: dict,
        db_session
    ) -> dict:
        """
        Insere novo documento ou atualiza existente.
        Retorna: {"acao": "inserido"|"atualizado"|"ignorado", "id": ...}
        """
        regra = self.REGRAS_DEDUP[tipo_documento]

        # Construir condição de unicidade
        chave = {campo: dados[campo] for campo in regra["campos_chave"]}

        # Usar UPSERT do PostgreSQL
        stmt = insert(regra["tabela"]).values(**dados)
        stmt = stmt.on_conflict_do_update(
            index_elements=regra["campos_chave"],
            set_={
                **{k: v for k, v in dados.items() if k not in regra["campos_chave"]},
                "updated_at": func.now(),
                "versao": stmt.excluded.versao + 1,
            }
        ).returning(literal_column("*"))

        result = await db_session.execute(stmt)
        return result.fetchone()
```

### 2.4 Versionamento de Documentos Retificados

```sql
-- Tabela de histórico de versões
CREATE TABLE documentos_historico (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    documento_id UUID NOT NULL REFERENCES documentos_fiscais(id),
    versao INTEGER NOT NULL,
    dados_anteriores JSONB NOT NULL,
    motivo_alteracao VARCHAR(255),
    usuario_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Índice para consultas por documento
    CONSTRAINT idx_doc_versao UNIQUE (documento_id, versao)
);

-- Flag de versão ativa na tabela principal
ALTER TABLE documentos_fiscais ADD COLUMN versao_ativa BOOLEAN DEFAULT TRUE;
ALTER TABLE documentos_fiscais ADD COLUMN versao INTEGER DEFAULT 1;

-- Trigger para histórico automático
CREATE OR REPLACE FUNCTION fn_historico_documento()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND OLD.* IS DISTINCT FROM NEW.* THEN
        INSERT INTO documentos_historico (
            documento_id, versao, dados_anteriores, motivo_alteracao
        ) VALUES (
            OLD.id, OLD.versao, to_jsonb(OLD), 'Retificação'
        );
        NEW.versao := OLD.versao + 1;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_historico_documento
BEFORE UPDATE ON documentos_fiscais
FOR EACH ROW EXECUTE FUNCTION fn_historico_documento();
```

### 2.5 Validação de Schema XSD

```python
from lxml import etree
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ValidadorXSD:
    """Valida XMLs contra schemas XSD oficiais."""

    XSD_PATHS = {
        "nfe_4.00": "/opt/conecta-pro/schemas/nfe/nfe_v4.00.xsd",
        "cte_4.00": "/opt/conecta-pro/schemas/cte/cte_v4.00.xsd",
        "mdfe_3.00": "/opt/conecta-pro/schemas/mdfe/mdfe_v3.00.xsd",
        "esocial_s1.2": "/opt/conecta-pro/schemas/esocial/evtInfoEmpregador_v_S_01_02_00.xsd",
    }

    _schemas_cache: dict = {}

    @classmethod
    def _carregar_schema(cls, tipo: str) -> etree.XMLSchema:
        """Carrega e cacheia schema XSD."""
        if tipo not in cls._schemas_cache:
            xsd_path = Path(cls.XSD_PATHS[tipo])
            if not xsd_path.exists():
                raise FileNotFoundError(f"Schema não encontrado: {xsd_path}")

            with open(xsd_path, "rb") as f:
                xsd_doc = etree.parse(f)
                cls._schemas_cache[tipo] = etree.XMLSchema(xsd_doc)

        return cls._schemas_cache[tipo]

    @classmethod
    def validar(cls, xml_content: bytes, tipo: str) -> tuple[bool, list[str]]:
        """
        Valida XML contra XSD.
        Retorna: (valido, lista_de_erros)
        """
        try:
            schema = cls._carregar_schema(tipo)
            xml_doc = etree.fromstring(xml_content)

            if schema.validate(xml_doc):
                return True, []
            else:
                erros = [str(e) for e in schema.error_log]
                logger.warning(f"XML inválido ({tipo}): {erros}")
                return False, erros

        except etree.XMLSyntaxError as e:
            return False, [f"Erro de sintaxe XML: {e}"]
        except Exception as e:
            return False, [f"Erro na validação: {e}"]
```

### 2.6 Normalização de Dados

```python
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
import re

class NormalizadorDados:
    """Normaliza dados para padrão interno."""

    @staticmethod
    def normalizar_cnpj(cnpj: str) -> str:
        """Remove formatação e valida CNPJ."""
        if not cnpj:
            return None
        return re.sub(r'\D', '', cnpj).zfill(14)

    @staticmethod
    def normalizar_cpf(cpf: str) -> str:
        """Remove formatação e valida CPF."""
        if not cpf:
            return None
        return re.sub(r'\D', '', cpf).zfill(11)

    @staticmethod
    def normalizar_data(data: str) -> datetime:
        """
        Converte data para ISO 8601 com timezone.
        Aceita formatos: YYYY-MM-DD, DD/MM/YYYY, YYYY-MM-DDTHH:MM:SS
        """
        if not data:
            return None

        # Já é datetime
        if isinstance(data, datetime):
            return data
        if isinstance(data, date):
            return datetime.combine(data, datetime.min.time())

        # Tentar formatos comuns
        formatos = [
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d/%m/%Y %H:%M:%S",
        ]

        for fmt in formatos:
            try:
                return datetime.strptime(data.strip(), fmt)
            except ValueError:
                continue

        raise ValueError(f"Formato de data não reconhecido: {data}")

    @staticmethod
    def normalizar_valor(valor: str | float | Decimal) -> Decimal:
        """
        Converte valor para Decimal com 2 casas.
        Remove separadores de milhar e normaliza decimal.
        """
        if valor is None:
            return Decimal("0.00")

        if isinstance(valor, Decimal):
            return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if isinstance(valor, (int, float)):
            return Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # String: remover formatação brasileira
        valor_str = str(valor).strip()
        valor_str = valor_str.replace(".", "").replace(",", ".")

        return Decimal(valor_str).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def normalizar_ie(ie: str, uf: str) -> str:
        """Normaliza Inscrição Estadual por UF."""
        if not ie or ie.upper() == "ISENTO":
            return "ISENTO"
        return re.sub(r'\D', '', ie)
```

---

## 3. GERENCIAMENTO DE ERROS E FALLBACK

### 3.1 Categorização de Erros

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)

class CategoriaErro(Enum):
    """Categorias de erro para tratamento diferenciado."""
    AUTENTICACAO = "autenticacao"      # Token/certificado inválido
    CERTIFICADO = "certificado"        # Certificado vencido/inválido
    TIMEOUT = "timeout"                # Serviço não respondeu
    INDISPONIVEL = "indisponivel"      # Serviço fora do ar
    SCHEMA = "schema"                  # XML/dados inválidos
    NEGOCIO = "negocio"                # Regra de negócio violada
    REDE = "rede"                      # Erro de conexão
    DESCONHECIDO = "desconhecido"      # Outros

@dataclass
class ErroIntegracao:
    """Estrutura padronizada de erro."""
    categoria: CategoriaErro
    codigo: str
    mensagem: str
    servico: str
    tentativas: int = 0
    pode_retentar: bool = True
    acao_recomendada: Optional[str] = None
    dados_adicionais: Optional[dict] = None

class ClassificadorErros:
    """Classifica erros e determina ação apropriada."""

    PADROES_ERRO = {
        CategoriaErro.AUTENTICACAO: [
            "token expired", "invalid_token", "unauthorized",
            "401", "403", "token inválido", "sessão expirada"
        ],
        CategoriaErro.CERTIFICADO: [
            "certificate", "ssl", "x509", "certificado vencido",
            "bad certificate", "certificate expired"
        ],
        CategoriaErro.TIMEOUT: [
            "timeout", "timed out", "tempo limite", "deadline exceeded"
        ],
        CategoriaErro.INDISPONIVEL: [
            "503", "502", "504", "service unavailable",
            "connection refused", "host unreachable"
        ],
        CategoriaErro.SCHEMA: [
            "xml", "xsd", "schema", "validation", "parse error",
            "malformed", "invalid format"
        ],
        CategoriaErro.NEGOCIO: [
            "rejeição", "rejeitado", "não autorizado",
            "duplicado", "já existe", "não encontrado"
        ],
    }

    @classmethod
    def classificar(cls, erro: Exception, servico: str) -> ErroIntegracao:
        """Classifica erro e retorna estrutura padronizada."""
        erro_str = str(erro).lower()

        # Identificar categoria
        categoria = CategoriaErro.DESCONHECIDO
        for cat, padroes in cls.PADROES_ERRO.items():
            if any(p in erro_str for p in padroes):
                categoria = cat
                break

        # Determinar se pode retentar
        pode_retentar = categoria in [
            CategoriaErro.TIMEOUT,
            CategoriaErro.INDISPONIVEL,
            CategoriaErro.REDE,
        ]

        # Definir ação recomendada
        acoes = {
            CategoriaErro.AUTENTICACAO: "Renovar token automaticamente",
            CategoriaErro.CERTIFICADO: "CRÍTICO: Suspender serviço e alertar admin",
            CategoriaErro.TIMEOUT: "Aplicar retry com backoff exponencial",
            CategoriaErro.INDISPONIVEL: "Tentar endpoint de contingência",
            CategoriaErro.SCHEMA: "Marcar para reprocessamento manual",
            CategoriaErro.NEGOCIO: "Registrar e notificar usuário",
        }

        return ErroIntegracao(
            categoria=categoria,
            codigo=type(erro).__name__,
            mensagem=str(erro)[:500],
            servico=servico,
            pode_retentar=pode_retentar,
            acao_recomendada=acoes.get(categoria),
        )
```

### 3.2 Estratégia de Retry com Backoff Exponencial

```python
import asyncio
from typing import TypeVar, Callable, Awaitable
from functools import wraps
import random

T = TypeVar('T')

class RetryConfig:
    """Configuração de retry por serviço."""

    CONFIGS = {
        "sefaz": {"max_tentativas": 3, "base_delay": 2.0, "max_delay": 60.0},
        "esocial": {"max_tentativas": 5, "base_delay": 5.0, "max_delay": 120.0},
        "fgts_digital": {"max_tentativas": 3, "base_delay": 3.0, "max_delay": 30.0},
        "nfse": {"max_tentativas": 3, "base_delay": 2.0, "max_delay": 30.0},
        "default": {"max_tentativas": 3, "base_delay": 1.0, "max_delay": 30.0},
    }

    @classmethod
    def get(cls, servico: str) -> dict:
        return cls.CONFIGS.get(servico, cls.CONFIGS["default"])

async def retry_com_backoff(
    func: Callable[..., Awaitable[T]],
    *args,
    servico: str = "default",
    **kwargs
) -> T:
    """
    Executa função com retry e backoff exponencial.

    Fórmula: delay = min(base_delay * (2 ** tentativa) + jitter, max_delay)
    """
    config = RetryConfig.get(servico)
    max_tentativas = config["max_tentativas"]
    base_delay = config["base_delay"]
    max_delay = config["max_delay"]

    ultimo_erro = None

    for tentativa in range(max_tentativas):
        try:
            return await func(*args, **kwargs)

        except Exception as e:
            ultimo_erro = e
            erro_info = ClassificadorErros.classificar(e, servico)

            # Se não pode retentar, falha imediatamente
            if not erro_info.pode_retentar:
                logger.error(f"[{servico}] Erro não recuperável: {e}")
                raise

            # Última tentativa, não espera
            if tentativa == max_tentativas - 1:
                break

            # Calcular delay com jitter
            delay = min(base_delay * (2 ** tentativa), max_delay)
            jitter = random.uniform(0, delay * 0.1)
            delay_total = delay + jitter

            logger.warning(
                f"[{servico}] Tentativa {tentativa + 1}/{max_tentativas} "
                f"falhou: {e}. Aguardando {delay_total:.1f}s..."
            )

            await asyncio.sleep(delay_total)

    # Todas tentativas falharam
    logger.error(
        f"[{servico}] Todas as {max_tentativas} tentativas falharam. "
        f"Último erro: {ultimo_erro}"
    )
    raise ultimo_erro

def com_retry(servico: str = "default"):
    """Decorator para adicionar retry automático."""
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await retry_com_backoff(func, *args, servico=servico, **kwargs)
        return wrapper
    return decorator
```

### 3.3 Sistema de Fallback e Contingência

```python
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class EndpointConfig:
    """Configuração de endpoint com contingências."""
    url_principal: str
    url_contingencia: Optional[str] = None
    url_contingencia_2: Optional[str] = None
    timeout: int = 30
    requer_certificado: bool = True

class GerenciadorContingencia:
    """Gerencia fallback entre serviços principal e contingência."""

    # Mapeamento de contingências SEFAZ NF-e
    CONTINGENCIAS_NFE = {
        # UFs que usam SVC-AN (Ambiente Nacional)
        "AM": EndpointConfig(
            url_principal="https://nfe.sefaz.am.gov.br/services2/services/",
            url_contingencia="https://www.svc.fazenda.gov.br/NFeAutorizacao4/",  # SVC-AN
        ),
        "BA": EndpointConfig(
            url_principal="https://nfe.sefaz.ba.gov.br/webservices/",
            url_contingencia="https://www.svc.fazenda.gov.br/NFeAutorizacao4/",
        ),
        "SP": EndpointConfig(
            url_principal="https://nfe.fazenda.sp.gov.br/ws/",
            url_contingencia="https://www.svc.fazenda.gov.br/NFeAutorizacao4/",
        ),
        # UFs que usam SVC-RS
        "GO": EndpointConfig(
            url_principal="https://nfe.sefaz.go.gov.br/nfe/services/",
            url_contingencia="https://nfe.svrs.rs.gov.br/ws/",  # SVC-RS
        ),
        "MT": EndpointConfig(
            url_principal="https://nfe.sefaz.mt.gov.br/nfews/",
            url_contingencia="https://nfe.svrs.rs.gov.br/ws/",
        ),
        # UFs sem SEFAZ própria (usam SVRS diretamente)
        "AC": EndpointConfig(
            url_principal="https://nfe.svrs.rs.gov.br/ws/",
            url_contingencia="https://www.svc.fazenda.gov.br/NFeAutorizacao4/",
        ),
    }

    # Contingências para CT-e e MDF-e
    CONTINGENCIAS_CTE = {
        "default": EndpointConfig(
            url_principal="https://cte.svrs.rs.gov.br/ws/",
            url_contingencia="https://cte.svc.rs.gov.br/ws/",
        ),
        # UFs com SEFAZ própria para CT-e
        "SP": EndpointConfig(
            url_principal="https://nfe.fazenda.sp.gov.br/cteWEB/services/",
            url_contingencia="https://cte.svrs.rs.gov.br/ws/",
        ),
    }

    _status_endpoints: Dict[str, bool] = {}  # Cache de status

    @classmethod
    async def obter_endpoint_ativo(
        cls,
        tipo_documento: str,
        uf: str,
        servico: str
    ) -> str:
        """Retorna endpoint ativo, tentando principal e depois contingência."""

        # Selecionar configuração
        if tipo_documento == "nfe":
            config = cls.CONTINGENCIAS_NFE.get(uf, cls.CONTINGENCIAS_NFE.get("AC"))
        elif tipo_documento in ["cte", "mdfe"]:
            config = cls.CONTINGENCIAS_CTE.get(uf, cls.CONTINGENCIAS_CTE["default"])
        else:
            raise ValueError(f"Tipo de documento não suportado: {tipo_documento}")

        # Construir URL completa
        url_principal = f"{config.url_principal}{servico}"

        # Verificar cache de status
        cache_key = f"{tipo_documento}:{uf}:principal"
        if cls._status_endpoints.get(cache_key, True):
            return url_principal

        # Principal indisponível, usar contingência
        if config.url_contingencia:
            logger.warning(
                f"[{tipo_documento.upper()}] Usando contingência para {uf}: "
                f"{config.url_contingencia}"
            )
            return f"{config.url_contingencia}{servico}"

        return url_principal

    @classmethod
    def marcar_indisponivel(cls, tipo_documento: str, uf: str, principal: bool = True):
        """Marca endpoint como indisponível."""
        cache_key = f"{tipo_documento}:{uf}:{'principal' if principal else 'contingencia'}"
        cls._status_endpoints[cache_key] = False
        logger.warning(f"Endpoint marcado como indisponível: {cache_key}")

    @classmethod
    def marcar_disponivel(cls, tipo_documento: str, uf: str):
        """Marca endpoint principal como disponível novamente."""
        cache_key = f"{tipo_documento}:{uf}:principal"
        cls._status_endpoints[cache_key] = True
```

### 3.4 Fila de Reprocessamento

```python
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID, uuid4
import json

class StatusReprocessamento(Enum):
    PENDENTE = "pendente"
    EM_PROCESSAMENTO = "em_processamento"
    SUCESSO = "sucesso"
    FALHA_PERMANENTE = "falha_permanente"

class FilaReprocessamento:
    """Gerencia fila de documentos para reprocessamento."""

    MAX_TENTATIVAS = 5
    INTERVALO_BASE = timedelta(minutes=15)

    @staticmethod
    async def adicionar(
        db_session,
        tipo_documento: str,
        documento_id: UUID,
        erro: ErroIntegracao,
        dados_originais: dict
    ):
        """Adiciona documento à fila de reprocessamento."""

        # Calcular próxima tentativa com backoff
        tentativa_atual = erro.tentativas + 1
        if tentativa_atual >= FilaReprocessamento.MAX_TENTATIVAS:
            status = StatusReprocessamento.FALHA_PERMANENTE
            proxima_tentativa = None
        else:
            status = StatusReprocessamento.PENDENTE
            delay = FilaReprocessamento.INTERVALO_BASE * (2 ** tentativa_atual)
            proxima_tentativa = datetime.utcnow() + delay

        await db_session.execute(
            """
            INSERT INTO fila_reprocessamento (
                id, tipo_documento, documento_id, status,
                tentativas, proxima_tentativa, ultimo_erro,
                dados_originais, created_at
            ) VALUES (
                :id, :tipo, :doc_id, :status,
                :tentativas, :proxima, :erro,
                :dados, NOW()
            )
            ON CONFLICT (documento_id) DO UPDATE SET
                tentativas = EXCLUDED.tentativas,
                proxima_tentativa = EXCLUDED.proxima_tentativa,
                ultimo_erro = EXCLUDED.ultimo_erro,
                status = EXCLUDED.status,
                updated_at = NOW()
            """,
            {
                "id": uuid4(),
                "tipo": tipo_documento,
                "doc_id": documento_id,
                "status": status.value,
                "tentativas": tentativa_atual,
                "proxima": proxima_tentativa,
                "erro": json.dumps({
                    "categoria": erro.categoria.value,
                    "mensagem": erro.mensagem,
                    "servico": erro.servico,
                }),
                "dados": json.dumps(dados_originais),
            }
        )

        if status == StatusReprocessamento.FALHA_PERMANENTE:
            logger.error(
                f"Documento {documento_id} marcado como falha permanente "
                f"após {tentativa_atual} tentativas"
            )

    @staticmethod
    async def processar_pendentes(db_session, worker_id: str):
        """Processa itens pendentes na fila."""

        # Buscar itens prontos para reprocessamento
        itens = await db_session.execute(
            """
            UPDATE fila_reprocessamento
            SET status = :em_proc, worker_id = :worker, updated_at = NOW()
            WHERE id IN (
                SELECT id FROM fila_reprocessamento
                WHERE status = :pendente
                AND proxima_tentativa <= NOW()
                ORDER BY proxima_tentativa
                LIMIT 10
                FOR UPDATE SKIP LOCKED
            )
            RETURNING *
            """,
            {
                "em_proc": StatusReprocessamento.EM_PROCESSAMENTO.value,
                "pendente": StatusReprocessamento.PENDENTE.value,
                "worker": worker_id,
            }
        )

        return itens.fetchall()
```

---

## 4. ESCALABILIDADE E CONCORRÊNCIA

### 4.1 Rate Limits por Serviço

```python
from dataclasses import dataclass
from typing import Dict
import time

@dataclass
class RateLimitConfig:
    """Configuração de rate limit por serviço."""
    requisicoes_por_minuto: int
    requisicoes_por_hora: int
    burst_maximo: int  # Máximo de requisições simultâneas
    cooldown_apos_429: int  # Segundos para esperar após 429

# Limites baseados em documentação oficial e testes
RATE_LIMITS: Dict[str, RateLimitConfig] = {
    # SEFAZ - Geralmente não documentam, mas testado
    "sefaz_nfe": RateLimitConfig(
        requisicoes_por_minuto=60,
        requisicoes_por_hora=1000,
        burst_maximo=10,
        cooldown_apos_429=60,
    ),
    "sefaz_cte": RateLimitConfig(
        requisicoes_por_minuto=60,
        requisicoes_por_hora=1000,
        burst_maximo=10,
        cooldown_apos_429=60,
    ),

    # eSocial - Documentado em manual técnico
    "esocial": RateLimitConfig(
        requisicoes_por_minuto=20,
        requisicoes_por_hora=500,
        burst_maximo=5,
        cooldown_apos_429=120,
    ),

    # EFD-Reinf
    "efd_reinf": RateLimitConfig(
        requisicoes_por_minuto=30,
        requisicoes_por_hora=600,
        burst_maximo=5,
        cooldown_apos_429=60,
    ),

    # FGTS Digital
    "fgts_digital": RateLimitConfig(
        requisicoes_por_minuto=30,
        requisicoes_por_hora=500,
        burst_maximo=5,
        cooldown_apos_429=60,
    ),

    # DCTFWeb
    "dctfweb": RateLimitConfig(
        requisicoes_por_minuto=20,
        requisicoes_por_hora=300,
        burst_maximo=3,
        cooldown_apos_429=120,
    ),

    # NFS-e Municipal (varia por prefeitura)
    "nfse_manaus": RateLimitConfig(
        requisicoes_por_minuto=30,
        requisicoes_por_hora=500,
        burst_maximo=5,
        cooldown_apos_429=60,
    ),

    # Gov.br OAuth
    "govbr": RateLimitConfig(
        requisicoes_por_minuto=100,
        requisicoes_por_hora=2000,
        burst_maximo=20,
        cooldown_apos_429=30,
    ),
}
```

### 4.2 Arquitetura de Filas com Celery

```python
# celery_config.py
from celery import Celery
from kombu import Queue, Exchange

app = Celery('conecta_pro_gov')

# Configuração de filas separadas por serviço
app.conf.task_queues = (
    # Filas de alta prioridade (consultas)
    Queue('gov_consultas', Exchange('gov'), routing_key='gov.consulta.#'),

    # Filas por tipo de serviço
    Queue('gov_nfe', Exchange('gov'), routing_key='gov.nfe.#'),
    Queue('gov_esocial', Exchange('gov'), routing_key='gov.esocial.#'),
    Queue('gov_fgts', Exchange('gov'), routing_key='gov.fgts.#'),
    Queue('gov_nfse', Exchange('gov'), routing_key='gov.nfse.#'),
    Queue('gov_sped', Exchange('gov'), routing_key='gov.sped.#'),

    # Fila de reprocessamento (baixa prioridade)
    Queue('gov_reprocessamento', Exchange('gov'), routing_key='gov.reprocessamento'),
)

# Roteamento de tarefas para filas
app.conf.task_routes = {
    'tasks.gov.consultar_*': {'queue': 'gov_consultas'},
    'tasks.gov.nfe.*': {'queue': 'gov_nfe'},
    'tasks.gov.esocial.*': {'queue': 'gov_esocial'},
    'tasks.gov.fgts.*': {'queue': 'gov_fgts'},
    'tasks.gov.nfse.*': {'queue': 'gov_nfse'},
    'tasks.gov.sped.*': {'queue': 'gov_sped'},
    'tasks.gov.reprocessar_*': {'queue': 'gov_reprocessamento'},
}

# Concorrência por fila
app.conf.worker_concurrency = 4  # Workers por processo

# Rate limiting nativo do Celery
app.conf.task_annotations = {
    'tasks.gov.nfe.*': {'rate_limit': '60/m'},
    'tasks.gov.esocial.*': {'rate_limit': '20/m'},
    'tasks.gov.fgts.*': {'rate_limit': '30/m'},
    'tasks.gov.nfse.*': {'rate_limit': '30/m'},
}

# Configurações de retry
app.conf.task_acks_late = True  # ACK após conclusão
app.conf.task_reject_on_worker_lost = True
app.conf.task_default_retry_delay = 60
app.conf.task_max_retries = 3
```

### 4.3 Escalonamento Automático

```yaml
# docker-compose.gov.yml - Configuração de workers
version: '3.8'

services:
  # Workers para NF-e/CT-e/MDF-e
  worker-sefaz:
    image: conecta-pro/worker:latest
    command: celery -A celery_config worker -Q gov_nfe,gov_consultas -c 4
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 512M
    environment:
      - CELERY_WORKER_PREFETCH_MULTIPLIER=1
    depends_on:
      - redis
      - rabbitmq

  # Workers para eSocial (menor concorrência por rate limit)
  worker-esocial:
    image: conecta-pro/worker:latest
    command: celery -A celery_config worker -Q gov_esocial -c 2
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

  # Workers para FGTS/DCTFWeb
  worker-fgts:
    image: conecta-pro/worker:latest
    command: celery -A celery_config worker -Q gov_fgts -c 2
    deploy:
      replicas: 1

  # Worker de reprocessamento (baixa prioridade)
  worker-reprocessamento:
    image: conecta-pro/worker:latest
    command: celery -A celery_config worker -Q gov_reprocessamento -c 1
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: '0.25'
          memory: 128M

  # Flower para monitoramento
  flower:
    image: mher/flower:latest
    command: celery --broker=redis://redis:6379/0 flower --port=5555
    ports:
      - "5555:5555"
```

### 4.4 Monitoramento e Métricas

```python
# metrics.py - Métricas Prometheus
from prometheus_client import Counter, Histogram, Gauge
import time

# Contadores
documentos_processados = Counter(
    'gov_documentos_processados_total',
    'Total de documentos processados',
    ['servico', 'tipo_documento', 'status']
)

erros_integracao = Counter(
    'gov_erros_total',
    'Total de erros de integração',
    ['servico', 'categoria_erro']
)

# Histogramas
tempo_processamento = Histogram(
    'gov_tempo_processamento_seconds',
    'Tempo de processamento por operação',
    ['servico', 'operacao'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

tempo_resposta_api = Histogram(
    'gov_api_response_seconds',
    'Tempo de resposta das APIs governamentais',
    ['servico', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# Gauges
fila_pendente = Gauge(
    'gov_fila_pendente',
    'Documentos pendentes na fila',
    ['servico']
)

workers_ativos = Gauge(
    'gov_workers_ativos',
    'Número de workers ativos',
    ['fila']
)

# Decorator para métricas automáticas
def com_metricas(servico: str, operacao: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            with tempo_processamento.labels(
                servico=servico, operacao=operacao
            ).time():
                try:
                    result = await func(*args, **kwargs)
                    documentos_processados.labels(
                        servico=servico,
                        tipo_documento=operacao,
                        status='sucesso'
                    ).inc()
                    return result
                except Exception as e:
                    documentos_processados.labels(
                        servico=servico,
                        tipo_documento=operacao,
                        status='erro'
                    ).inc()
                    erros_integracao.labels(
                        servico=servico,
                        categoria_erro=type(e).__name__
                    ).inc()
                    raise
        return wrapper
    return decorator
```

---

## 5. GOVERNANÇA DE CREDENCIAIS

### 5.1 Política de Rotação

```yaml
# Política de rotação de credenciais
rotacao_credenciais:
  certificados_a1:
    validade_maxima: 365 dias  # ICP-Brasil define 1-3 anos
    alerta_renovacao: 60 dias antes do vencimento
    alerta_critico: 30 dias antes
    acao_automatica: "Suspender integrações e notificar admin"

  certificados_a3:
    validade_maxima: 1095 dias  # 3 anos típico
    alerta_renovacao: 90 dias antes
    alerta_critico: 30 dias

  client_secret_govbr:
    rotacao_obrigatoria: 90 dias
    alerta_rotacao: 15 dias antes
    procedimento: "Gerar novo secret no Gov.br e atualizar Vault"

  tokens_oauth:
    access_token_ttl: 3600 segundos  # 1 hora
    refresh_token_ttl: 86400 segundos  # 24 horas
    renovacao_automatica: true

  senhas_certificados:
    rotacao_recomendada: 180 dias
    complexidade_minima: "16 caracteres, maiúsculas, minúsculas, números, especiais"
```

### 5.2 Armazenamento Seguro

```python
# vault_manager.py - Integração com HashiCorp Vault
import hvac
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class VaultManager:
    """Gerencia acesso seguro a credenciais no Vault."""

    def __init__(self):
        self.client = hvac.Client(
            url=os.environ.get("VAULT_ADDR", "http://vault:8200"),
            token=os.environ.get("VAULT_TOKEN"),
        )

        # Verificar conexão
        if not self.client.is_authenticated():
            raise RuntimeError("Falha na autenticação com Vault")

    @lru_cache(maxsize=100)
    def obter_certificado(self, tenant_id: str) -> tuple[bytes, str]:
        """
        Obtém certificado PFX e senha do Vault.
        Cache por 5 minutos para evitar chamadas excessivas.
        """
        try:
            secret = self.client.secrets.kv.v2.read_secret_version(
                path=f"conecta-pro/certificates/{tenant_id}",
                mount_point="secret",
            )

            data = secret["data"]["data"]
            cert_base64 = data["certificate"]
            password = data["password"]

            # Log de auditoria (sem dados sensíveis)
            logger.info(
                f"Certificado acessado",
                extra={
                    "tenant_id": tenant_id,
                    "cert_hash": hashlib.sha256(cert_base64.encode()).hexdigest()[:16],
                }
            )

            return base64.b64decode(cert_base64), password

        except hvac.exceptions.InvalidPath:
            logger.error(f"Certificado não encontrado para tenant {tenant_id}")
            raise ValueError(f"Certificado não configurado para tenant {tenant_id}")

    def obter_client_secret(self, servico: str) -> str:
        """Obtém client_secret para serviços OAuth."""
        secret = self.client.secrets.kv.v2.read_secret_version(
            path=f"conecta-pro/oauth/{servico}",
            mount_point="secret",
        )
        return secret["data"]["data"]["client_secret"]

    def rotacionar_secret(self, servico: str, novo_secret: str):
        """Rotaciona secret de serviço OAuth."""
        self.client.secrets.kv.v2.create_or_update_secret(
            path=f"conecta-pro/oauth/{servico}",
            secret={
                "client_secret": novo_secret,
                "rotacionado_em": datetime.utcnow().isoformat(),
            },
            mount_point="secret",
        )

        # Limpar cache
        self.obter_client_secret.cache_clear()

        logger.info(f"Secret rotacionado para serviço {servico}")

# Singleton para acesso global
_vault_instance = None

def get_vault() -> VaultManager:
    global _vault_instance
    if _vault_instance is None:
        _vault_instance = VaultManager()
    return _vault_instance
```

### 5.3 Política de Acesso (RBAC)

```yaml
# Política de acesso a credenciais
politicas_acesso:
  roles:
    admin_integracao:
      descricao: "Administrador de integrações governamentais"
      permissoes:
        - ler_certificados
        - rotacionar_secrets
        - visualizar_logs_auditoria
        - configurar_endpoints

    worker_gov:
      descricao: "Worker de processamento (service account)"
      permissoes:
        - ler_certificados  # Apenas do próprio tenant
        - ler_tokens_oauth
      restricoes:
        - "Acesso apenas via IP interno"
        - "Rate limit: 100 leituras/hora"

    desenvolvedor:
      descricao: "Desenvolvedor (ambiente de homologação)"
      permissoes:
        - ler_certificados_homologacao
      restricoes:
        - "Sem acesso a produção"

  auditoria:
    registrar_acessos: true
    campos_registrados:
      - timestamp
      - usuario_ou_servico
      - acao
      - recurso_acessado
      - ip_origem
      - resultado
    retencao: 365 dias
```

### 5.4 Monitoramento de Certificados

```python
# certificate_monitor.py
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import asyncio

class MonitorCertificados:
    """Monitora validade de certificados e emite alertas."""

    ALERTAS = {
        "critico": timedelta(days=30),
        "alto": timedelta(days=60),
        "medio": timedelta(days=90),
    }

    async def verificar_todos_certificados(self, db_session):
        """Verifica todos os certificados ativos."""
        certificados = await db_session.execute(
            "SELECT id, tenant_id, certificate_data FROM certificates WHERE ativo = true"
        )

        alertas = []

        for cert_row in certificados:
            try:
                cert = x509.load_pkcs12(
                    cert_row.certificate_data,
                    password=None,  # Já decriptado
                    backend=default_backend()
                )

                dias_restantes = (cert.not_valid_after_utc - datetime.utcnow()).days

                # Determinar nível de alerta
                nivel = None
                for nome, limite in self.ALERTAS.items():
                    if dias_restantes <= limite.days:
                        nivel = nome
                        break

                if nivel:
                    alertas.append({
                        "tenant_id": cert_row.tenant_id,
                        "dias_restantes": dias_restantes,
                        "nivel": nivel,
                        "vencimento": cert.not_valid_after_utc.isoformat(),
                    })

            except Exception as e:
                alertas.append({
                    "tenant_id": cert_row.tenant_id,
                    "nivel": "critico",
                    "erro": f"Erro ao ler certificado: {e}",
                })

        return alertas

    async def notificar_alertas(self, alertas: list):
        """Envia notificações sobre certificados próximos do vencimento."""
        for alerta in alertas:
            if alerta["nivel"] == "critico":
                # Email para admin + webhook
                await self._enviar_email_critico(alerta)
                await self._enviar_webhook(alerta)
            elif alerta["nivel"] == "alto":
                # Email para admin
                await self._enviar_email_alerta(alerta)
            else:
                # Apenas log
                logger.warning(f"Certificado próximo do vencimento: {alerta}")
```

---

## 6. AUDITORIA, COMPLIANCE E LOGS

### 6.1 Estrutura de Logs

```python
# logging_config.py
import logging
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger
import hashlib

class ConectaProFormatter(jsonlogger.JsonFormatter):
    """Formatter customizado com campos obrigatórios."""

    CAMPOS_SENSIVEIS = ["cpf", "cnpj", "senha", "password", "token", "secret"]

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        # Campos obrigatórios
        log_record["timestamp"] = datetime.utcnow().isoformat() + "Z"
        log_record["level"] = record.levelname
        log_record["module"] = record.module
        log_record["correlation_id"] = getattr(record, "correlation_id", None)
        log_record["tenant_id"] = getattr(record, "tenant_id", None)
        log_record["user_id"] = getattr(record, "user_id", None)
        log_record["service"] = "government_integrations"

        # Mascarar dados sensíveis
        self._mascarar_sensiveis(log_record)

    def _mascarar_sensiveis(self, log_record):
        """Mascara dados sensíveis conforme LGPD."""
        for key, value in list(log_record.items()):
            if isinstance(value, str):
                # CPF: mostrar apenas últimos 3 dígitos
                if key.lower() in ["cpf", "cpf_titular"]:
                    log_record[key] = f"***.***.***-{value[-2:]}" if len(value) >= 11 else "***"

                # CNPJ: mostrar apenas últimos 4 dígitos
                elif key.lower() in ["cnpj", "cnpj_emitente", "cnpj_destinatario"]:
                    log_record[key] = f"**.***.***/{value[-6:-2]}-{value[-2:]}" if len(value) >= 14 else "***"

                # Tokens/senhas: nunca logar
                elif any(s in key.lower() for s in self.CAMPOS_SENSIVEIS):
                    log_record[key] = "[REDACTED]"

# Configuração
def configurar_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(ConectaProFormatter())

    logger = logging.getLogger("government_integrations")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger
```

### 6.2 Registro de Auditoria

```sql
-- Tabela de auditoria imutável
CREATE TABLE auditoria_gov (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    -- Identificação
    tenant_id UUID NOT NULL,
    user_id UUID,
    correlation_id UUID,

    -- Operação
    servico VARCHAR(50) NOT NULL,
    operacao VARCHAR(100) NOT NULL,
    recurso VARCHAR(255),

    -- Requisição
    parametros_hash VARCHAR(64),  -- SHA256 dos parâmetros (sem dados sensíveis)
    ip_origem INET,
    user_agent VARCHAR(255),

    -- Resposta
    status VARCHAR(20) NOT NULL,  -- sucesso, erro, timeout
    codigo_retorno VARCHAR(20),
    tempo_processamento_ms INTEGER,

    -- Metadados
    metadata JSONB,

    -- Imutabilidade
    hash_registro VARCHAR(64) NOT NULL,  -- Hash do registro anterior + este

    -- Índices para consulta
    CONSTRAINT idx_audit_tenant_data UNIQUE (tenant_id, timestamp, id)
);

-- Particionamento por mês para performance
CREATE TABLE auditoria_gov_2026_01 PARTITION OF auditoria_gov
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- Índices
CREATE INDEX idx_audit_servico ON auditoria_gov (servico, timestamp);
CREATE INDEX idx_audit_operacao ON auditoria_gov (operacao, timestamp);
CREATE INDEX idx_audit_correlation ON auditoria_gov (correlation_id);

-- Função para hash encadeado (garantia de imutabilidade)
CREATE OR REPLACE FUNCTION fn_calcular_hash_auditoria()
RETURNS TRIGGER AS $$
DECLARE
    hash_anterior VARCHAR(64);
    dados_registro TEXT;
BEGIN
    -- Obter hash do registro anterior
    SELECT hash_registro INTO hash_anterior
    FROM auditoria_gov
    WHERE tenant_id = NEW.tenant_id
    ORDER BY id DESC
    LIMIT 1;

    IF hash_anterior IS NULL THEN
        hash_anterior := 'GENESIS';
    END IF;

    -- Calcular hash do registro atual
    dados_registro := CONCAT(
        hash_anterior, '|',
        NEW.timestamp, '|',
        NEW.tenant_id, '|',
        NEW.servico, '|',
        NEW.operacao, '|',
        NEW.status
    );

    NEW.hash_registro := encode(sha256(dados_registro::bytea), 'hex');

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_hash_auditoria
BEFORE INSERT ON auditoria_gov
FOR EACH ROW EXECUTE FUNCTION fn_calcular_hash_auditoria();
```

### 6.3 Compliance LGPD

```python
# lgpd_compliance.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class BaseLegalLGPD(Enum):
    """Bases legais para tratamento de dados (Art. 7º LGPD)."""
    OBRIGACAO_LEGAL = "obrigacao_legal"  # Art. 7º, II
    EXECUCAO_CONTRATO = "execucao_contrato"  # Art. 7º, V
    LEGITIMO_INTERESSE = "legitimo_interesse"  # Art. 7º, IX

@dataclass
class TratamentoDados:
    """Registro de tratamento de dados pessoais."""
    tipo_dado: str
    finalidade: str
    base_legal: BaseLegalLGPD
    retencao_dias: int
    compartilhamento: Optional[str] = None

# Mapeamento de dados tratados nas integrações governamentais
TRATAMENTOS_GOV = {
    "cpf_colaborador": TratamentoDados(
        tipo_dado="CPF",
        finalidade="Cumprimento de obrigações trabalhistas (eSocial, FGTS)",
        base_legal=BaseLegalLGPD.OBRIGACAO_LEGAL,
        retencao_dias=365 * 30,  # 30 anos (prazo trabalhista)
        compartilhamento="eSocial, FGTS Digital, INSS",
    ),
    "dados_remuneracao": TratamentoDados(
        tipo_dado="Remuneração",
        finalidade="Cálculo de encargos e declarações fiscais",
        base_legal=BaseLegalLGPD.OBRIGACAO_LEGAL,
        retencao_dias=365 * 5,  # 5 anos (prazo fiscal)
        compartilhamento="eSocial, EFD-Reinf, DCTFWeb",
    ),
    "dados_cliente_pf": TratamentoDados(
        tipo_dado="CPF/Nome cliente PF",
        finalidade="Emissão de documentos fiscais",
        base_legal=BaseLegalLGPD.OBRIGACAO_LEGAL,
        retencao_dias=365 * 5,
        compartilhamento="SEFAZ (NF-e/NFC-e)",
    ),
}

class GerenciadorLGPD:
    """Gerencia conformidade LGPD nas integrações."""

    @staticmethod
    def registrar_tratamento(
        tenant_id: str,
        tipo_tratamento: str,
        titular_id: str,
        dados_tratados: list[str],
        db_session
    ):
        """Registra tratamento de dados para auditoria LGPD."""
        tratamento = TRATAMENTOS_GOV.get(tipo_tratamento)
        if not tratamento:
            logger.warning(f"Tipo de tratamento não mapeado: {tipo_tratamento}")
            return

        # Registrar no log de tratamentos
        db_session.execute(
            """
            INSERT INTO lgpd_tratamentos (
                tenant_id, tipo_tratamento, titular_hash,
                finalidade, base_legal, dados_tratados,
                compartilhamento, created_at
            ) VALUES (
                :tenant_id, :tipo, :titular_hash,
                :finalidade, :base_legal, :dados,
                :compartilhamento, NOW()
            )
            """,
            {
                "tenant_id": tenant_id,
                "tipo": tipo_tratamento,
                "titular_hash": hashlib.sha256(titular_id.encode()).hexdigest(),
                "finalidade": tratamento.finalidade,
                "base_legal": tratamento.base_legal.value,
                "dados": dados_tratados,
                "compartilhamento": tratamento.compartilhamento,
            }
        )

    @staticmethod
    async def atender_direito_acesso(titular_cpf: str, db_session) -> dict:
        """Atende direito de acesso do titular (Art. 18, II LGPD)."""
        titular_hash = hashlib.sha256(titular_cpf.encode()).hexdigest()

        tratamentos = await db_session.execute(
            """
            SELECT tipo_tratamento, finalidade, base_legal,
                   compartilhamento, created_at
            FROM lgpd_tratamentos
            WHERE titular_hash = :hash
            ORDER BY created_at DESC
            """,
            {"hash": titular_hash}
        )

        return {
            "titular": f"***.***.***-{titular_cpf[-2:]}",
            "tratamentos": [dict(t) for t in tratamentos.fetchall()],
            "data_relatorio": datetime.utcnow().isoformat(),
        }
```

### 6.4 Relatório de Conformidade

```python
# compliance_report.py
from datetime import datetime, timedelta
from typing import Dict, Any
import json

class RelatorioConformidade:
    """Gera relatórios periódicos de conformidade das integrações."""

    async def gerar_relatorio_mensal(
        self,
        tenant_id: str,
        mes: int,
        ano: int,
        db_session
    ) -> Dict[str, Any]:
        """Gera relatório mensal de conformidade."""

        data_inicio = datetime(ano, mes, 1)
        if mes == 12:
            data_fim = datetime(ano + 1, 1, 1)
        else:
            data_fim = datetime(ano, mes + 1, 1)

        # Estatísticas de sincronização
        stats_sync = await db_session.execute(
            """
            SELECT
                servico,
                COUNT(*) as total_operacoes,
                SUM(CASE WHEN status = 'sucesso' THEN 1 ELSE 0 END) as sucessos,
                SUM(CASE WHEN status = 'erro' THEN 1 ELSE 0 END) as erros,
                AVG(tempo_processamento_ms) as tempo_medio_ms
            FROM auditoria_gov
            WHERE tenant_id = :tenant_id
            AND timestamp >= :inicio
            AND timestamp < :fim
            GROUP BY servico
            """,
            {"tenant_id": tenant_id, "inicio": data_inicio, "fim": data_fim}
        )

        # Erros críticos
        erros_criticos = await db_session.execute(
            """
            SELECT
                servico, operacao, codigo_retorno,
                COUNT(*) as ocorrencias
            FROM auditoria_gov
            WHERE tenant_id = :tenant_id
            AND timestamp >= :inicio
            AND timestamp < :fim
            AND status = 'erro'
            GROUP BY servico, operacao, codigo_retorno
            ORDER BY ocorrencias DESC
            LIMIT 20
            """,
            {"tenant_id": tenant_id, "inicio": data_inicio, "fim": data_fim}
        )

        # Acessos a credenciais
        acessos_credenciais = await db_session.execute(
            """
            SELECT
                DATE(timestamp) as data,
                COUNT(*) as acessos
            FROM auditoria_gov
            WHERE tenant_id = :tenant_id
            AND timestamp >= :inicio
            AND timestamp < :fim
            AND operacao LIKE '%certificado%'
            GROUP BY DATE(timestamp)
            ORDER BY data
            """,
            {"tenant_id": tenant_id, "inicio": data_inicio, "fim": data_fim}
        )

        # Integridade dos registros
        integridade = await self._verificar_integridade_auditoria(
            tenant_id, data_inicio, data_fim, db_session
        )

        return {
            "periodo": {
                "inicio": data_inicio.isoformat(),
                "fim": data_fim.isoformat(),
            },
            "tenant_id": tenant_id,
            "gerado_em": datetime.utcnow().isoformat(),

            "resumo_sincronizacao": [dict(r) for r in stats_sync.fetchall()],
            "erros_mais_frequentes": [dict(r) for r in erros_criticos.fetchall()],
            "acessos_credenciais": [dict(r) for r in acessos_credenciais.fetchall()],

            "integridade_auditoria": integridade,

            "conformidade": {
                "lgpd": "Tratamentos registrados conforme Art. 37",
                "fiscal": "Documentos armazenados por 5+ anos",
                "trabalhista": "Eventos eSocial com retenção de 30 anos",
            }
        }

    async def _verificar_integridade_auditoria(
        self, tenant_id, data_inicio, data_fim, db_session
    ) -> dict:
        """Verifica integridade da cadeia de hashes de auditoria."""

        registros = await db_session.execute(
            """
            SELECT id, hash_registro
            FROM auditoria_gov
            WHERE tenant_id = :tenant_id
            AND timestamp >= :inicio
            AND timestamp < :fim
            ORDER BY id
            """,
            {"tenant_id": tenant_id, "inicio": data_inicio, "fim": data_fim}
        )

        total = 0
        validos = 0

        # Aqui seria feita a verificação real da cadeia de hashes
        # Simplificado para o exemplo
        for r in registros:
            total += 1
            if r.hash_registro:  # Hash presente
                validos += 1

        return {
            "total_registros": total,
            "registros_integros": validos,
            "integridade_percentual": (validos / total * 100) if total > 0 else 100,
            "status": "OK" if validos == total else "ALERTA",
        }
```

---

## 7. PLANOS DE CONTINGÊNCIA POR UF

### 7.1 Matriz de Contingência

```yaml
# contingencia_uf.yaml
matriz_contingencia:
  # ===== NORTE =====
  AC:
    nfe:
      principal: "SVRS"
      contingencia: "SVC-RS"
      epec: "AN"
    cte: "SVRS"
    mdfe: "SVRS"

  AM:
    nfe:
      principal: "SEFAZ-AM"
      url: "https://nfe.sefaz.am.gov.br/services2/services/"
      contingencia: "SVC-AN"
      epec: "AN"
    nfce:
      principal: "SEFAZ-AM"
      contingencia: "SVC-AN"
    cte: "SVRS"
    mdfe: "SVRS"

  AP:
    nfe:
      principal: "SVRS"
      contingencia: "SVC-RS"
    cte: "SVRS"
    mdfe: "SVRS"

  PA:
    nfe:
      principal: "SVAN"
      contingencia: "SVC-AN"
    cte: "SVRS"
    mdfe: "SVRS"

  RO:
    nfe:
      principal: "SVRS"
      contingencia: "SVC-RS"
    cte: "SVRS"
    mdfe: "SVRS"

  RR:
    nfe:
      principal: "SVRS"
      contingencia: "SVC-RS"
    cte: "SVRS"
    mdfe: "SVRS"

  TO:
    nfe:
      principal: "SVRS"
      contingencia: "SVC-RS"
    cte: "SVRS"
    mdfe: "SVRS"

  # ===== NORDESTE =====
  AL:
    nfe:
      principal: "SVRS"
      contingencia: "SVC-RS"
    cte: "SVRS"
    mdfe: "SVRS"

  BA:
    nfe:
      principal: "SEFAZ-BA"
      url: "https://nfe.sefaz.ba.gov.br/webservices/NFeAutorizacao4/"
      contingencia: "SVC-AN"
    cte: "SVRS"
    mdfe: "SVRS"

  CE:
    nfe:
      principal: "SEFAZ-CE"
      contingencia: "SVC-AN"
    cte: "SVRS"
    mdfe: "SVRS"

  MA:
    nfe:
      principal: "SVAN"
      contingencia: "SVC-AN"
    cte: "SVRS"
    mdfe: "SVRS"

  PB:
    nfe:
      principal: "SVRS"
      contingencia: "SVC-RS"
    cte: "SVRS"
    mdfe: "SVRS"

  PE:
    nfe:
      principal: "SEFAZ-PE"
      url: "https://nfe.sefaz.pe.gov.br/nfe-service/"
      contingencia: "SVC-AN"
    cte: "SVRS"
    mdfe: "SVRS"

  PI:
    nfe:
      principal: "SVAN"
      contingencia: "SVC-AN"
    cte: "SVRS"
    mdfe: "SVRS"

  RN:
    nfe:
      principal: "SVRS"
      contingencia: "SVC-RS"
    cte: "SVRS"
    mdfe: "SVRS"

  SE:
    nfe:
      principal: "SVRS"
      contingencia: "SVC-RS"
    cte: "SVRS"
    mdfe: "SVRS"

  # ===== CENTRO-OESTE =====
  DF:
    nfe:
      principal: "SVRS"
      contingencia: "SVC-RS"
    cte: "SVRS"
    mdfe: "SVRS"

  GO:
    nfe:
      principal: "SEFAZ-GO"
      url: "https://nfe.sefaz.go.gov.br/nfe/services/"
      contingencia: "SVC-RS"
    cte: "SVRS"
    mdfe: "SVRS"

  MS:
    nfe:
      principal: "SEFAZ-MS"
      contingencia: "SVC-RS"
    cte: "SVRS"
    mdfe: "SVRS"

  MT:
    nfe:
      principal: "SEFAZ-MT"
      url: "https://nfe.sefaz.mt.gov.br/nfews/"
      contingencia: "SVC-RS"
    cte: "SVRS"
    mdfe: "SVRS"

  # ===== SUDESTE =====
  ES:
    nfe:
      principal: "SVRS"
      contingencia: "SVC-RS"
    cte: "SVRS"
    mdfe: "SVRS"

  MG:
    nfe:
      principal: "SEFAZ-MG"
      url: "https://nfe.fazenda.mg.gov.br/nfe2/"
      contingencia: "SVC-AN"
    cte:
      principal: "SEFAZ-MG"
      contingencia: "SVRS"
    mdfe: "SVRS"

  RJ:
    nfe:
      principal: "SVRS"
      contingencia: "SVC-RS"
    cte: "SVRS"
    mdfe: "SVRS"

  SP:
    nfe:
      principal: "SEFAZ-SP"
      url: "https://nfe.fazenda.sp.gov.br/ws/"
      contingencia: "SVC-AN"
    nfce:
      principal: "SEFAZ-SP"
      url: "https://nfce.fazenda.sp.gov.br/ws/"
    cte:
      principal: "SEFAZ-SP"
      url: "https://nfe.fazenda.sp.gov.br/cteWEB/services/"
      contingencia: "SVRS"
    mdfe: "SVRS"

  # ===== SUL =====
  PR:
    nfe:
      principal: "SEFAZ-PR"
      url: "https://nfe.sefa.pr.gov.br/nfe/"
      contingencia: "SVC-RS"
    cte:
      principal: "SEFAZ-PR"
      contingencia: "SVRS"
    mdfe: "SVRS"

  RS:
    nfe:
      principal: "SEFAZ-RS"
      url: "https://nfe.sefazrs.rs.gov.br/ws/"
      contingencia: "SVC-AN"
    cte:
      principal: "SEFAZ-RS"
      url: "https://cte.svrs.rs.gov.br/ws/"
    mdfe:
      principal: "SEFAZ-RS"
      url: "https://mdfe.svrs.rs.gov.br/ws/"

  SC:
    nfe:
      principal: "SVRS"
      contingencia: "SVC-RS"
    cte: "SVRS"
    mdfe: "SVRS"

# Endpoints centralizados
endpoints_centralizados:
  SVRS:
    nfe: "https://nfe.svrs.rs.gov.br/ws/"
    cte: "https://cte.svrs.rs.gov.br/ws/"
    mdfe: "https://mdfe.svrs.rs.gov.br/ws/"

  SVAN:
    nfe: "https://www.sefazvirtual.fazenda.gov.br/NFeAutorizacao4/"

  SVC-AN:
    nfe: "https://www.svc.fazenda.gov.br/NFeAutorizacao4/"

  SVC-RS:
    nfe: "https://nfe-svc.svrs.rs.gov.br/ws/"

  AN:
    epec: "https://www.nfe.fazenda.gov.br/NFeRecepcaoEvento4/"
```

### 7.2 Comutação Automática de Endpoints

```python
# endpoint_switcher.py
import yaml
from typing import Optional
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)

class ComutadorEndpoints:
    """Gerencia comutação automática entre endpoints."""

    def __init__(self, config_path: str = "/opt/conecta-pro/config/contingencia_uf.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self._status_endpoints: dict = {}
        self._ultimo_teste: dict = {}

    def obter_endpoint(
        self,
        uf: str,
        tipo_documento: str,
        servico: str
    ) -> str:
        """Obtém endpoint ativo para UF e tipo de documento."""

        uf_config = self.config["matriz_contingencia"].get(uf.upper())
        if not uf_config:
            raise ValueError(f"UF não configurada: {uf}")

        doc_config = uf_config.get(tipo_documento.lower())
        if not doc_config:
            raise ValueError(f"Tipo de documento não configurado: {tipo_documento}")

        # Se é string simples, é um endpoint centralizado
        if isinstance(doc_config, str):
            return self._resolver_endpoint_centralizado(doc_config, tipo_documento, servico)

        # Verificar status do endpoint principal
        cache_key = f"{uf}:{tipo_documento}:principal"

        if self._status_endpoints.get(cache_key, True):
            # Principal disponível
            if "url" in doc_config:
                return f"{doc_config['url']}{servico}"
            else:
                return self._resolver_endpoint_centralizado(
                    doc_config["principal"], tipo_documento, servico
                )

        # Principal indisponível, usar contingência
        if "contingencia" in doc_config:
            logger.warning(
                f"Usando contingência para {uf}/{tipo_documento}: {doc_config['contingencia']}"
            )
            return self._resolver_endpoint_centralizado(
                doc_config["contingencia"], tipo_documento, servico
            )

        raise RuntimeError(f"Nenhum endpoint disponível para {uf}/{tipo_documento}")

    def _resolver_endpoint_centralizado(
        self,
        nome: str,
        tipo_documento: str,
        servico: str
    ) -> str:
        """Resolve nome de endpoint centralizado para URL."""
        endpoints = self.config["endpoints_centralizados"].get(nome)
        if not endpoints:
            raise ValueError(f"Endpoint centralizado não encontrado: {nome}")

        base_url = endpoints.get(tipo_documento.lower())
        if not base_url:
            raise ValueError(f"URL não configurada para {nome}/{tipo_documento}")

        return f"{base_url}{servico}"

    def marcar_indisponivel(self, uf: str, tipo_documento: str):
        """Marca endpoint principal como indisponível."""
        cache_key = f"{uf}:{tipo_documento}:principal"
        self._status_endpoints[cache_key] = False
        logger.warning(f"Endpoint marcado como indisponível: {cache_key}")

    def marcar_disponivel(self, uf: str, tipo_documento: str):
        """Marca endpoint principal como disponível."""
        cache_key = f"{uf}:{tipo_documento}:principal"
        self._status_endpoints[cache_key] = True
        logger.info(f"Endpoint restaurado: {cache_key}")

    async def testar_endpoints_periodicamente(self, intervalo_minutos: int = 5):
        """Testa endpoints periodicamente para detectar recuperação."""
        while True:
            for cache_key, disponivel in list(self._status_endpoints.items()):
                if not disponivel:
                    # Tentar reconectar
                    uf, tipo_doc, _ = cache_key.split(":")
                    try:
                        # Fazer teste de conexão
                        endpoint = self.obter_endpoint(uf, tipo_doc, "NFeStatusServico4")
                        # Aqui faria a requisição de teste
                        # Se sucesso:
                        self.marcar_disponivel(uf, tipo_doc)
                    except Exception as e:
                        logger.debug(f"Endpoint ainda indisponível: {cache_key}")

            await asyncio.sleep(intervalo_minutos * 60)
```

### 7.3 Testes Automáticos de Contingência

```python
# contingency_tester.py
from datetime import datetime
import asyncio
import aiohttp
import ssl
from typing import List, Dict

class TesterContingencia:
    """Testa periodicamente endpoints de contingência."""

    SERVICOS_TESTE = {
        "nfe": "NFeStatusServico4",
        "cte": "CTeStatusServico",
        "mdfe": "MDFeStatusServico",
    }

    async def testar_todos_endpoints(self) -> List[Dict]:
        """Testa todos os endpoints configurados."""
        comutador = ComutadorEndpoints()
        resultados = []

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        async with aiohttp.ClientSession() as session:
            for uf in comutador.config["matriz_contingencia"].keys():
                for tipo_doc in ["nfe", "cte", "mdfe"]:
                    try:
                        # Testar principal
                        url_principal = comutador.obter_endpoint(
                            uf, tipo_doc, self.SERVICOS_TESTE[tipo_doc]
                        )
                        resultado_principal = await self._testar_url(
                            session, url_principal, ssl_context
                        )

                        # Testar contingência (forçar)
                        comutador.marcar_indisponivel(uf, tipo_doc)
                        try:
                            url_contingencia = comutador.obter_endpoint(
                                uf, tipo_doc, self.SERVICOS_TESTE[tipo_doc]
                            )
                            resultado_contingencia = await self._testar_url(
                                session, url_contingencia, ssl_context
                            )
                        except:
                            resultado_contingencia = {"status": "N/A"}
                        finally:
                            comutador.marcar_disponivel(uf, tipo_doc)

                        resultados.append({
                            "uf": uf,
                            "tipo_documento": tipo_doc,
                            "principal": {
                                "url": url_principal,
                                **resultado_principal,
                            },
                            "contingencia": {
                                "url": url_contingencia if resultado_contingencia["status"] != "N/A" else None,
                                **resultado_contingencia,
                            },
                            "testado_em": datetime.utcnow().isoformat(),
                        })

                    except Exception as e:
                        resultados.append({
                            "uf": uf,
                            "tipo_documento": tipo_doc,
                            "erro": str(e),
                        })

        return resultados

    async def _testar_url(
        self,
        session: aiohttp.ClientSession,
        url: str,
        ssl_context
    ) -> Dict:
        """Testa uma URL específica."""
        inicio = datetime.utcnow()

        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=10),
                ssl=ssl_context,
            ) as resp:
                tempo_ms = (datetime.utcnow() - inicio).total_seconds() * 1000

                # 200, 403, 405 indicam servidor online
                if resp.status in [200, 403, 405, 500]:
                    return {
                        "status": "online",
                        "http_status": resp.status,
                        "tempo_ms": round(tempo_ms, 1),
                    }
                else:
                    return {
                        "status": "erro",
                        "http_status": resp.status,
                        "tempo_ms": round(tempo_ms, 1),
                    }

        except aiohttp.ClientSSLError:
            tempo_ms = (datetime.utcnow() - inicio).total_seconds() * 1000
            return {
                "status": "online_ssl",
                "nota": "Requer certificado",
                "tempo_ms": round(tempo_ms, 1),
            }
        except asyncio.TimeoutError:
            return {"status": "timeout"}
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)[:100]}
```

---

## 8. INTEGRAÇÃO COM MÓDULOS INTERNOS

### 8.1 Mapa de Integração

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MÓDULO GOVERNMENT_INTEGRATIONS                            │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│   COMPRAS/    │       │  FINANCEIRO   │       │   CONTÁBIL    │
│   ESTOQUE     │       │               │       │               │
├───────────────┤       ├───────────────┤       ├───────────────┤
│ • NF-e entrada│       │ • FGTS Digital│       │ • SPED Contábil│
│ • CT-e receb. │       │ • DCTFWeb     │       │ • SPED Fiscal  │
│ • MDF-e       │       │ • DAS (Simples│       │ • Livros       │
│ • Fornecedores│       │ • DARF        │       │   contábeis    │
└───────┬───────┘       └───────┬───────┘       └───────┬───────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│      RH       │       │    FISCAL     │       │   VENDAS/CRM  │
├───────────────┤       ├───────────────┤       ├───────────────┤
│ • eSocial     │       │ • NF-e/NFC-e  │       │ • NF-e saída  │
│ • Folha       │       │ • NFS-e       │       │ • Clientes    │
│ • Férias      │       │ • CT-e        │       │ • Contratos   │
│ • Afastamentos│       │ • ICMS/IPI/ISS│       │               │
└───────────────┘       └───────────────┘       └───────────────┘
```

### 8.2 Eventos de Integração

```python
# integration_events.py
from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, Optional
from datetime import datetime
import json

class TipoEventoIntegracao(Enum):
    """Tipos de eventos que disparam integrações."""

    # Documentos fiscais
    NFE_ENTRADA_RECEBIDA = "nfe_entrada_recebida"
    NFE_SAIDA_AUTORIZADA = "nfe_saida_autorizada"
    NFSE_EMITIDA = "nfse_emitida"
    CTE_RECEBIDO = "cte_recebido"

    # Trabalhista
    ESOCIAL_EVENTO_RECEBIDO = "esocial_evento_recebido"
    FGTS_GUIA_GERADA = "fgts_guia_gerada"

    # Fiscal
    SPED_GERADO = "sped_gerado"
    DCTFWEB_TRANSMITIDA = "dctfweb_transmitida"

@dataclass
class EventoIntegracao:
    """Evento de integração entre módulos."""
    tipo: TipoEventoIntegracao
    tenant_id: str
    dados: Dict[str, Any]
    origem: str
    timestamp: datetime = None
    correlation_id: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class DispatcherEventos:
    """Dispatcher de eventos para módulos internos."""

    # Mapeamento de eventos para handlers
    HANDLERS = {
        TipoEventoIntegracao.NFE_ENTRADA_RECEBIDA: [
            "compras.processar_nfe_entrada",
            "estoque.atualizar_entrada",
            "financeiro.gerar_conta_pagar",
            "fiscal.registrar_credito_icms",
        ],
        TipoEventoIntegracao.NFE_SAIDA_AUTORIZADA: [
            "financeiro.gerar_conta_receber",
            "estoque.baixar_estoque",
            "fiscal.registrar_debito_icms",
            "vendas.atualizar_pedido",
        ],
        TipoEventoIntegracao.NFSE_EMITIDA: [
            "financeiro.gerar_conta_receber",
            "fiscal.registrar_iss",
            "contabil.lancamento_receita",
        ],
        TipoEventoIntegracao.ESOCIAL_EVENTO_RECEBIDO: [
            "rh.atualizar_cadastro",
            "rh.processar_folha",
            "contabil.provisao_encargos",
        ],
        TipoEventoIntegracao.FGTS_GUIA_GERADA: [
            "financeiro.gerar_obrigacao_pagamento",
            "contabil.lancamento_fgts",
        ],
        TipoEventoIntegracao.CTE_RECEBIDO: [
            "compras.registrar_frete",
            "financeiro.gerar_conta_pagar",
            "fiscal.registrar_credito_icms_frete",
        ],
    }

    @classmethod
    async def dispatch(cls, evento: EventoIntegracao, db_session):
        """Despacha evento para todos os handlers registrados."""
        handlers = cls.HANDLERS.get(evento.tipo, [])

        resultados = []
        for handler_path in handlers:
            try:
                # Importar e executar handler
                module_name, func_name = handler_path.rsplit(".", 1)
                module = __import__(f"modules.{module_name}", fromlist=[func_name])
                handler = getattr(module, func_name)

                resultado = await handler(evento, db_session)
                resultados.append({
                    "handler": handler_path,
                    "status": "sucesso",
                    "resultado": resultado,
                })

            except Exception as e:
                logger.error(f"Erro no handler {handler_path}: {e}")
                resultados.append({
                    "handler": handler_path,
                    "status": "erro",
                    "erro": str(e),
                })

        return resultados
```

### 8.3 Integração: Compras/Estoque

```python
# modules/compras/handlers/gov_integration.py
from modules.government_integrations.integration_events import EventoIntegracao
from modules.compras.services import ComprasService
from modules.estoque.services import EstoqueService
from modules.financeiro.services import ContasPagarService

async def processar_nfe_entrada(evento: EventoIntegracao, db_session):
    """
    Processa NF-e de entrada (compra).

    Fluxo:
    1. Buscar/criar fornecedor
    2. Criar pedido de compra (se não existir)
    3. Dar entrada no estoque
    4. Gerar conta a pagar
    """
    dados = evento.dados
    tenant_id = evento.tenant_id

    compras_service = ComprasService(db_session)
    estoque_service = EstoqueService(db_session)
    financeiro_service = ContasPagarService(db_session)

    # 1. Buscar ou criar fornecedor
    fornecedor = await compras_service.buscar_ou_criar_fornecedor(
        cnpj=dados["emitente_cnpj"],
        razao_social=dados["emitente_razao_social"],
        ie=dados.get("emitente_ie"),
        endereco=dados.get("emitente_endereco"),
        tenant_id=tenant_id,
    )

    # 2. Processar itens
    for item in dados.get("itens", []):
        # Buscar produto pelo código ou criar
        produto = await estoque_service.buscar_ou_criar_produto(
            codigo=item["codigo"],
            descricao=item["descricao"],
            ncm=item.get("ncm"),
            unidade=item["unidade"],
            tenant_id=tenant_id,
        )

        # Dar entrada no estoque
        await estoque_service.registrar_entrada(
            produto_id=produto.id,
            quantidade=item["quantidade"],
            custo_unitario=item["valor_unitario"],
            documento_ref=dados["chave_acesso"],
            tenant_id=tenant_id,
        )

    # 3. Gerar conta a pagar
    await financeiro_service.criar_conta_pagar(
        fornecedor_id=fornecedor.id,
        valor=dados["valor_total"],
        data_vencimento=dados.get("data_vencimento"),
        documento_ref=dados["chave_acesso"],
        descricao=f"NF-e {dados['numero']} - {fornecedor.razao_social}",
        tenant_id=tenant_id,
    )

    return {
        "fornecedor_id": str(fornecedor.id),
        "itens_processados": len(dados.get("itens", [])),
        "conta_pagar_gerada": True,
    }
```

### 8.4 Integração: Financeiro

```python
# modules/financeiro/handlers/gov_integration.py
from decimal import Decimal
from datetime import datetime, timedelta

async def processar_guia_fgts(evento: EventoIntegracao, db_session):
    """
    Processa guia FGTS Digital.

    Fluxo:
    1. Registrar obrigação de pagamento
    2. Anexar guia ao lançamento
    3. Criar lançamento contábil
    """
    dados = evento.dados
    tenant_id = evento.tenant_id

    from modules.financeiro.services import ObrigacoesService
    from modules.contabil.services import LancamentoService

    obrigacoes_service = ObrigacoesService(db_session)
    contabil_service = LancamentoService(db_session)

    # 1. Registrar obrigação
    obrigacao = await obrigacoes_service.criar_obrigacao(
        tipo="FGTS",
        competencia=dados["competencia"],
        valor=Decimal(str(dados["valor_total"])),
        data_vencimento=datetime.fromisoformat(dados["data_vencimento"]),
        codigo_barras=dados.get("codigo_barras"),
        linha_digitavel=dados.get("linha_digitavel"),
        tenant_id=tenant_id,
    )

    # 2. Se houver PDF da guia, anexar
    if dados.get("pdf_guia"):
        await obrigacoes_service.anexar_documento(
            obrigacao_id=obrigacao.id,
            tipo="guia_fgts",
            conteudo=dados["pdf_guia"],
            nome_arquivo=f"GRFGTS_{dados['competencia']}.pdf",
        )

    # 3. Lançamento contábil
    # D - FGTS a Recolher (Passivo)
    # C - Banco (Ativo) - quando pago
    await contabil_service.criar_lancamento(
        data=datetime.utcnow(),
        historico=f"Provisão FGTS {dados['competencia']}",
        debito_conta="2.1.2.01.001",  # FGTS a Recolher
        credito_conta="2.1.2.01.002",  # Provisão FGTS
        valor=Decimal(str(dados["valor_total"])),
        documento_ref=f"FGTS-{dados['competencia']}",
        tenant_id=tenant_id,
    )

    return {
        "obrigacao_id": str(obrigacao.id),
        "valor": dados["valor_total"],
        "vencimento": dados["data_vencimento"],
    }

async def processar_dctfweb(evento: EventoIntegracao, db_session):
    """
    Processa DCTFWeb transmitida.

    Gera obrigações para cada DARF/GPS gerado.
    """
    dados = evento.dados
    tenant_id = evento.tenant_id

    from modules.financeiro.services import ObrigacoesService

    obrigacoes_service = ObrigacoesService(db_session)

    obrigacoes_criadas = []

    # Processar DARFs
    for darf in dados.get("darfs", []):
        obrigacao = await obrigacoes_service.criar_obrigacao(
            tipo="DARF",
            codigo_receita=darf["codigo_receita"],
            competencia=dados["periodo_apuracao"],
            valor=Decimal(str(darf["valor"])),
            data_vencimento=datetime.fromisoformat(darf["vencimento"]),
            tenant_id=tenant_id,
        )
        obrigacoes_criadas.append(str(obrigacao.id))

    return {
        "obrigacoes_criadas": len(obrigacoes_criadas),
        "ids": obrigacoes_criadas,
    }
```

### 8.5 Integração: RH

```python
# modules/rh/handlers/gov_integration.py
from datetime import datetime

async def processar_evento_esocial(evento: EventoIntegracao, db_session):
    """
    Processa evento eSocial recebido.

    Atualiza cadastros de colaboradores com base nos eventos.
    """
    dados = evento.dados
    tenant_id = evento.tenant_id
    tipo_evento = dados.get("tipo_evento")

    from modules.rh.services import ColaboradorService, FolhaService

    colaborador_service = ColaboradorService(db_session)
    folha_service = FolhaService(db_session)

    # Mapear tipos de evento para ações
    handlers_evento = {
        "S-2200": _processar_admissao,      # Cadastramento Inicial / Admissão
        "S-2206": _processar_alteracao,     # Alteração de Contrato
        "S-2230": _processar_afastamento,   # Afastamento Temporário
        "S-2299": _processar_desligamento,  # Desligamento
        "S-1200": _processar_remuneracao,   # Remuneração
    }

    handler = handlers_evento.get(tipo_evento)
    if handler:
        return await handler(dados, tenant_id, db_session)

    return {"status": "evento_ignorado", "tipo": tipo_evento}

async def _processar_admissao(dados: dict, tenant_id: str, db_session):
    """Processa evento de admissão S-2200."""
    from modules.rh.services import ColaboradorService

    service = ColaboradorService(db_session)

    colaborador = await service.criar_ou_atualizar(
        cpf=dados["trabalhador"]["cpf"],
        nome=dados["trabalhador"]["nome"],
        data_nascimento=dados["trabalhador"].get("data_nascimento"),
        matricula=dados["vinculo"].get("matricula"),
        data_admissao=dados["vinculo"]["data_admissao"],
        cargo=dados["vinculo"].get("cargo"),
        salario=dados["vinculo"].get("salario_contratual"),
        tenant_id=tenant_id,
    )

    return {
        "acao": "admissao",
        "colaborador_id": str(colaborador.id),
        "cpf": f"***.***.***-{dados['trabalhador']['cpf'][-2:]}",
    }

async def _processar_remuneracao(dados: dict, tenant_id: str, db_session):
    """Processa evento de remuneração S-1200."""
    from modules.rh.services import FolhaService

    service = FolhaService(db_session)

    # Atualizar informações de folha
    await service.registrar_remuneracao(
        cpf=dados["trabalhador"]["cpf"],
        competencia=dados["competencia"],
        remuneracao_bruta=dados["valor_bruto"],
        descontos=dados.get("descontos", []),
        tenant_id=tenant_id,
    )

    return {
        "acao": "remuneracao",
        "competencia": dados["competencia"],
    }
```

### 8.6 Integração: Fiscal

```python
# modules/fiscal/handlers/gov_integration.py
from decimal import Decimal

async def processar_nfe_fiscal(evento: EventoIntegracao, db_session):
    """
    Processa NF-e para apuração fiscal.

    Registra créditos/débitos de ICMS, IPI, PIS, COFINS.
    """
    dados = evento.dados
    tenant_id = evento.tenant_id
    tipo_nfe = dados.get("tipo")  # 0=Entrada, 1=Saída

    from modules.fiscal.services import ApuracaoService

    apuracao_service = ApuracaoService(db_session)

    # Período de apuração (mês/ano da emissão)
    data_emissao = datetime.fromisoformat(dados["data_emissao"])
    periodo = f"{data_emissao.year}{data_emissao.month:02d}"

    if tipo_nfe == 0:  # Entrada - Créditos
        await apuracao_service.registrar_credito(
            periodo=periodo,
            tipo="ICMS",
            valor=Decimal(str(dados.get("valor_icms", 0))),
            documento_ref=dados["chave_acesso"],
            tenant_id=tenant_id,
        )

        if dados.get("valor_ipi"):
            await apuracao_service.registrar_credito(
                periodo=periodo,
                tipo="IPI",
                valor=Decimal(str(dados["valor_ipi"])),
                documento_ref=dados["chave_acesso"],
                tenant_id=tenant_id,
            )

    else:  # Saída - Débitos
        await apuracao_service.registrar_debito(
            periodo=periodo,
            tipo="ICMS",
            valor=Decimal(str(dados.get("valor_icms", 0))),
            documento_ref=dados["chave_acesso"],
            tenant_id=tenant_id,
        )

        if dados.get("valor_ipi"):
            await apuracao_service.registrar_debito(
                periodo=periodo,
                tipo="IPI",
                valor=Decimal(str(dados["valor_ipi"])),
                documento_ref=dados["chave_acesso"],
                tenant_id=tenant_id,
            )

    # PIS/COFINS (regime não-cumulativo)
    if dados.get("valor_pis"):
        await apuracao_service.registrar_movimento(
            periodo=periodo,
            tipo="PIS",
            natureza="credito" if tipo_nfe == 0 else "debito",
            valor=Decimal(str(dados["valor_pis"])),
            documento_ref=dados["chave_acesso"],
            tenant_id=tenant_id,
        )

    if dados.get("valor_cofins"):
        await apuracao_service.registrar_movimento(
            periodo=periodo,
            tipo="COFINS",
            natureza="credito" if tipo_nfe == 0 else "debito",
            valor=Decimal(str(dados["valor_cofins"])),
            documento_ref=dados["chave_acesso"],
            tenant_id=tenant_id,
        )

    return {
        "periodo": periodo,
        "tipo_operacao": "entrada" if tipo_nfe == 0 else "saida",
        "impostos_processados": ["ICMS", "IPI", "PIS", "COFINS"],
    }

async def processar_nfse_fiscal(evento: EventoIntegracao, db_session):
    """
    Processa NFS-e para apuração de ISS.
    """
    dados = evento.dados
    tenant_id = evento.tenant_id

    from modules.fiscal.services import ApuracaoService

    apuracao_service = ApuracaoService(db_session)

    data_emissao = datetime.fromisoformat(dados["data_emissao"])
    periodo = f"{data_emissao.year}{data_emissao.month:02d}"

    # ISS é sempre débito (prestador paga)
    await apuracao_service.registrar_debito(
        periodo=periodo,
        tipo="ISS",
        valor=Decimal(str(dados.get("valor_iss", 0))),
        municipio=dados.get("codigo_municipio"),
        documento_ref=dados["numero_nfse"],
        tenant_id=tenant_id,
    )

    return {
        "periodo": periodo,
        "valor_iss": dados.get("valor_iss"),
        "municipio": dados.get("codigo_municipio"),
    }
```

---

## 9. APÊNDICES

### 9.1 Checklist de Implementação

```markdown
## Checklist - Extração de Dados Governamentais

### Fase 1: Infraestrutura
- [ ] Configurar Vault para credenciais
- [ ] Implementar sistema de filas (Celery + Redis)
- [ ] Configurar monitoramento (Prometheus + Grafana)
- [ ] Criar tabelas de auditoria com particionamento

### Fase 2: Core
- [ ] Implementar classificador de erros
- [ ] Implementar retry com backoff
- [ ] Implementar comutador de endpoints
- [ ] Implementar validador XSD

### Fase 3: Serviços Federais
- [ ] eSocial: extração de eventos
- [ ] EFD-Reinf: extração de movimentos
- [ ] DCTFWeb: consulta de declarações
- [ ] FGTS Digital: extração de guias
- [ ] Simples Nacional: consulta e DAS

### Fase 4: Serviços Estaduais
- [ ] SEFAZ-AM: todos os 7 endpoints
- [ ] Contingência: SVC-AN e SVC-RS
- [ ] CT-e via SVRS
- [ ] MDF-e via SVRS

### Fase 5: Serviços Municipais
- [ ] NFS-e Manaus
- [ ] Preparação NFS-e Nacional

### Fase 6: Integrações Internas
- [ ] Eventos para módulo Compras
- [ ] Eventos para módulo Financeiro
- [ ] Eventos para módulo RH
- [ ] Eventos para módulo Fiscal
- [ ] Eventos para módulo Contábil

### Fase 7: Compliance
- [ ] Logs estruturados com mascaramento
- [ ] Auditoria com hash encadeado
- [ ] Relatórios de conformidade
- [ ] Documentação LGPD
```

### 9.2 Glossário

| Termo | Definição |
|-------|-----------|
| **SEFAZ** | Secretaria da Fazenda (estadual) |
| **SVRS** | SEFAZ Virtual Rio Grande do Sul |
| **SVAN** | SEFAZ Virtual Ambiente Nacional |
| **SVC** | Servidor Virtual de Contingência |
| **EPEC** | Evento Prévio de Emissão em Contingência |
| **NSU** | Número Sequencial Único |
| **DF-e** | Documento Fiscal eletrônico |
| **XSD** | XML Schema Definition |
| **ETL** | Extract, Transform, Load |
| **LGPD** | Lei Geral de Proteção de Dados |

### 9.3 Referências

- Manual de Orientação do Contribuinte NF-e v7.00
- Manual eSocial v. S-1.2
- Manual EFD-Reinf v2.1.2
- Especificação Técnica FGTS Digital
- Padrão Nacional NFS-e (ABRASF/Serpro)
- Lei nº 13.709/2018 (LGPD)

---

**Documento gerado em:** 2026-01-16
**Próxima revisão:** 2026-02-16
**Responsável:** Equipe de Integração Governamental - Conecta PRO

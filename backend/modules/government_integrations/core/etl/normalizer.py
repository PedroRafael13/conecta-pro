"""
Normalizador de Dados para Integrações Governamentais.

Padroniza formatos de dados recebidos dos serviços governamentais.
"""

import logging
import re
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

logger = logging.getLogger(__name__)


def normalizar_cnpj(cnpj: str | None) -> str | None:
    """
    Remove formatação e normaliza CNPJ para 14 dígitos.

    Args:
        cnpj: CNPJ com ou sem formatação

    Returns:
        CNPJ apenas com dígitos (14 caracteres) ou None
    """
    if not cnpj:
        return None

    # Remover tudo que não é dígito
    cnpj_limpo = re.sub(r"\D", "", str(cnpj))

    if not cnpj_limpo:
        return None

    # Garantir 14 dígitos
    return cnpj_limpo.zfill(14)


def normalizar_cpf(cpf: str | None) -> str | None:
    """
    Remove formatação e normaliza CPF para 11 dígitos.

    Args:
        cpf: CPF com ou sem formatação

    Returns:
        CPF apenas com dígitos (11 caracteres) ou None
    """
    if not cpf:
        return None

    # Remover tudo que não é dígito
    cpf_limpo = re.sub(r"\D", "", str(cpf))

    if not cpf_limpo:
        return None

    # Garantir 11 dígitos
    return cpf_limpo.zfill(11)


def normalizar_data(data: str | datetime | date | None, com_timezone: bool = True) -> datetime | None:
    """
    Converte data para datetime UTC.

    Aceita formatos:
    - ISO 8601: YYYY-MM-DDTHH:MM:SS, YYYY-MM-DDTHH:MM:SS-03:00
    - Brasileiro: DD/MM/YYYY, DD/MM/YYYY HH:MM:SS
    - Simples: YYYY-MM-DD

    Args:
        data: Data em string ou objeto datetime/date
        com_timezone: Se True, retorna com timezone UTC

    Returns:
        datetime normalizado ou None
    """
    if not data:
        return None

    # Já é datetime
    if isinstance(data, datetime):
        if com_timezone and data.tzinfo is None:
            return data.replace(tzinfo=UTC)
        return data

    # É date (sem hora)
    if isinstance(data, date):
        dt = datetime.combine(data, datetime.min.time())
        if com_timezone:
            return dt.replace(tzinfo=UTC)
        return dt

    # Converter string
    data_str = str(data).strip()

    # Formatos a tentar (ordem de prioridade)
    formatos = [
        # ISO com timezone
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        # ISO sem timezone
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        # Apenas data ISO
        "%Y-%m-%d",
        # Formato brasileiro
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
        # Outros comuns
        "%Y%m%d",
        "%d-%m-%Y",
    ]

    for fmt in formatos:
        try:
            dt = datetime.strptime(data_str, fmt)
            if com_timezone and dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            return dt
        except ValueError:
            continue

    # Tentar parse ISO mais flexível
    try:
        # Remover microsegundos extras
        data_str = re.sub(r"\.(\d{6})\d+", r".\1", data_str)
        # Normalizar timezone
        data_str = re.sub(r"([+-])(\d{2}):(\d{2})$", r"\1\2\3", data_str)

        for fmt in formatos[:4]:
            try:
                dt = datetime.strptime(data_str, fmt)
                if com_timezone and dt.tzinfo is None:
                    dt = dt.replace(tzinfo=UTC)
                return dt
            except ValueError:
                continue
    except Exception as e:
        logger.debug(f"Erro ao normalizar data: {e}")

    logger.warning(f"Formato de data não reconhecido: {data}")
    return None


def normalizar_valor(valor: str | float | int | Decimal | None, casas_decimais: int = 2) -> Decimal:
    """
    Converte valor para Decimal com precisão definida.

    Remove separadores de milhar e normaliza decimal.
    Aceita formatos brasileiro (1.234,56) e americano (1,234.56).

    Args:
        valor: Valor a normalizar
        casas_decimais: Número de casas decimais

    Returns:
        Decimal normalizado (padrão 0.00 se inválido)
    """
    if valor is None:
        return Decimal("0").quantize(Decimal(10) ** -casas_decimais, rounding=ROUND_HALF_UP)

    # Já é Decimal
    if isinstance(valor, Decimal):
        return valor.quantize(Decimal(10) ** -casas_decimais, rounding=ROUND_HALF_UP)

    # Numérico simples
    if isinstance(valor, (int, float)):
        return Decimal(str(valor)).quantize(Decimal(10) ** -casas_decimais, rounding=ROUND_HALF_UP)

    # String
    valor_str = str(valor).strip()

    if not valor_str:
        return Decimal("0").quantize(Decimal(10) ** -casas_decimais, rounding=ROUND_HALF_UP)

    try:
        # Detectar formato
        # Brasileiro: 1.234,56 -> vírgula como decimal
        # Americano: 1,234.56 -> ponto como decimal

        # Contar ocorrências
        pontos = valor_str.count(".")
        virgulas = valor_str.count(",")

        if virgulas == 1 and pontos >= 1:
            # Formato brasileiro: 1.234,56
            valor_str = valor_str.replace(".", "").replace(",", ".")
        elif virgulas >= 1 and pontos == 1:
            # Formato americano: 1,234.56
            valor_str = valor_str.replace(",", "")
        elif virgulas == 1 and pontos == 0:
            # Apenas vírgula: 123,45
            valor_str = valor_str.replace(",", ".")
        elif pontos == 1 and virgulas == 0:
            # Apenas ponto: 123.45 (já está ok)
            pass
        else:
            # Remover tudo que não é número ou ponto
            valor_str = re.sub(r"[^\d.-]", "", valor_str)

        return Decimal(valor_str).quantize(Decimal(10) ** -casas_decimais, rounding=ROUND_HALF_UP)

    except (InvalidOperation, ValueError) as e:
        logger.warning(f"Valor inválido para conversão: {valor} - {e}")
        return Decimal("0").quantize(Decimal(10) ** -casas_decimais, rounding=ROUND_HALF_UP)


def normalizar_ie(ie: str | None, uf: str | None = None) -> str:
    """
    Normaliza Inscrição Estadual.

    Args:
        ie: Inscrição Estadual
        uf: UF para validação específica (opcional)

    Returns:
        IE normalizada ou "ISENTO"
    """
    if not ie:
        return "ISENTO"

    ie_upper = str(ie).upper().strip()

    # Verificar se é isento
    if ie_upper in ("ISENTO", "ISENTA", "ISENT", ""):
        return "ISENTO"

    # Remover caracteres não numéricos
    ie_limpa = re.sub(r"\D", "", ie_upper)

    if not ie_limpa:
        return "ISENTO"

    return ie_limpa


class NormalizadorDados:
    """
    Classe utilitária para normalização de dados.

    Agrupa todas as funções de normalização com métodos estáticos.
    """

    normalizar_cnpj = staticmethod(normalizar_cnpj)
    normalizar_cpf = staticmethod(normalizar_cpf)
    normalizar_data = staticmethod(normalizar_data)
    normalizar_valor = staticmethod(normalizar_valor)
    normalizar_ie = staticmethod(normalizar_ie)

    @staticmethod
    def normalizar_texto(texto: str | None, max_length: int = None) -> str | None:
        """
        Normaliza texto removendo espaços extras.

        Args:
            texto: Texto a normalizar
            max_length: Tamanho máximo (trunca se exceder)

        Returns:
            Texto normalizado
        """
        if not texto:
            return None

        # Remover espaços extras
        texto_limpo = " ".join(str(texto).split())

        # Truncar se necessário
        if max_length and len(texto_limpo) > max_length:
            texto_limpo = texto_limpo[:max_length]

        return texto_limpo if texto_limpo else None

    @staticmethod
    def normalizar_cep(cep: str | None) -> str | None:
        """
        Normaliza CEP para 8 dígitos.

        Args:
            cep: CEP com ou sem formatação

        Returns:
            CEP apenas com dígitos ou None
        """
        if not cep:
            return None

        cep_limpo = re.sub(r"\D", "", str(cep))

        if len(cep_limpo) < 8:
            return None

        return cep_limpo[:8]

    @staticmethod
    def normalizar_telefone(telefone: str | None) -> str | None:
        """
        Normaliza telefone removendo formatação.

        Args:
            telefone: Telefone com ou sem formatação

        Returns:
            Telefone apenas com dígitos ou None
        """
        if not telefone:
            return None

        # Remover tudo que não é dígito
        tel_limpo = re.sub(r"\D", "", str(telefone))

        if len(tel_limpo) < 8:
            return None

        return tel_limpo

    @staticmethod
    def normalizar_email(email: str | None) -> str | None:
        """
        Normaliza email para minúsculas.

        Args:
            email: Email

        Returns:
            Email em minúsculas ou None se inválido
        """
        if not email:
            return None

        email_limpo = str(email).strip().lower()

        # Validação básica
        if "@" not in email_limpo or "." not in email_limpo:
            return None

        return email_limpo

    @staticmethod
    def normalizar_codigo_municipio(codigo: str | None) -> str | None:
        """
        Normaliza código IBGE de município para 7 dígitos.

        Args:
            codigo: Código do município

        Returns:
            Código com 7 dígitos ou None
        """
        if not codigo:
            return None

        codigo_limpo = re.sub(r"\D", "", str(codigo))

        if len(codigo_limpo) != 7:
            return None

        return codigo_limpo

    @staticmethod
    def normalizar_ncm(ncm: str | None) -> str | None:
        """
        Normaliza NCM para 8 dígitos.

        Args:
            ncm: Código NCM

        Returns:
            NCM com 8 dígitos ou None
        """
        if not ncm:
            return None

        ncm_limpo = re.sub(r"\D", "", str(ncm))

        if len(ncm_limpo) != 8:
            return None

        return ncm_limpo

    @staticmethod
    def normalizar_chave_acesso(chave: str | None) -> str | None:
        """
        Normaliza chave de acesso para 44 dígitos.

        Args:
            chave: Chave de acesso NF-e/CT-e/MDF-e

        Returns:
            Chave com 44 dígitos ou None
        """
        if not chave:
            return None

        chave_limpa = re.sub(r"\D", "", str(chave))

        if len(chave_limpa) != 44:
            return None

        return chave_limpa

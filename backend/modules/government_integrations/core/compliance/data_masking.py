"""
Sistema de Mascaramento de Dados Sensíveis.

Implementa mascaramento para compliance LGPD.
"""

import logging
import re
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TipoDadoSensivel(Enum):
    """Tipos de dados sensíveis."""

    CPF = "cpf"
    CNPJ = "cnpj"
    RG = "rg"
    CNH = "cnh"
    PIS = "pis"
    NIS = "nis"
    TITULO_ELEITOR = "titulo_eleitor"
    EMAIL = "email"
    TELEFONE = "telefone"
    CARTAO_CREDITO = "cartao_credito"
    CONTA_BANCARIA = "conta_bancaria"
    ENDERECO = "endereco"
    NOME = "nome"
    DATA_NASCIMENTO = "data_nascimento"
    SENHA = "senha"
    CHAVE_PIX = "chave_pix"


@dataclass
class RegrasMascaramento:
    """Regras de mascaramento para um tipo de dado."""

    tipo: TipoDadoSensivel
    regex_deteccao: str  # Regex para detectar o dado
    funcao_mascara: Callable[[str], str]
    campos: list[str]  # Nomes de campos que contêm este tipo


def mascarar_cpf(cpf: str) -> str:
    """Mascara CPF mantendo apenas últimos 3 dígitos."""
    if not cpf:
        return ""
    # Remover formatação
    cpf_limpo = re.sub(r"\D", "", cpf)
    if len(cpf_limpo) != 11:
        return "***.***.***-**"
    return f"***.***.*{cpf_limpo[8:11]}-**"


def mascarar_cnpj(cnpj: str) -> str:
    """Mascara CNPJ mantendo apenas primeiros dígitos."""
    if not cnpj:
        return ""
    cnpj_limpo = re.sub(r"\D", "", cnpj)
    if len(cnpj_limpo) != 14:
        return "**.***.***/****.."
    return f"{cnpj_limpo[:2]}.***.***/{cnpj_limpo[8:12]}-**"


def mascarar_email(email: str) -> str:
    """Mascara email mantendo primeiro char e domínio."""
    if not email or "@" not in email:
        return "***@***.***"
    partes = email.split("@")
    usuario = partes[0]
    dominio = partes[1]
    if len(usuario) > 2:
        usuario_mascarado = f"{usuario[0]}***{usuario[-1]}"
    else:
        usuario_mascarado = "***"
    return f"{usuario_mascarado}@{dominio}"


def mascarar_telefone(telefone: str) -> str:
    """Mascara telefone mantendo DDD e últimos 2 dígitos."""
    if not telefone:
        return ""
    telefone_limpo = re.sub(r"\D", "", telefone)
    if len(telefone_limpo) < 10:
        return "(***) ****-****"
    ddd = telefone_limpo[:2]
    ultimos = telefone_limpo[-2:]
    return f"({ddd}) ****-**{ultimos}"


def mascarar_cartao(numero: str) -> str:
    """Mascara número do cartão mantendo últimos 4 dígitos."""
    if not numero:
        return ""
    numero_limpo = re.sub(r"\D", "", numero)
    if len(numero_limpo) < 4:
        return "**** **** **** ****"
    ultimos = numero_limpo[-4:]
    return f"**** **** **** {ultimos}"


def mascarar_conta_bancaria(conta: str) -> str:
    """Mascara conta bancária mantendo último dígito."""
    if not conta:
        return ""
    conta_limpa = re.sub(r"\D", "", conta)
    if len(conta_limpa) < 2:
        return "****-*"
    return f"****-{conta_limpa[-1]}"


def mascarar_nome(nome: str) -> str:
    """Mascara nome mantendo iniciais."""
    if not nome:
        return ""
    partes = nome.split()
    if len(partes) == 1:
        return f"{nome[0]}***"
    return f"{partes[0][0]}. {'*.' * (len(partes) - 2)} {partes[-1][0]}."


def mascarar_endereco(endereco: str) -> str:
    """Mascara endereço mantendo tipo de logradouro."""
    if not endereco:
        return ""
    # Detectar tipo de logradouro
    tipos = ["Rua", "Avenida", "Av.", "Alameda", "Praça", "Travessa"]
    for tipo in tipos:
        if endereco.lower().startswith(tipo.lower()):
            return f"{tipo} ***"
    return "*** ***"


def mascarar_data(data: str) -> str:
    """Mascara data mantendo apenas ano."""
    if not data:
        return ""
    # Tentar extrair ano
    match = re.search(r"\d{4}", data)
    if match:
        return "**/**/****"
    return "**/**/****"


def mascarar_generico(valor: str, manter_inicio: int = 0, manter_fim: int = 0) -> str:
    """Mascaramento genérico."""
    if not valor:
        return ""
    if len(valor) <= manter_inicio + manter_fim:
        return "*" * len(valor)
    inicio = valor[:manter_inicio] if manter_inicio > 0 else ""
    fim = valor[-manter_fim:] if manter_fim > 0 else ""
    meio = "*" * (len(valor) - manter_inicio - manter_fim)
    return f"{inicio}{meio}{fim}"


class MascaradorDados:
    """
    Mascarador de dados sensíveis para compliance LGPD.

    Detecta e mascara automaticamente dados sensíveis em dicionários.
    """

    # Mapeamento de campos para tipos de dados
    MAPEAMENTO_CAMPOS = {
        # CPF
        "cpf": TipoDadoSensivel.CPF,
        "cpf_titular": TipoDadoSensivel.CPF,
        "cpf_responsavel": TipoDadoSensivel.CPF,
        "numero_cpf": TipoDadoSensivel.CPF,
        # CNPJ
        "cnpj": TipoDadoSensivel.CNPJ,
        "cnpj_empresa": TipoDadoSensivel.CNPJ,
        "numero_cnpj": TipoDadoSensivel.CNPJ,
        # RG
        "rg": TipoDadoSensivel.RG,
        "numero_rg": TipoDadoSensivel.RG,
        # PIS/NIS
        "pis": TipoDadoSensivel.PIS,
        "numero_pis": TipoDadoSensivel.PIS,
        "nis": TipoDadoSensivel.NIS,
        "numero_nis": TipoDadoSensivel.NIS,
        # Contato
        "email": TipoDadoSensivel.EMAIL,
        "email_pessoal": TipoDadoSensivel.EMAIL,
        "email_corporativo": TipoDadoSensivel.EMAIL,
        "telefone": TipoDadoSensivel.TELEFONE,
        "celular": TipoDadoSensivel.TELEFONE,
        "fone": TipoDadoSensivel.TELEFONE,
        # Financeiro
        "numero_cartao": TipoDadoSensivel.CARTAO_CREDITO,
        "cartao_credito": TipoDadoSensivel.CARTAO_CREDITO,
        "conta_bancaria": TipoDadoSensivel.CONTA_BANCARIA,
        "conta_corrente": TipoDadoSensivel.CONTA_BANCARIA,
        "numero_conta": TipoDadoSensivel.CONTA_BANCARIA,
        # Pessoal
        "nome": TipoDadoSensivel.NOME,
        "nome_completo": TipoDadoSensivel.NOME,
        "nome_funcionario": TipoDadoSensivel.NOME,
        "data_nascimento": TipoDadoSensivel.DATA_NASCIMENTO,
        "nascimento": TipoDadoSensivel.DATA_NASCIMENTO,
        # Endereço
        "endereco": TipoDadoSensivel.ENDERECO,
        "logradouro": TipoDadoSensivel.ENDERECO,
        "endereco_residencial": TipoDadoSensivel.ENDERECO,
        # Segurança
        "senha": TipoDadoSensivel.SENHA,
        "password": TipoDadoSensivel.SENHA,
        "secret": TipoDadoSensivel.SENHA,
        "token": TipoDadoSensivel.SENHA,
        "api_key": TipoDadoSensivel.SENHA,
        # PIX
        "chave_pix": TipoDadoSensivel.CHAVE_PIX,
        "pix": TipoDadoSensivel.CHAVE_PIX,
    }

    # Funções de mascaramento por tipo
    FUNCOES_MASCARA = {
        TipoDadoSensivel.CPF: mascarar_cpf,
        TipoDadoSensivel.CNPJ: mascarar_cnpj,
        TipoDadoSensivel.RG: lambda x: mascarar_generico(x, manter_fim=3),
        TipoDadoSensivel.CNH: lambda x: mascarar_generico(x, manter_fim=4),
        TipoDadoSensivel.PIS: lambda x: mascarar_generico(x, manter_fim=4),
        TipoDadoSensivel.NIS: lambda x: mascarar_generico(x, manter_fim=4),
        TipoDadoSensivel.TITULO_ELEITOR: lambda x: mascarar_generico(x, manter_fim=4),
        TipoDadoSensivel.EMAIL: mascarar_email,
        TipoDadoSensivel.TELEFONE: mascarar_telefone,
        TipoDadoSensivel.CARTAO_CREDITO: mascarar_cartao,
        TipoDadoSensivel.CONTA_BANCARIA: mascarar_conta_bancaria,
        TipoDadoSensivel.ENDERECO: mascarar_endereco,
        TipoDadoSensivel.NOME: mascarar_nome,
        TipoDadoSensivel.DATA_NASCIMENTO: mascarar_data,
        TipoDadoSensivel.SENHA: lambda x: "********",
        TipoDadoSensivel.CHAVE_PIX: lambda x: mascarar_generico(x, manter_inicio=3, manter_fim=3),
    }

    # Regex para detecção automática
    REGEX_DETECCAO = {
        TipoDadoSensivel.CPF: r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}",
        TipoDadoSensivel.CNPJ: r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}",
        TipoDadoSensivel.EMAIL: r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        TipoDadoSensivel.TELEFONE: r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}",
        TipoDadoSensivel.CARTAO_CREDITO: r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}",
    }

    def __init__(self, campos_customizados: dict[str, TipoDadoSensivel] | None = None):
        self.mapeamento_campos = self.MAPEAMENTO_CAMPOS.copy()
        if campos_customizados:
            self.mapeamento_campos.update(campos_customizados)

    def mascarar(
        self, dados: dict[str, Any], campos_excluir: list[str] | None = None, detectar_automatico: bool = True
    ) -> dict[str, Any]:
        """
        Mascara dados sensíveis em um dicionário.

        Args:
            dados: Dicionário com dados a mascarar
            campos_excluir: Campos que não devem ser mascarados
            detectar_automatico: Se deve detectar dados sensíveis por regex

        Returns:
            Dicionário com dados mascarados
        """
        if not dados:
            return {}

        campos_excluir = campos_excluir or []
        resultado = {}

        for campo, valor in dados.items():
            # Ignorar campos excluídos
            if campo in campos_excluir:
                resultado[campo] = valor
                continue

            # Processar dicionários aninhados
            if isinstance(valor, dict):
                resultado[campo] = self.mascarar(valor, campos_excluir, detectar_automatico)
                continue

            # Processar listas
            if isinstance(valor, list):
                resultado[campo] = [
                    self.mascarar(item, campos_excluir, detectar_automatico) if isinstance(item, dict) else item
                    for item in valor
                ]
                continue

            # Verificar se é campo sensível conhecido
            campo_lower = campo.lower()
            tipo = self.mapeamento_campos.get(campo_lower)

            if tipo and isinstance(valor, str):
                funcao = self.FUNCOES_MASCARA.get(tipo)
                if funcao:
                    resultado[campo] = funcao(valor)
                    continue

            # Detecção automática
            if detectar_automatico and isinstance(valor, str):
                valor_mascarado = self._detectar_e_mascarar(valor)
                resultado[campo] = valor_mascarado
            else:
                resultado[campo] = valor

        return resultado

    def _detectar_e_mascarar(self, texto: str) -> str:
        """Detecta e mascara dados sensíveis em texto livre."""
        if not texto:
            return texto

        resultado = texto

        for tipo, regex in self.REGEX_DETECCAO.items():
            funcao = self.FUNCOES_MASCARA.get(tipo)
            if not funcao:
                continue

            matches = re.finditer(regex, resultado)
            for match in matches:
                valor_original = match.group()
                valor_mascarado = funcao(valor_original)
                resultado = resultado.replace(valor_original, valor_mascarado, 1)

        return resultado

    def mascarar_campo(self, valor: str, tipo: TipoDadoSensivel) -> str:
        """Mascara um campo específico."""
        funcao = self.FUNCOES_MASCARA.get(tipo)
        if funcao:
            return funcao(valor)
        return mascarar_generico(valor)

    def adicionar_mapeamento(self, campo: str, tipo: TipoDadoSensivel):
        """Adiciona mapeamento customizado de campo."""
        self.mapeamento_campos[campo.lower()] = tipo

    def obter_campos_sensiveis(self, dados: dict) -> list[str]:
        """Lista campos sensíveis encontrados nos dados."""
        campos = []

        def buscar(d: dict, prefixo: str = ""):
            for campo, valor in d.items():
                caminho = f"{prefixo}.{campo}" if prefixo else campo
                campo_lower = campo.lower()

                if campo_lower in self.mapeamento_campos:
                    campos.append(caminho)

                if isinstance(valor, dict):
                    buscar(valor, caminho)

        buscar(dados)
        return campos


# Funções de conveniência exportadas
__all__ = [
    "MascaradorDados",
    "TipoDadoSensivel",
    "mascarar_cpf",
    "mascarar_cnpj",
    "mascarar_email",
    "mascarar_telefone",
    "mascarar_cartao",
    "mascarar_nome",
    "mascarar_generico",
]

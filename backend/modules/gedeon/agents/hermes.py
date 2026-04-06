"""
HERMES — Agente Documental do GEDEON
"Nenhum documento se perde, nenhum é duplicado"

Responsabilidades:
- Classificação automática de documentos uploadados
- Detecção de duplicatas por hash SHA-256
- Cache de documentos reutilizáveis entre meses
- Validação de autenticidade (chave de acesso NFS-e)
"""

import hashlib
import logging
import re

logger = logging.getLogger(__name__)

# Tipos de documento reconhecidos automaticamente
TIPOS_DOCUMENTO = {
    # Folha de pagamento
    r"holerite|contracheque|recibo.*salario": "holerite",
    r"folha.*pagamento|payroll": "folha_pagamento",
    r"espelho.*ponto|ponto.*espelho|timesheet": "espelho_ponto",
    # Admissão/Demissão
    r"admiss[aã]o|contrato.*trabalho": "contrato_admissao",
    r"demiss[aã]o|rescis[aã]o|trct": "rescisao",
    r"seguro.*desemprego": "seguro_desemprego",
    # Saúde
    r"aso|atestado.*saude.*ocupacional": "aso",
    r"atestado.*medico|medical.*certificate": "atestado_medico",
    r"epi|equipamento.*protecao": "ficha_epi",
    # Certidões
    r"cnd|certidao.*negativa.*debito": "cnd_federal",
    r"crf.*fgts|regularidade.*fgts": "crf_fgts",
    r"certidao.*trabalhista": "certidao_trabalhista",
    r"alvara.*funcionamento": "alvara_funcionamento",
    # Fiscal
    r"nota.*fiscal|nfs?-?e|nfse": "nota_fiscal",
    r"boleto|cobranca": "boleto",
    # Treinamentos
    r"nr-?\d+|treinamento|certificado.*curso": "certificado_nr",
}

# Categorias por tipo
_CATEGORIAS: dict[str, str] = {
    "holerite": "folha_pagamento",
    "folha_pagamento": "folha_pagamento",
    "espelho_ponto": "folha_pagamento",
    "contrato_admissao": "admissao",
    "rescisao": "demissao",
    "seguro_desemprego": "demissao",
    "aso": "saude",
    "atestado_medico": "saude",
    "ficha_epi": "saude",
    "cnd_federal": "certidoes",
    "crf_fgts": "certidoes",
    "certidao_trabalhista": "certidoes",
    "alvara_funcionamento": "certidoes",
    "nota_fiscal": "fiscal",
    "boleto": "fiscal",
    "certificado_nr": "treinamento",
}

# Tipos reutilizáveis entre meses
_REUTILIZAVEIS: dict[str, bool] = {
    "cnd_federal": True,
    "crf_fgts": False,  # validade mensal
    "certidao_trabalhista": True,
    "alvara_funcionamento": True,
    "holerite": False,
    "espelho_ponto": False,
    "aso": True,  # validade anual
    "ficha_epi": False,
    "nota_fiscal": False,
    "boleto": False,
}


class Hermes:
    """
    Agente Documental — classificação e gestão inteligente
    de documentos do GEDEON.
    """

    def classificar_documento(
        self,
        nome_arquivo: str,
        conteudo_preview: str = "",
    ) -> dict:
        """
        Classificar documento automaticamente.
        Retorna tipo, categoria e metadados detectados.
        """
        texto = (nome_arquivo + " " + conteudo_preview).lower()
        texto = re.sub(r"[_\-.]", " ", texto)

        for pattern, tipo in TIPOS_DOCUMENTO.items():
            if re.search(pattern, texto, re.IGNORECASE):
                return {
                    "tipo": tipo,
                    "categoria": _CATEGORIAS.get(tipo, "outros"),
                    "confianca": "alta",
                    "auto": True,
                }

        return {
            "tipo": "outros",
            "categoria": "outros",
            "confianca": "baixa",
            "auto": False,
        }

    def detectar_duplicata(
        self,
        arquivo_hash: str,
        documentos_existentes: list[dict],
    ) -> dict | None:
        """Detectar se documento já existe pelo hash."""
        for doc in documentos_existentes:
            if doc.get("hash") == arquivo_hash:
                return doc
        return None

    def calcular_hash(self, conteudo: bytes) -> str:
        """Calcular hash SHA-256 do documento."""
        return hashlib.sha256(conteudo).hexdigest()

    def pode_reutilizar(
        self,
        tipo: str,
        competencia_anterior: str,
        competencia_atual: str,
    ) -> bool:
        """
        Verificar se documento pode ser reutilizado do mês anterior.
        Certidões de longa validade: podem reutilizar.
        Holerites e espelhos de ponto: sempre novo.
        """
        return _REUTILIZAVEIS.get(tipo, False)

    async def processar_upload(
        self,
        nome_arquivo: str,
        conteudo: bytes,
        cliente_id: str,
        competencia: str,
        funcionario_id: str | None = None,
    ) -> dict:
        """
        Processar upload completo:
        1. Classificar automaticamente
        2. Calcular hash (detecção de duplicata)
        3. Retornar metadados para salvar
        """
        classificacao = self.classificar_documento(nome_arquivo)
        arquivo_hash = self.calcular_hash(conteudo)

        resultado = {
            "nome_original": nome_arquivo,
            "tipo": classificacao["tipo"],
            "categoria": classificacao["categoria"],
            "auto_classificado": classificacao["auto"],
            "hash": arquivo_hash,
            "cliente_id": cliente_id,
            "competencia": competencia,
            "funcionario_id": funcionario_id,
            "tamanho_bytes": len(conteudo),
        }

        logger.info(
            "HERMES: documento classificado — %s → %s [%s]",
            nome_arquivo,
            classificacao["tipo"],
            "auto" if classificacao["auto"] else "manual",
        )
        return resultado


# Singleton global
hermes = Hermes()

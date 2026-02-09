"""
Service de IA para Licitacoes
=============================
Analise inteligente de editais e propostas.
"""

import logging
import re
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class BiddingAIService:
    """Service de IA para analise de licitacoes."""

    # Palavras-chave por segmento
    SEGMENTOS_KEYWORDS = {
        "seguranca": [
            "vigilância",
            "vigilancia",
            "segurança",
            "seguranca",
            "portaria",
            "monitoramento",
            "cftv",
            "alarme",
            "ronda",
            "vigilante",
            "controlador de acesso",
        ],
        "limpeza": [
            "limpeza",
            "conservação",
            "conservacao",
            "asseio",
            "higienização",
            "higienizacao",
            "faxina",
            "jardinagem",
            "copeira",
            "servente",
        ],
        "facilities": [
            "facilities",
            "terceirização",
            "terceirizacao",
            "mão de obra",
            "mao de obra",
            "apoio administrativo",
            "recepção",
            "recepcao",
            "telefonista",
        ],
        "manutencao": [
            "manutenção",
            "manutencao",
            "predial",
            "elétrica",
            "eletrica",
            "hidráulica",
            "hidraulica",
            "ar condicionado",
            "elevador",
        ],
        "ti": [
            "tecnologia",
            "informática",
            "informatica",
            "software",
            "hardware",
            "rede",
            "suporte técnico",
            "suporte tecnico",
        ],
    }

    # Documentos comuns exigidos
    DOCUMENTOS_COMUNS = {
        "habilitacao_juridica": ["contrato social", "estatuto", "cnpj", "procuração"],
        "regularidade_fiscal": ["cnd federal", "cnd estadual", "cnd municipal", "fgts", "crf", "cndt", "trabalhista"],
        "qualificacao_tecnica": ["atestado", "capacidade técnica", "acervo", "registro", "crea", "cra"],
        "qualificacao_economica": ["balanço", "patrimônio líquido", "índice", "falência", "recuperação judicial"],
    }

    def __init__(self, db: Session):
        self.db = db

    async def classificar_edital(self, texto_objeto: str) -> dict[str, Any]:
        """
        Classifica um edital por segmento baseado no objeto.

        Args:
            texto_objeto: Texto do objeto da licitacao

        Returns:
            Dict com segmento identificado e confianca
        """
        texto_lower = texto_objeto.lower()
        scores = {}

        for segmento, keywords in self.SEGMENTOS_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in texto_lower)
            if score > 0:
                scores[segmento] = score

        if not scores:
            return {"segmento": "outros", "confianca": 0, "segmentos_possiveis": []}

        # Segmento com maior score
        segmento_principal = max(scores, key=scores.get)
        total_matches = sum(scores.values())

        return {
            "segmento": segmento_principal,
            "confianca": scores[segmento_principal] / total_matches if total_matches > 0 else 0,
            "segmentos_possiveis": [
                {"segmento": s, "score": sc} for s, sc in sorted(scores.items(), key=lambda x: -x[1])
            ],
        }

    async def extrair_requisitos(self, texto_edital: str) -> dict[str, list[str]]:
        """
        Extrai requisitos de habilitacao do texto do edital.

        Args:
            texto_edital: Texto completo do edital

        Returns:
            Dict com requisitos por categoria
        """
        texto_lower = texto_edital.lower()
        requisitos = {
            "habilitacao_juridica": [],
            "regularidade_fiscal": [],
            "qualificacao_tecnica": [],
            "qualificacao_economica": [],
            "outros": [],
        }

        for categoria, keywords in self.DOCUMENTOS_COMUNS.items():
            for kw in keywords:
                if kw in texto_lower:
                    # Tenta extrair contexto
                    pattern = rf"[^.]*{re.escape(kw)}[^.]*\."
                    matches = re.findall(pattern, texto_lower)
                    if matches:
                        requisitos[categoria].extend(matches[:3])  # Max 3 por keyword

        return requisitos

    async def analisar_viabilidade(
        self, valor_estimado: Decimal, segmento: str, documentos_disponiveis: list[str], documentos_exigidos: list[str]
    ) -> dict[str, Any]:
        """
        Analisa viabilidade de participacao em licitacao.

        Args:
            valor_estimado: Valor estimado da licitacao
            segmento: Segmento identificado
            documentos_disponiveis: Documentos que a empresa possui
            documentos_exigidos: Documentos exigidos pelo edital

        Returns:
            Analise de viabilidade
        """
        # Verifica documentacao
        docs_faltantes = [d for d in documentos_exigidos if d not in documentos_disponiveis]

        # Score de documentacao
        if not documentos_exigidos:
            score_docs = 100
        else:
            score_docs = (len(documentos_exigidos) - len(docs_faltantes)) / len(documentos_exigidos) * 100

        # Analise de valor
        analise_valor = self._analisar_faixa_valor(valor_estimado, segmento)

        # Score geral
        score_geral = (score_docs * 0.6) + (analise_valor["score"] * 0.4)

        # Recomendacao
        if score_geral >= 80:
            recomendacao = "ALTA - Recomendado participar"
        elif score_geral >= 60:
            recomendacao = "MEDIA - Avaliar com atencao"
        elif score_geral >= 40:
            recomendacao = "BAIXA - Necessario providencias"
        else:
            recomendacao = "MUITO BAIXA - Nao recomendado"

        return {
            "score_geral": round(score_geral, 1),
            "score_documentacao": round(score_docs, 1),
            "score_valor": analise_valor["score"],
            "documentos_faltantes": docs_faltantes,
            "analise_valor": analise_valor,
            "recomendacao": recomendacao,
            "acoes_necessarias": self._gerar_acoes(docs_faltantes, analise_valor),
        }

    async def sugerir_bdi(
        self, tipo_servico: str, valor_base: Decimal, regime_tributario: str = "lucro_presumido"
    ) -> dict[str, Any]:
        """
        Sugere composicao de BDI baseado no tipo de servico.

        Args:
            tipo_servico: Tipo de servico (seguranca, limpeza, etc)
            valor_base: Valor base para calculo
            regime_tributario: Regime tributario da empresa

        Returns:
            Sugestao de BDI
        """
        # BDI padrao por tipo de servico (baseado em referencias de mercado)
        bdi_referencia = {
            "seguranca": {
                "administracao": 4.0,
                "seguro": 0.8,
                "garantia": 0.5,
                "risco": 1.5,
                "despesas_financeiras": 1.0,
                "lucro": 6.5,
            },
            "limpeza": {
                "administracao": 3.5,
                "seguro": 0.6,
                "garantia": 0.5,
                "risco": 1.0,
                "despesas_financeiras": 0.8,
                "lucro": 6.0,
            },
            "facilities": {
                "administracao": 4.0,
                "seguro": 0.7,
                "garantia": 0.5,
                "risco": 1.2,
                "despesas_financeiras": 0.9,
                "lucro": 6.0,
            },
            "default": {
                "administracao": 4.0,
                "seguro": 0.8,
                "garantia": 0.5,
                "risco": 1.0,
                "despesas_financeiras": 1.0,
                "lucro": 7.0,
            },
        }

        # Tributos por regime
        tributos = {
            "simples": {"pis": 0, "cofins": 0, "iss": 5.0},
            "lucro_presumido": {"pis": 0.65, "cofins": 3.0, "iss": 5.0},
            "lucro_real": {"pis": 1.65, "cofins": 7.6, "iss": 5.0},
        }

        ref = bdi_referencia.get(tipo_servico, bdi_referencia["default"])
        trib = tributos.get(regime_tributario, tributos["lucro_presumido"])

        # Calcula BDI
        custos = ref["administracao"] + ref["seguro"] + ref["garantia"] + ref["risco"] + ref["despesas_financeiras"]
        tributos_total = trib["pis"] + trib["cofins"] + trib["iss"]

        # Formula: BDI = [(1 + AC + S + G + R + DF) * (1 + L)] / (1 - T) - 1
        fator_custos = 1 + (custos / 100)
        fator_lucro = 1 + (ref["lucro"] / 100)
        fator_tributos = 1 - (tributos_total / 100)

        bdi_percentual = ((fator_custos * fator_lucro) / fator_tributos - 1) * 100
        valor_com_bdi = valor_base * (1 + bdi_percentual / 100)

        return {
            "bdi_percentual": round(bdi_percentual, 2),
            "valor_base": float(valor_base),
            "valor_com_bdi": round(float(valor_com_bdi), 2),
            "composicao": {**ref, "tributos": tributos_total},
            "tributos_detalhados": trib,
            "regime_tributario": regime_tributario,
            "observacao": f"BDI sugerido para {tipo_servico} em regime {regime_tributario}",
        }

    async def analisar_concorrentes(
        self, historico_lances: list[dict[str, Any]], valor_estimado: Decimal
    ) -> dict[str, Any]:
        """
        Analisa padrao de concorrentes baseado em historico.

        Args:
            historico_lances: Historico de lances de licitacoes anteriores
            valor_estimado: Valor estimado atual

        Returns:
            Analise de concorrentes
        """
        if not historico_lances:
            return {"analise_disponivel": False, "mensagem": "Sem historico suficiente para analise"}

        # Extrai valores
        valores = [Decimal(str(lance.get("valor", 0))) for lance in historico_lances if lance.get("valor")]

        if not valores:
            return {"analise_disponivel": False, "mensagem": "Historico sem valores validos"}

        # Estatisticas
        valor_medio = sum(valores) / len(valores)
        valor_min = min(valores)
        valor_max = max(valores)

        # Desconto medio sobre estimado
        descontos = []
        for lance in historico_lances:
            if lance.get("valor") and lance.get("valor_estimado"):
                desc = (1 - Decimal(str(lance["valor"])) / Decimal(str(lance["valor_estimado"]))) * 100
                descontos.append(desc)

        desconto_medio = sum(descontos) / len(descontos) if descontos else Decimal("0")

        # Sugestao de lance
        lance_sugerido = valor_estimado * (1 - desconto_medio / 100)

        return {
            "analise_disponivel": True,
            "total_lances_analisados": len(valores),
            "valor_medio_lances": float(valor_medio),
            "valor_minimo": float(valor_min),
            "valor_maximo": float(valor_max),
            "desconto_medio_percentual": float(desconto_medio),
            "lance_sugerido": float(lance_sugerido),
            "faixa_competitiva": {
                "minimo": float(lance_sugerido * Decimal("0.95")),
                "maximo": float(lance_sugerido * Decimal("1.05")),
            },
        }

    def _analisar_faixa_valor(self, valor: Decimal, segmento: str) -> dict[str, Any]:
        """Analisa se valor esta em faixa adequada."""
        # Faixas de referencia por segmento (valores mensais tipicos)
        faixas = {
            "seguranca": {"min": 50000, "ideal_min": 100000, "ideal_max": 2000000, "max": 5000000},
            "limpeza": {"min": 30000, "ideal_min": 80000, "ideal_max": 1500000, "max": 3000000},
            "facilities": {"min": 50000, "ideal_min": 100000, "ideal_max": 2000000, "max": 5000000},
            "default": {"min": 30000, "ideal_min": 100000, "ideal_max": 2000000, "max": 5000000},
        }

        faixa = faixas.get(segmento, faixas["default"])
        valor_float = float(valor)

        if valor_float < faixa["min"]:
            return {"score": 40, "classificacao": "muito_baixo", "mensagem": "Valor abaixo do minimo recomendado"}
        elif valor_float < faixa["ideal_min"]:
            return {"score": 60, "classificacao": "baixo", "mensagem": "Valor abaixo do ideal"}
        elif valor_float <= faixa["ideal_max"]:
            return {"score": 100, "classificacao": "ideal", "mensagem": "Valor dentro da faixa ideal"}
        elif valor_float <= faixa["max"]:
            return {"score": 80, "classificacao": "alto", "mensagem": "Valor acima do ideal mas viavel"}
        else:
            return {"score": 50, "classificacao": "muito_alto", "mensagem": "Valor muito elevado"}

    def _gerar_acoes(self, docs_faltantes: list[str], analise_valor: dict[str, Any]) -> list[str]:
        """Gera lista de acoes necessarias."""
        acoes = []

        if docs_faltantes:
            acoes.append(f"Providenciar {len(docs_faltantes)} documento(s) faltante(s)")
            for doc in docs_faltantes[:3]:
                acoes.append(f"  - Obter: {doc}")

        if analise_valor["classificacao"] == "muito_baixo":
            acoes.append("Avaliar se margem e viavel para esse valor")
        elif analise_valor["classificacao"] == "muito_alto":
            acoes.append("Verificar capacidade operacional para contrato de grande porte")

        if not acoes:
            acoes.append("Nenhuma acao pendente - pronto para participar")

        return acoes

"""
ARGOS — Agente de Conformidade do GEDEON
"Nenhum kit sai incompleto"

Responsabilidades:
- Verificar conformidade de cada kit contra checklist contratual
- Calcular score de conformidade 0-100%
- Identificar documentos faltantes
- Bloquear envio de kits abaixo do score mínimo
- Adaptar checklist ao tipo de kit (mão de obra vs seg. eletrônica)
"""

import logging

logger = logging.getLogger(__name__)

# ── Checklists por tipo de kit ────────────────────────────────────────────────

CHECKLIST_MAOS_DE_OBRA: dict = {
    "obrigatorio": [
        "holerite",
        "espelho_ponto",
        "nota_fiscal",
    ],
    "recomendado": [
        "cnd_federal",
        "crf_fgts",
        "certidao_trabalhista",
    ],
    "condicional": {
        "admissao": ["contrato_admissao", "aso"],
        "demissao": ["rescisao", "seguro_desemprego"],
        "atestado": ["atestado_medico"],
        "cat": ["ficha_cat"],
    },
}

CHECKLIST_SEGURANCA_ELETRONICA: dict = {
    "obrigatorio": [
        "nota_fiscal",
        "boleto",
    ],
    "recomendado": [],
    "condicional": {},
}

SCORE_MINIMO_ENVIO = 70  # % mínimo para permitir envio


class Argos:
    """
    Agente de Conformidade — verifica se o kit está
    completo antes de permitir o envio ao cliente.
    """

    def _get_checklist(self, tipo_kit: str) -> dict:
        if tipo_kit == "seguranca_eletronica":
            return CHECKLIST_SEGURANCA_ELETRONICA
        return CHECKLIST_MAOS_DE_OBRA

    def verificar_conformidade(
        self,
        tipo_kit: str,
        documentos_presentes: list[str],
        movimentacoes: list[dict],
        certidoes_status: dict,
    ) -> dict:
        """
        Verificar conformidade completa do kit.
        Retorna score, itens ok, itens faltando e bloqueios.
        """
        checklist = self._get_checklist(tipo_kit)
        faltando: list[dict] = []
        presentes: list[str] = []
        alertas: list[dict] = []

        # Verificar obrigatórios
        for doc_tipo in checklist["obrigatorio"]:
            if doc_tipo in documentos_presentes:
                presentes.append(doc_tipo)
            else:
                faltando.append(
                    {
                        "tipo": doc_tipo,
                        "nivel": "critico",
                        "mensagem": f"{doc_tipo} obrigatório ausente",
                    }
                )

        # Verificar recomendados
        for doc_tipo in checklist.get("recomendado", []):
            if doc_tipo in documentos_presentes:
                presentes.append(doc_tipo)
            else:
                alertas.append(
                    {
                        "tipo": doc_tipo,
                        "nivel": "alerta",
                        "mensagem": f"{doc_tipo} recomendado ausente",
                    }
                )

        # Verificar condicionais baseado em movimentações
        for mov in movimentacoes:
            tipo_mov = mov.get("tipo", "")
            docs_cond = checklist.get("condicional", {}).get(tipo_mov, [])
            for doc_tipo in docs_cond:
                if doc_tipo not in documentos_presentes:
                    faltando.append(
                        {
                            "tipo": doc_tipo,
                            "nivel": "critico",
                            "funcionario": mov.get("funcionario", ""),
                            "mensagem": (f"{doc_tipo} necessário por {tipo_mov} de {mov.get('funcionario', '')}"),
                        }
                    )

        # Penalizar por certidões críticas
        certidoes_criticas = certidoes_status.get("critico", 0)
        penalidade = certidoes_criticas * 20

        # Calcular score
        total_obrig = len(checklist["obrigatorio"])
        docs_faltando_obrig = [f for f in faltando if f["nivel"] == "critico" and f["tipo"] in checklist["obrigatorio"]]
        if total_obrig > 0:
            score_docs = (total_obrig - len(docs_faltando_obrig)) / total_obrig * 100
        else:
            score_docs = 100.0

        score_final = max(0, int(score_docs - penalidade))
        pode_enviar = score_final >= SCORE_MINIMO_ENVIO and len(faltando) == 0

        return {
            "score": score_final,
            "pode_enviar": pode_enviar,
            "presentes": presentes,
            "faltando": faltando,
            "alertas": alertas,
            "certidoes_criticas": certidoes_criticas,
            "bloqueado_por": ([f["mensagem"] for f in faltando] if not pode_enviar else []),
        }

    def gerar_relatorio_conformidade(
        self,
        cliente_nome: str,
        competencia: str,
        resultado: dict,
    ) -> str:
        """Gerar relatório textual de conformidade."""
        score = resultado["score"]
        emoji = "✅" if score >= 90 else ("⚠️" if score >= 70 else "🔴")
        linhas = [
            f"ARGOS — Conformidade {cliente_nome} {competencia}",
            f"Score: {score}% {emoji}",
            f"Status: {'APROVADO' if resultado['pode_enviar'] else 'BLOQUEADO'}",
        ]
        if resultado["faltando"]:
            linhas.append("\nDocs faltando:")
            for f in resultado["faltando"]:
                linhas.append(f"  🔴 {f['mensagem']}")
        if resultado["alertas"]:
            linhas.append("\nAlertas:")
            for a in resultado["alertas"]:
                linhas.append(f"  ⚠️  {a['mensagem']}")
        return "\n".join(linhas)


# Singleton global
argos = Argos()

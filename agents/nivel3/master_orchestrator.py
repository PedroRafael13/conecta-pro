"""
MasterOrchestrator — Coordena TODOS os agentes dos 3 níveis.
Gera o relatório noturno completo para Jordan via Telegram.

Ciclos:
- 30min: Compliance + DataQuality (lightweight)
- Diário (2h): + Performance + Security + Coverage + Contract
- Semanal (domingo 3h): + Business + AuditAgent completo
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "/opt/conecta-pro/agents/core")
sys.path.insert(0, "/opt/conecta-pro/agents/nivel3")
sys.path.insert(0, "/opt/conecta-pro/agents")

TELEGRAM_TOKEN = "8562364686:AAESOC6uXddwShWSs3_1-qJ4lBiZHBiSuBQ"  # pragma: allowlist secret
TELEGRAM_CHAT = "5536961034"
REPORTS_DIR = Path("/opt/conecta-pro/reports/master")


def _obter_token() -> str:
    r = subprocess.run(
        "curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login "
        "-H 'Content-Type: application/x-www-form-urlencoded' "
        "-d 'username=jjesus@conectamais.pro&password=Jordan0612'",  # pragma: allowlist secret
        shell=True, capture_output=True, text=True,
    )
    try:
        return json.loads(r.stdout).get("access_token", "")
    except Exception:
        return ""


class MasterOrchestrator:
    """Orquestra os 3 níveis de agentes."""

    def __init__(self, token: str = "", ciclo: str = "30min"):
        """
        ciclo: '30min' | 'diario' | 'semanal'
        """
        self.token = token or _obter_token()
        self.ciclo = ciclo
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    def _telegram(self, mensagem: str):
        subprocess.run(
            f'curl -sf -X POST '
            f'"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage" '
            f'-d "chat_id={TELEGRAM_CHAT}&parse_mode=HTML" '
            f'--data-urlencode "text={mensagem}" > /dev/null',
            shell=True,
        )

    def _rodar_agente(self, nome: str, cls, *args) -> dict:
        """Executa um agente capturando exceções."""
        try:
            return cls(*args).auditar()
        except Exception as e:
            print(f"  ❌ {nome}: {e}")
            return {"agente": nome, "score": 0, "bugs": [], "erro": str(e)}

    def executar(self) -> dict:
        """Executa o ciclo conforme o tipo."""
        inicio = datetime.now()

        print(f"\n{'='*60}")
        print(
            f"MASTER ORCHESTRATOR — {self.ciclo.upper()} — "
            f"{inicio.strftime('%Y-%m-%d %H:%M')}"
        )
        print(f"{'='*60}")

        resultados = {}

        # ─── SEMPRE: Compliance + DataQuality ─────────────
        from compliance_agent import ComplianceAgent
        from data_quality_agent import DataQualityAgent

        print("\n[N3] ComplianceAgent...")
        resultados["compliance"] = self._rodar_agente(
            "compliance", ComplianceAgent, self.token
        )

        print("\n[N3] DataQualityAgent...")
        resultados["data_quality"] = self._rodar_agente(
            "data_quality", DataQualityAgent, self.token
        )

        # ─── DIÁRIO: + Performance + Security + Coverage + Contract
        if self.ciclo in ["diario", "semanal"]:
            from performance_agent import PerformanceAgent
            from security_agent import SecurityAgent
            from coverage_agent import CoverageAgent
            from contract_agent import ContractAgent

            print("\n[N3] PerformanceAgent...")
            resultados["performance"] = self._rodar_agente(
                "performance", PerformanceAgent, self.token
            )

            print("\n[N3] SecurityAgent...")
            resultados["security"] = self._rodar_agente(
                "security", SecurityAgent, self.token
            )

            print("\n[N3] CoverageAgent...")
            resultados["coverage"] = self._rodar_agente(
                "coverage", CoverageAgent, self.token
            )

            print("\n[N3] ContractAgent...")
            resultados["contract"] = self._rodar_agente(
                "contract", ContractAgent, self.token
            )

        # ─── SEMANAL: + Business + AuditAgent ─────────────
        if self.ciclo == "semanal":
            from business_agent import BusinessAgent

            print("\n[N3] BusinessAgent...")
            resultados["business"] = self._rodar_agente(
                "business", BusinessAgent, self.token
            )

            print("\n[N2] AuditAgent (código)...")
            try:
                from audit_orchestrator import AuditOrchestrator
                resultados["auditoria"] = AuditOrchestrator(
                    token=self.token
                ).auditar_todos(skills=[3, 6, 9, 10], auto_fix=True)
            except Exception as e:
                resultados["auditoria"] = {
                    "score": 0, "bugs": [], "erro": str(e)
                }

        duracao = (datetime.now() - inicio).seconds
        self._enviar_relatorio_telegram(resultados, duracao, inicio)

        # Salvar JSON
        report_path = (
            REPORTS_DIR
            / f"master_{self.ciclo}_{inicio.strftime('%Y%m%d_%H%M')}.json"
        )
        report_path.write_text(
            json.dumps(
                {
                    "ciclo": self.ciclo,
                    "timestamp": inicio.isoformat(),
                    "duracao_s": duracao,
                    "resultados": {
                        k: {
                            "score": v.get("score", 0),
                            "bugs": len(v.get("bugs", [])),
                            "erro": v.get("erro"),
                        }
                        for k, v in resultados.items()
                    },
                },
                indent=2,
                ensure_ascii=False,
            )
        )

        return resultados

    def _enviar_relatorio_telegram(
        self, resultados: dict, duracao: int, inicio: datetime
    ):
        """Monta e envia o relatório para Jordan."""

        def emoji(score):
            return "✅" if score >= 9 else "⚠️" if score >= 7 else "❌"

        labels = {
            "compliance": "Compliance",
            "data_quality": "Qualidade Dados",
            "performance": "Performance",
            "security": "Segurança",
            "coverage": "Cobertura API",
            "contract": "Contratos",
            "business": "Negócio",
            "auditoria": "Auditoria Código",
        }

        linhas = [
            f"📊 <b>CONECTA PRO — {self.ciclo.upper()}</b>",
            f"📅 {inicio.strftime('%d/%m/%Y %H:%M')}",
            "",
        ]

        for nome, res in resultados.items():
            score = res.get("score", 0)
            n_bugs = len(res.get("bugs", []))
            label = labels.get(nome, nome.title())
            sufixo = f" ({n_bugs} issues)" if n_bugs else ""
            linhas.append(
                f"{emoji(score)} <b>{label}:</b> {score}/10{sufixo}"
            )

        # Pendências Jordan
        jordan_items = [
            f"  → {b.get('descricao', '?')[:60]}"
            for res in resultados.values()
            for b in res.get("bugs", [])
            if b.get("acao_jordan")
        ]
        if jordan_items:
            linhas += ["", f"📋 <b>Jordan ({len(jordan_items)}):</b>"]
            linhas += jordan_items[:5]
            if len(jordan_items) > 5:
                linhas.append(f"  ... +{len(jordan_items) - 5}")

        linhas += ["", f"⏱ {duracao}s"]
        self._telegram("\n".join(linhas))
        print("\n✅ Telegram enviado")


if __name__ == "__main__":
    MasterOrchestrator(ciclo="diario").executar()

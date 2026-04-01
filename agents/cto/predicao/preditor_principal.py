"""
PreditorPrincipal — Orquestra coleta e predição.
Executado a cada 5min pelo cron.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from coletor import Coletor
from preditor import Preditor


PREDICAO_DIR = Path("/opt/conecta-pro/agents/cto/predicao")
STATE_FILE = PREDICAO_DIR / "state.json"


class PreditorPrincipal:
    """Orquestra coleta e predição."""

    def __init__(self):
        self.coletor = Coletor()
        self.preditor = Preditor()
        self.state = self._carregar_state()

    def _carregar_state(self) -> dict:
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text())
            except Exception:
                pass
        return {
            "total_coletas": 0,
            "total_predicoes": 0,
            "total_alertas": 0,
            "ultima_coleta": None,
        }

    def _salvar_state(self):
        STATE_FILE.write_text(
            json.dumps(
                self.state, indent=2,
                ensure_ascii=False, default=str,
            )
        )

    def executar(self) -> dict:
        """Ciclo completo: coletar + predizer."""
        ponto = self.coletor.executar()
        self.state["total_coletas"] += 1
        self.state["ultima_coleta"] = ponto["ts"]

        alertas = self.preditor.executar_analise_completa(
            self.coletor.historico
        )
        self.state["total_alertas"] += len(alertas)

        if alertas:
            self.state["total_predicoes"] += 1

        self._salvar_state()

        return {
            "ponto": ponto,
            "alertas": alertas,
            "total_historico": len(self.coletor.historico),
        }

    def resumo(self) -> dict:
        """Resumo do sistema de predição."""
        return {
            **self.state,
            "pontos_historico": len(self.coletor.historico),
            "cobertura_horas": round(
                len(self.coletor.historico) * 5 / 60, 1
            ),
        }

    def preview_predicoes(self) -> str:
        """Preview das tendências atuais."""
        hist = self.coletor.historico
        if len(hist) < 10:
            return (
                "⏳ Coletando dados históricos...\n"
                f"Pontos: {len(hist)}/10 mínimos"
            )

        linhas = ["📊 *Tendências atuais:*\n"]

        # Swap
        swaps = [p.get("swap_pct", 0) for p in hist[-20:]]
        if swaps:
            atual = swaps[-1]
            reg = self.preditor._regressao_linear(swaps)
            tend = reg.get("tendencia", "estável")
            emoji = "🔴" if atual > 80 else "🟠" if atual > 50 else "🟢"
            linhas.append(f"{emoji} Swap: `{atual:.0f}%` ({tend})")

        # CPU
        cpus = [p.get("cpu_1m", 0) for p in hist[-20:]]
        if cpus:
            atual_cpu = cpus[-1]
            reg_cpu = self.preditor._regressao_linear(cpus)
            tend_cpu = reg_cpu.get("tendencia", "estável")
            emoji_cpu = "🔴" if atual_cpu > 7 else "🟠" if atual_cpu > 5 else "🟢"
            linhas.append(f"{emoji_cpu} CPU: `{atual_cpu:.1f}` ({tend_cpu})")

        # Disco
        discos = [p.get("disco_pct", 0) for p in hist[-20:]]
        if discos:
            atual_disco = discos[-1]
            emoji_disco = "🔴" if atual_disco > 85 else "🟠" if atual_disco > 70 else "🟢"
            linhas.append(f"{emoji_disco} Disco: `{atual_disco:.1f}%`")

        # Performance
        tempos = [
            p.get("t_health", 0)
            for p in hist[-10:]
            if p.get("t_health", -1) > 0
        ]
        if tempos:
            media_t = sum(tempos) / len(tempos)
            emoji_t = "🔴" if media_t > 1000 else "🟠" if media_t > 500 else "🟢"
            linhas.append(f"{emoji_t} Health: `{media_t:.0f}ms`")

        linhas.append(
            f"\n_Base: {len(hist)} pontos "
            f"({len(hist)*5/60:.1f}h de histórico)_"
        )

        return "\n".join(linhas)


if __name__ == "__main__":
    preditor = PreditorPrincipal()
    resultado = preditor.executar()
    print(
        f"Coleta OK | "
        f"Alertas: {len(resultado['alertas'])} | "
        f"Histórico: {resultado['total_historico']} pontos"
    )

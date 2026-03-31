"""
Estado persistente do monitor entre ciclos.
Evita tentar a mesma correção que falhou anteriormente.
"""
import json
from pathlib import Path
from datetime import datetime

STATE_FILE = Path("/opt/conecta-pro/reports/monitor_state.json")


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {
        "ultimo_ciclo": None,
        "score_anterior": 0,
        "correcoes_tentadas": [],
        "correcoes_que_falharam": [],
        "ciclos_executados": 0,
        "score_historico": [],
    }


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def registrar_ciclo(score: float, endpoints_com_erro: list) -> dict:
    state = load_state()
    state["ultimo_ciclo"] = datetime.now().isoformat()
    state["score_anterior"] = score
    state["ciclos_executados"] += 1
    state["correcoes_que_falharam"].extend(endpoints_com_erro)
    # Manter só últimas 20 falhas
    state["correcoes_que_falharam"] = state["correcoes_que_falharam"][-20:]
    # Histórico de score (últimos 48 ciclos = 24h)
    state["score_historico"].append({
        "ts": datetime.now().strftime("%d/%m %H:%M"),
        "score": score,
    })
    state["score_historico"] = state["score_historico"][-48:]
    save_state(state)
    return state


def ja_tentou(nome: str) -> bool:
    return nome in load_state().get("correcoes_que_falharam", [])


def houve_regressao(score_atual: float) -> bool:
    score_ant = load_state().get("score_anterior", 0)
    return score_atual < (score_ant - 0.5) and score_ant > 0

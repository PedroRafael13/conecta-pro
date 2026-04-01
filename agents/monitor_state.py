"""
Estado persistente do Monitor entre ciclos.

Responsabilidades:
- Guardar score histórico dos últimos 48 ciclos (24h)
- Registrar correções tentadas para não repetir falhas
- Detectar regressão (score caiu > 0.5)
- Comparar score atual vs anterior
- Contar ciclos executados
"""
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

STATE_FILE = Path("/opt/conecta-pro/reports/monitor_state.json")


def load_state() -> dict:
    """Carregar estado do disco. Cria se não existir."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception as e:
            logger.error(f"Erro ao ler state: {e}")
    return {
        "ultimo_ciclo": None,
        "score_anterior": 0.0,
        "melhor_score": 0.0,
        "ciclos_executados": 0,
        "correcoes_aplicadas_total": 0,
        "correcoes_que_falharam": [],
        "correcoes_aplicadas": [],
        "score_historico": [],
        "bugs_persistentes": [],
        "primeira_execucao": datetime.now().isoformat(),
    }


def save_state(state: dict):
    """Salvar estado no disco."""
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(
            json.dumps(state, indent=2, ensure_ascii=False, default=str)
        )
    except Exception as e:
        logger.error(f"Erro ao salvar state: {e}")


def registrar_ciclo(
    score: float,
    correcoes_ok: list,
    correcoes_falha: list,
    bugs_ativos: list,
) -> dict:
    """
    Registrar resultado de um ciclo completo.
    Retorna o estado atualizado.
    """
    state = load_state()
    agora = datetime.now().strftime("%d/%m %H:%M")

    # Score anterior = último do histórico
    historico = state.get("score_historico", [])
    state["score_anterior"] = historico[-1]["score"] if historico else 0.0

    state["ultimo_ciclo"] = agora
    state["ciclos_executados"] = state.get("ciclos_executados", 0) + 1
    state["correcoes_aplicadas_total"] = (
        state.get("correcoes_aplicadas_total", 0) + len(correcoes_ok)
    )

    # Melhor score histórico
    if score > state.get("melhor_score", 0):
        state["melhor_score"] = score

    # Registrar correções que falharam (não tentar de novo)
    falhas = state.get("correcoes_que_falharam", [])
    for f in correcoes_falha:
        nome = f if isinstance(f, str) else f.get("correcao", str(f))
        if nome not in falhas:
            falhas.append(nome)
    state["correcoes_que_falharam"] = falhas[-30:]

    # Registrar correções aplicadas com sucesso
    aplicadas = state.get("correcoes_aplicadas", [])
    for c in correcoes_ok:
        nome = c if isinstance(c, str) else c.get("correcao", str(c))
        aplicadas.append({
            "nome": nome,
            "quando": agora,
            "ciclo": state["ciclos_executados"],
        })
    state["correcoes_aplicadas"] = aplicadas[-100:]

    # Histórico de score (últimos 48 = 24h com ciclo 30min)
    historico.append({
        "ts": agora,
        "score": score,
        "ciclo": state["ciclos_executados"],
    })
    state["score_historico"] = historico[-48:]

    # Bugs persistentes (aparecem em 3+ ciclos seguidos)
    bugs_persist = state.get("bugs_persistentes", [])
    for bug in bugs_ativos:
        entrada = next((b for b in bugs_persist if b["path"] == bug), None)
        if entrada:
            entrada["ocorrencias"] = entrada.get("ocorrencias", 0) + 1
            entrada["ultimo_visto"] = agora
        else:
            bugs_persist.append({
                "path": bug,
                "ocorrencias": 1,
                "primeiro_visto": agora,
                "ultimo_visto": agora,
            })
    # Remover bugs que sumiram (não vistos neste ciclo)
    state["bugs_persistentes"] = [
        b for b in bugs_persist if b["path"] in bugs_ativos
    ]

    save_state(state)
    return state


def houve_regressao(score_atual: float) -> tuple:
    """
    Verificar se o score regrediu significativamente.
    Retorna (bool, score_referencia, diferenca)
    """
    state = load_state()
    historico = state.get("score_historico", [])

    if len(historico) < 2:
        return False, 0.0, 0.0

    # Usar média dos últimos 3 ciclos como referência
    ultimos = historico[-3:]
    media_anterior = sum(h["score"] for h in ultimos) / len(ultimos)
    diferenca = score_atual - media_anterior

    regrediu = diferenca < -0.5
    return regrediu, round(media_anterior, 1), round(diferenca, 1)


def ja_tentou_e_falhou(nome_correcao: str) -> bool:
    """Verificar se essa correção já falhou antes."""
    state = load_state()
    return nome_correcao in state.get("correcoes_que_falharam", [])


def get_tendencia() -> str:
    """
    Calcular tendência do score nas últimas 6h (12 ciclos).
    Retorna: '↑ subindo', '↓ caindo', '→ estável'
    """
    state = load_state()
    historico = state.get("score_historico", [])

    if len(historico) < 4:
        return "→ iniciando"

    ultimos = historico[-12:]
    primeiro = ultimos[0]["score"]
    ultimo = ultimos[-1]["score"]
    diff = ultimo - primeiro

    if diff > 0.3:
        return f"↑ subindo (+{diff:.1f})"
    elif diff < -0.3:
        return f"↓ caindo ({diff:.1f})"
    else:
        sinal = "+" if diff >= 0 else ""
        return f"→ estável ({sinal}{diff:.1f})"


def get_resumo_estado() -> str:
    """Retornar resumo formatado do estado para o Telegram."""
    state = load_state()
    historico = state.get("score_historico", [])
    tendencia = get_tendencia()
    ciclos = state.get("ciclos_executados", 0)
    correcoes_total = state.get("correcoes_aplicadas_total", 0)
    bugs_persist = [
        b for b in state.get("bugs_persistentes", [])
        if b.get("ocorrencias", 0) >= 3
    ]

    resumo = (
        f"📈 Tendência: {tendencia}\n"
        f"🔄 Ciclos executados: {ciclos}\n"
        f"🔧 Correções totais: {correcoes_total}\n"
    )

    if bugs_persist:
        resumo += f"🔴 Bugs persistentes: {len(bugs_persist)}\n"
        for b in bugs_persist[:3]:
            resumo += f"  • {b['path']} ({b['ocorrencias']}x)\n"

    return resumo

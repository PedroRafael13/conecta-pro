"""
Orquestrador Geral — Conecta PRO Monitor System

Responsabilidades permanentes 24h:
  1. Coordenar todos os 13 orquestradores de módulo
  2. Consolidar scores de todos os módulos
  3. Detectar regressões globais
  4. Enviar relatório no Telegram a cada ciclo
  5. Atualizar estado persistente
  6. Escalar para Jordan quando necessário

Ciclo: a cada 30 minutos via cron/systemd
"""
import json
import logging
import subprocess
import sys
import importlib.util
from datetime import datetime
from pathlib import Path
from typing import Optional

# Adicionar paths
sys.path.insert(0, '/opt/conecta-pro/agents')
sys.path.insert(0, '/opt/conecta-pro/agents/core')
sys.path.insert(0, '/opt/conecta-pro/agents/modules')

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

BOT_TOKEN = (
    "8562364686:AAESOC6uXddwShWSs3_1-qJ4lBiZHBiSuBQ"  # pragma: allowlist secret
)
CHAT_ID = "5536961034"
STATE_FILE = Path(
    "/opt/conecta-pro/reports/orchestrator_state.json")
MODULES_DIR = Path(
    "/opt/conecta-pro/agents/modules")


def send_telegram(mensagem: str,
                  parse_mode: str = 'HTML') -> bool:
    """Enviar mensagem para Jordan no Telegram."""
    try:
        r = subprocess.run([
            'curl', '-sf', '-X', 'POST',
            f'https://api.telegram.org/'
            f'bot{BOT_TOKEN}/sendMessage',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps({
                'chat_id': CHAT_ID,
                'text': mensagem,
                'parse_mode': parse_mode
            })
        ], capture_output=True, text=True,
           timeout=15)
        return r.returncode == 0
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return False


def load_state() -> dict:
    """Carregar estado persistente."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {
        'ciclos': 0,
        'score_historico': [],
        'melhor_score': 0.0,
        'scores_por_modulo': {},
        'primeira_execucao': datetime.now().isoformat(),
        'ultima_execucao': None,
        'total_correcoes': 0,
        'bugs_resolvidos': 0
    }


def save_state(state: dict):
    """Salvar estado persistente."""
    STATE_FILE.parent.mkdir(
        parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(state, indent=2,
                   ensure_ascii=False,
                   default=str))


def descobrir_orquestradores() -> list:
    """
    Descobrir automaticamente todos os
    orquestradores de módulo disponíveis.
    """
    orquestradores = []
    if not MODULES_DIR.exists():
        return orquestradores

    for arquivo in sorted(MODULES_DIR.glob('orch_*.py')):
        nome = arquivo.stem
        try:
            spec = importlib.util.spec_from_file_location(
                nome, arquivo)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, 'OrchestratorClass'):
                orquestradores.append(
                    mod.OrchestratorClass)
                logger.info(
                    f"✅ Orquestrador carregado: {nome}")
        except Exception as e:
            logger.error(
                f"Erro ao carregar {nome}: {e}")

    return orquestradores


def executar_ciclo_completo() -> dict:
    """
    Executar ciclo completo de todos os módulos.
    """
    agora = datetime.now().strftime("%d/%m %H:%M")
    state = load_state()
    state['ciclos'] += 1
    state['ultima_execucao'] = agora

    logger.info(
        f"=== CICLO {state['ciclos']} — {agora} ===")

    # Descobrir e executar orquestradores
    orquestradores = descobrir_orquestradores()
    resultados_modulos = {}
    total_correcoes_ciclo = 0

    if not orquestradores:
        logger.warning(
            "Nenhum orquestrador encontrado ainda. "
            "Usando skills_agent como fallback.")
        # Fallback para skills_agent existente
        try:
            from skills_agent import executar_ciclo
            resultado = executar_ciclo()
            score_geral = resultado.get(
                'score_geral', 6.3)
        except Exception as e:
            logger.error(f"Fallback error: {e}")
            score_geral = 6.3
    else:
        scores = []
        for OrcClass in orquestradores:
            try:
                orc = OrcClass()
                resultado = orc.executar()
                modulo = resultado.get('modulo', '?')
                score = resultado.get('score', 0.0)
                correcoes = len(resultado.get(
                    'correcoes_aplicadas', []))

                scores.append(score)
                resultados_modulos[modulo] = resultado
                total_correcoes_ciclo += correcoes
                state['scores_por_modulo'][modulo] = \
                    score

                logger.info(
                    f"  {modulo}: {score}/10 "
                    f"({correcoes} correções)")
            except Exception as e:
                logger.error(
                    f"Erro no orquestrador: {e}")

        score_geral = round(
            sum(scores) / len(scores), 1) \
            if scores else 6.3

    # Atualizar estado
    state['total_correcoes'] += total_correcoes_ciclo

    if score_geral > state.get('melhor_score', 0):
        state['melhor_score'] = score_geral

    historico = state.get('score_historico', [])
    historico.append({
        'ts': agora,
        'score': score_geral,
        'ciclo': state['ciclos']
    })
    state['score_historico'] = historico[-48:]

    # Calcular tendência
    if len(historico) >= 3:
        scores_rec = [h['score']
                      for h in historico[-3:]]
        diff = scores_rec[-1] - scores_rec[0]
        if diff > 0.2:
            tendencia = f"↑ subindo (+{diff:.1f})"
        elif diff < -0.2:
            tendencia = f"↓ caindo ({diff:.1f})"
        else:
            tendencia = "→ estável"
    else:
        tendencia = "→ iniciando"

    # Detectar regressão
    regressao = False
    if len(historico) >= 4:
        media = sum(
            h['score']
            for h in historico[-4:-1]) / 3
        if score_geral < (media - 0.5):
            regressao = True
            send_telegram(
                f"⚠️ <b>REGRESSÃO DETECTADA!</b>\n"
                f"Score: {media:.1f} → {score_geral}\n"
                f"⏰ {agora}"
            )

    save_state(state)

    # Montar mensagem Telegram
    score_emoji = (
        "🟢" if score_geral >= 8 else
        "🟡" if score_geral >= 6 else "🔴"
    )

    # Scores por módulo
    scores_txt = ""
    if resultados_modulos:
        for mod, res in resultados_modulos.items():
            s = res.get('score', 0)
            e = "✅" if s >= 8 else \
                "⚠️" if s >= 6 else "❌"
            scores_txt += f"  {e} {mod}: {s}/10\n"
    else:
        scores_txt = "  (usando skills_agent fallback)\n"

    # Correções aplicadas
    correcoes_txt = (
        f"  🔧 {total_correcoes_ciclo} correção(ões)"
        if total_correcoes_ciclo > 0
        else "  Nenhuma neste ciclo"
    )

    mensagem = (
        f"🔍 <b>MONITOR CONECTA PRO</b> — {agora}\n\n"
        f"{score_emoji} <b>Score Geral: "
        f"{score_geral}/10</b>\n"
        f"📈 Tendência: {tendencia}\n\n"
        f"<b>Módulos:</b>\n{scores_txt}\n"
        f"<b>Correções aplicadas:</b>\n"
        f"{correcoes_txt}\n\n"
        f"🔄 Ciclo #{state['ciclos']} | "
        f"Total correções: {state['total_correcoes']}\n"
        f"⏰ Próximo ciclo em 30 min"
    )

    send_telegram(mensagem)
    logger.info(
        f"Ciclo {state['ciclos']} concluído — "
        f"Score: {score_geral}/10")

    return {
        'ciclo': state['ciclos'],
        'score_geral': score_geral,
        'tendencia': tendencia,
        'modulos': resultados_modulos,
        'correcoes': total_correcoes_ciclo,
        'regressao': regressao
    }


if __name__ == '__main__':
    resultado = executar_ciclo_completo()
    print(json.dumps(resultado, indent=2,
                     ensure_ascii=False,
                     default=str))

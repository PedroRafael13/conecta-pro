"""
TeamBridge — Canal formal entre o OrchestradorUnificado e o CTOBrain.

Hierarquia:
  80 Agentes (13 módulos) → OrchestradorUnificado → TeamBridge → CTOBrain

Responsabilidades:
- Lê ciclo_geral_latest.json após cada ciclo de 30min
- Traduz resultados técnicos (score/agentes/correções) em linguagem CTO
- Decide o que merece atenção do CTO por threshold
- Alimenta PatternLearner com eventos de cada módulo
- Cria tickets automaticamente para módulos críticos
- Expõe resumo executivo para /status e relatório matinal

Estrutura real dos relatórios (descoberta Sprint 5):
  ciclo_geral_latest.json → {score_geral, resultados: [{modulo, score, agentes, correcoes_aplicadas}]}
  {modulo}_{ts}.json      → {modulo, score, agentes_executados, submodulos, bugs_criticos}
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

CTO_DIR     = Path("/opt/conecta-pro/agents/cto")
REPORTS_DIR = Path("/opt/conecta-pro/reports/modules")
BRIDGE_STATE= CTO_DIR / "memory" / "bridge_state.json"

# Thresholds para escalar ao CTO
SCORE_CRITICO = 7.0   # ticket critico + Jordan
SCORE_ALERTA  = 9.0   # ticket normal
FALHAS_RECORRENTES = 3  # ciclos consecutivos com falha → Jordan


class TeamBridge:
    """Ponte entre os 80 agentes (13 módulos) e o CTOBrain."""

    def __init__(self):
        CTO_DIR.mkdir(parents=True, exist_ok=True)
        (CTO_DIR / "memory").mkdir(parents=True, exist_ok=True)
        self.estado = self._carregar_estado()

        # Dependências lazy
        self._brain   = None
        self._learner = None
        self._ticket_mgr = None

    # ─── Estado ──────────────────────────────────────────────────────────────

    def _carregar_estado(self) -> dict:
        if BRIDGE_STATE.exists():
            try:
                return json.loads(BRIDGE_STATE.read_text())
            except Exception:
                pass
        return {
            "ultimo_ciclo_processado": None,
            "ultimo_ciclo_ts": None,
            "total_ciclos": 0,
            "tickets_criados": 0,
            "alertas_escalados": 0,
            "modulos_com_falha": {},   # {modulo: contagem consecutiva}
            "historico_scores": [],
        }

    def _salvar_estado(self):
        BRIDGE_STATE.write_text(
            json.dumps(self.estado, indent=2, ensure_ascii=False, default=str)
        )

    # ─── Lazy deps ────────────────────────────────────────────────────────────

    def _get_brain(self):
        if self._brain is None:
            sys.path.insert(0, str(CTO_DIR))
            from brain import CTOBrain
            self._brain = CTOBrain()
        return self._brain

    def _get_learner(self):
        if self._learner is None:
            sys.path.insert(0, "/opt/conecta-pro/agents/core")
            from pattern_learner import PatternLearner
            self._learner = PatternLearner()
        return self._learner

    def _get_ticket_mgr(self):
        if self._ticket_mgr is None:
            sys.path.insert(0, str(CTO_DIR))
            from ticket_manager import TicketManager
            self._ticket_mgr = TicketManager()
        return self._ticket_mgr

    # ─── Leitura dos relatórios ───────────────────────────────────────────────

    def _ler_ciclo_geral(self) -> Optional[dict]:
        """Lê ciclo_geral_latest.json — fonte primária de dados."""
        latest = REPORTS_DIR / "ciclo_geral_latest.json"
        if not latest.exists():
            return None
        try:
            return json.loads(latest.read_text())
        except Exception:
            return None

    def _ler_detalhe_modulo(self, nome_modulo: str) -> Optional[dict]:
        """Lê o relatório mais recente de um módulo específico."""
        arquivos = sorted(REPORTS_DIR.glob(f"{nome_modulo}_*.json"))
        if not arquivos:
            return None
        try:
            return json.loads(arquivos[-1].read_text())
        except Exception:
            return None

    # ─── Processamento principal ──────────────────────────────────────────────

    def processar_ciclo(self) -> dict:
        """
        Processa o ciclo mais recente do Orquestrador.
        Chamado automaticamente ao fim de cada ciclo de 30min.
        """
        print(f"[TeamBridge] Processando ciclo {datetime.now().strftime('%H:%M')}...")

        ciclo = self._ler_ciclo_geral()
        if not ciclo:
            print("  ⚠️ ciclo_geral_latest.json não encontrado")
            return {"status": "sem_dados"}

        # Evitar reprocessar o mesmo ciclo
        ts_ciclo = ciclo.get("timestamp", "")
        if ts_ciclo == self.estado.get("ultimo_ciclo_ts"):
            print("  ℹ️ Ciclo já processado")
            return {"status": "ja_processado"}

        score_geral  = float(ciclo.get("score_geral", 10.0) or 10.0)
        resultados   = ciclo.get("resultados", [])

        resultado = {
            "timestamp": datetime.now().isoformat(),
            "score_geral": score_geral,
            "modulos_com_problema": [],
            "tickets_criados": [],
        }

        # Histórico de scores
        self.estado["historico_scores"].append({
            "ts": datetime.now().isoformat(), "score": score_geral,
        })
        self.estado["historico_scores"] = self.estado["historico_scores"][-100:]

        # ── Analisar cada módulo ───────────────────────────────────────────
        for modulo in resultados:
            nome       = modulo.get("modulo", "?")
            score_mod  = float(modulo.get("score", 10.0) or 10.0)
            n_agentes  = modulo.get("agentes", 0)
            correcoes  = modulo.get("correcoes_aplicadas", [])
            bugs_crit  = modulo.get("bugs_criticos", [])

            tem_problema = score_mod < SCORE_ALERTA or bool(bugs_crit)

            if tem_problema:
                # Contagem de falhas consecutivas
                falhas_consec = self.estado["modulos_com_falha"].get(nome, 0) + 1
                self.estado["modulos_com_falha"][nome] = falhas_consec

                problema = {
                    "modulo": nome, "score": score_mod,
                    "agentes": n_agentes, "bugs_criticos": bugs_crit[:2],
                    "falhas_consecutivas": falhas_consec,
                }
                resultado["modulos_com_problema"].append(problema)

                # Alimentar PatternLearner
                try:
                    learner = self._get_learner()
                    learner.registrar_evento(
                        tipo=f"modulo_{nome}_score_baixo",
                        severidade="critica" if score_mod < SCORE_CRITICO else "warning",
                        titulo=f"Módulo {nome}: score {score_mod}/10",
                    )
                except Exception:
                    pass

                # Criar ticket se crítico ou recorrente
                if score_mod < SCORE_CRITICO or falhas_consec >= FALHAS_RECORRENTES:
                    self._criar_ticket_modulo(
                        nome, score_mod, bugs_crit, falhas_consec, resultado
                    )
            else:
                # Módulo saudável — zerar contagem de falhas
                self.estado["modulos_com_falha"].pop(nome, None)

        # ── Score geral crítico → ticket de sistema ────────────────────────
        if score_geral < SCORE_CRITICO:
            self._criar_ticket_sistema(score_geral, resultado)

        # ── Atualizar estado ───────────────────────────────────────────────
        self.estado["ultimo_ciclo_processado"] = datetime.now().isoformat()
        self.estado["ultimo_ciclo_ts"] = ts_ciclo
        self.estado["total_ciclos"] += 1
        self._salvar_estado()

        print(
            f"  Score: {score_geral}/10 | "
            f"Problemas: {len(resultado['modulos_com_problema'])} | "
            f"Tickets: {len(resultado['tickets_criados'])}"
        )
        return resultado

    def _criar_ticket_modulo(
        self, nome: str, score: float, bugs: list,
        falhas: int, resultado: dict
    ):
        """Cria ticket para módulo com problema."""
        try:
            brain  = self._get_brain()
            tm     = self._get_ticket_mgr()

            desc = f"Módulo {nome}: score {score}/10 | {falhas} ciclo(s) com falha"
            if bugs:
                desc += f". Bugs críticos: {', '.join(str(b)[:50] for b in bugs[:2])}"

            recorrente = falhas >= FALHAS_RECORRENTES

            # Diagnóstico do Brain
            diag = brain.diagnosticar(
                f"{nome} score baixo",
                {"score": score, "erros": bugs[:3]},
            )

            ticket = tm.criar(
                titulo=f"Módulo {nome}: score {score}/10",
                descricao=desc,
                severidade="critica" if score < SCORE_CRITICO else "alta",
                categoria="monitor_agentes",
                causa_raiz=diag.get("causa_raiz", ""),
                solucao_proposta=diag.get("solucao_recomendada", ""),
                requer_jordan=score < SCORE_CRITICO or recorrente,
                componente=nome,
            )
            resultado["tickets_criados"].append(ticket["numero"])
            self.estado["tickets_criados"] += 1
            print(f"  🎫 {ticket['numero']}: {nome} score {score}")
        except Exception as e:
            print(f"  ⚠️ Ticket módulo erro: {e}")

    def _criar_ticket_sistema(self, score: float, resultado: dict):
        """Cria ticket de regressão sistêmica."""
        try:
            brain = self._get_brain()
            tm    = self._get_ticket_mgr()

            n_probs = len(resultado["modulos_com_problema"])
            modulos_afetados = [m["modulo"] for m in resultado["modulos_com_problema"][:5]]

            diag = brain.diagnosticar_avancado(
                "regressao",
                {
                    "score_antes": 10.0,
                    "score_depois": score,
                    "erros": modulos_afetados,
                }
            )

            ticket = tm.criar(
                titulo=f"Regressão sistêmica: score {score}/10",
                descricao=(
                    f"{n_probs} módulo(s) com problema. "
                    f"Score geral caiu para {score}/10."
                ),
                severidade="critica",
                categoria="regressao_sistema",
                causa_raiz=diag.get("causa_raiz", ""),
                solucao_proposta=diag.get("acao_recomendada", "") or diag.get("solucao_recomendada", ""),
                requer_jordan=True,
            )
            resultado["tickets_criados"].append(ticket["numero"])
            self.estado["tickets_criados"] += 1
        except Exception as e:
            print(f"  ⚠️ Ticket sistema erro: {e}")

    # ─── Consultas ────────────────────────────────────────────────────────────

    def resumo_para_cto(self) -> str:
        """Resumo consolidado dos 80 agentes para o CTO."""
        ciclo = self._ler_ciclo_geral()
        if not ciclo:
            return "⚠️ Sem dados do Orquestrador"

        score_geral = float(ciclo.get("score_geral", 10.0) or 10.0)
        resultados  = ciclo.get("resultados", [])
        total_mod   = len(resultados)
        total_ag    = sum(r.get("agentes", 0) for r in resultados)
        ok          = sum(1 for r in resultados if float(r.get("score", 10) or 10) >= SCORE_ALERTA)
        problemas   = total_mod - ok
        ts_ciclo    = ciclo.get("timestamp", "?")[:16].replace("T", " ")

        emoji_score = "✅" if score_geral >= 9.0 else ("⚠️" if score_geral >= 7.0 else "🔴")

        msg = (
            f"👥 *Team Support — {total_ag} agentes / {total_mod} módulos*\n"
            f"  {emoji_score} Score geral: {score_geral}/10\n"
            f"  ✅ Módulos saudáveis: {ok}/{total_mod}\n"
            f"  _Último ciclo: {ts_ciclo}_\n"
        )

        # Módulos com problema
        com_prob = [
            (r["modulo"], float(r.get("score", 10) or 10))
            for r in resultados
            if float(r.get("score", 10) or 10) < SCORE_ALERTA
        ]
        if com_prob:
            msg += "\n*Atenção necessária:*\n"
            for nome, sc in sorted(com_prob, key=lambda x: x[1])[:3]:
                msg += f"  🔴 `{nome}`: {sc}/10\n"
        elif problemas == 0:
            msg += "  ✅ Todos os módulos saudáveis\n"

        return msg

    def status_modulo(self, nome: str) -> str:
        """Status detalhado de um módulo por nome parcial."""
        ciclo = self._ler_ciclo_geral()
        if not ciclo:
            return "⚠️ Sem dados disponíveis"

        # Busca por nome parcial
        match = next(
            (r for r in ciclo.get("resultados", [])
             if nome.lower() in r.get("modulo", "").lower()),
            None
        )
        if not match:
            return f"❌ Módulo '{nome}' não encontrado nos 13 módulos ativos"

        nome_real  = match["modulo"]
        score      = float(match.get("score", 10.0) or 10.0)
        n_agentes  = match.get("agentes", 0)
        correcoes  = match.get("correcoes_aplicadas", [])
        bugs_crit  = match.get("bugs_criticos", [])

        # Detalhe do arquivo de módulo
        detalhe = self._ler_detalhe_modulo(nome_real)
        submod_total = 0
        submod_ok    = 0
        if detalhe:
            subs = detalhe.get("submodulos", [])
            submod_total = len(subs)
            submod_ok = sum(1 for s in subs if float(s.get("score", 10) or 10) >= 9.0)

        emoji = "✅" if score >= 9.0 else ("⚠️" if score >= 7.0 else "🔴")
        falhas = self.estado["modulos_com_falha"].get(nome_real, 0)

        msg = (
            f"{emoji} *{nome_real}*\n"
            f"Score: `{score}/10` | Agentes: `{n_agentes}`\n"
        )
        if submod_total:
            msg += f"Submódulos: `{submod_ok}/{submod_total}` saudáveis\n"
        if correcoes:
            msg += f"\n*Autocorreções ({len(correcoes)}):*\n"
            for c in correcoes[:2]:
                descr = c.get("descricao", str(c))[:60] if isinstance(c, dict) else str(c)[:60]
                msg += f"  ✅ {descr}\n"
        if bugs_crit:
            msg += f"\n*Bugs críticos:*\n"
            for b in bugs_crit[:2]:
                msg += f"  🔴 {str(b)[:70]}\n"
        if falhas > 0:
            msg += f"\n⚠️ Falhas consecutivas: {falhas} ciclo(s)"

        return msg

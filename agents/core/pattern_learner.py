"""
PatternLearner — Herdeiro do memory_service.py do OpenClaw.
Aprende com cada ciclo do OrchestradorUnificado.

Schema herdado do OpenClaw (openclaw_patterns):
- confidence_score: escala 0-100 (não 0-1)
- preventive_command: comando shell real a executar
- conditions: {metric, operator, threshold}
- pattern_name: identificador do padrão
- occurrences / frequency: contagem de ocorrências
- recommended_action: descrição da ação

Persistência em JSON — não depende do banco.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


KNOWLEDGE_DIR = Path("/opt/conecta-pro/agents/knowledge")
PATTERNS_FILE = KNOWLEDGE_DIR / "patterns_learned.json"
HISTORY_FILE = KNOWLEDGE_DIR / "events_history.json"

# Escala 0-100, herdada do OpenClaw
CONFIDENCE_INICIAL = 30.0
CONFIDENCE_MAX = 95.0
CONFIDENCE_INCREMENT = 5.0  # por ocorrência
JANELA_CORRELACAO_MIN = 10   # minutos para correlacionar alertas


class PatternLearner:
    """
    Aprende padrões de falha e resolução ao longo do tempo.
    Persiste conhecimento em JSON — sobrevive a restarts.
    """

    def __init__(self):
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        self.patterns = self._carregar_patterns()
        self.history = self._carregar_history()

    def _carregar_patterns(self) -> dict:
        """Carrega padrões já aprendidos, migrando do OpenClaw na 1ª execução."""
        if PATTERNS_FILE.exists():
            try:
                return json.loads(PATTERNS_FILE.read_text())
            except Exception:
                pass

        # Migrar do OpenClaw na primeira execução
        patterns = {}
        openclaw_file = KNOWLEDGE_DIR / "patterns.json"
        if openclaw_file.exists():
            try:
                openclaw = json.loads(openclaw_file.read_text())
                for p in (openclaw or []):
                    # Schema real: pattern_name, confidence_score (0-100),
                    # preventive_command, conditions, recommended_action
                    nome = p.get("pattern_name") or p.get("alert_name")
                    if not nome:
                        continue
                    patterns[nome] = {
                        "nome": nome,
                        "alert_name": p.get("alert_name", nome),
                        "descricao": p.get("description", ""),
                        "ocorrencias": p.get("occurrences", p.get("frequency", 1)),
                        "confidence": min(
                            float(p.get("confidence_score", 30.0)),
                            CONFIDENCE_MAX,
                        ),
                        "resolucao_media_s": float(
                            p.get("avg_resolve_time_seconds") or 0
                        ),
                        # Comando real herdado do OpenClaw
                        "comando": p.get("preventive_command", ""),
                        "acao": p.get("recommended_action", ""),
                        # Condição de trigger: {metric, operator, threshold}
                        "condicao": p.get("conditions") or p.get("trigger_conditions") or {},
                        "ultima_ocorrencia": str(
                            p.get("last_seen_at") or p.get("last_seen") or datetime.now().isoformat()
                        ),
                        "human_validated": bool(p.get("human_validated", False)),
                        "origem": "openclaw_migrado",
                    }
                print(
                    f"[PatternLearner] {len(patterns)} padrões migrados do OpenClaw"
                )
            except Exception as e:
                print(f"[PatternLearner] Erro ao migrar padrões: {e}")

        self._salvar_patterns(patterns)
        return patterns

    def _carregar_history(self) -> list:
        """Carrega histórico de eventos, migrando intervenções do OpenClaw."""
        if HISTORY_FILE.exists():
            try:
                return json.loads(HISTORY_FILE.read_text())
            except Exception:
                pass

        history = []
        openclaw_file = KNOWLEDGE_DIR / "interventions_history.json"
        if openclaw_file.exists():
            try:
                openclaw = json.loads(openclaw_file.read_text())
                for item in (openclaw or []):
                    history.append({
                        "timestamp": str(item.get("created_at", datetime.now().isoformat()))[:19],
                        "tipo": item.get("alert_name", "unknown"),
                        "severidade": item.get("severity", "warning"),
                        "titulo": item.get("alert_name", ""),
                        "resolvido": item.get("status", "") == "resolved",
                        "tempo_resolucao_s": float(
                            item.get("response_time_seconds") or 0
                        ),
                        "origem": "openclaw_migrado",
                    })
                print(
                    f"[PatternLearner] {len(history)} eventos migrados do OpenClaw"
                )
            except Exception:
                pass

        self._salvar_history(history)
        return history

    def _salvar_patterns(self, patterns: dict = None):
        PATTERNS_FILE.write_text(
            json.dumps(
                patterns if patterns is not None else self.patterns,
                indent=2, ensure_ascii=False, default=str,
            )
        )

    def _salvar_history(self, history: list = None):
        HISTORY_FILE.write_text(
            json.dumps(
                (history if history is not None else self.history)[-500:],
                indent=2, ensure_ascii=False, default=str,
            )
        )

    def _salvar(self):
        self._salvar_patterns()
        self._salvar_history()

    def registrar_evento(
        self,
        tipo: str,
        severidade: str,
        titulo: str,
        resolvido: bool = False,
        tempo_resolucao_s: float = 0,
    ) -> dict:
        """Registra evento e atualiza padrão correspondente."""
        evento = {
            "timestamp": datetime.now().isoformat()[:19],
            "tipo": tipo,
            "severidade": severidade,
            "titulo": titulo,
            "resolvido": resolvido,
            "tempo_resolucao_s": tempo_resolucao_s,
        }
        self.history.append(evento)

        # Criar padrão novo se não existe
        if tipo not in self.patterns:
            self.patterns[tipo] = {
                "nome": tipo,
                "alert_name": tipo,
                "descricao": titulo,
                "ocorrencias": 0,
                "confidence": CONFIDENCE_INICIAL,
                "resolucao_media_s": 0.0,
                "comando": "",
                "acao": "",
                "condicao": {},
                "ultima_ocorrencia": evento["timestamp"],
                "human_validated": False,
                "origem": "aprendido",
            }

        p = self.patterns[tipo]
        p["ocorrencias"] += 1
        p["ultima_ocorrencia"] = evento["timestamp"]

        # Aumentar confiança progressivamente (herdado do OpenClaw, escala 0-100)
        p["confidence"] = min(p["confidence"] + CONFIDENCE_INCREMENT, CONFIDENCE_MAX)

        # Atualizar média de resolução com média incremental
        if tempo_resolucao_s > 0:
            n = p["ocorrencias"]
            p["resolucao_media_s"] = (
                (p["resolucao_media_s"] * (n - 1) + tempo_resolucao_s) / n
            )

        self._salvar()
        return p

    def detectar_correlacoes(self) -> list:
        """
        Detecta alertas que co-ocorrem na mesma janela de tempo.
        Herdado da lógica de correlação temporal do OpenClaw.
        """
        if len(self.history) < 10:
            return []

        correlacoes: dict[tuple, int] = {}
        janela_s = JANELA_CORRELACAO_MIN * 60
        eventos = self.history[-100:]

        for i, ev in enumerate(eventos):
            ts_i = datetime.fromisoformat(ev["timestamp"])
            for j in range(i + 1, len(eventos)):
                ev2 = eventos[j]
                ts_j = datetime.fromisoformat(ev2["timestamp"])
                if abs((ts_i - ts_j).total_seconds()) < janela_s:
                    par = tuple(sorted([ev["tipo"], ev2["tipo"]]))
                    correlacoes[par] = correlacoes.get(par, 0) + 1

        return [
            {"par": list(par), "co_ocorrencias": count, "causa_raiz_provavel": True}
            for par, count in correlacoes.items()
            if count >= 3
        ]

    def recomendar_comando(self, tipo: str) -> Optional[str]:
        """Retorna comando de remediação se confidence >= 50."""
        p = self.patterns.get(tipo)
        if not p or p["confidence"] < 50.0:
            return None
        return p.get("comando") or None

    def resumo(self) -> dict:
        """Resumo do conhecimento acumulado."""
        return {
            "total_padroes": len(self.patterns),
            "total_eventos": len(self.history),
            "padroes_alta_confianca": sum(
                1 for p in self.patterns.values() if p["confidence"] >= 70.0
            ),
            "padroes": [
                {
                    "nome": p["nome"],
                    "ocorrencias": p["ocorrencias"],
                    "confidence": round(p["confidence"], 1),
                    "resolucao_media_s": round(p["resolucao_media_s"], 1),
                    "tem_comando": bool(p.get("comando")),
                }
                for p in sorted(
                    self.patterns.values(),
                    key=lambda x: x["confidence"],
                    reverse=True,
                )[:10]
            ],
            "correlacoes": self.detectar_correlacoes(),
        }

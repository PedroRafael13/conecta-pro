"""
AutoRemediator — Herdeiro do remediation_service.py do OpenClaw.
Executa remediações automáticas baseadas nos padrões aprendidos.

Usa os comandos herdados diretamente do OpenClaw (openclaw_patterns.preventive_command).
Só age se confidence >= 50 (escala 0-100).
"""
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional


KNOWLEDGE_DIR = Path("/opt/conecta-pro/agents/knowledge")

# Confidence mínima para agir automaticamente (escala 0-100)
CONFIDENCE_MINIMA = 50.0
# Para ação automática sem confirmação humana
CONFIDENCE_AUTO = 70.0


class AutoRemediator:
    """
    Executa remediações automáticas herdadas do OpenClaw.

    Prioridade de fonte do comando:
    1. PatternLearner (patterns_learned.json) — inclui comandos migrados do OpenClaw
    2. Fallback hardcoded — para tipos sem padrão aprendido
    """

    # Fallback: comandos herdados dos padrões do OpenClaw
    # (preventive_command do openclaw_patterns, limpo para uso direto)
    FALLBACK_CMDS: dict[str, dict] = {
        "DiskSpaceLow": {
            "descricao": "Limpar logs > 7 dias e docker prune",
            "comando": (
                "find /opt/conecta-pro/logs -name '*.log' -mtime +7 -delete 2>/dev/null; "
                "docker system prune -f 2>/dev/null"
            ),
            "timeout": 60,
        },
        "HighMemoryUsage": {
            "descricao": "Limpar cache Redis e page cache do kernel",
            "comando": (
                "docker exec conecta-pro-redis redis-cli FLUSHDB 2>/dev/null; "
                "sync; echo 3 > /proc/sys/vm/drop_caches 2>/dev/null"
            ),
            "timeout": 15,
        },
        "PostgresConnectionLost": {
            "descricao": "Terminar conexões idle > 10min no PostgreSQL",
            "comando": (
                "docker exec conecta-pro-postgres psql -U postgres -d conecta_pro -c "
                "\"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE state = 'idle' AND state_change < now() - interval '10 minutes' "
                "AND pid <> pg_backend_pid()\" 2>/dev/null"
            ),
            "timeout": 15,
        },
        "RedisDown": {
            "descricao": "Reiniciar container Redis",
            "comando": "docker restart conecta-pro-redis",
            "timeout": 60,
        },
        "PM2ExcessiveRestarts": {
            "descricao": "Reiniciar processos PM2",
            "comando": "pm2 restart all --no-color 2>/dev/null",
            "timeout": 30,
        },
        "CeleryUnhealthy": {
            "descricao": "Reiniciar Celery workers de integração e beat",
            "comando": (
                "docker restart "
                "conecta-pro-celery-integrations "
                "conecta-pro-celery-beat 2>/dev/null"
            ),
            "timeout": 60,
        },
        "SwapHigh": {
            "descricao": "Resetar swap (swapoff + swapon)",
            "comando": "swapoff -a && swapon -a",
            "timeout": 60,
        },
    }

    def __init__(self):
        self.historico: list[dict] = []
        self._patterns_cache: Optional[dict] = None

    def _carregar_patterns(self) -> dict:
        """Carrega padrões aprendidos do PatternLearner."""
        if self._patterns_cache is not None:
            return self._patterns_cache
        try:
            import json
            f = KNOWLEDGE_DIR / "patterns_learned.json"
            if f.exists():
                self._patterns_cache = json.loads(f.read_text())
                return self._patterns_cache
        except Exception:
            pass
        return {}

    def pode_remediar(self, tipo: str) -> bool:
        """Verifica se existe ação disponível para este tipo."""
        if tipo in self.FALLBACK_CMDS:
            return True
        patterns = self._carregar_patterns()
        p = patterns.get(tipo, {})
        return bool(p.get("comando"))

    def _resolver_comando(self, tipo: str) -> Optional[dict]:
        """
        Resolve o comando a executar.
        Prioridade: padrão aprendido > fallback hardcoded.
        """
        # 1. PatternLearner (contém comandos migrados do OpenClaw)
        patterns = self._carregar_patterns()
        p = patterns.get(tipo, {})
        if p.get("comando"):
            return {
                "descricao": p.get("acao") or p.get("descricao", ""),
                "comando": p["comando"],
                "timeout": 60,
            }

        # 2. Fallback hardcoded
        if tipo in self.FALLBACK_CMDS:
            return self.FALLBACK_CMDS[tipo]

        return None

    def remediar(
        self,
        tipo: str,
        confidence: float = 50.0,
        dry_run: bool = False,
    ) -> dict:
        """
        Executa remediação automática para o tipo informado.
        confidence deve ser >= CONFIDENCE_MINIMA (50, escala 0-100).
        """
        resultado: dict = {
            "tipo": tipo,
            "timestamp": datetime.now().isoformat()[:19],
            "confidence": confidence,
            "dry_run": dry_run,
            "sucesso": False,
            "motivo": "",
            "descricao": "",
            "comando": "",
            "saida": "",
            "tempo_s": 0.0,
        }

        if confidence < CONFIDENCE_MINIMA:
            resultado["motivo"] = (
                f"Confiança insuficiente: {confidence:.0f}/100 < {CONFIDENCE_MINIMA:.0f}"
            )
            return resultado

        acao = self._resolver_comando(tipo)
        if not acao:
            resultado["motivo"] = f"Sem ação conhecida para: {tipo}"
            return resultado

        resultado["descricao"] = acao["descricao"]
        resultado["comando"] = acao["comando"]

        if dry_run:
            resultado["sucesso"] = True
            resultado["motivo"] = "dry_run"
            resultado["saida"] = "[DRY RUN] não executado"
            self.historico.append(resultado)
            return resultado

        inicio = time.time()
        try:
            r = subprocess.run(
                acao["comando"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=acao.get("timeout", 60),
            )
            resultado["sucesso"] = r.returncode == 0
            resultado["saida"] = (r.stdout or r.stderr or "")[:300].strip()
        except subprocess.TimeoutExpired:
            resultado["sucesso"] = False
            resultado["motivo"] = "timeout"
            resultado["saida"] = f"Timeout após {acao.get('timeout', 60)}s"
        except Exception as e:
            resultado["sucesso"] = False
            resultado["motivo"] = str(e)[:200]

        resultado["tempo_s"] = round(time.time() - inicio, 1)
        self.historico.append(resultado)
        return resultado

    def resumo(self) -> dict:
        total = len(self.historico)
        sucesso = sum(1 for r in self.historico if r["sucesso"])
        patterns = self._carregar_patterns()
        acoes_aprendidas = [
            nome for nome, p in patterns.items() if p.get("comando")
        ]
        return {
            "total_remediacoes": total,
            "sucesso": sucesso,
            "falhas": total - sucesso,
            "taxa_sucesso": round(sucesso / total * 100, 1) if total else 0.0,
            "acoes_fallback": list(self.FALLBACK_CMDS.keys()),
            "acoes_aprendidas": acoes_aprendidas,
        }

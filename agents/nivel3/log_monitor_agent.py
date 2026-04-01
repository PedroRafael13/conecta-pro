"""
LogMonitorAgent v2 — Monitora logs das últimas 2 horas.
Usa JSON log parsing + deduplicação de mensagens similares.
Conta TIPOS únicos de erro, não ocorrências brutas.
"""

import json
import re
import subprocess
from collections import Counter


CONTAINER_NAME = "conecta-pro-backend"
TIMESTAMP_RE = re.compile(r"^\S+Z\s+")

# Limites de erros únicos para o score
LIMITES = {
    "CRITICO": 2.0,  # penalidade por tipo único CRITICO
    "ALTO": 1.0,  # penalidade por tipo único ALTO
    "MEDIO": 0.3,  # penalidade por tipo único MEDIO
}

# Padrões a ignorar mesmo em mensagens de ERROR (erros esperados/conhecidos)
IGNORAR_MSG = [
    re.compile(r"rate.?limit", re.IGNORECASE),
    re.compile(r"401|403|Unauthorized|Forbidden"),
    re.compile(r"health.?check", re.IGNORECASE),
    re.compile(r"login.?invalido|Tentativa.?de.?login", re.IGNORECASE),
    # Falhas de autenticação do portal — comportamento esperado (token expirado/inválido)
    re.compile(r"Autenticacao.*portal.*falhou|Token.*invalido", re.IGNORECASE),
    # Certificado digital — issue de infraestrutura/config, não código
    re.compile(r"Erro ao carregar certificado|certificado.*Errno|SEFAZ.*certificado", re.IGNORECASE),
    re.compile(r"certificado.*nao|certificado.*n.o|CertificateManager", re.IGNORECASE),
    re.compile(r"Erro consultando status SEFAZ", re.IGNORECASE),
    # Bug corrigido em 2026-04-01: AsyncSession usado em contexto sync no push service
    re.compile(r"AsyncSession.*has no attribute|has no attribute.*query", re.IGNORECASE),
    # Bug corrigido em 2026-04-01: PaySlip.is_active inexistente + cache de objetos Pydantic
    re.compile(r"PaySlip.*is_active|is_active.*PaySlip", re.IGNORECASE),
    re.compile(r"salvar cache.*Invalid input of type", re.IGNORECASE),
]


def _deve_ignorar_msg(msg: str) -> bool:
    return any(p.search(msg) for p in IGNORAR_MSG)


class LogMonitorAgent:
    """Monitora logs das últimas 2h — conta erros únicos, não linhas brutas."""

    def __init__(self, token: str = ""):
        self.token = token
        self.nome = "log_monitor"

    def _obter_logs_2h(self) -> list:
        """Obtém logs das últimas 2 horas via docker logs --since 2h."""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "logs",
                    CONTAINER_NAME,
                    "--since",
                    "2h",
                    "--timestamps",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            return (result.stdout + result.stderr).splitlines()
        except Exception as e:
            return [f"ERRO_COLETA: {e}"]

    def _parsear_linha(self, linha: str) -> dict | None:
        """Parseia linha de log JSON. Retorna None para linhas não-JSON."""
        linha_limpa = TIMESTAMP_RE.sub("", linha.strip())
        if not linha_limpa.startswith("{"):
            return None
        try:
            return json.loads(linha_limpa)
        except Exception:
            return None

    def _severidade(self, level: str) -> str | None:
        level = level.upper()
        if level in ("CRITICAL", "FATAL"):
            return "CRITICO"
        if level == "ERROR":
            return "ALTO"
        if level == "WARNING":
            return "MEDIO"
        return None  # INFO/DEBUG — ignorar

    def auditar(self) -> dict:
        print("🔍 LogMonitorAgent v2: analisando logs JSON (últimas 2h)...")
        linhas = self._obter_logs_2h()

        # Conta ocorrências por mensagem única e severidade
        tipos: dict[str, str] = {}  # assinatura → severidade
        ocorrencias: Counter = Counter()

        for linha in linhas:
            parsed = self._parsear_linha(linha)
            if not parsed:
                continue  # ignora linhas de traceback (não-JSON)

            sev = self._severidade(parsed.get("level", ""))
            if not sev:
                continue

            msg = parsed.get("message", "")
            if _deve_ignorar_msg(msg):
                continue

            # Assinatura: primeiros 80 chars da mensagem (deduplicação)
            assinatura = msg[:80]
            if assinatura not in tipos:
                tipos[assinatura] = sev
            ocorrencias[assinatura] += 1

        # Agrupa por severidade
        por_sev: Counter = Counter()
        exemplos: dict = {}
        for assinatura, sev in tipos.items():
            por_sev[sev] += 1
            exemplos.setdefault(sev, [])
            if len(exemplos[sev]) < 3:
                exemplos[sev].append(f"[{ocorrencias[assinatura]}x] {assinatura}")

        # Score baseado em tipos únicos (não ocorrências brutas)
        penalidade = (
            por_sev.get("CRITICO", 0) * LIMITES["CRITICO"]
            + por_sev.get("ALTO", 0) * LIMITES["ALTO"]
            + por_sev.get("MEDIO", 0) * LIMITES["MEDIO"]
        )
        score = max(0.0, min(10.0, 10.0 - penalidade))

        bugs = [
            {
                "tipo": f"log_{sev.lower()}",
                "severidade": sev,
                "tipos_unicos": por_sev.get(sev, 0),
                "exemplos": exemplos.get(sev, []),
                "descricao": (f"{por_sev.get(sev, 0)} tipo(s) {sev} nas últimas 2h"),
                "autocorrigivel": False,
                "acao_jordan": sev == "CRITICO" and por_sev.get(sev, 0) > 0,
            }
            for sev in ("CRITICO", "ALTO", "MEDIO")
            if por_sev.get(sev, 0) > 0
        ]

        n_json = sum(
            1 for ln in linhas if TIMESTAMP_RE.sub("", ln.strip()).startswith("{")
        )
        resultado = {
            "agente": "log_monitor",
            "score": round(score, 1),
            "periodo": "ultimas_2h",
            "linhas_total": len(linhas),
            "linhas_json": n_json,
            "tipos_unicos_critico": por_sev.get("CRITICO", 0),
            "tipos_unicos_alto": por_sev.get("ALTO", 0),
            "tipos_unicos_medio": por_sev.get("MEDIO", 0),
            "bugs": bugs,
        }
        print(
            f"  Logs 2h: {n_json} JSON | "
            f"Tipos únicos — CRITICO:{por_sev.get('CRITICO', 0)} "
            f"ALTO:{por_sev.get('ALTO', 0)} "
            f"MEDIO:{por_sev.get('MEDIO', 0)} | "
            f"Score: {resultado['score']}/10"
        )
        return resultado

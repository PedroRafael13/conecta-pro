"""
LogMonitorAgent — Monitora logs do container backend.
Detecta erros silenciosos (ERROR, Exception, Traceback)
que não chegam ao cliente como 5xx mas indicam problemas.
"""

import re
import subprocess
from collections import Counter
from datetime import datetime


CONTAINER_NAME = "conecta-pro-backend"
LINHAS_ANALISAR = 500

# Padrões que indicam problema
PADROES_ERRO = [
    re.compile(r"\bERROR\b", re.IGNORECASE),
    re.compile(r"\bException\b"),
    re.compile(r"\bTraceback\b"),
    re.compile(r"\bCRITICAL\b", re.IGNORECASE),
    re.compile(r"IntegrityError"),
    re.compile(r"OperationalError"),
    re.compile(r"TimeoutError"),
    re.compile(r"ConnectionRefusedError"),
    re.compile(r"sqlalchemy.*error", re.IGNORECASE),
]

# Padrões a ignorar (ruído esperado)
PADROES_IGNORAR = [
    re.compile(r"404 Not Found"),
    re.compile(r"401 Unauthorized"),
    re.compile(r"health.*check", re.IGNORECASE),
    re.compile(r"INFO.*uvicorn"),
    re.compile(r"DEBUG"),
    re.compile(r"Access-Control"),
]

# Palavras-chave para categorizar
CATEGORIAS = {
    "banco": [
        "IntegrityError",
        "OperationalError",
        "sqlalchemy",
        "psycopg2",
        "deadlock",
    ],
    "autenticacao": ["JWT", "token", "401", "403", "Unauthorized"],
    "performance": ["timeout", "TimeoutError", "slow query", "too many connections"],
    "sistema": ["MemoryError", "OSError", "FileNotFoundError", "CRITICAL"],
}


class LogMonitorAgent:
    """Monitora logs do container por erros silenciosos."""

    def __init__(self, token: str = ""):
        self.token = token  # não usa HTTP, apenas docker logs
        self.nome = "log_monitor"

    def _obter_logs(self) -> list:
        """Obtém últimas N linhas dos logs do container."""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "logs",
                    CONTAINER_NAME,
                    "--tail",
                    str(LINHAS_ANALISAR),
                    "--timestamps",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            # logs vão para stderr no docker
            linhas = (result.stdout + result.stderr).splitlines()
            return linhas
        except Exception as e:
            return [f"ERRO_COLETA: {e}"]

    def _deve_ignorar(self, linha: str) -> bool:
        return any(p.search(linha) for p in PADROES_IGNORAR)

    def _categorizar(self, linha: str) -> str:
        for cat, palavras in CATEGORIAS.items():
            if any(p.lower() in linha.lower() for p in palavras):
                return cat
        return "geral"

    def auditar(self) -> dict:
        print(
            f"🔍 LogMonitorAgent: analisando últimas {LINHAS_ANALISAR} linhas de log..."
        )
        linhas = self._obter_logs()

        erros_encontrados = []
        categorias_count: Counter = Counter()

        for linha in linhas:
            if self._deve_ignorar(linha):
                continue
            for padrao in PADROES_ERRO:
                if padrao.search(linha):
                    cat = self._categorizar(linha)
                    categorias_count[cat] += 1
                    erros_encontrados.append(
                        {
                            "linha": linha[:200],
                            "categoria": cat,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    break  # evita contar a mesma linha duas vezes

        # Agrupa por categoria para bugs
        bugs = []
        for cat, count in categorias_count.most_common():
            severidade = "ALTO" if cat in ["banco", "sistema"] else "MEDIO"
            bugs.append(
                {
                    "tipo": f"log_error_{cat}",
                    "quantidade": count,
                    "categoria": cat,
                    "descricao": (
                        f"Log: {count} erros de '{cat}' nas últimas "
                        f"{LINHAS_ANALISAR} linhas"
                    ),
                    "autocorrigivel": False,
                    "acao_jordan": severidade == "ALTO" and count > 5,
                    "severidade": severidade,
                }
            )

        total_erros = len(erros_encontrados)
        score = max(0.0, 10.0 - total_erros * 0.1 - len(bugs) * 0.5)

        resultado = {
            "agente": "log_monitor",
            "score": round(min(score, 10.0), 1),
            "linhas_analisadas": len(linhas),
            "total_erros": total_erros,
            "categorias": dict(categorias_count),
            "amostras": [e["linha"] for e in erros_encontrados[:5]],
            "bugs": bugs,
        }
        print(
            f"  Linhas: {len(linhas)} | "
            f"Erros: {total_erros} | "
            f"Categorias: {dict(categorias_count)} | "
            f"Score: {resultado['score']}/10"
        )
        return resultado

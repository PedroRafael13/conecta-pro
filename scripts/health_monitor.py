#!/usr/bin/env python3
"""
Monitor de Saude - ERP Conecta Mais
Verifica todos os componentes do sistema e envia alertas.
Pode ser executado via cron ou como servico.
"""

import argparse
import json
import os
import smtplib
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from email.mime.text import MIMEText
from typing import Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

import psycopg2
import redis


@dataclass
class HealthResult:
    """Resultado de verificacao de saude."""
    component: str
    status: str  # healthy, degraded, unhealthy
    message: str
    latency_ms: Optional[float] = None
    details: Optional[Dict] = None


class HealthMonitor:
    """Monitor de saude do sistema."""

    def __init__(
        self,
        api_url: str = "http://localhost:8080",
        db_url: Optional[str] = None,
        redis_url: Optional[str] = None,
        alert_email: Optional[str] = None,
        alert_webhook: Optional[str] = None,
    ):
        self.api_url = api_url
        self.db_url = db_url or os.getenv("DATABASE_URL", "")
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.alert_email = alert_email
        self.alert_webhook = alert_webhook
        self.results: List[HealthResult] = []

    def check_all(self) -> bool:
        """Executa todas as verificacoes."""
        self.results = []

        # Verificar API
        self.results.append(self._check_api())

        # Verificar Database
        self.results.append(self._check_database())

        # Verificar Redis
        self.results.append(self._check_redis())

        # Verificar endpoints criticos
        critical_endpoints = [
            "/api/v1/auth/login",
        ]
        for endpoint in critical_endpoints:
            self.results.append(self._check_endpoint(endpoint))

        # Verificar espaco em disco
        self.results.append(self._check_disk_space())

        # Verificar memoria
        self.results.append(self._check_memory())

        # Calcular status geral
        unhealthy = [r for r in self.results if r.status == "unhealthy"]
        degraded = [r for r in self.results if r.status == "degraded"]

        if unhealthy:
            self._send_alert(unhealthy)
            return False

        if degraded:
            print(f"WARNING: {len(degraded)} componentes degradados")

        return True

    def _check_api(self) -> HealthResult:
        """Verifica API principal."""
        start = time.time()
        try:
            req = Request(f"{self.api_url}/health", method="GET")
            req.add_header("User-Agent", "HealthMonitor/1.0")

            with urlopen(req, timeout=10) as response:
                latency = (time.time() - start) * 1000
                data = json.loads(response.read().decode())

                if response.status == 200 and data.get("status") == "healthy":
                    return HealthResult(
                        component="API",
                        status="healthy",
                        message="API respondendo normalmente",
                        latency_ms=latency,
                        details=data,
                    )
                else:
                    return HealthResult(
                        component="API",
                        status="degraded",
                        message=f"API retornou status inesperado: {data}",
                        latency_ms=latency,
                    )

        except HTTPError as e:
            return HealthResult(
                component="API",
                status="unhealthy",
                message=f"API retornou erro HTTP: {e.code}",
            )
        except URLError as e:
            return HealthResult(
                component="API",
                status="unhealthy",
                message=f"Falha ao conectar na API: {e.reason}",
            )
        except Exception as e:
            return HealthResult(
                component="API",
                status="unhealthy",
                message=f"Erro inesperado: {str(e)}",
            )

    def _check_database(self) -> HealthResult:
        """Verifica conexao com banco de dados."""
        if not self.db_url:
            return HealthResult(
                component="Database",
                status="degraded",
                message="DATABASE_URL nao configurada",
            )

        start = time.time()
        try:
            # Parse URL
            # postgresql://user:pass@host:port/db
            url = self.db_url.replace("postgresql+asyncpg://", "postgresql://")
            conn = psycopg2.connect(url, connect_timeout=5)
            cursor = conn.cursor()

            # Verificar conexao
            cursor.execute("SELECT 1")
            cursor.fetchone()

            # Verificar latencia
            cursor.execute("SELECT NOW()")
            db_time = cursor.fetchone()[0]

            latency = (time.time() - start) * 1000

            cursor.close()
            conn.close()

            return HealthResult(
                component="Database",
                status="healthy",
                message="Conexao com banco OK",
                latency_ms=latency,
                details={"db_time": str(db_time)},
            )

        except psycopg2.OperationalError as e:
            return HealthResult(
                component="Database",
                status="unhealthy",
                message=f"Falha ao conectar no banco: {str(e)[:100]}",
            )
        except Exception as e:
            return HealthResult(
                component="Database",
                status="unhealthy",
                message=f"Erro no banco: {str(e)[:100]}",
            )

    def _check_redis(self) -> HealthResult:
        """Verifica conexao com Redis."""
        start = time.time()
        try:
            client = redis.from_url(self.redis_url, socket_timeout=5)
            client.ping()
            latency = (time.time() - start) * 1000

            # Info basico
            info = client.info("server")

            return HealthResult(
                component="Redis",
                status="healthy",
                message="Redis respondendo",
                latency_ms=latency,
                details={
                    "version": info.get("redis_version"),
                    "uptime_days": info.get("uptime_in_days"),
                },
            )

        except redis.ConnectionError as e:
            return HealthResult(
                component="Redis",
                status="degraded",  # Redis eh opcional
                message=f"Falha ao conectar no Redis: {str(e)[:50]}",
            )
        except Exception as e:
            return HealthResult(
                component="Redis",
                status="degraded",
                message=f"Erro no Redis: {str(e)[:50]}",
            )

    def _check_endpoint(self, path: str) -> HealthResult:
        """Verifica endpoint especifico (apenas se existe)."""
        start = time.time()
        try:
            # Apenas verifica se endpoint responde (sem auth)
            req = Request(f"{self.api_url}{path}", method="GET")
            req.add_header("User-Agent", "HealthMonitor/1.0")

            with urlopen(req, timeout=10) as response:
                latency = (time.time() - start) * 1000
                # 401/403 eh OK - significa que endpoint existe
                return HealthResult(
                    component=f"Endpoint {path}",
                    status="healthy",
                    message="Endpoint acessivel",
                    latency_ms=latency,
                )

        except HTTPError as e:
            latency = (time.time() - start) * 1000
            if e.code in [401, 403, 405, 422]:
                # Erro de auth/method eh esperado
                return HealthResult(
                    component=f"Endpoint {path}",
                    status="healthy",
                    message=f"Endpoint acessivel (HTTP {e.code})",
                    latency_ms=latency,
                )
            else:
                return HealthResult(
                    component=f"Endpoint {path}",
                    status="degraded",
                    message=f"Endpoint retornou HTTP {e.code}",
                    latency_ms=latency,
                )

        except Exception as e:
            return HealthResult(
                component=f"Endpoint {path}",
                status="unhealthy",
                message=f"Endpoint inacessivel: {str(e)[:50]}",
            )

    def _check_disk_space(self) -> HealthResult:
        """Verifica espaco em disco."""
        try:
            statvfs = os.statvfs("/")
            total = statvfs.f_blocks * statvfs.f_frsize
            free = statvfs.f_bavail * statvfs.f_frsize
            used_percent = ((total - free) / total) * 100

            if used_percent >= 90:
                status = "unhealthy"
            elif used_percent >= 80:
                status = "degraded"
            else:
                status = "healthy"

            return HealthResult(
                component="Disk",
                status=status,
                message=f"Uso de disco: {used_percent:.1f}%",
                details={
                    "total_gb": round(total / (1024**3), 2),
                    "free_gb": round(free / (1024**3), 2),
                    "used_percent": round(used_percent, 2),
                },
            )

        except Exception as e:
            return HealthResult(
                component="Disk",
                status="degraded",
                message=f"Erro ao verificar disco: {str(e)[:50]}",
            )

    def _check_memory(self) -> HealthResult:
        """Verifica uso de memoria."""
        try:
            with open("/proc/meminfo", "r") as f:
                meminfo = {}
                for line in f:
                    parts = line.split(":")
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().split()[0]
                        meminfo[key] = int(value)

            total = meminfo.get("MemTotal", 0)
            available = meminfo.get("MemAvailable", 0)
            used_percent = ((total - available) / total) * 100 if total > 0 else 0

            if used_percent >= 95:
                status = "unhealthy"
            elif used_percent >= 85:
                status = "degraded"
            else:
                status = "healthy"

            return HealthResult(
                component="Memory",
                status=status,
                message=f"Uso de memoria: {used_percent:.1f}%",
                details={
                    "total_mb": round(total / 1024, 2),
                    "available_mb": round(available / 1024, 2),
                    "used_percent": round(used_percent, 2),
                },
            )

        except Exception as e:
            return HealthResult(
                component="Memory",
                status="degraded",
                message=f"Erro ao verificar memoria: {str(e)[:50]}",
            )

    def _send_alert(self, unhealthy_results: List[HealthResult]):
        """Envia alerta sobre componentes com falha."""
        message = f"ALERTA - ERP Conecta Mais - {datetime.now()}\n\n"
        message += "Componentes com falha:\n\n"

        for result in unhealthy_results:
            message += f"- {result.component}: {result.message}\n"

        print(f"\n{'='*60}")
        print("ALERTA DE SAUDE!")
        print(message)
        print(f"{'='*60}\n")

        # Enviar por email se configurado
        if self.alert_email:
            self._send_email_alert(message)

        # Enviar para webhook se configurado
        if self.alert_webhook:
            self._send_webhook_alert(unhealthy_results)

    def _send_email_alert(self, message: str):
        """Envia alerta por email."""
        try:
            smtp_host = os.getenv("SMTP_HOST", "localhost")
            smtp_port = int(os.getenv("SMTP_PORT", "25"))
            smtp_user = os.getenv("SMTP_USER")
            smtp_pass = os.getenv("SMTP_PASSWORD")

            msg = MIMEText(message)
            msg["Subject"] = f"[ALERTA] ERP Conecta Mais - {datetime.now():%Y-%m-%d %H:%M}"
            msg["From"] = smtp_user or "monitor@erp-conecta-mais.local"
            msg["To"] = self.alert_email

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if smtp_user and smtp_pass:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)

            print(f"Email de alerta enviado para {self.alert_email}")

        except Exception as e:
            print(f"Falha ao enviar email: {e}")

    def _send_webhook_alert(self, unhealthy_results: List[HealthResult]):
        """Envia alerta para webhook (Slack, Discord, etc)."""
        try:
            payload = {
                "text": f"ALERTA - ERP Conecta Mais",
                "attachments": [
                    {
                        "color": "danger",
                        "title": r.component,
                        "text": r.message,
                    }
                    for r in unhealthy_results
                ],
            }

            data = json.dumps(payload).encode("utf-8")
            req = Request(self.alert_webhook, data=data, method="POST")
            req.add_header("Content-Type", "application/json")

            with urlopen(req, timeout=10) as response:
                if response.status == 200:
                    print("Alerta enviado para webhook")

        except Exception as e:
            print(f"Falha ao enviar webhook: {e}")

    def print_report(self):
        """Imprime relatorio de saude."""
        print(f"\n{'='*60}")
        print(f"RELATORIO DE SAUDE - {datetime.now():%Y-%m-%d %H:%M:%S}")
        print(f"{'='*60}\n")

        status_icons = {
            "healthy": "[OK]",
            "degraded": "[WARN]",
            "unhealthy": "[FAIL]",
        }

        for result in self.results:
            icon = status_icons.get(result.status, "[???]")
            latency = f" ({result.latency_ms:.0f}ms)" if result.latency_ms else ""
            print(f"{icon} {result.component}: {result.message}{latency}")

        print(f"\n{'='*60}")

        # Resumo
        healthy = sum(1 for r in self.results if r.status == "healthy")
        degraded = sum(1 for r in self.results if r.status == "degraded")
        unhealthy = sum(1 for r in self.results if r.status == "unhealthy")

        print(f"Resumo: {healthy} OK | {degraded} WARN | {unhealthy} FAIL")
        print(f"{'='*60}\n")

    def to_json(self) -> str:
        """Retorna resultados em JSON."""
        return json.dumps(
            {
                "timestamp": datetime.now().isoformat(),
                "results": [
                    {
                        "component": r.component,
                        "status": r.status,
                        "message": r.message,
                        "latency_ms": r.latency_ms,
                        "details": r.details,
                    }
                    for r in self.results
                ],
                "summary": {
                    "healthy": sum(1 for r in self.results if r.status == "healthy"),
                    "degraded": sum(1 for r in self.results if r.status == "degraded"),
                    "unhealthy": sum(1 for r in self.results if r.status == "unhealthy"),
                },
            },
            indent=2,
        )


def main():
    parser = argparse.ArgumentParser(description="Monitor de Saude - ERP Conecta Mais")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8080",
        help="URL da API (default: http://localhost:8080)",
    )
    parser.add_argument(
        "--db-url",
        default=os.getenv("DATABASE_URL"),
        help="URL do banco de dados",
    )
    parser.add_argument(
        "--redis-url",
        default=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        help="URL do Redis",
    )
    parser.add_argument(
        "--alert-email",
        help="Email para envio de alertas",
    )
    parser.add_argument(
        "--alert-webhook",
        help="URL do webhook para alertas (Slack, Discord)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Saida em formato JSON",
    )
    parser.add_argument(
        "--loop",
        type=int,
        metavar="SECONDS",
        help="Executar em loop a cada N segundos",
    )

    args = parser.parse_args()

    monitor = HealthMonitor(
        api_url=args.api_url,
        db_url=args.db_url,
        redis_url=args.redis_url,
        alert_email=args.alert_email,
        alert_webhook=args.alert_webhook,
    )

    if args.loop:
        print(f"Executando monitor a cada {args.loop} segundos...")
        while True:
            try:
                monitor.check_all()
                if args.json:
                    print(monitor.to_json())
                else:
                    monitor.print_report()
                time.sleep(args.loop)
            except KeyboardInterrupt:
                print("\nMonitor encerrado.")
                break
    else:
        is_healthy = monitor.check_all()
        if args.json:
            print(monitor.to_json())
        else:
            monitor.print_report()
        sys.exit(0 if is_healthy else 1)


if __name__ == "__main__":
    main()

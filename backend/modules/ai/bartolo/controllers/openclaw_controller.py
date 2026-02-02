"""
Controller para API do OpenClaw - Sistema de Checagem de Código.

Expõe endpoints para executar checks, visualizar relatórios e monitorar status.
"""

import asyncio
import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db
from core.models import User

logger = logging.getLogger(__name__)

# Router
openclaw_router = APIRouter(prefix="/openclaw", tags=["OpenClaw - Code Quality"])

# Configurações
OPENCLAW_RUNNER = "/opt/conecta-pro/scripts/openclaw/runner.py"
OPENCLAW_REPORTS_DIR = Path("/opt/conecta-pro/reports/openclaw")


# ==========================================
# Schemas
# ==========================================


class RunCheckRequest(BaseModel):
    """Request para executar check."""

    check: str = Field(
        ...,
        description="Tipo de check: tests|lint|security|coverage|health|full",
        pattern="^(tests|lint|security|coverage|health|full)$",
    )


class CheckDetail(BaseModel):
    """Detalhe de um check individual."""

    check: str
    status: str
    duration_seconds: float
    message: str
    details: dict | None = None


class RunCheckResponse(BaseModel):
    """Response de execução de check."""

    cycle_id: str
    overall_status: str
    duration_seconds: float
    summary: dict
    checks: list[CheckDetail]


class ReportResponse(BaseModel):
    """Response de relatório completo."""

    cycle_id: str
    overall_status: str
    duration_seconds: float
    timestamp: str
    summary: dict
    checks: list[CheckDetail]


class HistoryItem(BaseModel):
    """Item do histórico."""

    cycle_id: str
    overall_status: str
    duration_seconds: float
    timestamp: str


class HistoryResponse(BaseModel):
    """Response de histórico."""

    reports: list[HistoryItem]
    total: int


class StatusResponse(BaseModel):
    """Response de status do daemon."""

    daemon_running: bool
    last_cycle: dict | None = None
    next_cycle_at: str | None = None


# ==========================================
# Endpoints
# ==========================================


@openclaw_router.post("/run", response_model=RunCheckResponse)
async def run_openclaw_check(
    request: RunCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Executa check do OpenClaw.

    Tipos de check disponíveis:
    - **tests**: Executa testes pytest
    - **lint**: Verifica qualidade de código (ruff, black)
    - **security**: Análise de segurança (bandit)
    - **coverage**: Cobertura de testes
    - **health**: Health check de serviços
    - **full**: Executa todos os checks

    Requer autenticação.
    """
    check_type = request.check

    # Mapeia tipo de check para flag do runner
    check_map = {
        "tests": "tests",
        "lint": "lint",
        "security": "security",
        "coverage": "coverage",
        "health": "health",
        "full": None,  # full não usa --only
    }

    # Monta comando
    cmd = ["python3", OPENCLAW_RUNNER]
    if check_type != "full":
        cmd.extend(["--only", check_map[check_type]])

    logger.info(f"[OpenClaw API] Usuario {current_user.email} executando: {' '.join(cmd)}")

    # Executa subprocess
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/opt/conecta-pro",
        )

        # Timeout de 5 minutos
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)

        if process.returncode != 0:
            logger.warning(f"[OpenClaw API] Processo retornou codigo {process.returncode}: {stderr.decode()[:200]}")

    except TimeoutError:
        process.kill()
        logger.error("[OpenClaw API] Timeout na execução do runner")
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Timeout: execução ultrapassou 5 minutos",
        )
    except Exception as e:
        logger.error(f"[OpenClaw API] Erro ao executar runner: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar check: {str(e)}",
        )

    # Lê relatório gerado
    latest_json = OPENCLAW_REPORTS_DIR / "latest.json"
    if not latest_json.exists():
        logger.error("[OpenClaw API] Relatório latest.json não foi gerado")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Relatório não foi gerado. Verifique logs do runner.",
        )

    try:
        report = json.loads(latest_json.read_text())
    except Exception as e:
        logger.error(f"[OpenClaw API] Erro ao ler relatório: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar relatório gerado",
        )

    # Formata checks
    checks = [
        CheckDetail(
            check=c["check"],
            status=c["status"],
            duration_seconds=c["duration_seconds"],
            message=c["message"],
            details=c.get("details"),
        )
        for c in report.get("checks", [])
    ]

    logger.info(f"[OpenClaw API] Check concluído: {report['overall_status']} em {report['duration_seconds']:.2f}s")

    return RunCheckResponse(
        cycle_id=report["cycle_id"],
        overall_status=report["overall_status"],
        duration_seconds=report["duration_seconds"],
        summary=report.get("summary", {}),
        checks=checks,
    )


@openclaw_router.get("/report", response_model=ReportResponse)
async def get_latest_report(
    current_user: User = Depends(get_current_user),
):
    """
    Retorna o último relatório do OpenClaw.

    Útil para dashboard e visualização rápida do status atual.
    """
    latest_json = OPENCLAW_REPORTS_DIR / "latest.json"

    if not latest_json.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum relatório encontrado. Execute um check primeiro.",
        )

    try:
        report = json.loads(latest_json.read_text())
    except Exception as e:
        logger.error(f"[OpenClaw API] Erro ao ler relatório: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao ler relatório",
        )

    # Formata checks
    checks = [
        CheckDetail(
            check=c["check"],
            status=c["status"],
            duration_seconds=c["duration_seconds"],
            message=c["message"],
            details=c.get("details"),
        )
        for c in report.get("checks", [])
    ]

    return ReportResponse(
        cycle_id=report["cycle_id"],
        overall_status=report["overall_status"],
        duration_seconds=report["duration_seconds"],
        timestamp=report["timestamp"],
        summary=report.get("summary", {}),
        checks=checks,
    )


@openclaw_router.get("/history", response_model=HistoryResponse)
async def get_history(
    limit: int = Query(10, ge=1, le=100, description="Número de relatórios a retornar"),
    current_user: User = Depends(get_current_user),
):
    """
    Retorna histórico de ciclos do OpenClaw.

    Permite visualizar tendências e evolução da qualidade do código.
    """
    try:
        # Busca todos os ciclos, ordena por mais recente
        reports = sorted(OPENCLAW_REPORTS_DIR.glob("cycle_*.json"), reverse=True)[:limit]

        history = []
        for report_path in reports:
            try:
                data = json.loads(report_path.read_text())
                history.append(
                    HistoryItem(
                        cycle_id=data["cycle_id"],
                        overall_status=data["overall_status"],
                        duration_seconds=data["duration_seconds"],
                        timestamp=data["timestamp"],
                    )
                )
            except Exception as e:
                logger.warning(f"[OpenClaw API] Erro ao processar {report_path.name}: {e}")
                continue

        logger.info(f"[OpenClaw API] Retornando {len(history)} relatórios do histórico")

        return HistoryResponse(reports=history, total=len(history))

    except Exception as e:
        logger.error(f"[OpenClaw API] Erro ao buscar histórico: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar histórico",
        )


@openclaw_router.get("/status", response_model=StatusResponse)
async def get_daemon_status(
    current_user: User = Depends(get_current_user),
):
    """
    Retorna status do daemon do OpenClaw.

    Indica se o daemon está rodando e quando foi o último ciclo.
    """
    # Verifica se o service está rodando
    daemon_running = False
    try:
        process = await asyncio.create_subprocess_exec(
            "systemctl",
            "is-active",
            "openclaw",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await process.communicate()
        daemon_running = stdout.decode().strip() == "active"
    except Exception as e:
        logger.debug(f"[OpenClaw API] Não foi possível verificar status do daemon: {e}")

    # Lê último ciclo
    last_cycle = None
    next_cycle_at = None

    latest_json = OPENCLAW_REPORTS_DIR / "latest.json"
    if latest_json.exists():
        try:
            data = json.loads(latest_json.read_text())
            last_cycle = {
                "cycle_id": data["cycle_id"],
                "overall_status": data["overall_status"],
                "timestamp": data["timestamp"],
                "duration_seconds": data["duration_seconds"],
            }

            # TODO: Calcular next_cycle_at baseado em config do daemon
            # Por enquanto, retorna None

        except Exception as e:
            logger.warning(f"[OpenClaw API] Erro ao ler último ciclo: {e}")

    return StatusResponse(
        daemon_running=daemon_running,
        last_cycle=last_cycle,
        next_cycle_at=next_cycle_at,
    )

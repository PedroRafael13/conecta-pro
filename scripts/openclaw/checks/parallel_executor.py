"""
Executor paralelo para OpenClaw checks.

Executa múltiplos checks simultaneamente usando asyncio,
reduzindo drasticamente o tempo total de execução.

Author: Conecta PRO Team
Date: 2026-02-02
"""

import asyncio
import logging
import subprocess
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CheckResult:
    """Resultado de um check individual."""

    name: str
    status: str  # pass, fail, warn, error, skip
    duration: float
    message: str
    details: dict


class ParallelExecutor:
    """Executa checks em paralelo usando asyncio."""

    def __init__(self, max_concurrent: int = 3):
        """
        Initialize parallel executor.

        Args:
            max_concurrent: Número máximo de checks executando simultaneamente
        """
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def run_check(
        self, name: str, func: Callable, timeout: int, *args, **kwargs
    ) -> CheckResult:
        """
        Executa um check individual com timeout e error handling.

        Args:
            name: Nome do check
            func: Função async ou sync a executar
            timeout: Timeout em segundos
            *args, **kwargs: Argumentos para a função

        Returns:
            CheckResult com status e detalhes
        """
        async with self.semaphore:
            start = time.time()

            try:
                # Se função não é async, executa em thread pool
                if not asyncio.iscoroutinefunction(func):
                    result = await asyncio.wait_for(
                        asyncio.to_thread(func, *args, **kwargs), timeout=timeout
                    )
                else:
                    result = await asyncio.wait_for(
                        func(*args, **kwargs), timeout=timeout
                    )

                duration = time.time() - start

                # Normaliza resultado
                if isinstance(result, dict):
                    return CheckResult(
                        name=name,
                        status=result.get("status", "pass"),
                        duration=duration,
                        message=result.get("message", ""),
                        details=result.get("details", {}),
                    )
                elif hasattr(result, 'status') and hasattr(result, 'message'):
                    # Resultado é um CheckResult do runner (dataclass)
                    return CheckResult(
                        name=result.name if hasattr(result, 'name') else name,
                        status=result.status.value if hasattr(result.status, 'value') else result.status,
                        duration=duration,
                        message=result.message,
                        details=result.details if hasattr(result, 'details') else {},
                    )
                else:
                    # Resultado simples (bool ou string)
                    status = "pass" if result else "fail"
                    return CheckResult(
                        name=name,
                        status=status,
                        duration=duration,
                        message=str(result) if result else "",
                        details={},
                    )

            except asyncio.TimeoutError:
                logger.warning(f"Check {name} timeout após {timeout}s")
                return CheckResult(
                    name=name,
                    status="error",
                    duration=timeout,
                    message=f"Timeout após {timeout}s",
                    details={"timeout": timeout},
                )

            except subprocess.CalledProcessError as e:
                logger.error(f"Check {name} falhou: {e}")
                return CheckResult(
                    name=name,
                    status="fail",
                    duration=time.time() - start,
                    message=str(e),
                    details={"returncode": e.returncode, "stderr": e.stderr},
                )

            except Exception as e:
                logger.error(f"Check {name} error: {e}", exc_info=True)
                return CheckResult(
                    name=name,
                    status="error",
                    duration=time.time() - start,
                    message=str(e),
                    details={"exception": type(e).__name__},
                )

    async def run_all(self, checks: List[Dict]) -> List[CheckResult]:
        """
        Executa todos os checks em paralelo.

        Args:
            checks: Lista de dicionários com:
                - name: str
                - func: Callable
                - timeout: int
                - args: tuple (opcional)
                - kwargs: dict (opcional)

        Returns:
            Lista de CheckResults
        """
        logger.info(f"Iniciando {len(checks)} checks em paralelo (max {self.max_concurrent} simultâneos)")

        tasks = []
        for check in checks:
            task = self.run_check(
                name=check["name"],
                func=check["func"],
                timeout=check.get("timeout", 120),
                *check.get("args", ()),
                **check.get("kwargs", {}),
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        logger.info(f"Todos os checks concluídos")
        return results

    @staticmethod
    def results_to_dict(results: List[CheckResult]) -> List[Dict]:
        """Converte lista de CheckResults para lista de dicts."""
        return [
            {
                "name": r.name,
                "status": r.status,
                "duration_seconds": r.duration,
                "message": r.message,
                "details": r.details,
            }
            for r in results
        ]

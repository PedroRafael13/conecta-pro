"""Schemas para operações em batch."""

from typing import Any

from pydantic import BaseModel, Field


class BatchOperation(BaseModel):
    """Operação individual em um batch."""

    id: str = Field(..., description="ID único da operação")
    method: str = Field(..., description="GET, POST, PUT, PATCH, DELETE")
    endpoint: str = Field(..., description="Endpoint da API")
    data: dict[str, Any] | None = Field(default=None, description="Dados do request")
    params: dict[str, Any] | None = Field(default=None, description="Query params")
    headers: dict[str, str] | None = Field(default=None, description="Headers adicionais")
    can_parallelize: bool = Field(default=True, description="Pode executar em paralelo")
    depends_on: str | None = Field(default=None, description="ID de operação dependente")
    timeout_ms: int = Field(default=30000, description="Timeout em ms")
    retry_on_failure: bool = Field(default=True)
    max_retries: int = Field(default=2, ge=0, le=5)

    model_config = {"from_attributes": True}


class BatchRequest(BaseModel):
    """Request para operações em batch."""

    operations: list[BatchOperation] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Lista de operações (máx 50)",
    )
    parallel_execution: bool = Field(
        default=True,
        description="Executar operações em paralelo quando possível",
    )
    stop_on_error: bool = Field(
        default=False,
        description="Parar execução no primeiro erro",
    )
    transaction_mode: bool = Field(
        default=False,
        description="Executar em transação (rollback em caso de erro)",
    )

    model_config = {"from_attributes": True}


class BatchOperationResult(BaseModel):
    """Resultado de uma operação do batch."""

    id: str = Field(..., description="ID da operação")
    status: str = Field(..., description="success, error, skipped")
    status_code: int = Field(..., description="HTTP status code")
    data: dict[str, Any] | None = Field(default=None, description="Dados da resposta")
    error: str | None = Field(default=None, description="Mensagem de erro")
    execution_time_ms: int = Field(..., description="Tempo de execução em ms")
    retries: int = Field(default=0, description="Número de retries")

    model_config = {"from_attributes": True}


class BatchResponse(BaseModel):
    """Response de operações em batch."""

    results: list[BatchOperationResult] = Field(..., description="Resultados das operações")
    execution_time_ms: float = Field(..., description="Tempo total de execução")
    success_count: int = Field(..., description="Operações bem sucedidas")
    error_count: int = Field(..., description="Operações com erro")
    skipped_count: int = Field(default=0, description="Operações puladas")
    transaction_committed: bool | None = Field(
        default=None,
        description="Se transação foi commitada",
    )

    model_config = {"from_attributes": True}

    @property
    def all_successful(self) -> bool:
        """Verifica se todas operações foram bem sucedidas."""
        return self.error_count == 0 and self.skipped_count == 0

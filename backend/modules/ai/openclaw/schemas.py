"""Schemas Pydantic para o webhook do Alertmanager."""

from pydantic import BaseModel, Field


class AlertLabel(BaseModel):
    alertname: str = ""
    severity: str = "warning"
    job: str = ""
    instance: str = ""

    model_config = {"extra": "allow"}


class AlertAnnotation(BaseModel):
    summary: str = ""
    description: str = ""

    model_config = {"extra": "allow"}


class AlertItem(BaseModel):
    status: str = "firing"  # firing | resolved
    labels: AlertLabel = Field(default_factory=AlertLabel)
    annotations: AlertAnnotation = Field(default_factory=AlertAnnotation)
    startsAt: str = ""  # noqa: N815
    endsAt: str = ""  # noqa: N815
    generatorURL: str = ""  # noqa: N815
    fingerprint: str = ""

    model_config = {"extra": "allow"}


class AlertmanagerPayload(BaseModel):
    """Payload enviado pelo Alertmanager via webhook."""

    version: str = "4"
    groupKey: str = ""  # noqa: N815
    status: str = "firing"  # firing | resolved
    receiver: str = ""
    alerts: list[AlertItem] = Field(default_factory=list)

    model_config = {"extra": "allow"}


class InterventionResponse(BaseModel):
    """Resposta do webhook."""

    intervention_id: str
    alert_name: str
    status: str
    diagnosis: str | None = None
    actions_taken: list[str] = Field(default_factory=list)
    telegram_sent: bool = False

    model_config = {"from_attributes": True}


class FeedbackRequest(BaseModel):
    """Feedback humano sobre uma intervenção."""

    intervention_id: str
    approved: bool
    feedback: str = ""
    validated_by: str = "Jordan"


class FeedbackResponse(BaseModel):
    """Resposta do endpoint de feedback."""

    intervention_id: str
    human_validated: bool
    confidence_updated: bool = False
    pattern_name: str | None = None
    new_confidence: float | None = None
    message: str

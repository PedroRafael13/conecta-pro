"""APNsService - Apple Push Notification Service.

Sprint 37 - Push Notifications Mobile.
"""

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class APNsPayload:
    """Estrutura de payload APNs."""

    def __init__(
        self,
        alert: dict[str, Any] | None = None,
        badge: int | None = None,
        sound: str | None = None,
        content_available: bool = False,
        mutable_content: bool = False,
        category: str | None = None,
        thread_id: str | None = None,
        target_content_id: str | None = None,
        interruption_level: str = "active",
        relevance_score: float | None = None,
        custom_data: dict[str, Any] | None = None,
    ):
        self.alert = alert
        self.badge = badge
        self.sound = sound
        self.content_available = content_available
        self.mutable_content = mutable_content
        self.category = category
        self.thread_id = thread_id
        self.target_content_id = target_content_id
        self.interruption_level = interruption_level
        self.relevance_score = relevance_score
        self.custom_data = custom_data or {}

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário APNs."""
        aps: dict[str, Any] = {}

        if self.alert:
            aps["alert"] = self.alert

        if self.badge is not None:
            aps["badge"] = self.badge

        if self.sound:
            aps["sound"] = self.sound

        if self.content_available:
            aps["content-available"] = 1

        if self.mutable_content:
            aps["mutable-content"] = 1

        if self.category:
            aps["category"] = self.category

        if self.thread_id:
            aps["thread-id"] = self.thread_id

        if self.target_content_id:
            aps["target-content-id"] = self.target_content_id

        if self.interruption_level:
            aps["interruption-level"] = self.interruption_level

        if self.relevance_score is not None:
            aps["relevance-score"] = self.relevance_score

        payload = {"aps": aps}
        payload.update(self.custom_data)

        return payload

    @classmethod
    def create_alert(
        cls,
        title: str,
        body: str,
        subtitle: str | None = None,
        title_loc_key: str | None = None,
        title_loc_args: list[str] | None = None,
        body_loc_key: str | None = None,
        body_loc_args: list[str] | None = None,
        action_loc_key: str | None = None,
        launch_image: str | None = None,
    ) -> dict[str, Any]:
        """Cria estrutura de alert APNs."""
        alert: dict[str, Any] = {
            "title": title,
            "body": body,
        }

        if subtitle:
            alert["subtitle"] = subtitle

        if title_loc_key:
            alert["title-loc-key"] = title_loc_key

        if title_loc_args:
            alert["title-loc-args"] = title_loc_args

        if body_loc_key:
            alert["loc-key"] = body_loc_key

        if body_loc_args:
            alert["loc-args"] = body_loc_args

        if action_loc_key:
            alert["action-loc-key"] = action_loc_key

        if launch_image:
            alert["launch-image"] = launch_image

        return alert


class APNsResponse:  # noqa: B903
    """Resposta do APNs."""

    def __init__(
        self,
        success: bool,
        apns_id: str | None = None,
        status_code: int | None = None,
        reason: str | None = None,
        timestamp: int | None = None,
    ):
        self.success = success
        self.apns_id = apns_id
        self.status_code = status_code
        self.reason = reason
        self.timestamp = timestamp


class APNsService:
    """Serviço de integração com Apple Push Notification Service."""

    # Códigos de erro que indicam token inválido
    INVALID_TOKEN_REASONS = [
        "BadDeviceToken",
        "Unregistered",
        "DeviceTokenNotForTopic",
        "ExpiredProviderToken",
    ]

    # Códigos de erro que permitem retry
    RETRYABLE_REASONS = [
        "ServiceUnavailable",
        "InternalServerError",
        "Shutdown",
        "TooManyRequests",
    ]

    def __init__(
        self,
        team_id: str,
        key_id: str,
        key_path: str | None = None,
        key_content: str | None = None,
        bundle_id: str = "",
        use_sandbox: bool = False,
    ):
        """Inicializa o serviço APNs.

        Args:
            team_id: Apple Team ID.
            key_id: ID da chave de autenticação.
            key_path: Caminho para arquivo .p8.
            key_content: Conteúdo da chave .p8.
            bundle_id: Bundle ID do app.
            use_sandbox: Usar ambiente sandbox.
        """
        self.team_id = team_id
        self.key_id = key_id
        self.key_path = key_path
        self.key_content = key_content
        self.bundle_id = bundle_id
        self.use_sandbox = use_sandbox
        self._initialized = False
        self._client = None

    @property
    def server_url(self) -> str:
        """Retorna URL do servidor APNs."""
        if self.use_sandbox:
            return "https://api.sandbox.push.apple.com"
        return "https://api.push.apple.com"

    def _initialize(self) -> None:
        """Inicializa o cliente APNs (lazy)."""
        if self._initialized:
            return

        try:
            # Em produção, usar biblioteca como aioapns ou apns2
            # import jwt
            # from httpx import AsyncClient
            #
            # self._client = ...
            self._initialized = True
            logger.info(
                "APNs Service initialized for bundle %s (sandbox=%s)",
                self.bundle_id,
                self.use_sandbox,
            )

        except Exception as e:
            logger.error("Failed to initialize APNs: %s", e)
            raise

    def _generate_token(self) -> str:
        """Gera JWT token para autenticação APNs."""
        # Em produção:
        # import jwt
        # import time
        #
        # headers = {
        #     "alg": "ES256",
        #     "kid": self.key_id,
        # }
        # payload = {
        #     "iss": self.team_id,
        #     "iat": int(time.time()),
        # }
        #
        # key = self.key_content or open(self.key_path).read()
        # return jwt.encode(payload, key, algorithm="ES256", headers=headers)

        return f"apns_token_{datetime.utcnow().timestamp()}"

    def send(
        self,
        device_token: str,
        payload: APNsPayload,
        topic: str | None = None,
        priority: int = 10,
        expiration: int = 0,
        collapse_id: str | None = None,
        push_type: str = "alert",
    ) -> APNsResponse:
        """Envia uma notificação via APNs.

        Args:
            device_token: Token do dispositivo iOS.
            payload: Payload APNs.
            topic: Tópico (bundle ID).
            priority: Prioridade (5 ou 10).
            expiration: Timestamp de expiração.
            collapse_id: ID para colapsar notificações.
            push_type: Tipo de push (alert, background, voip, etc.).

        Returns:
            APNsResponse com resultado.
        """
        self._initialize()

        topic = topic or self.bundle_id

        try:
            # Em produção:
            # import httpx
            # import json
            #
            # headers = {
            #     "authorization": f"bearer {self._generate_token()}",
            #     "apns-topic": topic,
            #     "apns-push-type": push_type,
            #     "apns-priority": str(priority),
            # }
            #
            # if expiration:
            #     headers["apns-expiration"] = str(expiration)
            # if collapse_id:
            #     headers["apns-collapse-id"] = collapse_id
            #
            # url = f"{self.server_url}/3/device/{device_token}"
            #
            # async with httpx.AsyncClient(http2=True) as client:
            #     response = await client.post(
            #         url,
            #         headers=headers,
            #         json=payload.to_dict(),
            #     )
            #
            # if response.status_code == 200:
            #     return APNsResponse(
            #         success=True,
            #         apns_id=response.headers.get("apns-id"),
            #         status_code=200,
            #     )
            # else:
            #     data = response.json()
            #     return APNsResponse(
            #         success=False,
            #         status_code=response.status_code,
            #         reason=data.get("reason"),
            #         timestamp=data.get("timestamp"),
            #     )

            # Simulação para desenvolvimento
            logger.info(
                "APNs: Sending to token %s... - Topic: %s",
                device_token[:20],
                topic,
            )

            return APNsResponse(
                success=True,
                apns_id=f"apns_{datetime.utcnow().timestamp()}",
                status_code=200,
            )

        except Exception as e:
            logger.error("APNs send error: %s", e)
            return APNsResponse(
                success=False,
                status_code=500,
                reason=str(e),
            )

    def send_batch(
        self,
        device_tokens: list[str],
        payload: APNsPayload,
        topic: str | None = None,
        priority: int = 10,
    ) -> dict[str, Any]:
        """Envia notificações para múltiplos dispositivos.

        Args:
            device_tokens: Lista de tokens iOS.
            payload: Payload APNs.
            topic: Tópico (bundle ID).
            priority: Prioridade.

        Returns:
            Resultados por token.
        """
        results = {
            "success_count": 0,
            "failure_count": 0,
            "responses": [],
        }

        for token in device_tokens:
            response = self.send(
                device_token=token,
                payload=payload,
                topic=topic,
                priority=priority,
            )

            if response.success:
                results["success_count"] += 1
            else:
                results["failure_count"] += 1

            results["responses"].append(
                {
                    "token": token,
                    "success": response.success,
                    "apns_id": response.apns_id,
                    "reason": response.reason,
                }
            )

        logger.info(
            "APNs batch: %d success, %d failed",
            results["success_count"],
            results["failure_count"],
        )

        return results

    def send_silent(
        self,
        device_token: str,
        data: dict[str, Any],
        topic: str | None = None,
    ) -> APNsResponse:
        """Envia notificação silenciosa (background).

        Args:
            device_token: Token do dispositivo iOS.
            data: Dados para o app.
            topic: Tópico (bundle ID).

        Returns:
            APNsResponse com resultado.
        """
        payload = APNsPayload(
            content_available=True,
            custom_data=data,
        )

        return self.send(
            device_token=device_token,
            payload=payload,
            topic=topic,
            priority=5,  # Low priority for background
            push_type="background",
        )

    def send_voip(
        self,
        device_token: str,
        data: dict[str, Any],
        topic: str | None = None,
    ) -> APNsResponse:
        """Envia notificação VoIP.

        Args:
            device_token: Token VoIP do dispositivo.
            data: Dados para o app.
            topic: Tópico (bundle ID + .voip).

        Returns:
            APNsResponse com resultado.
        """
        payload = APNsPayload(custom_data=data)
        voip_topic = f"{topic or self.bundle_id}.voip"

        return self.send(
            device_token=device_token,
            payload=payload,
            topic=voip_topic,
            priority=10,
            push_type="voip",
        )

    def build_payload(
        self,
        title: str,
        body: str,
        subtitle: str | None = None,
        badge: int | None = None,
        sound: str = "default",
        category: str | None = None,
        thread_id: str | None = None,
        mutable_content: bool = False,
        interruption_level: str = "active",
        custom_data: dict[str, Any] | None = None,
    ) -> APNsPayload:
        """Constrói payload APNs conveniente.

        Args:
            title: Título da notificação.
            body: Corpo da notificação.
            subtitle: Subtítulo (opcional).
            badge: Número do badge (opcional).
            sound: Som da notificação.
            category: Categoria de ações.
            thread_id: Thread para agrupamento.
            mutable_content: Permite modificação (Notification Extension).
            interruption_level: Nível de interrupção.
            custom_data: Dados extras.

        Returns:
            APNsPayload configurado.
        """
        alert = APNsPayload.create_alert(
            title=title,
            body=body,
            subtitle=subtitle,
        )

        return APNsPayload(
            alert=alert,
            badge=badge,
            sound=sound,
            mutable_content=mutable_content,
            category=category,
            thread_id=thread_id,
            interruption_level=interruption_level,
            custom_data=custom_data,
        )

    def is_invalid_token_error(self, reason: str) -> bool:
        """Verifica se o erro indica token inválido.

        Args:
            reason: Razão do erro APNs.

        Returns:
            True se o token é inválido.
        """
        return reason in self.INVALID_TOKEN_REASONS

    def is_retryable_error(self, reason: str) -> bool:
        """Verifica se o erro permite retry.

        Args:
            reason: Razão do erro APNs.

        Returns:
            True se pode tentar novamente.
        """
        return reason in self.RETRYABLE_REASONS

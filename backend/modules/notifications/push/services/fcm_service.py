"""FCMService - Firebase Cloud Messaging Service.

Sprint 37 - Push Notifications Mobile.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from modules.notifications.push.models import (
    NotificationPriority,
    NotificationStatus,
    PushDevice,
    PushNotification,
)

logger = logging.getLogger(__name__)


class FCMMessage:
    """Estrutura de mensagem FCM."""

    def __init__(
        self,
        token: str,
        title: str,
        body: str,
        image: Optional[str] = None,
        data: Optional[Dict[str, str]] = None,
        android: Optional[Dict[str, Any]] = None,
        webpush: Optional[Dict[str, Any]] = None,
        apns: Optional[Dict[str, Any]] = None,
        fcm_options: Optional[Dict[str, Any]] = None,
    ):
        self.token = token
        self.title = title
        self.body = body
        self.image = image
        self.data = data or {}
        self.android = android
        self.webpush = webpush
        self.apns = apns
        self.fcm_options = fcm_options

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário FCM."""
        message = {
            "token": self.token,
            "notification": {
                "title": self.title,
                "body": self.body,
            },
        }

        if self.image:
            message["notification"]["image"] = self.image

        if self.data:
            message["data"] = {k: str(v) for k, v in self.data.items()}

        if self.android:
            message["android"] = self.android

        if self.webpush:
            message["webpush"] = self.webpush

        if self.apns:
            message["apns"] = self.apns

        if self.fcm_options:
            message["fcm_options"] = self.fcm_options

        return message


class FCMResponse:
    """Resposta do FCM."""

    def __init__(
        self,
        success: bool,
        message_id: Optional[str] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        self.success = success
        self.message_id = message_id
        self.error_code = error_code
        self.error_message = error_message


class FCMService:
    """Serviço de integração com Firebase Cloud Messaging."""

    # Códigos de erro que indicam token inválido
    INVALID_TOKEN_ERRORS = [
        "messaging/invalid-registration-token",
        "messaging/registration-token-not-registered",
        "UNREGISTERED",
        "INVALID_ARGUMENT",
    ]

    # Códigos de erro que permitem retry
    RETRYABLE_ERRORS = [
        "messaging/server-unavailable",
        "messaging/internal-error",
        "UNAVAILABLE",
        "INTERNAL",
        "QUOTA_EXCEEDED",
    ]

    def __init__(
        self,
        project_id: str,
        credentials_path: Optional[str] = None,
        credentials_dict: Optional[Dict[str, Any]] = None,
    ):
        """Inicializa o serviço FCM.

        Args:
            project_id: ID do projeto Firebase.
            credentials_path: Caminho para arquivo de credenciais.
            credentials_dict: Dicionário com credenciais.
        """
        self.project_id = project_id
        self.credentials_path = credentials_path
        self.credentials_dict = credentials_dict
        self._initialized = False
        self._app = None

    def _initialize(self) -> None:
        """Inicializa o Firebase Admin SDK (lazy)."""
        if self._initialized:
            return

        try:
            # Em produção, usar firebase_admin
            # import firebase_admin
            # from firebase_admin import credentials, messaging
            #
            # if self.credentials_path:
            #     cred = credentials.Certificate(self.credentials_path)
            # elif self.credentials_dict:
            #     cred = credentials.Certificate(self.credentials_dict)
            # else:
            #     cred = credentials.ApplicationDefault()
            #
            # self._app = firebase_admin.initialize_app(cred)
            self._initialized = True
            logger.info("FCM Service initialized for project %s", self.project_id)

        except Exception as e:
            logger.error("Failed to initialize FCM: %s", e)
            raise

    def send(self, message: FCMMessage) -> FCMResponse:
        """Envia uma notificação via FCM.

        Args:
            message: Mensagem FCM para enviar.

        Returns:
            FCMResponse com resultado.
        """
        self._initialize()

        try:
            # Em produção:
            # from firebase_admin import messaging
            # fcm_message = messaging.Message(**message.to_dict())
            # response = messaging.send(fcm_message)
            # return FCMResponse(success=True, message_id=response)

            # Simulação para desenvolvimento
            logger.info(
                "FCM: Sending to token %s... - Title: %s",
                message.token[:20],
                message.title,
            )

            # Simula sucesso
            return FCMResponse(
                success=True,
                message_id=f"fcm_{datetime.utcnow().timestamp()}",
            )

        except Exception as e:
            error_str = str(e)
            error_code = self._extract_error_code(error_str)

            logger.error("FCM send error: %s", error_str)

            return FCMResponse(
                success=False,
                error_code=error_code,
                error_message=error_str,
            )

    def send_multicast(
        self,
        tokens: List[str],
        title: str,
        body: str,
        image: Optional[str] = None,
        data: Optional[Dict[str, str]] = None,
        android: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Envia notificação para múltiplos tokens.

        Args:
            tokens: Lista de tokens FCM.
            title: Título da notificação.
            body: Corpo da notificação.
            image: URL da imagem (opcional).
            data: Dados extras (opcional).
            android: Configurações Android (opcional).

        Returns:
            Dicionário com resultados por token.
        """
        self._initialize()

        results = {
            "success_count": 0,
            "failure_count": 0,
            "responses": [],
        }

        try:
            # Em produção:
            # from firebase_admin import messaging
            # multicast = messaging.MulticastMessage(
            #     tokens=tokens,
            #     notification=messaging.Notification(title=title, body=body, image=image),
            #     data=data,
            #     android=messaging.AndroidConfig(**android) if android else None,
            # )
            # response = messaging.send_each_for_multicast(multicast)
            #
            # for idx, resp in enumerate(response.responses):
            #     if resp.success:
            #         results["success_count"] += 1
            #         results["responses"].append({
            #             "token": tokens[idx],
            #             "success": True,
            #             "message_id": resp.message_id,
            #         })
            #     else:
            #         results["failure_count"] += 1
            #         results["responses"].append({
            #             "token": tokens[idx],
            #             "success": False,
            #             "error": str(resp.exception),
            #         })

            # Simulação para desenvolvimento
            for token in tokens:
                results["success_count"] += 1
                results["responses"].append({
                    "token": token,
                    "success": True,
                    "message_id": f"fcm_{datetime.utcnow().timestamp()}",
                })

            logger.info(
                "FCM multicast: %d success, %d failed",
                results["success_count"],
                results["failure_count"],
            )

        except Exception as e:
            logger.error("FCM multicast error: %s", e)
            results["failure_count"] = len(tokens)
            for token in tokens:
                results["responses"].append({
                    "token": token,
                    "success": False,
                    "error": str(e),
                })

        return results

    def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        image: Optional[str] = None,
        data: Optional[Dict[str, str]] = None,
    ) -> FCMResponse:
        """Envia notificação para um tópico.

        Args:
            topic: Nome do tópico.
            title: Título da notificação.
            body: Corpo da notificação.
            image: URL da imagem (opcional).
            data: Dados extras (opcional).

        Returns:
            FCMResponse com resultado.
        """
        self._initialize()

        try:
            # Em produção:
            # from firebase_admin import messaging
            # message = messaging.Message(
            #     topic=topic,
            #     notification=messaging.Notification(title=title, body=body, image=image),
            #     data=data,
            # )
            # response = messaging.send(message)
            # return FCMResponse(success=True, message_id=response)

            logger.info("FCM: Sending to topic '%s' - Title: %s", topic, title)

            return FCMResponse(
                success=True,
                message_id=f"fcm_topic_{datetime.utcnow().timestamp()}",
            )

        except Exception as e:
            logger.error("FCM topic send error: %s", e)
            return FCMResponse(
                success=False,
                error_code="TOPIC_SEND_ERROR",
                error_message=str(e),
            )

    def subscribe_to_topic(self, tokens: List[str], topic: str) -> Dict[str, Any]:
        """Inscreve dispositivos em um tópico.

        Args:
            tokens: Lista de tokens FCM.
            topic: Nome do tópico.

        Returns:
            Resultado da operação.
        """
        self._initialize()

        try:
            # Em produção:
            # from firebase_admin import messaging
            # response = messaging.subscribe_to_topic(tokens, topic)
            # return {
            #     "success_count": response.success_count,
            #     "failure_count": response.failure_count,
            #     "errors": [str(e) for e in response.errors],
            # }

            logger.info("FCM: Subscribing %d tokens to topic '%s'", len(tokens), topic)

            return {
                "success_count": len(tokens),
                "failure_count": 0,
                "errors": [],
            }

        except Exception as e:
            logger.error("FCM subscribe error: %s", e)
            return {
                "success_count": 0,
                "failure_count": len(tokens),
                "errors": [str(e)],
            }

    def unsubscribe_from_topic(self, tokens: List[str], topic: str) -> Dict[str, Any]:
        """Remove dispositivos de um tópico.

        Args:
            tokens: Lista de tokens FCM.
            topic: Nome do tópico.

        Returns:
            Resultado da operação.
        """
        self._initialize()

        try:
            # Em produção:
            # from firebase_admin import messaging
            # response = messaging.unsubscribe_from_topic(tokens, topic)
            # return {
            #     "success_count": response.success_count,
            #     "failure_count": response.failure_count,
            #     "errors": [str(e) for e in response.errors],
            # }

            logger.info("FCM: Unsubscribing %d tokens from topic '%s'", len(tokens), topic)

            return {
                "success_count": len(tokens),
                "failure_count": 0,
                "errors": [],
            }

        except Exception as e:
            logger.error("FCM unsubscribe error: %s", e)
            return {
                "success_count": 0,
                "failure_count": len(tokens),
                "errors": [str(e)],
            }

    def build_android_config(
        self,
        channel_id: str = "default",
        priority: str = "high",
        ttl: int = 86400,
        collapse_key: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        sound: Optional[str] = None,
        tag: Optional[str] = None,
        click_action: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Constrói configuração específica do Android.

        Args:
            channel_id: ID do canal de notificação.
            priority: Prioridade (normal, high).
            ttl: Time to live em segundos.
            collapse_key: Chave para colapsar notificações.
            color: Cor em hex (#RRGGBB).
            icon: Ícone da notificação.
            sound: Som da notificação.
            tag: Tag para substituição.
            click_action: Ação ao clicar.

        Returns:
            Configuração Android para FCM.
        """
        config: Dict[str, Any] = {
            "priority": priority,
            "ttl": f"{ttl}s",
            "notification": {
                "channel_id": channel_id,
            },
        }

        if collapse_key:
            config["collapse_key"] = collapse_key

        if color:
            config["notification"]["color"] = color

        if icon:
            config["notification"]["icon"] = icon

        if sound:
            config["notification"]["sound"] = sound

        if tag:
            config["notification"]["tag"] = tag

        if click_action:
            config["notification"]["click_action"] = click_action

        return config

    def is_invalid_token_error(self, error_code: str) -> bool:
        """Verifica se o erro indica token inválido.

        Args:
            error_code: Código do erro.

        Returns:
            True se o token é inválido.
        """
        return error_code in self.INVALID_TOKEN_ERRORS

    def is_retryable_error(self, error_code: str) -> bool:
        """Verifica se o erro permite retry.

        Args:
            error_code: Código do erro.

        Returns:
            True se pode tentar novamente.
        """
        return error_code in self.RETRYABLE_ERRORS

    def _extract_error_code(self, error_str: str) -> str:
        """Extrai código de erro da string de exceção."""
        for code in self.INVALID_TOKEN_ERRORS + self.RETRYABLE_ERRORS:
            if code in error_str:
                return code
        return "UNKNOWN_ERROR"

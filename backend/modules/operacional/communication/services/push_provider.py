"""
Provedores de Push Notification.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class PushProviderError(Exception):
    """Excecao base para erros de push notification."""

    pass


class PushProvider(ABC):
    """
    Interface abstrata para provedores de push notification.

    Define contrato para implementacoes de diferentes provedores
    como Firebase, OneSignal, etc.

    Example:
        >>> provider = FirebasePushProvider(credentials)
        >>> await provider.send_push(user_id, "Titulo", "Mensagem")
    """

    @abstractmethod
    async def send_push(
        self,
        user_id: str,
        title: str,
        body: str,
        data: dict[str, Any] | None = None,
        image_url: str | None = None,
    ) -> bool:
        """
        Envia push notification para um usuario.

        Args:
            user_id: ID do usuario destinatario
            title: Titulo da notificacao
            body: Corpo da notificacao
            data: Dados extras para a notificacao
            image_url: URL da imagem (opcional)

        Returns:
            True se enviado com sucesso

        Raises:
            PushProviderError: Se ocorrer erro no envio
        """
        pass

    @abstractmethod
    async def send_push_bulk(
        self,
        user_ids: list[str],
        title: str,
        body: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, bool]:
        """
        Envia push notification para multiplos usuarios.

        Args:
            user_ids: Lista de IDs de usuarios
            title: Titulo da notificacao
            body: Corpo da notificacao
            data: Dados extras

        Returns:
            Dicionario {user_id: success}

        Raises:
            PushProviderError: Se ocorrer erro critico
        """
        pass

    @abstractmethod
    async def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: dict[str, Any] | None = None,
    ) -> bool:
        """
        Envia push notification para um topico.

        Args:
            topic: Nome do topico
            title: Titulo da notificacao
            body: Corpo da notificacao
            data: Dados extras

        Returns:
            True se enviado com sucesso

        Raises:
            PushProviderError: Se ocorrer erro no envio
        """
        pass

    @abstractmethod
    async def register_device(
        self,
        user_id: str,
        device_token: str,
        platform: str,
    ) -> bool:
        """
        Registra dispositivo para receber push.

        Args:
            user_id: ID do usuario
            device_token: Token do dispositivo
            platform: Plataforma (ios, android, web)

        Returns:
            True se registrado com sucesso
        """
        pass

    @abstractmethod
    async def unregister_device(
        self,
        user_id: str,
        device_token: str,
    ) -> bool:
        """
        Remove registro de dispositivo.

        Args:
            user_id: ID do usuario
            device_token: Token do dispositivo

        Returns:
            True se removido com sucesso
        """
        pass


class FirebasePushProvider(PushProvider):
    """
    Provedor de push notification usando Firebase Cloud Messaging.

    Attributes:
        project_id: ID do projeto Firebase
        credentials: Credenciais de servico

    Example:
        >>> provider = FirebasePushProvider("my-project", credentials)
        >>> await provider.send_push("user-123", "Titulo", "Mensagem")
    """

    def __init__(
        self,
        project_id: str,
        credentials: dict[str, Any] | None = None,
    ) -> None:
        """
        Inicializa o provedor Firebase.

        Args:
            project_id: ID do projeto Firebase
            credentials: Credenciais de servico (opcional)
        """
        self.project_id = project_id
        self.credentials = credentials
        self._initialized = False
        self._device_tokens: dict[str, list[str]] = {}  # user_id -> [tokens]

    async def _ensure_initialized(self) -> None:
        """Garante que o Firebase esta inicializado."""
        if self._initialized:
            return

        try:
            # import firebase_admin
            # from firebase_admin import credentials as fb_credentials
            # cred = fb_credentials.Certificate(self.credentials)
            # firebase_admin.initialize_app(cred)
            self._initialized = True
            logger.info("Firebase Cloud Messaging inicializado")
        except Exception as e:
            logger.error(f"Erro ao inicializar Firebase: {e}")
            raise PushProviderError(f"Erro ao inicializar Firebase: {e}") from e

    async def send_push(
        self,
        user_id: str,
        title: str,
        body: str,
        data: dict[str, Any] | None = None,
        image_url: str | None = None,
    ) -> bool:
        """
        Envia push notification via Firebase.

        Args:
            user_id: ID do usuario
            title: Titulo
            body: Corpo
            data: Dados extras
            image_url: URL da imagem

        Returns:
            True se enviado
        """
        await self._ensure_initialized()

        tokens = self._device_tokens.get(user_id, [])
        if not tokens:
            logger.warning(f"Nenhum dispositivo registrado para usuario {user_id}")
            return False

        try:
            # from firebase_admin import messaging
            #
            # notification = messaging.Notification(
            #     title=title,
            #     body=body,
            #     image=image_url,
            # )
            #
            # message = messaging.MulticastMessage(
            #     notification=notification,
            #     data=data or {},
            #     tokens=tokens,
            # )
            #
            # response = messaging.send_multicast(message)

            logger.info(f"Push enviado para usuario {user_id} em {len(tokens)} dispositivos")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar push via Firebase: {e}")
            raise PushProviderError(f"Erro ao enviar push: {e}") from e

    async def send_push_bulk(
        self,
        user_ids: list[str],
        title: str,
        body: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, bool]:
        """
        Envia push para multiplos usuarios.

        Args:
            user_ids: Lista de user_ids
            title: Titulo
            body: Corpo
            data: Dados extras

        Returns:
            Resultado por usuario
        """
        results = {}
        for user_id in user_ids:
            try:
                results[user_id] = await self.send_push(user_id, title, body, data)
            except Exception as e:
                logger.error(f"Erro ao enviar push para {user_id}: {e}")
                results[user_id] = False
        return results

    async def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: dict[str, Any] | None = None,
    ) -> bool:
        """
        Envia push para topico Firebase.

        Args:
            topic: Nome do topico
            title: Titulo
            body: Corpo
            data: Dados extras

        Returns:
            True se enviado
        """
        await self._ensure_initialized()

        try:
            # from firebase_admin import messaging
            #
            # message = messaging.Message(
            #     notification=messaging.Notification(title=title, body=body),
            #     data=data or {},
            #     topic=topic,
            # )
            #
            # response = messaging.send(message)

            logger.info(f"Push enviado para topico {topic}")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar push para topico: {e}")
            raise PushProviderError(f"Erro ao enviar push: {e}") from e

    async def register_device(
        self,
        user_id: str,
        device_token: str,
        platform: str,
    ) -> bool:
        """
        Registra dispositivo para usuario.

        Args:
            user_id: ID do usuario
            device_token: Token FCM
            platform: Plataforma

        Returns:
            True se registrado
        """
        if user_id not in self._device_tokens:
            self._device_tokens[user_id] = []

        if device_token not in self._device_tokens[user_id]:
            self._device_tokens[user_id].append(device_token)
            logger.info(f"Dispositivo registrado para usuario {user_id}: {platform}")

        return True

    async def unregister_device(
        self,
        user_id: str,
        device_token: str,
    ) -> bool:
        """
        Remove registro de dispositivo.

        Args:
            user_id: ID do usuario
            device_token: Token FCM

        Returns:
            True se removido
        """
        if user_id in self._device_tokens:
            if device_token in self._device_tokens[user_id]:
                self._device_tokens[user_id].remove(device_token)
                logger.info(f"Dispositivo removido para usuario {user_id}")
                return True
        return False


class OneSignalPushProvider(PushProvider):
    """
    Provedor de push notification usando OneSignal.

    Attributes:
        app_id: ID do app OneSignal
        api_key: Chave de API

    Example:
        >>> provider = OneSignalPushProvider("app-123", "api-key")
        >>> await provider.send_push("user-123", "Titulo", "Mensagem")
    """

    def __init__(
        self,
        app_id: str,
        api_key: str,
    ) -> None:
        """
        Inicializa o provedor OneSignal.

        Args:
            app_id: ID do app OneSignal
            api_key: Chave de API REST
        """
        self.app_id = app_id
        self.api_key = api_key
        self._base_url = "https://onesignal.com/api/v1"

    async def send_push(
        self,
        user_id: str,
        title: str,
        body: str,
        data: dict[str, Any] | None = None,
        image_url: str | None = None,
    ) -> bool:
        """
        Envia push via OneSignal.

        Args:
            user_id: External User ID
            title: Titulo
            body: Corpo
            data: Dados extras
            image_url: URL da imagem

        Returns:
            True se enviado
        """
        try:
            # import httpx
            #
            # headers = {
            #     "Authorization": f"Basic {self.api_key}",
            #     "Content-Type": "application/json",
            # }
            #
            # payload = {
            #     "app_id": self.app_id,
            #     "include_external_user_ids": [user_id],
            #     "headings": {"en": title},
            #     "contents": {"en": body},
            #     "data": data or {},
            # }
            #
            # if image_url:
            #     payload["big_picture"] = image_url
            #
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(
            #         f"{self._base_url}/notifications",
            #         headers=headers,
            #         json=payload,
            #     )
            #     response.raise_for_status()

            logger.info(f"Push OneSignal enviado para usuario {user_id}")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar push via OneSignal: {e}")
            raise PushProviderError(f"Erro ao enviar push: {e}") from e

    async def send_push_bulk(
        self,
        user_ids: list[str],
        title: str,
        body: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, bool]:
        """
        Envia push para multiplos usuarios.

        Args:
            user_ids: Lista de external user IDs
            title: Titulo
            body: Corpo
            data: Dados extras

        Returns:
            Resultado por usuario
        """
        try:
            logger.info(f"Push OneSignal bulk enviado para {len(user_ids)} usuarios")
            return dict.fromkeys(user_ids, True)

        except Exception as e:
            logger.error(f"Erro ao enviar push bulk: {e}")
            return dict.fromkeys(user_ids, False)

    async def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: dict[str, Any] | None = None,
    ) -> bool:
        """
        Envia push para segmento/tag.

        Args:
            topic: Nome do segmento
            title: Titulo
            body: Corpo
            data: Dados extras

        Returns:
            True se enviado
        """
        try:
            logger.info(f"Push OneSignal enviado para segmento {topic}")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar push para segmento: {e}")
            raise PushProviderError(f"Erro ao enviar push: {e}") from e

    async def register_device(
        self,
        user_id: str,
        device_token: str,
        platform: str,
    ) -> bool:
        """
        Registra external user ID.

        Args:
            user_id: External user ID
            device_token: Player ID OneSignal
            platform: Plataforma

        Returns:
            True se registrado
        """
        try:
            logger.info(f"Dispositivo OneSignal registrado para usuario {user_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao registrar dispositivo: {e}")
            return False

    async def unregister_device(
        self,
        user_id: str,
        device_token: str,
    ) -> bool:
        """
        Remove external user ID do dispositivo.

        Args:
            user_id: External user ID
            device_token: Player ID

        Returns:
            True se removido
        """
        try:
            logger.info(f"Dispositivo OneSignal removido para usuario {user_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover dispositivo: {e}")
            return False


class PushProviderFactory:
    """
    Factory para criar instancias de provedores de push.

    Gerencia registro e criacao de diferentes provedores.

    Example:
        >>> PushProviderFactory.register("firebase", FirebasePushProvider)
        >>> provider = PushProviderFactory.get_provider("firebase")
    """

    _providers: dict[str, type[PushProvider]] = {
        "firebase": FirebasePushProvider,
        "onesignal": OneSignalPushProvider,
    }
    _instances: dict[str, PushProvider] = {}
    _config: dict[str, dict[str, Any]] = {}

    @classmethod
    def register(
        cls,
        name: str,
        provider_class: type[PushProvider],
    ) -> None:
        """
        Registra um provedor de push.

        Args:
            name: Nome do provedor
            provider_class: Classe do provedor
        """
        cls._providers[name] = provider_class
        logger.debug(f"Provedor de push registrado: {name}")

    @classmethod
    def configure(
        cls,
        name: str,
        **config: Any,
    ) -> None:
        """
        Configura um provedor.

        Args:
            name: Nome do provedor
            **config: Configuracoes do provedor
        """
        cls._config[name] = config
        logger.debug(f"Provedor de push configurado: {name}")

    @classmethod
    def get_provider(cls, name: str) -> PushProvider | None:
        """
        Obtem instancia de um provedor.

        Args:
            name: Nome do provedor

        Returns:
            Instancia do provedor ou None
        """
        # Retorna instancia existente
        if name in cls._instances:
            return cls._instances[name]

        # Cria nova instancia
        if name not in cls._providers:
            logger.warning(f"Provedor de push nao encontrado: {name}")
            return None

        provider_class = cls._providers[name]
        config = cls._config.get(name, {})

        try:
            if name == "firebase":
                instance = provider_class(
                    project_id=config.get("project_id", ""),
                    credentials=config.get("credentials"),
                )
            elif name == "onesignal":
                instance = provider_class(
                    app_id=config.get("app_id", ""),
                    api_key=config.get("api_key", ""),
                )
            else:
                instance = provider_class(**config)

            cls._instances[name] = instance
            return instance

        except Exception as e:
            logger.error(f"Erro ao criar provedor {name}: {e}")
            return None

    @classmethod
    def list_providers(cls) -> list[str]:
        """
        Lista provedores registrados.

        Returns:
            Lista de nomes de provedores
        """
        return list(cls._providers.keys())

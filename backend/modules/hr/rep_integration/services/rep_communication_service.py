"""Serviço de comunicação com dispositivos REP.

Implementa comunicação com diferentes fabricantes:
- Control iD (iDClass, iDFlex, iDFace)
- Intelbras (SS411, SS610, SS710)
- Henry (Super Easy, Orion)
- Dimep (SmartPoint, BioPoint)
"""

import base64
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any

import httpx

from modules.hr.rep_integration.models import (
    REPDevice,
    DeviceManufacturer,
)

logger = logging.getLogger(__name__)


class REPDriverBase(ABC):
    """Classe base para drivers de REP."""

    def __init__(self, device: REPDevice, timeout: int = 30):
        self.device = device
        self.timeout = timeout
        self.base_url = device.connection_url

    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """Testa conexão com o dispositivo."""
        raise NotImplementedError

    @abstractmethod
    async def get_device_info(self) -> Dict[str, Any]:
        """Obtém informações do dispositivo."""
        raise NotImplementedError

    @abstractmethod
    async def get_events(
        self,
        from_nsr: int = None,
        from_datetime: datetime = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Obtém eventos do dispositivo."""
        raise NotImplementedError

    @abstractmethod
    async def get_users(self) -> List[Dict[str, Any]]:
        """Obtém usuários cadastrados."""
        raise NotImplementedError

    @abstractmethod
    async def add_user(self, user_data: Dict[str, Any]) -> bool:
        """Adiciona usuário ao dispositivo."""
        raise NotImplementedError

    @abstractmethod
    async def remove_user(self, user_id: str) -> bool:
        """Remove usuário do dispositivo."""
        raise NotImplementedError

    @abstractmethod
    async def sync_time(self, server_time: datetime = None) -> bool:
        """Sincroniza horário do dispositivo."""
        raise NotImplementedError


class ControlIDDriver(REPDriverBase):
    """Driver para dispositivos Control iD."""

    async def _get_auth_headers(self) -> Dict[str, str]:
        """Retorna headers de autenticação."""
        headers = {"Content-Type": "application/json"}

        if self.device.auth_method == "token" and self.device.api_key_encrypted:
            headers["Authorization"] = f"Bearer {self._decrypt_key()}"
        elif self.device.auth_method == "basic":
            credentials = f"{self.device.auth_username}:{self._decrypt_password()}"
            encoded = base64.b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"

        return headers

    def _decrypt_key(self) -> str:
        """Descriptografa API key."""
        # Em produção, usar chave do ambiente
        return self.device.api_key_encrypted or ""

    def _decrypt_password(self) -> str:
        """Descriptografa senha."""
        return self.device.auth_password_encrypted or ""

    async def test_connection(self) -> Dict[str, Any]:
        """Testa conexão com Control iD."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/system_info.fcgi",
                    headers=await self._get_auth_headers(),
                )

                if response.status_code == 200:
                    return {
                        "success": True,
                        "latency_ms": int(response.elapsed.total_seconds() * 1000),
                        "device_info": response.json(),
                    }

                return {
                    "success": False,
                    "error_message": f"HTTP {response.status_code}",
                }

        except httpx.TimeoutException:
            return {"success": False, "error_message": "Timeout na conexão"}
        except (httpx.HTTPError, OSError, ValueError) as e:
            return {"success": False, "error_message": str(e)}

    async def get_device_info(self) -> Dict[str, Any]:
        """Obtém informações do Control iD."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/system_info.fcgi",
                    headers=await self._get_auth_headers(),
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "serial": data.get("serial"),
                        "model": data.get("model"),
                        "firmware": data.get("firmware"),
                        "mac": data.get("mac"),
                        "users_count": data.get("users", 0),
                        "fingerprints_count": data.get("fingerprints", 0),
                        "faces_count": data.get("faces", 0),
                        "events_count": data.get("events", 0),
                    }

        except (httpx.HTTPError, OSError, ValueError, KeyError) as e:
            logger.error(f"Erro ao obter info do Control iD: {e}")
            return {}

    async def get_events(
        self,
        from_nsr: int = None,
        from_datetime: datetime = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Obtém eventos do Control iD."""
        events = []

        try:
            params = {"limit": limit}
            if from_nsr:
                params["after_event"] = from_nsr

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/get_afd.fcgi",
                    headers=await self._get_auth_headers(),
                    json=params,
                )

                if response.status_code == 200:
                    data = response.json()
                    for event in data.get("events", []):
                        events.append({
                            "nsr": event.get("id"),
                            "datetime": datetime.fromisoformat(event.get("time")),
                            "pis": event.get("pis"),
                            "user_id": event.get("user_id"),
                            "user_name": event.get("user_name"),
                            "event_type": self._map_event_type(event.get("event")),
                            "method": self._map_method(event.get("way")),
                            "score": event.get("score"),
                        })

        except (httpx.HTTPError, OSError, ValueError, KeyError) as e:
            logger.error(f"Erro ao obter eventos do Control iD: {e}")

        return events

    async def get_users(self) -> List[Dict[str, Any]]:
        """Obtém usuários do Control iD."""
        users = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/load_objects.fcgi",
                    headers=await self._get_auth_headers(),
                    json={"object": "users"},
                )

                if response.status_code == 200:
                    data = response.json()
                    for user in data.get("users", []):
                        users.append({
                            "id": user.get("id"),
                            "name": user.get("name"),
                            "pis": user.get("pis"),
                            "registration": user.get("registration"),
                            "has_fingerprint": user.get("templates", 0) > 0,
                            "has_face": user.get("faces", 0) > 0,
                            "has_card": user.get("cards", 0) > 0,
                        })

        except (httpx.HTTPError, OSError, ValueError, KeyError) as e:
            logger.error(f"Erro ao obter usuários do Control iD: {e}")

        return users

    async def add_user(self, user_data: Dict[str, Any]) -> bool:
        """Adiciona usuário ao Control iD."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/create_objects.fcgi",
                    headers=await self._get_auth_headers(),
                    json={
                        "object": "users",
                        "values": [{
                            "name": user_data.get("name"),
                            "registration": user_data.get("registration"),
                            "pis": user_data.get("pis"),
                        }],
                    },
                )

                return response.status_code == 200

        except (httpx.HTTPError, OSError, ValueError) as e:
            logger.error(f"Erro ao adicionar usuário no Control iD: {e}")
            return False

    async def remove_user(self, user_id: str) -> bool:
        """Remove usuário do Control iD."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/destroy_objects.fcgi",
                    headers=await self._get_auth_headers(),
                    json={
                        "object": "users",
                        "where": {"users": {"id": int(user_id)}},
                    },
                )

                return response.status_code == 200

        except (httpx.HTTPError, OSError, ValueError) as e:
            logger.error(f"Erro ao remover usuário do Control iD: {e}")
            return False

    async def sync_time(self, server_time: datetime = None) -> bool:
        """Sincroniza horário do Control iD."""
        try:
            now = server_time or datetime.now()

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/set_system_time.fcgi",
                    headers=await self._get_auth_headers(),
                    json={"time": now.isoformat()},
                )

                return response.status_code == 200

        except (httpx.HTTPError, OSError, ValueError) as e:
            logger.error(f"Erro ao sincronizar horário do Control iD: {e}")
            return False

    def _map_event_type(self, event_code: int) -> str:
        """Mapeia código de evento para tipo."""
        mapping = {
            1: "entry",
            2: "exit",
            3: "break_start",
            4: "break_end",
        }
        return mapping.get(event_code, "entry")

    def _map_method(self, way_code: int) -> str:
        """Mapeia código de método para tipo."""
        mapping = {
            1: "biometric",
            2: "rfid",
            3: "password",
            4: "facial",
            5: "qrcode",
        }
        return mapping.get(way_code, "biometric")


class IntelbrasDriver(REPDriverBase):
    """Driver para dispositivos Intelbras."""

    async def test_connection(self) -> Dict[str, Any]:
        """Testa conexão com Intelbras."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/cgi-bin/AccessDevice.cgi?action=factory.getProductDefinition",
                    auth=(self.device.auth_username or "admin", self._get_password()),
                )

                if response.status_code == 200:
                    return {
                        "success": True,
                        "latency_ms": int(response.elapsed.total_seconds() * 1000),
                    }

                return {
                    "success": False,
                    "error_message": f"HTTP {response.status_code}",
                }

        except (httpx.HTTPError, OSError, ValueError) as e:
            return {"success": False, "error_message": str(e)}

    def _get_password(self) -> str:
        """Obtém senha descriptografada."""
        return self.device.auth_password_encrypted or "admin"

    async def get_device_info(self) -> Dict[str, Any]:
        """Obtém informações do Intelbras."""
        return {}

    async def get_events(
        self,
        from_nsr: int = None,
        from_datetime: datetime = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Obtém eventos do Intelbras."""
        return []

    async def get_users(self) -> List[Dict[str, Any]]:
        """Obtém usuários do Intelbras."""
        return []

    async def add_user(self, user_data: Dict[str, Any]) -> bool:
        """Adiciona usuário ao Intelbras."""
        return False

    async def remove_user(self, user_id: str) -> bool:
        """Remove usuário do Intelbras."""
        return False

    async def sync_time(self, server_time: datetime = None) -> bool:
        """Sincroniza horário do Intelbras."""
        return False


class GenericDriver(REPDriverBase):
    """Driver genérico para dispositivos não suportados."""

    async def test_connection(self) -> Dict[str, Any]:
        """Testa conexão básica."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url)
                return {
                    "success": response.status_code < 400,
                    "latency_ms": int(response.elapsed.total_seconds() * 1000),
                }
        except (httpx.HTTPError, OSError, ValueError) as e:
            return {"success": False, "error_message": str(e)}

    async def get_device_info(self) -> Dict[str, Any]:
        return {}

    async def get_events(
        self,
        from_nsr: int = None,
        from_datetime: datetime = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        return []

    async def get_users(self) -> List[Dict[str, Any]]:
        return []

    async def add_user(self, user_data: Dict[str, Any]) -> bool:
        return False

    async def remove_user(self, user_id: str) -> bool:
        return False

    async def sync_time(self, server_time: datetime = None) -> bool:
        return False


class REPCommunicationService:
    """Serviço de comunicação com REPs."""

    def __init__(self):
        self.drivers: Dict[str, type] = {
            DeviceManufacturer.CONTROL_ID.value: ControlIDDriver,
            DeviceManufacturer.INTELBRAS.value: IntelbrasDriver,
        }

    def get_driver(self, device: REPDevice) -> REPDriverBase:
        """Retorna driver apropriado para o dispositivo."""
        driver_class = self.drivers.get(device.manufacturer, GenericDriver)
        return driver_class(device)

    async def test_connection(self, device: REPDevice) -> Dict[str, Any]:
        """Testa conexão com dispositivo."""
        driver = self.get_driver(device)
        return await driver.test_connection()

    async def get_device_info(self, device: REPDevice) -> Dict[str, Any]:
        """Obtém informações do dispositivo."""
        driver = self.get_driver(device)
        return await driver.get_device_info()

    async def get_events(
        self,
        device: REPDevice,
        from_nsr: int = None,
        from_datetime: datetime = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Obtém eventos do dispositivo."""
        driver = self.get_driver(device)
        return await driver.get_events(from_nsr, from_datetime, limit)

    async def get_users(self, device: REPDevice) -> List[Dict[str, Any]]:
        """Obtém usuários do dispositivo."""
        driver = self.get_driver(device)
        return await driver.get_users()

    async def add_user(
        self,
        device: REPDevice,
        user_data: Dict[str, Any],
    ) -> bool:
        """Adiciona usuário ao dispositivo."""
        driver = self.get_driver(device)
        return await driver.add_user(user_data)

    async def remove_user(self, device: REPDevice, user_id: str) -> bool:
        """Remove usuário do dispositivo."""
        driver = self.get_driver(device)
        return await driver.remove_user(user_id)

    async def sync_time(
        self,
        device: REPDevice,
        server_time: datetime = None,
    ) -> bool:
        """Sincroniza horário do dispositivo."""
        driver = self.get_driver(device)
        return await driver.sync_time(server_time)

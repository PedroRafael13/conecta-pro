"""Service para preferências do funcionário."""

import logging
import secrets
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import pyotp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.employee_portal.models import EmployeePreferences

logger = logging.getLogger(__name__)


class PreferencesService:
    """Service para operações de preferências."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_preferences(self, employee_id: UUID) -> EmployeePreferences:
        """Obtém ou cria preferências do funcionário."""
        query = select(EmployeePreferences).where(EmployeePreferences.employee_id == employee_id)
        result = await self.db.execute(query)
        preferences = result.scalar_one_or_none()

        if not preferences:
            preferences = EmployeePreferences(employee_id=employee_id)
            self.db.add(preferences)
            await self.db.commit()
            await self.db.refresh(preferences)

        return preferences

    async def update_preferences(self, employee_id: UUID, data: Any) -> EmployeePreferences:
        """Atualiza preferências gerais."""
        preferences = await self.get_or_create_preferences(employee_id)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(preferences, key):
                setattr(preferences, key, value)

        await self.db.commit()
        await self.db.refresh(preferences)
        return preferences

    async def update_notification_settings(self, employee_id: UUID, data: Any) -> EmployeePreferences:
        """Atualiza configurações de notificações."""
        return await self.update_preferences(employee_id, data)

    async def update_privacy_settings(self, employee_id: UUID, data: Any) -> EmployeePreferences:
        """Atualiza configurações de privacidade."""
        return await self.update_preferences(employee_id, data)

    async def update_dashboard_widgets(self, employee_id: UUID, widgets: list[str]) -> EmployeePreferences:
        """Atualiza widgets do dashboard."""
        preferences = await self.get_or_create_preferences(employee_id)
        preferences.dashboard_widgets = widgets
        await self.db.commit()
        await self.db.refresh(preferences)
        return preferences

    async def setup_two_factor(self, employee_id: UUID) -> dict[str, Any]:
        """Configura autenticação em dois fatores."""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)

        preferences = await self.get_or_create_preferences(employee_id)
        preferences.two_factor_secret = secret
        await self.db.commit()

        return {
            "secret": secret,
            "qr_code_url": totp.provisioning_uri(name=str(employee_id), issuer_name="ERP Conecta Mais"),
        }

    async def verify_and_enable_two_factor(self, employee_id: UUID, code: str) -> bool:
        """Verifica código e ativa 2FA."""
        preferences = await self.get_or_create_preferences(employee_id)

        if not preferences.two_factor_secret:
            return False

        totp = pyotp.TOTP(preferences.two_factor_secret)
        if totp.verify(code):
            preferences.two_factor_enabled = True
            await self.db.commit()
            return True

        return False

    async def disable_two_factor(self, employee_id: UUID, code: str) -> bool:
        """Desativa 2FA."""
        preferences = await self.get_or_create_preferences(employee_id)

        if not preferences.two_factor_secret:
            return False

        totp = pyotp.TOTP(preferences.two_factor_secret)
        if totp.verify(code):
            preferences.two_factor_enabled = False
            preferences.two_factor_secret = None
            await self.db.commit()
            return True

        return False

    async def generate_backup_codes(self, employee_id: UUID) -> list[str]:
        """Gera códigos de backup para 2FA."""
        codes = [secrets.token_hex(4).upper() for _ in range(10)]

        preferences = await self.get_or_create_preferences(employee_id)
        preferences.two_factor_backup_codes = codes
        await self.db.commit()

        return codes

    async def list_trusted_devices(self, employee_id: UUID) -> list[dict[str, Any]]:
        """Lista dispositivos confiáveis."""
        preferences = await self.get_or_create_preferences(employee_id)
        return preferences.trusted_devices or []

    async def add_trusted_device(self, employee_id: UUID, device_info: Any) -> dict[str, Any]:
        """Adiciona dispositivo confiável."""
        preferences = await self.get_or_create_preferences(employee_id)

        device = {
            "id": secrets.token_hex(8),
            "name": device_info.name,
            "user_agent": device_info.user_agent,
            "ip_address": device_info.ip_address,
            "added_at": str(datetime.now(UTC)),
        }

        devices = preferences.trusted_devices or []
        devices.append(device)
        preferences.trusted_devices = devices

        await self.db.commit()
        return device

    async def remove_trusted_device(self, employee_id: UUID, device_id: str) -> bool:
        """Remove dispositivo confiável."""
        preferences = await self.get_or_create_preferences(employee_id)

        devices = preferences.trusted_devices or []
        original_len = len(devices)
        devices = [d for d in devices if d.get("id") != device_id]

        if len(devices) == original_len:
            return False

        preferences.trusted_devices = devices
        await self.db.commit()
        return True

    async def revoke_all_devices(self, employee_id: UUID) -> int:
        """Revoga todos os dispositivos."""
        preferences = await self.get_or_create_preferences(employee_id)
        count = len(preferences.trusted_devices or [])
        preferences.trusted_devices = []
        await self.db.commit()
        return count

    async def reset_to_defaults(self, employee_id: UUID) -> EmployeePreferences:
        """Restaura preferências para valores padrão."""
        preferences = await self.get_or_create_preferences(employee_id)

        # Reset to defaults
        preferences.theme = "system"
        preferences.language = "pt_BR"
        preferences.font_size = "medium"
        preferences.compact_mode = False
        preferences.animations_enabled = True
        preferences.notifications_enabled = True
        preferences.notification_sound = True

        await self.db.commit()
        await self.db.refresh(preferences)
        return preferences

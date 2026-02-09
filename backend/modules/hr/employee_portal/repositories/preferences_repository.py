"""Repository para preferências do funcionário."""

import logging
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.employee_portal.models import EmployeePreferences
from modules.hr.employee_portal.schemas import PreferencesCreate, PreferencesUpdate

logger = logging.getLogger(__name__)


class PreferencesRepository:
    """Repository para operações de preferências."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: PreferencesCreate,
        condominio_id: UUID,
    ) -> EmployeePreferences:
        """Cria preferências para funcionário."""
        preferences = EmployeePreferences(
            id=uuid4(),
            condominio_id=condominio_id,
            employee_id=data.employee_id,
            theme=data.theme.value,
            language=data.language.value,
            font_size=data.font_size,
            compact_mode=data.compact_mode,
            animations_enabled=data.animations_enabled,
            notifications_enabled=data.notifications_enabled,
            notification_sound=data.notification_sound,
            notification_badge=data.notification_badge,
            dashboard_layout=data.dashboard_layout,
            dashboard_widgets=data.dashboard_widgets,
            default_page=data.default_page,
        )

        self.db.add(preferences)
        await self.db.commit()
        await self.db.refresh(preferences)

        logger.info("Preferências criadas para funcionário %s", data.employee_id)
        return preferences

    async def get_by_id(self, preferences_id: UUID) -> EmployeePreferences | None:
        """Busca preferências por ID."""
        result = await self.db.execute(select(EmployeePreferences).where(EmployeePreferences.id == preferences_id))
        return result.scalar_one_or_none()

    async def get_by_employee(
        self,
        employee_id: UUID,
        condominio_id: UUID,
    ) -> EmployeePreferences | None:
        """Busca preferências do funcionário."""
        result = await self.db.execute(
            select(EmployeePreferences).where(
                EmployeePreferences.employee_id == employee_id,
                EmployeePreferences.condominio_id == condominio_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        employee_id: UUID,
        condominio_id: UUID,
    ) -> EmployeePreferences:
        """Busca ou cria preferências do funcionário."""
        preferences = await self.get_by_employee(employee_id, condominio_id)

        if not preferences:
            # pylint: disable=import-outside-toplevel
            from modules.hr.employee_portal.models import (
                LanguagePreference,
                ThemePreference,
            )

            preferences = EmployeePreferences(
                id=uuid4(),
                condominio_id=condominio_id,
                employee_id=employee_id,
                theme=ThemePreference.SYSTEM.value,
                language=LanguagePreference.PT_BR.value,
            )

            self.db.add(preferences)
            await self.db.commit()
            await self.db.refresh(preferences)

            logger.info(
                "Preferências padrão criadas para funcionário %s",
                employee_id,
            )

        return preferences

    async def update(
        self,
        employee_id: UUID,
        condominio_id: UUID,
        data: PreferencesUpdate,
    ) -> EmployeePreferences | None:
        """Atualiza preferências do funcionário."""
        preferences = await self.get_by_employee(employee_id, condominio_id)
        if not preferences:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            # Converter enums para valores string
            if hasattr(value, "value"):
                value = value.value
            setattr(preferences, field, value)

        preferences.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(preferences)

        logger.info("Preferências atualizadas para funcionário %s", employee_id)
        return preferences

    async def update_theme(
        self,
        employee_id: UUID,
        condominio_id: UUID,
        theme: str,
    ) -> EmployeePreferences | None:
        """Atualiza apenas o tema."""
        preferences = await self.get_by_employee(employee_id, condominio_id)
        if not preferences:
            return None

        preferences.theme = theme
        preferences.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(preferences)

        return preferences

    async def update_language(
        self,
        employee_id: UUID,
        condominio_id: UUID,
        language: str,
    ) -> EmployeePreferences | None:
        """Atualiza apenas o idioma."""
        preferences = await self.get_by_employee(employee_id, condominio_id)
        if not preferences:
            return None

        preferences.language = language
        preferences.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(preferences)

        return preferences

    async def update_dashboard_widgets(
        self,
        employee_id: UUID,
        condominio_id: UUID,
        widgets: list,
    ) -> EmployeePreferences | None:
        """Atualiza widgets do dashboard."""
        preferences = await self.get_by_employee(employee_id, condominio_id)
        if not preferences:
            return None

        preferences.dashboard_widgets = widgets
        preferences.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(preferences)

        return preferences

    async def add_trusted_device(
        self,
        employee_id: UUID,
        condominio_id: UUID,
        device: dict,
    ) -> EmployeePreferences | None:
        """Adiciona dispositivo confiável."""
        preferences = await self.get_by_employee(employee_id, condominio_id)
        if not preferences:
            return None

        trusted = preferences.trusted_devices or []

        # Verificar se já existe
        existing = next(
            (d for d in trusted if d.get("device_id") == device.get("device_id")),
            None,
        )

        if existing:
            # Atualizar último uso
            existing["last_used"] = datetime.utcnow().isoformat()
        else:
            # Adicionar novo
            device["last_used"] = datetime.utcnow().isoformat()
            trusted.append(device)

        preferences.trusted_devices = trusted
        preferences.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(preferences)

        return preferences

    async def remove_trusted_device(
        self,
        employee_id: UUID,
        condominio_id: UUID,
        device_id: str,
    ) -> EmployeePreferences | None:
        """Remove dispositivo confiável."""
        preferences = await self.get_by_employee(employee_id, condominio_id)
        if not preferences:
            return None

        trusted = preferences.trusted_devices or []
        preferences.trusted_devices = [d for d in trusted if d.get("device_id") != device_id]
        preferences.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(preferences)

        return preferences

    async def record_login(
        self,
        employee_id: UUID,
        condominio_id: UUID,
        *,
        ip_address: str | None = None,
        device_info: str | None = None,
    ) -> EmployeePreferences | None:
        """Registra login do funcionário."""
        preferences = await self.get_or_create(employee_id, condominio_id)

        preferences.last_login_at = datetime.utcnow()
        preferences.last_login_ip = ip_address
        preferences.last_login_device = device_info
        preferences.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(preferences)

        return preferences

    async def enable_two_factor(
        self,
        employee_id: UUID,
        condominio_id: UUID,
        method: str,
    ) -> EmployeePreferences | None:
        """Habilita autenticação de dois fatores."""
        preferences = await self.get_by_employee(employee_id, condominio_id)
        if not preferences:
            return None

        preferences.two_factor_enabled = True
        preferences.two_factor_method = method
        preferences.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(preferences)

        logger.info("2FA habilitado para funcionário %s", employee_id)
        return preferences

    async def disable_two_factor(
        self,
        employee_id: UUID,
        condominio_id: UUID,
    ) -> EmployeePreferences | None:
        """Desabilita autenticação de dois fatores."""
        preferences = await self.get_by_employee(employee_id, condominio_id)
        if not preferences:
            return None

        preferences.two_factor_enabled = False
        preferences.two_factor_method = None
        preferences.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(preferences)

        logger.info("2FA desabilitado para funcionário %s", employee_id)
        return preferences

    async def reset_to_defaults(
        self,
        employee_id: UUID,
        condominio_id: UUID,
    ) -> EmployeePreferences | None:
        """Reseta preferências para padrões."""
        preferences = await self.get_by_employee(employee_id, condominio_id)
        if not preferences:
            return None

        # pylint: disable=import-outside-toplevel
        from modules.hr.employee_portal.models import (
            LanguagePreference,
            ThemePreference,
        )

        # Resetar para valores padrão
        preferences.theme = ThemePreference.SYSTEM.value
        preferences.language = LanguagePreference.PT_BR.value
        preferences.font_size = "medium"
        preferences.compact_mode = False
        preferences.animations_enabled = True
        preferences.notifications_enabled = True
        preferences.notification_sound = True
        preferences.notification_badge = True
        preferences.dashboard_layout = "default"
        preferences.dashboard_widgets = []
        preferences.default_page = "dashboard"
        preferences.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(preferences)

        logger.info("Preferências resetadas para funcionário %s", employee_id)
        return preferences

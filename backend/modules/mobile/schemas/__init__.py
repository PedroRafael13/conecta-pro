"""Schemas do módulo mobile."""

from modules.mobile.schemas.batch_schemas import (
    BatchOperation,
    BatchRequest,
    BatchResponse,
)
from modules.mobile.schemas.device_schemas import (
    DeviceTokenCreate,
    DeviceTokenResponse,
    DeviceTokenUpdate,
)
from modules.mobile.schemas.mobile_schemas import (
    MobileConfigResponse,
    MobileDashboardResponse,
    OfflineDataResponse,
)
from modules.mobile.schemas.notification_schemas import (
    NotificationPreferences,
    PushNotificationCreate,
    PushNotificationResponse,
)
from modules.mobile.schemas.sync_schemas import (
    MobileSyncOperation,
    MobileSyncRequest,
    MobileSyncResponse,
    SyncConflict,
)

__all__ = [
    "MobileSyncOperation",
    "MobileSyncRequest",
    "MobileSyncResponse",
    "SyncConflict",
    "BatchOperation",
    "BatchRequest",
    "BatchResponse",
    "DeviceTokenCreate",
    "DeviceTokenResponse",
    "DeviceTokenUpdate",
    "PushNotificationCreate",
    "PushNotificationResponse",
    "NotificationPreferences",
    "MobileDashboardResponse",
    "OfflineDataResponse",
    "MobileConfigResponse",
]

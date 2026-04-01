"""Models do módulo de Integração REP."""

from .afd_record import (
    AFDRecord,
    AFDRecordType,
)
from .rep_device import (
    AuthMethod,
    CommunicationProtocol,
    DeviceManufacturer,
    DeviceModel,
    DeviceStatus,
    REPDevice,
)
from .rep_event import (
    EventStatus,
    EventType,
    IdentificationMethod,
    REPEvent,
)
from .rep_sync import (
    REPSync,
    SyncStatus,
    SyncTrigger,
    SyncType,
)

__all__ = [
    # REPDevice
    "REPDevice",
    "DeviceManufacturer",
    "DeviceModel",
    "DeviceStatus",
    "CommunicationProtocol",
    "AuthMethod",
    # REPEvent
    "REPEvent",
    "EventType",
    "IdentificationMethod",
    "EventStatus",
    # REPSync
    "REPSync",
    "SyncType",
    "SyncStatus",
    "SyncTrigger",
    # AFDRecord
    "AFDRecord",
    "AFDRecordType",
]

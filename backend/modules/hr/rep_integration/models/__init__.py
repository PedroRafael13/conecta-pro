"""Models do módulo de Integração REP."""

from .rep_device import (
    REPDevice,
    DeviceManufacturer,
    DeviceModel,
    DeviceStatus,
    CommunicationProtocol,
    AuthMethod,
)
from .rep_event import (
    REPEvent,
    EventType,
    IdentificationMethod,
    EventStatus,
)
from .rep_sync import (
    REPSync,
    SyncType,
    SyncStatus,
    SyncTrigger,
)
from .afd_record import (
    AFDRecord,
    AFDRecordType,
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

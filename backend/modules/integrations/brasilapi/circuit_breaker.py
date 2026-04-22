"""Minimal in-memory circuit breaker for BrasilAPI."""

import time
from dataclasses import dataclass


@dataclass
class _State:
    failures: int = 0
    opened_at: float = 0.0


class CircuitBreaker:
    """
    Opens after N failures within window_seconds.
    Stays open for cooldown_seconds.
    Per-endpoint tracking.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        window_seconds: int = 60,
        cooldown_seconds: int = 120,
    ):
        self._threshold = failure_threshold
        self._window = window_seconds
        self._cooldown = cooldown_seconds
        self._state: dict[str, _State] = {}

    def is_open(self, key: str) -> bool:
        s = self._state.get(key)
        if not s or s.opened_at == 0:
            return False
        if time.monotonic() - s.opened_at > self._cooldown:
            self._state.pop(key, None)
            return False
        return True

    def record_success(self, key: str) -> None:
        self._state.pop(key, None)

    def record_failure(self, key: str) -> None:
        s = self._state.setdefault(key, _State())
        s.failures += 1
        if s.failures >= self._threshold:
            s.opened_at = time.monotonic()


# Singleton
_cb = CircuitBreaker()

"""Minimal in-memory circuit breaker for BrasilAPI."""

import time
from dataclasses import dataclass, field


@dataclass
class _State:
    failure_times: list = field(default_factory=list)
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
        now = time.monotonic()
        # Trim failures outside the sliding window
        s.failure_times = [t for t in s.failure_times if now - t <= self._window]
        s.failure_times.append(now)
        if len(s.failure_times) >= self._threshold:
            s.opened_at = now


# Singleton
_cb = CircuitBreaker()

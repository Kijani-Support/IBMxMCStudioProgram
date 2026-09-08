"""Small, process-local login throttle for the prototype.

Production deployments should put distributed rate limiting at the reverse proxy or
identity-provider layer. This guard still prevents the demo login from being an open
brute-force endpoint.
"""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone


WINDOW = timedelta(minutes=15)
MAX_FAILURES = 5
_failures: dict[str, deque[datetime]] = defaultdict(deque)


def _key(email: str) -> str:
    return email.strip().casefold()


def is_blocked(email: str, now: datetime | None = None) -> bool:
    current = now or datetime.now(timezone.utc)
    attempts = _failures[_key(email)]
    while attempts and current - attempts[0] > WINDOW:
        attempts.popleft()
    return len(attempts) >= MAX_FAILURES


def record_failure(email: str, now: datetime | None = None) -> None:
    _failures[_key(email)].append(now or datetime.now(timezone.utc))


def clear_failures(email: str) -> None:
    _failures.pop(_key(email), None)

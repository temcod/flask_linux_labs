# Тесты для _freeze.py. Здесь проверяем задания практики 3 (unittest).

from __future__ import annotations

import datetime as _dt
from contextlib import contextmanager
from typing import Iterator

try:
 
    from freezegun import freeze_time as _freezegun_freeze_time  # type: ignore
except Exception:  
    _freezegun_freeze_time = None


@contextmanager
def freeze_time(date_str: str, patch_targets: list[str] | None = None) -> Iterator[None]:
    
    if _freezegun_freeze_time is not None:
        with _freezegun_freeze_time(date_str):
            yield
        return

    
    if not patch_targets:
        raise RuntimeError(
            "freezegun is not installed and no patch_targets provided.\n"
            "Install freezegun: pip install freezegun"
        )

    from unittest.mock import patch

    fixed = _dt.datetime.fromisoformat(date_str)

    class FrozenDateTime(_dt.datetime):
        @classmethod
        def today(cls):  # type: ignore[override]
            return fixed

        @classmethod
        def now(cls, tz=None):  # type: ignore[override]
            if tz is None:
                return fixed
            return tz.fromutc(fixed.replace(tzinfo=_dt.timezone.utc))

    patchers = [patch(target, FrozenDateTime) for target in patch_targets]
    for p in patchers:
        p.start()
    try:
        yield
    finally:
        for p in reversed(patchers):
            p.stop()

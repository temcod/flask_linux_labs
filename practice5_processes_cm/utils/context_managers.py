from __future__ import annotations

import sys
from typing import IO, Iterable, Optional, Type


class BlockErrors:
    """Контекстный менеджер, который «глушит» указанные исключения.

    Пример:
        with BlockErrors({ZeroDivisionError}):
            1 / 0    # не упадёт
    """

    def __init__(self, err_types: Iterable[Type[BaseException]]):
        # Превращаем в tuple, чтобы issubclass работал стабильно и быстро.
        self._err_types = tuple(err_types)

    def __enter__(self) -> "BlockErrors":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        # Если исключения не было — ничего подавлять не надо.
        if exc_type is None:
            return False

        # issubclass автоматически учитывает наследников:
        # Exception подавит и ValueError, и TypeError и т.д.
        return issubclass(exc_type, self._err_types)


class Redirect:
    """Контекстный менеджер для перенаправления stdout/stderr.

    Важно: сохраняем предыдущие sys.stdout/sys.stderr, чтобы вложенные блоки работали нормально.
    Аргументы непозиционные, поэтому можно перенаправить только stdout или только stderr.
    """

    def __init__(self, *, stdout: Optional[IO[str]] = None, stderr: Optional[IO[str]] = None):
        self._new_stdout = stdout
        self._new_stderr = stderr
        self._old_stdout: Optional[IO[str]] = None
        self._old_stderr: Optional[IO[str]] = None

    def __enter__(self) -> "Redirect":
        # Запоминаем текущие потоки.
        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr

        # Подменяем только то, что реально передали.
        if self._new_stdout is not None:
            sys.stdout = self._new_stdout  # type: ignore[assignment]
        if self._new_stderr is not None:
            sys.stderr = self._new_stderr  # type: ignore[assignment]

        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        # Возвращаем потоки на место (даже если внутри блока было исключение).
        if self._old_stdout is not None:
            sys.stdout = self._old_stdout  # type: ignore[assignment]
        if self._old_stderr is not None:
            sys.stderr = self._old_stderr  # type: ignore[assignment]

        # False означает исключение — пусть летит дальше.
        return False

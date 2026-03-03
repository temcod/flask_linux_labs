from __future__ import annotations

import os
import signal
import subprocess
import time
from typing import Iterable


class LsofNotAvailable(RuntimeError):
    # Выбрасываем, если на системе нет lsof (в Windows его обычно нет).
    pass


def _lsof_pids_listening(port: int) -> list[int]:
    """Возвращает список PID, которые слушают TCP-порт.

    Используем lsof в режиме:
      -t                  -> выводит только PID (удобно парсить)
      -iTCP:<port>        -> фильтр по порту
      -sTCP:LISTEN        -> только слушающие сокеты
    """
    try:
        result = subprocess.run(
            ["lsof", "-t", f"-iTCP:{port}", "-sTCP:LISTEN"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise LsofNotAvailable("lsof is not installed") from exc

    pids: list[int] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.isdigit():
            pids.append(int(line))

    # убираем дубликаты (иногда lsof может повторять строки).
    seen: set[int] = set()
    uniq: list[int] = []
    for pid in pids:
        if pid not in seen:
            seen.add(pid)
            uniq.append(pid)
    return uniq


def kill_processes_on_port(port: int, *, sigterm_wait_seconds: float = 1.5) -> list[int]:
    """Завершает процессы, которые слушают указанный порт.

    Сначала отправляем SIGTERM, ждём немного, и если порт всё ещё занят — добиваем SIGKILL.
    Возвращаем список PID, которым отправляли сигналы.
    """
    pids = _lsof_pids_listening(port)

    current_pid = os.getpid()
    pids = [pid for pid in pids if pid != current_pid]

    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            # Процесс уже умер — ок.
            continue

    # Дадим процессам времени корректно закрыться.
    deadline = time.time() + sigterm_wait_seconds
    while time.time() < deadline:
        if not _lsof_pids_listening(port):
            return pids
        time.sleep(0.1)

    # Если порт всё ещё занят — добиваем.
    for pid in _lsof_pids_listening(port):
        if pid == current_pid:
            continue
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            continue

    return pids


def ensure_port_free(port: int) -> None:
    # Если порт занят — освобождаем.
    if _lsof_pids_listening(port):
        kill_processes_on_port(port)


def run_server_on_port(port: int, server_argv: Iterable[str]) -> subprocess.Popen:
    """Запускает сервер на порту.

    Если порт уже занят, сначала освобождаем его, потом запускаем сервер.
    """
    ensure_port_free(port)
    process = subprocess.Popen(list(server_argv))
    return process

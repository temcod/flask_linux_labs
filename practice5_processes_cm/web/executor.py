from __future__ import annotations

import dataclasses
import resource
import shutil
import subprocess
from typing import Optional


@dataclasses.dataclass(frozen=True)
class ExecutionResult:
    # Что получилось после запуска python-кода
    stdout: str
    stderr: str
    returncode: Optional[int]
    timed_out: bool


def _limit_resources(timeout_seconds: int) -> None:
    """Ограничиваем ресурсы дочернего процесса.

    Это не "идеальная песочница", но для учебного задания нормально:
    - CPU ограничиваем примерно временем таймаута
    - память ограничиваем сверху
    - количество процессов (nproc) стараемся прижать до 1
    """
    try:
        # RLIMIT_CPU — лимит по CPU-секундам (не "реальное" время).
        cpu_limit = max(1, int(timeout_seconds) + 1)
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
    except Exception:
        # На некоторых системах/в контейнерах это может быть запрещено.
        pass

    try:
        # RLIMIT_AS — лимит на адресное пространство (условно "память").
        mem_limit = 256 * 1024 * 1024  # 256 MiB
        resource.setrlimit(resource.RLIMIT_AS, (mem_limit, mem_limit))
    except Exception:
        pass

    try:
        # Ограничим число процессов: чтобы внутри кода нельзя было наспавнить кучу детей.
        resource.setrlimit(resource.RLIMIT_NPROC, (1, 1))
    except Exception:
        pass


def _build_command(code: str) -> list[str]:
    # Собираем команду запуска.
    # нельзя shell=True, иначе можно легко "вырваться" через кавычки.
    base_cmd = ["python3", "-c", code]

    # Если на системе есть prlimit — добавим ещё один уровень защиты.
    #  полезно ограничение --nproc (чтобы не запускали сторонние процессы).
    if shutil.which("prlimit"):
        return ["prlimit", "--nproc=1:1"] + base_cmd

    return base_cmd

def _sanitize_python_stderr(stderr: str) -> str:
    """Чистим stderr, чтобы в ответе не светить исходный код пользователя.

    У Python-трейсбеков часто есть строки, где показывается проблемная строка кода:
        File "<string>", line 1
          <тут сам код>
          ^

    Для задания (и для безопасности) удобнее эти 2 строки убрать, оставив саму ошибку.
    """
    if not stderr:
        return stderr

    lines = stderr.splitlines()
    cleaned: list[str] = []
    skip = 0

    for line in lines:
        if skip > 0:
            skip -= 1
            continue

        # Убираем строку с кодом и каретку после кадра "<string>" / "<stdin>".
        if 'File "<string>"' in line or 'File "<stdin>"' in line:
            cleaned.append(line)
            skip = 2
            continue

        cleaned.append(line)

    # Сохраняем завершающий \n, если он был (чтобы вывод выглядел привычно).
    tail_newline = "\n" if stderr.endswith("\n") else ""
    return "\n".join(cleaned) + tail_newline



def execute_python_code(code: str, timeout_seconds: int) -> ExecutionResult:
    """Запускаем код и возвращаем stdout/stderr.

    Схема такая:
      - стартуем процесс `python3 -c "<code>"`
      - ждём timeout_seconds
      - если не успел — убиваем и возвращаем timed_out=True
    """
    cmd = _build_command(code)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        # preexec_fn работает на Unix: вызывается в дочернем процессе перед exec().
        preexec_fn=lambda: _limit_resources(timeout_seconds),
    )

    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
        # В stderr Python иногда печатает исходный код. Убираем его из ответа.
        stderr = _sanitize_python_stderr(stderr)
        return ExecutionResult(
            stdout=stdout,
            stderr=stderr,
            returncode=process.returncode,
            timed_out=False,
        )
    except subprocess.TimeoutExpired:
        # Если по времени не уложились — гасим процесс.
        process.kill()
        stdout, stderr = process.communicate()
        # На таймауте тоже чистим stderr, чтобы не отдавать куски кода обратно.
        stderr = _sanitize_python_stderr(stderr)
        return ExecutionResult(
            stdout=stdout,
            stderr=stderr,
            returncode=None,
            timed_out=True,
        )

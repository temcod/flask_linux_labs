from __future__ import annotations

import argparse
import sys

from utils.port_tools import run_server_on_port


def main() -> int:
    #  утилита: запускаем Flask-сервер на нужном порту.
    # Если порт занят — сначала освобождаем (через lsof), потом стартуем.
    parser = argparse.ArgumentParser(description="Free port if needed and run Flask server on it.")
    parser.add_argument("port", type=int, help="Port to run the server on")
    args = parser.parse_args()

    # Запускаем `python web/app.py --port <PORT>`.
    server_argv = [sys.executable, "web/app.py", "--port", str(args.port)]
    run_server_on_port(args.port, server_argv)

    print(f"Server started on port {args.port}")
    print("Stop it with Ctrl+C in this terminal.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

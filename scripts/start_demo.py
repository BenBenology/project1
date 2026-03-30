"""Start the FastAPI backend and Streamlit frontend together for local demo use."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_env_file(env_path: Path) -> None:
    """Load a minimal .env file without adding new runtime dependencies."""
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def is_port_available(host: str, port: int) -> bool:
    """Check whether a TCP port is available on the given host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.connect_ex((host, port)) != 0


def find_available_port(host: str, preferred_port: int, max_tries: int = 20) -> int:
    """Return the first available port starting from the preferred port."""
    for port in range(preferred_port, preferred_port + max_tries):
        if is_port_available(host, port):
            return port
    raise RuntimeError(
        f"Could not find an available port near {preferred_port} on {host}."
    )


def start_process(
    command: list[str], name: str, env: dict[str, str] | None = None
) -> subprocess.Popen:
    """Launch one child process and keep stdio attached for easy debugging."""
    print(f"[start_demo] starting {name}: {' '.join(command)}")
    return subprocess.Popen(command, cwd=PROJECT_ROOT, env=env)


def terminate_process(process: subprocess.Popen, name: str) -> None:
    """Stop a child process gracefully, then force kill if needed."""
    if process.poll() is not None:
        return

    print(f"[start_demo] stopping {name}...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def main() -> int:
    """Start backend and frontend, then keep the parent process alive."""
    load_env_file(PROJECT_ROOT / ".env")

    api_host = os.getenv("API_HOST", "127.0.0.1")
    requested_api_port = int(os.getenv("API_PORT", "8000"))
    requested_streamlit_port = int(os.getenv("STREAMLIT_PORT", "8501"))

    api_port = find_available_port(api_host, requested_api_port)
    streamlit_port = find_available_port("127.0.0.1", requested_streamlit_port)

    if api_port != requested_api_port:
        print(
            f"[start_demo] port {requested_api_port} is busy, backend will use {api_port}"
        )
    if streamlit_port != requested_streamlit_port:
        print(
            f"[start_demo] port {requested_streamlit_port} is busy, frontend will use {streamlit_port}"
        )

    child_env = os.environ.copy()
    child_env["STREAMLIT_API_BASE_URL"] = f"http://{api_host}:{api_port}"

    backend_command = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.app.main:app",
        "--reload",
        "--host",
        api_host,
        "--port",
        str(api_port),
    ]
    frontend_command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "frontend/streamlit_app.py",
        "--server.port",
        str(streamlit_port),
    ]

    backend = start_process(backend_command, "backend", env=child_env)
    time.sleep(1)
    frontend = start_process(frontend_command, "frontend", env=child_env)

    print("")
    print("[start_demo] demo is starting")
    print(f"[start_demo] backend docs: http://{api_host}:{api_port}/docs")
    print(f"[start_demo] frontend:     http://127.0.0.1:{streamlit_port}")
    print("[start_demo] press Ctrl+C to stop both services")

    try:
        while True:
            if backend.poll() is not None:
                print("[start_demo] backend exited unexpectedly")
                return backend.returncode or 1
            if frontend.poll() is not None:
                print("[start_demo] frontend exited unexpectedly")
                return frontend.returncode or 1
            time.sleep(1)
    except KeyboardInterrupt:
        print("")
        print("[start_demo] shutdown requested")
        return 0
    finally:
        terminate_process(frontend, "frontend")
        terminate_process(backend, "backend")


if __name__ == "__main__":
    raise SystemExit(main())

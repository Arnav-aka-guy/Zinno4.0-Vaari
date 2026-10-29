#!/usr/bin/env python3
"""Cross-platform task runner for Vaari (Phase 1, 2, 3). Standard library only."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()


def get_venv_python() -> Path:
    """Return path to virtualenv python executable if .venv exists, else sys.executable."""
    if os.name == "nt":
        venv_py = ROOT / ".venv" / "Scripts" / "python.exe"
    else:
        venv_py = ROOT / ".venv" / "bin" / "python"
    if venv_py.exists():
        return venv_py
    return Path(sys.executable)


def run_cmd(cmd: list[str], env: dict | None = None, cwd: Path = ROOT) -> int:
    """Run a subprocess command and return exit code."""
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    res = subprocess.run(cmd, cwd=cwd, env=merged_env)
    return res.returncode


def task_setup() -> int:
    """Create .venv if missing, install requirements.txt, web dependencies and playwright."""
    venv_dir = ROOT / ".venv"
    if not venv_dir.exists():
        print("Creating .venv...")
        import venv
        venv.create(venv_dir, with_pip=True)

    py = get_venv_python()
    print("Installing requirements.txt...")
    ret = run_cmd([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    if ret != 0:
        return ret
    ret = run_cmd([str(py), "-m", "pip", "install", "-r", "requirements.txt"])
    if ret != 0:
        return ret
    dev_req = ROOT / "requirements-dev.txt"
    if dev_req.exists():
        print("Installing requirements-dev.txt...")
        ret = run_cmd([str(py), "-m", "pip", "install", "-r", str(dev_req)])
        if ret != 0:
            return ret

    web_dir = ROOT / "web"
    if web_dir.exists() and (web_dir / "package.json").exists():
        print("Running npm install in web/...")
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        ret = run_cmd([npm_cmd, "install"], cwd=web_dir)
        if ret != 0:
            return ret
        print("Installing Playwright chromium...")
        npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
        run_cmd([npx_cmd, "playwright", "install", "chromium"], cwd=web_dir)
        print("Building web assets...")
        task_build_web()
    return 0


def task_build_web() -> int:
    """Run npm run build in web/."""
    web_dir = ROOT / "web"
    if not web_dir.exists():
        print("web/ directory does not exist")
        return 1
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    return run_cmd([npm_cmd, "run", "build"], cwd=web_dir)


def task_dev() -> int:
    """Run uvicorn with reload on 127.0.0.1:8000 and start Vite dev server."""
    py = get_venv_python()
    web_dir = ROOT / "web"
    if web_dir.exists() and (web_dir / "package.json").exists():
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        procs = []
        try:
            p_api = subprocess.Popen(
                [
                    str(py),
                    "-m",
                    "uvicorn",
                    "app.main:app",
                    "--reload",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8000",
                ],
                cwd=ROOT,
            )
            procs.append(p_api)
            p_web = subprocess.Popen(
                [npm_cmd, "run", "dev"],
                cwd=web_dir,
            )
            procs.append(p_web)
            for p in procs:
                p.wait()
        except KeyboardInterrupt:
            for p in procs:
                p.terminate()
        return 0
    return run_cmd(
        [str(py), "-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"]
    )


def task_test(args: list[str]) -> int:
    """Run pytest -q (unit and API tests)."""
    py = get_venv_python()
    cmd = [str(py), "-m", "pytest", "-q"] + args
    return run_cmd(cmd)


def get_lan_ip() -> str:
    """Detect the local machine's primary LAN IP."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


def get_driver_urls(base_url: str) -> list[tuple[str, str]]:
    """Retrieve machine names and driver URLs from the database."""
    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from app.db import get_db
        from app.models import Machine
        with next(get_db()) as session:
            machines = (
                session.query(Machine)
                .filter(Machine.link_token.isnot(None))
                .order_by(Machine.id)
                .all()
            )
            return [(m.name, f"{base_url}/driver/{m.link_token}") for m in machines]
    except Exception:
        return []


def task_serve() -> int:
    """Build web assets and run uvicorn on 0.0.0.0:8000 serving API and frontend together."""
    task_build_web()

    lan_ip = get_lan_ip()
    local_url = "http://localhost:8000"
    lan_url = f"http://{lan_ip}:8000"

    print("\n" + "=" * 70, flush=True)
    print("  Vaari Operations Server (Serve Mode)", flush=True)
    print("=" * 70, flush=True)
    print(f"  Local URL:  {local_url}", flush=True)
    print(f"  LAN URL:    {lan_url}", flush=True)
    print("\n  Driver URLs (open on phone over LAN or HTTPS tunnel):", flush=True)

    driver_urls = get_driver_urls(lan_url)
    if driver_urls:
        for name, url in driver_urls:
            print(f"    - {name:<22}: {url}", flush=True)
    else:
        print("    (No machines found or database not initialized)", flush=True)
    print("=" * 70 + "\n", flush=True)
    sys.stdout.flush()

    py = get_venv_python()
    return run_cmd([str(py), "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"])


def find_cloudflared() -> Path | None:
    """Find cloudflared executable in PATH, virtualenv, or standard directories."""
    import shutil
    cmd = shutil.which("cloudflared")
    if cmd:
        return Path(cmd)

    venv_cf = (
        ROOT
        / ".venv"
        / ("Scripts" if os.name == "nt" else "bin")
        / ("cloudflared.exe" if os.name == "nt" else "cloudflared")
    )
    if venv_cf.exists():
        return venv_cf

    if os.name == "nt":
        for pf in [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
        ]:
            candidate = Path(pf) / "cloudflared" / "cloudflared.exe"
            if candidate.exists():
                return candidate
    return None


def task_tunnel() -> int:
    """Run cloudflared tunnel to expose port 8000 over HTTPS, or print installation steps."""
    cf = find_cloudflared()
    if not cf:
        print("\n" + "=" * 70)
        print("  cloudflared is not installed")
        print("=" * 70)
        print("To install cloudflared:")
        print("  Windows: winget install --id Cloudflare.cloudflared")
        print("  macOS:   brew install cloudflared")
        print("  Linux:   curl -L --output cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64")
        print("=" * 70 + "\n")
        return 1

    print(f"Starting Cloudflare Quick Tunnel using: {cf}")
    import re
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    proc = subprocess.Popen(
        [str(cf), "tunnel", "--url", "http://localhost:8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    url_found = False
    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            if not url_found:
                match = url_pattern.search(line)
                if match:
                    url = match.group(0)
                    url_found = True
                    print("\n" + "=" * 70)
                    print("  Cloudflare Quick Tunnel Connected!")
                    print(f"  Public HTTPS URL: {url}")
                    print("=" * 70 + "\n")
        return proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        return 0


def task_seed() -> int:
    """Load seed data into an existing database."""
    py = get_venv_python()
    return run_cmd([str(py), "-m", "app.seed.seed"])


def task_reset() -> int:
    """Delete database, photos, register pages, create tables, seed, run scheduler."""
    py = get_venv_python()
    return run_cmd([str(py), "-m", "app.seed.seed", "--reset"])


def task_smoke() -> int:
    """Run the smoke test."""
    py = get_venv_python()
    return run_cmd([str(py), "-m", "pytest", "-q", "tests/api/test_smoke.py"])


def task_reader_eval() -> int:
    """Run the configured reader on examples/register_pages/ and print counts."""
    py = get_venv_python()
    return run_cmd([str(py), "-m", "app.intake.eval"])


def task_purge_images(args: list[str]) -> int:
    """Delete register page images past image_delete_after."""
    dry_run = "--dry-run" in args
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from app.db import Base, get_engine, get_session_factory
    from app.routes.intake import purge_expired_register_images

    Base.metadata.create_all(bind=get_engine())
    sf = get_session_factory()
    with sf() as session:
        deleted = purge_expired_register_images(session, dry_run=dry_run)
    prefix = "[DRY RUN] Would delete" if dry_run else "Deleted"
    if deleted:
        for p in deleted:
            print(f"{prefix}: {p}")
    else:
        print(f"{prefix}: 0 expired register images.")
    return 0


def task_e2e(args: list[str]) -> int:
    """Run Playwright end-to-end tests against a freshly reset temporary database in serve mode."""
    import socket
    import tempfile
    import time
    import urllib.request

    print("Building web application for serve mode...")
    task_build_web()

    fixtures_dir = ROOT / "tests" / "fixtures"
    start_fix = fixtures_dir / "start_field.jpg"
    done_fix = fixtures_dir / "done_field.jpg"
    reg_fix = fixtures_dir / "register_page.jpg"
    if not start_fix.exists() or not done_fix.exists() or not reg_fix.exists():
        from tests.fixtures.synthetic_photos import TINY_JPEG
        start_jpg = TINY_JPEG[:20] + b"\xff\xfe\x00\x07START" + TINY_JPEG[20:]
        done_jpg = TINY_JPEG[:20] + b"\xff\xfe\x00\x06DONE" + TINY_JPEG[20:]
        reg_jpg = TINY_JPEG[:20] + b"\xff\xfe\x00\x08REGISTER" + TINY_JPEG[20:]
        start_fix.write_bytes(start_jpg)
        done_fix.write_bytes(done_jpg)
        reg_fix.write_bytes(reg_jpg)

    port = 8000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
        except OSError:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
                s2.bind(("127.0.0.1", 0))
                port = s2.getsockname()[1]

    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name)
    db_path = temp_path / "vaari_e2e.sqlite"
    data_dir = temp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["VAARI_DB_PATH"] = str(db_path)
    env["VAARI_DATA_DIR"] = str(data_dir)
    env["VAARI_DEMO_PASSCODE"] = "change-me"
    env["VAARI_PUBLIC_BASE_URL"] = f"http://127.0.0.1:{port}"
    env["VAARI_READER"] = "mock"

    py = get_venv_python()
    print(f"Initializing temporary database at {db_path}...")
    reset_ret = run_cmd([str(py), "-m", "app.seed.seed", "--reset"], env=env)
    if reset_ret != 0:
        print("Failed to initialize temporary database.")
        temp_dir.cleanup()
        return reset_ret

    print(f"Starting test server on http://127.0.0.1:{port}...")
    server_proc = subprocess.Popen(
        [str(py), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    health_url = f"http://127.0.0.1:{port}/api/health"
    ready = False
    t0 = time.time()
    while time.time() - t0 < 20:
        try:
            with urllib.request.urlopen(health_url, timeout=1) as resp:
                if resp.status == 200:
                    ready = True
                    break
        except Exception:
            time.sleep(0.2)

    if not ready:
        print("Test server failed to start within 20s.")
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(server_proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            server_proc.terminate()
        temp_dir.cleanup()
        return 1

    print("Server ready! Running Playwright tests...")
    playwright_env = env.copy()
    playwright_env["BASE_URL"] = f"http://127.0.0.1:{port}"
    npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
    web_dir = ROOT / "web"
    cmd = [npx_cmd, "playwright", "test"] + args
    exit_code = run_cmd(cmd, env=playwright_env, cwd=web_dir)

    print("Stopping test server...")
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(server_proc.pid)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()

    temp_dir.cleanup()
    return exit_code


def main():
    if len(sys.argv) < 2:
        print("Usage: python tasks.py <task> [args]")
        print(
            "Available tasks: setup, dev, test, seed, reset, smoke, serve, tunnel, "
            "build-web, e2e, reader-eval, purge-images"
        )
        sys.exit(1)

    task = sys.argv[1]
    extra_args = sys.argv[2:]

    if task == "setup":
        sys.exit(task_setup())
    elif task == "dev":
        sys.exit(task_dev())
    elif task == "test":
        sys.exit(task_test(extra_args))
    elif task == "serve":
        sys.exit(task_serve())
    elif task == "seed":
        sys.exit(task_seed())
    elif task == "reset":
        sys.exit(task_reset())
    elif task == "smoke":
        sys.exit(task_smoke())
    elif task == "build-web":
        sys.exit(task_build_web())
    elif task == "tunnel":
        sys.exit(task_tunnel())
    elif task == "e2e":
        sys.exit(task_e2e(extra_args))
    elif task == "reader-eval":
        sys.exit(task_reader_eval())
    elif task == "purge-images":
        sys.exit(task_purge_images(extra_args))
    else:
        print(f"Unknown task: {task}")
        sys.exit(1)


if __name__ == "__main__":
    main()

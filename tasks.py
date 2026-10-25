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
    """Create .venv if missing, install requirements.txt."""
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
    
    web_dir = ROOT / "web"
    if web_dir.exists() and (web_dir / "package.json").exists():
        print("Running npm install in web/...")
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        run_cmd([npm_cmd, "install"], cwd=web_dir)
    return 0


def task_dev() -> int:
    """Run uvicorn with reload on 127.0.0.1:8000."""
    py = get_venv_python()
    return run_cmd([str(py), "-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"])


def task_test(args: list[str]) -> int:
    """Run pytest -q (unit and API tests)."""
    py = get_venv_python()
    cmd = [str(py), "-m", "pytest", "-q"] + args
    return run_cmd(cmd)


def task_serve() -> int:
    """Run uvicorn on 0.0.0.0:8000 serving the API and built frontend."""
    py = get_venv_python()
    return run_cmd([str(py), "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"])


def task_seed() -> int:
    """Load seed data into an existing database."""
    py = get_venv_python()
    seed_file = ROOT / "app" / "seed" / "seed.py"
    if not seed_file.exists():
        print("not built yet")
        return 0
    return run_cmd([str(py), "-m", "app.seed.seed"])


def task_reset() -> int:
    """Delete database, photos, register pages, create tables, seed, run scheduler."""
    py = get_venv_python()
    seed_file = ROOT / "app" / "seed" / "seed.py"
    if not seed_file.exists():
        print("not built yet")
        return 0
    return run_cmd([str(py), "-m", "app.seed.seed", "--reset"])


def task_smoke() -> int:
    """Run the smoke test."""
    py = get_venv_python()
    smoke_file = ROOT / "tests" / "api" / "test_smoke.py"
    if not smoke_file.exists():
        print("not built yet")
        return 0
    return run_cmd([str(py), "-m", "pytest", "-q", "tests/api/test_smoke.py"])


def main():
    if len(sys.argv) < 2:
        print("Usage: python tasks.py <task> [args]")
        print("Available tasks: setup, dev, test, seed, reset, smoke, serve")
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
    elif task in ("build-web", "e2e", "tunnel", "reader-eval", "purge-images"):
        print("not built yet")
        sys.exit(0)
    else:
        print(f"Unknown task: {task}")
        sys.exit(1)


if __name__ == "__main__":
    main()

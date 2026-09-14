"""Caminhos canonicos do repositorio SNAP ENG."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Raiz do projeto (pasta que contem backend/ e engineering_templates/)."""
    return Path(__file__).resolve().parents[3]


def default_sqlite_path() -> Path:
    return repo_root() / "snapeng.db"


def resolve_sqlite_database_url(database_url: str) -> str:
    """
    Normaliza SQLite relativo para sempre apontar ao snapeng.db da raiz do repo.

    Evita dois bancos (cwd=raiz vs cwd=backend) com catalogs diferentes.
    URLs absolutas e Postgres nao sao alteradas.
    """
    raw = (database_url or "").strip()
    if not raw.lower().startswith("sqlite:"):
        return raw

    # sqlite:///./snapeng.db  | sqlite:///snapeng.db | sqlite:////abs/path
    prefix = "sqlite:///"
    if not raw.lower().startswith(prefix):
        return raw

    path_part = raw[len(prefix) :]
    # Absolute: sqlite:////C:/... (windows) or sqlite:////var/...
    if path_part.startswith("/") or (len(path_part) > 1 and path_part[1] == ":"):
        return raw

    # Relative paths always resolve to repo-root snapeng.db (canonical).
    # If the filename is something else (e.g. ci_snapeng.db), keep the name under repo root.
    name = Path(path_part).name or "snapeng.db"
    if name in {".", ""}:
        name = "snapeng.db"
    if path_part in {"./snapeng.db", "snapeng.db", ".\\snapeng.db"}:
        absolute = default_sqlite_path()
    else:
        absolute = repo_root() / name

    # SQLAlchemy on Windows wants sqlite:///C:/path (three slashes + drive)
    as_posix = absolute.resolve().as_posix()
    if absolute.drive:
        return f"sqlite:///{as_posix}"
    return f"sqlite:////{as_posix}"

"""Testes do caminho canonico do SQLite."""

from pathlib import Path

from app.core.paths import default_sqlite_path, repo_root, resolve_sqlite_database_url


def test_repo_root_contains_backend_and_templates():
    root = repo_root()
    assert (root / "backend").is_dir()
    assert (root / "engineering_templates").is_dir()


def test_relative_sqlite_always_points_to_repo_root():
    resolved = resolve_sqlite_database_url("sqlite:///./snapeng.db")
    expected = default_sqlite_path().resolve().as_posix()
    assert resolved.endswith(expected) or expected in resolved
    assert "sqlite:///" in resolved

    from_backend_cwd_style = resolve_sqlite_database_url("sqlite:///snapeng.db")
    assert resolve_sqlite_database_url("sqlite:///./snapeng.db") == from_backend_cwd_style


def test_postgres_url_untouched():
    url = "postgresql://user:pass@localhost:5432/snapeng"
    assert resolve_sqlite_database_url(url) == url


def test_ci_sqlite_name_stays_under_repo_root():
    resolved = resolve_sqlite_database_url("sqlite:///./ci_snapeng.db")
    assert (repo_root() / "ci_snapeng.db").as_posix() in resolved.replace("\\", "/")

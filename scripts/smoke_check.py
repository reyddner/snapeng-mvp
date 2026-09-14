"""Smoke check operacional do SNAPENG (sem Docker).

Uso (na raiz do projeto):
  .\\.venv\\Scripts\\python.exe scripts\\smoke_check.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient

from app.main import app


def main() -> int:
    client = TestClient(app)
    checks = []

    health = client.get("/health")
    checks.append(("GET /health", health.status_code == 200, health.json()))

    landing = client.get("/")
    checks.append(("GET /", landing.status_code == 200, None))

    memorials = client.get("/memorials/new")
    checks.append(("GET /memorials/new", memorials.status_code == 200, None))

    exemplos = client.get("/exemplos")
    checks.append(("GET /exemplos", exemplos.status_code == 200, None))

    demos = client.get("/api/v1/demos")
    demos_ok = demos.status_code == 200 and len((demos.json() or {}).get("demos") or []) >= 2
    checks.append(
        (
            "GET /api/v1/demos",
            demos_ok,
            {"count": len((demos.json() or {}).get("demos") or [])} if demos.status_code == 200 else demos.status_code,
        )
    )

    dashboard = client.get("/dashboard", follow_redirects=False)
    checks.append(
        ("GET /dashboard anonimo", dashboard.status_code == 302, dashboard.headers.get("location"))
    )

    csp = client.get("/health").headers.get("Content-Security-Policy", "")
    checks.append(("CSP presente", "default-src 'self'" in csp, csp[:80]))

    alpine = client.get("/static/js/alpine.min.js")
    checks.append(("Alpine local", alpine.status_code == 200, f"{len(alpine.content)} bytes"))

    templates = client.get("/api/v1/templates/")
    body = templates.json() if templates.status_code == 200 else []
    sensitive = [
        "protocolo",
        "proposta",
        "assinado",
        "questões",
        "gerado automaticamente",
    ]
    dirty = [
        item.get("name", "")
        for item in body
        if any(marker in (item.get("name") or "").casefold() for marker in sensitive)
        or "gerado automaticamente" in (item.get("description") or "").casefold()
    ]
    checks.append(
        (
            "GET /api/v1/templates limpo",
            templates.status_code == 200 and len(body) > 0 and not dirty,
            {"count": len(body), "dirty": dirty},
        )
    )

    failed = [item for item in checks if not item[1]]
    for name, ok, detail in checks:
        mark = "OK" if ok else "FAIL"
        print(f"[{mark}] {name}" + (f" -> {detail}" if detail is not None else ""))

    if failed:
        print(f"\nSmoke check falhou: {len(failed)} item(ns).")
        return 1
    print("\nSmoke check OK — piloto local saudável.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

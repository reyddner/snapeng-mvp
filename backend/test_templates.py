from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"

print(f"BASE_DIR: {BASE_DIR}")
print(f"TEMPLATES_DIR: {TEMPLATES_DIR}")
print(f"Templates dir existe: {TEMPLATES_DIR.exists()}")
print(f"Dashboard existe: {(TEMPLATES_DIR / 'dashboard.html').exists()}")
print(f"Base existe: {(TEMPLATES_DIR / 'base.html').exists()}")
print(f"Navbar existe: {(TEMPLATES_DIR / 'components' / 'navbar.html').exists()}")


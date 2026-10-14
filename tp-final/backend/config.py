import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_dotenv() -> None:
    """Carga `tp-final/.env` sin pisar variables que ya estén definidas."""
    path = ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"'))


load_dotenv()

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "")
AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID", "")
AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE", "")

# Con Auth0 configurado se entra con Google; si no, con usuario y contraseña. "dev" (entrar solo con un nombre)
# queda para los tests y los scripts de datos, o con GYMBRO_AUTH=dev.
AUTH_MODE = "auth0" if AUTH0_DOMAIN else os.environ.get("GYMBRO_AUTH", "local")

DB_PATH = Path(os.environ.get("GYMBRO_DB", ROOT / "gymbro.db"))

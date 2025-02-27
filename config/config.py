import os
from pathlib import Path

from dotenv import dotenv_values

BASE_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = BASE_DIR / "data"

ENV_VARIABLES = {
    **dotenv_values(dotenv_path=BASE_DIR / ".env"),
    **os.environ,
}
class Settings:
    # Aquí extraes la variable que necesitas; puedes definir un valor por defecto si lo deseas.
    MODALAB_DB_URL: str = ENV_VARIABLES.get("MODALAB_DB_URL", "")
    # Puedes agregar más variables si es necesario

# Instancia única de configuración para importar en otros módulos
settings = Settings()
import logging
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
    # Configuración para Vertex AI
    VERTEX_PROJECT: str = ENV_VARIABLES.get("VERTEX_PROJECT", "")
    VERTEX_REGION: str = ENV_VARIABLES.get("VERTEX_REGION", "us-central1")
    VERTEX_INDEX_ENDPOINT: str = ENV_VARIABLES.get("VERTEX_INDEX_ENDPOINT", "")
    VERTEX_DEPLOYED_INDEX_ID: str = ENV_VARIABLES.get("VERTEX_DEPLOYED_INDEX_ID", "")
    VERTEX_API_ENDPOINT: str = ENV_VARIABLES.get("VERTEX_API_ENDPOINT", "")


# Instancia única de configuración para importar en otros módulos
settings = Settings()


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    logger.addHandler(handler)

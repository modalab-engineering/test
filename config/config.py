import logging
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    # DB
    MODALAB_DB_URL: Optional[str] = None
    INSTANCE_CONNECTION_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASS: Optional[str] = None
    DB_NAME: Optional[str] = None

    # Vector DB
    VERTEX_PROJECT: str = Field(..., description="Vertex Project")
    VERTEX_REGION: str = Field(..., description="Vertex Region")
    VERTEX_INDEX_ENDPOINT: str = Field(..., description="Vertex index endpoint")
    VERTEX_DEPLOYED_INDEX_ID: str = Field(
        ..., description="Vertex deployed index id (streaming)"
    )
    VERTEX_API_ENDPOINT: str = Field(..., description="Vertex API endpoint")
    PRIVATE_IP: bool = Field(False)

    # API
    ROOT_PATH: str = Field(default="dev", description="API environment")

    class Config:
        env_file = ".env"


settings = Settings()


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    logger.addHandler(handler)

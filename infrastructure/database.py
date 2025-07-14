from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.config import settings

if settings.INSTANCE_CONNECTION_NAME:
    print(f"Connecting to Cloud SQL instance: {settings.INSTANCE_CONNECTION_NAME}")
    if not all([settings.DB_USER, settings.DB_PASS, settings.DB_NAME]):
        raise ValueError(
            "DB_USER, DB_PASS, and DB_NAME must be set for Cloud SQL connection."
        )

    ip_type = IPTypes.PRIVATE if settings.PRIVATE_IP else IPTypes.PUBLIC
    connector = Connector(ip_type=ip_type, refresh_strategy="LAZY")

    def getconn():
        return connector.connect(
            settings.INSTANCE_CONNECTION_NAME,
            "pg8000",
            user=settings.DB_USER,
            password=settings.DB_PASS,
            db=settings.DB_NAME,
        )

    engine = create_engine(
        "postgresql+pg8000://", creator=getconn, pool_pre_ping=True, pool_recycle=1800
    )
else:
    engine = create_engine(
        settings.MODALAB_DB_URL, pool_pre_ping=True, pool_recycle=1800
    )


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.config import settings

engine = create_engine(settings.MODALAB_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

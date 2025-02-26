from .vector_db import get_async_client
from .vector_db import get_client as get_vector_db_client


def init_dependencies():
    get_vector_db_client()

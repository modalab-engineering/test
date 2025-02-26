import qdrant_client

from config import ENV_VARIABLES

QDRANT_HOST_URL = ENV_VARIABLES.get("QDRANT_HOST_URL", "0.0.0.0")  # noqa: S104
QDRANT_PORT = int(ENV_VARIABLES.get("QDRANT_PORT", 6333))
QDRANT_API_KEY = ENV_VARIABLES.get("QDRANT_API_KEY", None)

COLLECTION_NAME = ENV_VARIABLES.get("COLLECTION_NAME", "modalab_products")

collection_exists = False
CLIENT_: qdrant_client.QdrantClient = None
ASYNC_CLIENT_: qdrant_client.AsyncQdrantClient = None


def get_client():
    global CLIENT_
    if not CLIENT_:
        CLIENT_ = qdrant_client.QdrantClient(
            url=QDRANT_HOST_URL,
            port=QDRANT_PORT,
            api_key=QDRANT_API_KEY,
        )
    return CLIENT_


def get_async_client():
    global ASYNC_CLIENT_
    if not ASYNC_CLIENT_:
        ASYNC_CLIENT_ = qdrant_client.AsyncQdrantClient(
            url=QDRANT_HOST_URL,
            port=QDRANT_PORT,
            api_key=QDRANT_API_KEY,
        )
    return ASYNC_CLIENT_

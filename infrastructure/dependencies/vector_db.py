from types import SimpleNamespace

from google.cloud import aiplatform

from config import ENV_VARIABLES

PROJECT_ID = ENV_VARIABLES.get("VERTEX_PROJECT", "")
REGION = ENV_VARIABLES.get("VERTEX_REGION", "us-central1")
INDEX_ENDPOINT = ENV_VARIABLES.get("VERTEX_INDEX_ENDPOINT", "")
DEPLOYED_INDEX_ID = ENV_VARIABLES.get("VERTEX_DEPLOYED_INDEX_ID", "")

CLIENT_ = None


class VertexVectorDBClient:
    def __init__(self) -> None:
        aiplatform.init(project=PROJECT_ID, location=REGION)
        self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=INDEX_ENDPOINT
        )

    def search(self, collection_name: str, query_vector: list[float], limit: int):
        response = self.index_endpoint.match(
            deployed_index_id=DEPLOYED_INDEX_ID,
            queries=[query_vector],
            num_neighbors=limit,
            return_full_datapoint=True,
        )
        neighbors = response[0].neighbors
        results = []
        for neighbor in neighbors:
            payload = neighbor.datapoint.metadata or {}
            results.append(SimpleNamespace(payload=payload))
        return results

    def upsert(self, collection_name: str, points: list):
        datapoints = []
        for p in points:
            datapoints.append(
                {
                    "datapoint_id": str(p["id"]),
                    "feature_vector": p["vector"],
                    "metadata": p.get("payload", {}),
                }
            )
        self.index_endpoint.upsert_datapoints(
            deployed_index_id=DEPLOYED_INDEX_ID, datapoints=datapoints
        )


def get_client() -> VertexVectorDBClient:
    global CLIENT_
    if CLIENT_ is None:
        CLIENT_ = VertexVectorDBClient()
    return CLIENT_


def get_async_client() -> VertexVectorDBClient:
    return get_client()


def get_existing_ids(client: VertexVectorDBClient, collection_name: str) -> set:
    # Listing datapoints is not directly supported; return empty set
    return set()


def upsert_points(client: VertexVectorDBClient, collection_name: str, points: list):
    client.upsert(collection_name=collection_name, points=points)

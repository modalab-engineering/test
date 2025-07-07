from types import SimpleNamespace

from google.cloud import aiplatform_v1

from config import ENV_VARIABLES

PROJECT_ID = ENV_VARIABLES.get("VERTEX_PROJECT", "")
REGION = ENV_VARIABLES.get("VERTEX_REGION", "us-central1")
INDEX_ENDPOINT = ENV_VARIABLES.get("VERTEX_INDEX_ENDPOINT", "")
DEPLOYED_INDEX_ID = ENV_VARIABLES.get("VERTEX_DEPLOYED_INDEX_ID", "")
API_ENDPOINT = ENV_VARIABLES.get("VERTEX_API_ENDPOINT", "")

CLIENT_ = None


class VertexVectorDBClient:
    def __init__(self) -> None:
        client_options = {}
        if API_ENDPOINT:
            client_options["api_endpoint"] = API_ENDPOINT

        self.match_client = aiplatform_v1.MatchServiceClient(
            client_options=client_options or None,
        )
        self.index_client = aiplatform_v1.IndexServiceClient(
            client_options=client_options or None,
        )

    def search(self, collection_name: str, query_vector: list[float], limit: int):
        datapoint = aiplatform_v1.IndexDatapoint(feature_vector=query_vector)
        query = aiplatform_v1.FindNeighborsRequest.Query(
            datapoint=datapoint,
            neighbor_count=limit,
        )

        request = aiplatform_v1.FindNeighborsRequest(
            index_endpoint=INDEX_ENDPOINT,
            deployed_index_id=DEPLOYED_INDEX_ID,
            queries=[query],
            return_full_datapoint=True,
        )

        response = self.match_client.find_neighbors(request=request)
        neighbors = response.nearest_neighbors[0].neighbors
        results = []
        for neighbor in neighbors:
            payload = neighbor.datapoint.metadata or {}
            results.append(SimpleNamespace(payload=payload))
        return results

    def upsert(self, collection_name: str, points: list):
        datapoints = []
        for p in points:
            datapoints.append(
                aiplatform_v1.IndexDatapoint(
                    datapoint_id=str(p["id"]),
                    feature_vector=p["vector"],
                    metadata=p.get("payload", {}),
                )
            )

        request = aiplatform_v1.UpsertDatapointsRequest(
            index=collection_name,
            datapoints=datapoints,
        )

        self.index_client.upsert_datapoints(request=request)


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

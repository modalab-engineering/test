import re
from types import SimpleNamespace
from typing import List, Set, Tuple

from google.api_core import exceptions as gexc
from google.cloud import aiplatform_v1

from config import ENV_VARIABLES

PROJECT_ID = ENV_VARIABLES.get("VERTEX_PROJECT", "")
REGION = ENV_VARIABLES.get("VERTEX_REGION", "us-central1")
INDEX_ENDPOINT = ENV_VARIABLES.get("VERTEX_INDEX_ENDPOINT", "")
DEPLOYED_INDEX_ID = ENV_VARIABLES.get("VERTEX_DEPLOYED_INDEX_ID", "")
API_ENDPOINT = ENV_VARIABLES.get("VERTEX_API_ENDPOINT", "")


CLIENT_ = None
CHUNK_ = 1_000


class VertexVectorDBClient:
    def __init__(self) -> None:
        client_options = {}
        if API_ENDPOINT:
            client_options["api_endpoint"] = API_ENDPOINT

        match_client_options = {"api_endpoint": API_ENDPOINT}
        endpoint_client_options = {
            "api_endpoint": f"{REGION}-aiplatform.googleapis.com"
        }

        self.match_client = aiplatform_v1.MatchServiceClient(
            client_options=match_client_options or None,
        )
        self.index_client = aiplatform_v1.IndexServiceClient(
            client_options=endpoint_client_options or None,
        )

    def search(self, query_vector: list[float], limit: int):
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
            id_ = neighbor.datapoint.datapoint_id
            results.append(SimpleNamespace(payload=int(id_)))
        return results

    def upsert(self, collection_name: str, points: list):
        datapoints = []
        for p in points:
            datapoints.append(
                aiplatform_v1.IndexDatapoint(
                    datapoint_id=str(p["id"]),
                    feature_vector=p["vector"],
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


def _parse_missing_ids(msg: str) -> Set[str]:
    return set(re.findall(r"\d+", msg))


def get_existing_ids(
    client: VertexVectorDBClient,
    candidate_ids: List[str],
) -> Tuple[Set[str], Set[str]]:
    unsaved: Set[str] = set()
    saved: Set[str] = set()

    for i in range(0, len(candidate_ids), CHUNK_):
        batch = candidate_ids[i : i + CHUNK_]

        queries = [
            aiplatform_v1.FindNeighborsRequest.Query(
                datapoint=aiplatform_v1.IndexDatapoint(datapoint_id=str(pid)),
                neighbor_count=1,
            )
            for pid in batch
        ]

        request = aiplatform_v1.FindNeighborsRequest(
            index_endpoint=INDEX_ENDPOINT,
            deployed_index_id=DEPLOYED_INDEX_ID,
            queries=queries,
            return_full_datapoint=False,
        )

        try:
            response = client.match_client.find_neighbors(request=request)

            for pid, nn in zip(batch, response.nearest_neighbors):
                if not nn.neighbors:
                    unsaved.add(pid)

        except gexc.NotFound as err:
            missing_ids = _parse_missing_ids(err.message or "")
            if missing_ids:
                unsaved.update({int(id_str) for id_str in missing_ids})
            else:
                unsaved.update({int(pid) for pid in batch})

    saved = {id for id in candidate_ids if id not in unsaved}

    return unsaved, saved


def upsert_points(client: VertexVectorDBClient, collection_name: str, points: list):
    client.upsert(collection_name=collection_name, points=points)

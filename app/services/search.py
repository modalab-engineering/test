import torch
from transformers import CLIPModel, CLIPProcessor

from app.schemas import Product, SearchByDescription, SearchResponse
from config import settings
from infrastructure.dependencies import get_vector_db_client


class SearchService:
    def __init__(self):
        self.processor = CLIPProcessor.from_pretrained(
            settings.MODEL_PATH, cache_dir=settings.CACHE_DIR
        )
        self.model = CLIPModel.from_pretrained(
            settings.MODEL_PATH, cache_dir=settings.CACHE_DIR
        )
        self.client = get_vector_db_client()

    async def generate_text_embedding(self, text: str):
        inputs_text = self.processor(text=[text], return_tensors="pt", padding=True)
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs_text)
        return (
            (text_features / text_features.norm(p=2, dim=-1, keepdim=True))
            .numpy()
            .flatten()
            .tolist()
        )

    async def search(self, input: SearchByDescription) -> SearchResponse:
        text_embedding = await self.generate_text_embedding(input.text)

        search_result = self.client.search(
            query_vector=text_embedding,
            limit=input.top_k,
        )

        products = []
        for item in search_result:
            payload = item.payload
            product = Product(id=payload)
            products.append(product)

        return SearchResponse(products=products)

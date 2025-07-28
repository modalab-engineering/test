from io import BytesIO

import requests
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

from app.schemas import (
    Product,
    SearchByDescription,
    SearchByImage,
    SearchByImageUrl,
    SearchResponse,
)
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

    async def generate_image_embedding(self, image: Image.Image):
        inputs = self.processor(images=image, return_tensors="pt")
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
        return (
            (image_features / image_features.norm(p=2, dim=-1, keepdim=True))
            .numpy()
            .flatten()
            .tolist()
        )

    async def _search_with_embedding(
        self, embedding: list[float], top_k: int, followed_stores: list[int] | None
    ) -> SearchResponse:
        search_result = self.client.search(
            query_vector=embedding,
            limit=top_k,
            followed_stores=followed_stores,
        )

        products = []
        for item in search_result:
            payload = item.payload
            product = Product(id=payload, similarity_score=item.similarity_score)
            products.append(product)

        return SearchResponse(products=products)

    async def search(self, input: SearchByDescription) -> SearchResponse:
        text_embedding = await self.generate_text_embedding(input.text)
        return await self._search_with_embedding(
            text_embedding, input.top_k, input.followed_stores
        )

    async def search_by_image(
        self, input: SearchByImage, image_bytes: bytes
    ) -> SearchResponse:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        image_embedding = await self.generate_image_embedding(image)
        return await self._search_with_embedding(
            image_embedding, input.top_k, input.followed_stores
        )

    async def search_by_image_url(self, input: SearchByImageUrl) -> SearchResponse:
        response = requests.get(input.url.strip(), timeout=10)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image_embedding = await self.generate_image_embedding(image)
        return await self._search_with_embedding(
            image_embedding, input.top_k, input.followed_stores
        )

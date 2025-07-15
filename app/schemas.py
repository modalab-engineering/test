from typing import List

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    top_k: int = Field(
        default=25, description="Number of results to return for each store."
    )


class SearchByDescription(SearchRequest):
    text: str = Field(
        description="Text to search for.",
        examples=["Crochet bags", "Statement earrings", "Red dress"],
    )
    followed_stores: List[int] = Field(
        default=None, description="Followd client stores"
    )


class Product(BaseModel):
    id: str | int = Field(description="Product ID", examples=["1234", 5678])


class SearchResponse(BaseModel):
    products: list[Product] = Field(..., description="List of products found.")

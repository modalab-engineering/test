from transformers import CLIPModel, CLIPProcessor

from app.schemas import SearchByDescription, SearchResponse


class SearchService:
    def __init__(self):
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

    async def search(cls, input: SearchByDescription) -> SearchResponse:
        return {"id": [input.text, "123"]}

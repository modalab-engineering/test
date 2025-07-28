from typing import Annotated, List

from fastapi import APIRouter, File, Form, status

import app.schemas as schemas
from config.globals import MODELS

router = APIRouter(
    prefix="/search",
    tags=["search"],
)


async def _search(request: schemas.SearchRequest) -> list[schemas.Product]:
    result = await MODELS["search"].search(input=request)
    return result.products


@router.post(
    "/description",
    status_code=status.HTTP_200_OK,
    response_model=list[schemas.Product],
)
async def search_description(
    request: schemas.SearchByDescription,
) -> list[schemas.Product]:
    """Search for products by using a description."""
    return await _search(request=request)


@router.post(
    "/image-url",
    status_code=status.HTTP_200_OK,
    response_model=list[schemas.Product],
)
async def search_image_url(
    request: schemas.SearchByImageUrl,
) -> list[schemas.Product]:
    """Search for products by using an image URL."""
    result = await MODELS["search"].search_by_image_url(input=request)
    return result.products


@router.post(
    "/image",
    status_code=status.HTTP_200_OK,
    response_model=list[schemas.Product],
)
async def search_image(
    image: Annotated[bytes, File(..., description="Image file")],
    top_k: Annotated[int, Form(25)] = 25,
    followed_stores: Annotated[List[int] | None, Form(None)] = None,
) -> list[schemas.Product]:
    """Search for products by uploading an image."""
    request = schemas.SearchByImage(top_k=top_k, followed_stores=followed_stores)
    result = await MODELS["search"].search_by_image(input=request, image_bytes=image)
    return result.products

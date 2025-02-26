from fastapi import APIRouter, status

import app.schemas as schemas
from config.globals import MODELS

router = APIRouter(
    prefix="/search",
    tags=["search"],
)


async def _search(request: schemas.SearchRequest) -> list[schemas.Product]:
    result = await MODELS["search"].search(input=request)
    return result


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

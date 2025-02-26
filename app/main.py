from contextlib import asynccontextmanager
from typing import Any

import orjson
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.api import api_router
from app.services import SearchService
from config import ENV_VARIABLES
from config.globals import MODELS
from infrastructure.dependencies import init_dependencies

ROOT_PATH = ENV_VARIABLES.get("ROOT_PATH", "local")


class CustomORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return orjson.dumps(content, option=orjson.OPT_INDENT_2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_dependencies()
    MODELS["search"] = SearchService()
    yield


app = FastAPI(
    default_response_class=CustomORJSONResponse,
    lifespan=lifespan,
    root_path=f"/{ROOT_PATH}" if ROOT_PATH != "local" else "",
)


app.include_router(api_router)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> str:
    return f"Running on {ROOT_PATH}!"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)  # noqa: S104

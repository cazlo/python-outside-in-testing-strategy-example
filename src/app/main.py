from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router as api_router_v1
from app.core.config import ModeEnum, settings
from app.utils.fastapi_globals import GlobalsMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("startup fastapi")
    yield
    # shutdown
    print("finished shutdown of fastapi")


# Core Application Instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)


app.add_middleware(
    SQLAlchemyMiddleware,
    db_url=str(settings.ASYNC_DATABASE_URI),
    engine_args={
        "echo": False,
        "poolclass": (
            NullPool if settings.MODE == ModeEnum.testing else AsyncAdaptedQueuePool
        ),
    },
)
app.add_middleware(GlobalsMiddleware)

# Set all CORS origins enabled
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
async def root():
    """
    An example "Hello world" FastAPI route.
    """
    return {"message": "Hello World"}


# Add Routers
app.include_router(api_router_v1, prefix=settings.API_V1_STR)

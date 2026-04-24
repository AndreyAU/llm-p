from fastapi import FastAPI

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    @app.on_event("startup")
    async def on_startup() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {
            "status": "ok",
            "env": settings.env,
        }

    return app


app = create_app()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.router import router

_app: FastAPI | None = None


def get_application() -> FastAPI:
    global _app

    if _app is not None:
        return _app

    _app = FastAPI(title=settings.PROJECT_NAME)

    if settings.CORS_ENABLED:
        _app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        _app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    _app.include_router(router)

    return _app

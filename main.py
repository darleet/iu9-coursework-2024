from app.core.config import settings
from app.main import get_application

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(get_application(), host=settings.APP_HOST, port=settings.APP_PORT)

from fastapi import FastAPI

from app.api.routes import router
from app.config import settings
from app.utils.logger import configure_logging


configure_logging()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Production Log Analyzer API"
)


app.include_router(
    router,
    prefix=settings.API_PREFIX
)
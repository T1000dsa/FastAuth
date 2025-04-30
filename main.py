from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
import logging

from src.core.config.config import settings
from src.core.services.database.postgres.dd_helper import db_helper, settings


logger = logging.getLogger(__name__)
logger.debug(settings)
app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    try:
        await db_helper.dispose()
        logger.debug("✅ Connection pool closed cleanly")
    except Exception as e:
        logger.warning(f"⚠️ Error closing connection pool: {e}")

@app.get('/ping')
async def some_func():
    return 'pong'

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
        log_level="warning"  # Reduce log verbosity
        )
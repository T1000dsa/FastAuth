from fastapi import APIRouter
import logging

from src.core.dependencies.db_helper import DBDI


logger = logging.getLogger(__name__)
router = APIRouter()

@router.get('/ping')
async def some_func(db:DBDI):
    logger.info(f'{db.is_active=}')
    logger.info('Everything is fine.')
    return 'pong'
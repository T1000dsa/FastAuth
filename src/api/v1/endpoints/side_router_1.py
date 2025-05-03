from fastapi import APIRouter
import logging

from src.core.dependencies.db_helper import DBDI
from src.core.services.user.user import UserService


logger = logging.getLogger(__name__)
router = APIRouter()

@router.get('/all_users')
async def get_all_users(
    session:DBDI
    ):
    user = UserService(session=session)
    data = await user.get_all_users()
    return data

@router.delete('/all_users')
async def del_all_users(
    session:DBDI
):
    user = UserService(session=session)

    data = await user.delete_all_users()
    return data
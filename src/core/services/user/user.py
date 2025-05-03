from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging
from passlib.context import CryptContext

from src.core.services.database.postgres.models.user import UserModel
from src.api.v1.orm.user_orm import select_user_email, select_data_user, insert_data, get_all_users, delete_users
from src.core.schemas.pydantic_schemas.user import UserSchema


logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    #Not for production, delete later
    async def get_all_users(self) -> list[UserModel]:
        return await get_all_users(self.session)
    
    #Not for production, delete later
    async def delete_all_users(self) -> None:
        return await delete_users(self.session)
    
    async def get_user_by_username(self, username: str) -> Optional[UserModel]:
        return await select_data_user(self.session, username)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[UserModel]:
        user = await self.get_user_by_username(username)
        if not user:
            return None
        return user
    
    async def create_user(self, data: UserSchema) -> None:
        await insert_data(self.session, data)
    
    def create_access_token(self, data: dict) -> str:
        # Implement JWT creation
        pass
    
    def verify_access_token(self, token: str) -> Optional[UserModel]:
        # Implement JWT verification
        pass
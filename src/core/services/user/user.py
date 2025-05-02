from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging
from passlib.context import CryptContext

from src.core.services.database.postgres.models.user import UserModel
from src.api.v1.orm.user_orm import select_user_email, select_data_user, insert_data
from src.core.schemas.pydantic_schemas.user import UserSchema

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        return await select_user_email(self.session, email)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        user = await self.get_user_by_email(email)
        if not user or not user.check_password(password):
            return None
        return user
    
    async def create_user(self, data: UserSchema) -> UserModel:
        hashed_password = ''#pwd_context.hash(data.password)
        user_data = data.model_dump(exclude={"password_again"})
        user_data["hashed_password"] = hashed_password
        return await insert_data(self.session, user_data)
    
    def create_access_token(self, data: dict) -> str:
        # Implement JWT creation
        pass
    
    def verify_access_token(self, token: str) -> Optional[UserModel]:
        # Implement JWT verification
        pass
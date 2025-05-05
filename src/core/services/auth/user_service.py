from fastapi import Response, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta, timezone
import logging

from src.core.config.config import settings
from src.core.services.auth.token_service import TokenService
from src.core.schemas.pydantic_schemas.auth_schema import RefreshToken
from src.core.services.database.postgres.models.user import UserModel
from src.core.schemas.pydantic_schemas.user import UserSchema
from src.core.services.database.postgres.orm.user_orm import (
    select_data_user, 
    insert_data, 
    get_all_users, 
    delete_users, 
    select_data_user_id
    )
from src.core.config.auth_config import REFRESH_TYPE



logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, session: AsyncSession, token_service: TokenService):
        self.session = session
        self.token_service = token_service  # Use injected service

    #Not for production, delete later
    async def get_all_users(self) -> list[UserModel]:
        return await get_all_users(self.session)
    
    #Not for production, delete later
    async def delete_all_users(self) -> None:
        return await delete_users(self.session)
    
    async def get_user_by_username(self, username: str, password:str) -> Optional[UserModel]:
        return await select_data_user(self.session, username, password)
    
    async def get_user_by_id(self, user_id:int) -> Optional[UserModel]:
        return await select_data_user_id(self.session, user_id)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        user = await self.get_user_by_username(username, password)
        if not user:
            return None
            
        try:
            # Create tokens
            tokens = await self.token_service.create_both_tokens({"sub": str(user.id)})
            
            # Store refresh token
            await self.token_service.store_refresh_token(
                session=self.session,
                user_id=user.id,
                raw_token=tokens[REFRESH_TYPE]
            )
            
            return tokens
            
        except Exception as err:
            logger.error(f'Authentication failed: {err}')
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication processing failed"
            )
    
    async def create_user(self, data: UserSchema) -> None:
        await insert_data(self.session, data)
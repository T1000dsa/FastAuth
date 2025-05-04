from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional
import logging
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt

from src.core.services.database.postgres.models.refresh_token import RefreshTokenModel
from src.core.services.database.postgres.models.user import UserModel
from src.core.services.database.postgres.orm.user_orm import select_data_user, insert_data, get_all_users, delete_users
from src.core.schemas.pydantic_schemas.user import UserSchema
from src.core.schemas.pydantic_schemas.auth_schema import RefreshToken
from src.core.services.user.token_service import token_service
from src.core.config.auth_config import (
    SECRET_KEY, 
    ALGORITHM, 
    ACCESS_TYPE, 
    REFRESH_TYPE, 
    ACCESS_TOKEN_EXPIRE_MINUTES, 
    REFRESH_TOKEN_EXPIRE_DAYS,
    credentials_exception
    )


logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.token_service = token_service  # Composition over inheritanc

    #Not for production, delete later
    async def get_all_users(self) -> list[UserModel]:
        return await get_all_users(self.session)
    
    #Not for production, delete later
    async def delete_all_users(self) -> None:
        return await delete_users(self.session)
    
    async def get_user_by_username(self, username: str, password:str) -> Optional[UserModel]:
        return await select_data_user(self.session, username, password)
    
    async def authenticate_user(self, username: str, password:str) -> Optional[UserModel]:
        user = await self.get_user_by_username(username, password)
        if not user:
            return None
        else:
            data_user = {"sub": str(user.id)}
            access_token = await self.token_service.create_access_token(
                data=data_user
                )
            
            refresh_token = await self.token_service.create_refresh_token(
                data=data_user
                )
            return {ACCESS_TYPE:access_token, REFRESH_TYPE:refresh_token}
    
    async def create_user(self, data: UserSchema) -> None:
        await insert_data(self.session, data)
    

    async def rotate_refresh_token(self, old_token: str, user_moderl: UserModel) -> tuple[str, str]:
        # 1. Verify and decode old token
        try:
            payload:dict = self.token_service.verify_token(old_token)
            if payload.get("type") != REFRESH_TYPE:
                raise HTTPException(status_code=400, detail="Not a refresh token")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # 2. Check if token was already used/revoked
        hashed_token = self.token_service.hash_token(old_token)
        stored_token:RefreshTokenModel = await self.token_service.get_refresh_token(hashed_token)
        
        if stored_token and (stored_token.revoked or stored_token.replaced_by_token):
            # Critical security event - someone might be trying to reuse a stolen token
            await self.token_service.revoke_all_user_tokens(self.session, user_moderl)
            raise HTTPException(status_code=401, detail="Token was reused - possible theft")
        
        # 3. Create new tokens
        new_access_token = await self.token_service.create_access_token(
            data={"sub": str(user_moderl.id)}
        )
        
        new_refresh_token = await self.token_service.create_refresh_token(
            data={"sub": str(user_moderl.id)}
        )
        token = self.token_service.hash_token(new_refresh_token)
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        token_data = RefreshToken(
            user_id=user_moderl.id,
            token=token,
            expires_at=expires_at
            )
        await self.token_service.store_refresh_token(
            token_data
        )
        
        # 5. Revoke old token
        if stored_token:
            await self.token_service.revoke_token(stored_token.id, replaced_by=new_refresh_token)
        
        return new_access_token, new_refresh_token
    
    